from . import (QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QFormLayout,
               QCheckBox, QTextEdit, QMessageBox, QWidget, QHBoxLayout, QColor, QPalette,
               Qt, computation_history_entry, history_cache, controller, aux_gui_funcs, job_queue)


class ComputationalControls(QWidget):

    def __init__(self, parent_panel):
        super().__init__()
        self.panel = parent_panel
        self.param_inputs = {}
        self.advanced_widgets = []

        # UI elements

        self.comp_select = QComboBox()
        self.comp_select.addItems(self.panel.comp_schemas.keys())
        self.comp_select.currentTextChanged.connect(self.update_parameter_fields)

        self.param_form = QFormLayout()
        self.advanced_toggle = QCheckBox("Show Advanced Parameters")
        self.advanced_toggle.stateChanged.connect(self.toggle_advanced_fields)

        self.launch_button = QPushButton("Launch")
        self.launch_button.clicked.connect(self.run_computation)

        self.enqueue_button = QPushButton("+")
        self.enqueue_button.setToolTip("Add to Job Queue")
        self.enqueue_button.clicked.connect(self.enqueue_job)

        self.set_launch_color("idle")

        self.mfpt_label = QLabel("MFPT: ")
        self.duration_label = QLabel("")
        self.duration_label.hide()

        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setFixedHeight(1)

        # Assemble layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Select Computation: "))
        self.layout.addWidget(self.comp_select)
        self.layout.addLayout(self.param_form)
        self.layout.addWidget(self.advanced_toggle)

        # Horizontal layout for Launch and Enqueue

        button_row = QHBoxLayout()
        button_row.addWidget(self.launch_button)
        button_row.addWidget(self.enqueue_button)
        self.layout.addLayout(button_row)
        self.layout.addWidget(self.mfpt_label)
        self.layout.addWidget(self.output_display)

        self.update_parameter_fields(self.comp_select.currentText())

    def update_parameter_fields(self, computation_name):
        while self.param_form.count():
            self.param_form.removeRow(0)
        self.param_inputs.clear()
        self.advanced_widgets.clear()

        schema = self.panel.comp_schemas[computation_name]

        for param, _ in schema.get("required", []):
            input_field = QLineEdit()
            self.param_form.addRow(f"{param}:", input_field)
            self.param_inputs[param] = input_field

        for param, value in schema.get("default", []):
            input_field = QLineEdit(str(value))
            self.param_inputs[param] = input_field
            label = QLabel(f"{param}:")
            label.setVisible(False)
            input_field.setVisible(False)
            self.param_form.addRow(label, input_field)
            self.advanced_widgets.append((label, input_field))

    def toggle_advanced_fields(self, state):
        show = state == Qt.Checked
        for label, field in self.advanced_widgets:
            label.setVisible(show)
            field.setVisible(show)

    def set_launch_color(self, state):
        palette = self.launch_button.palette()
        color = QColor("lightgray")
        if state == "running":
            color = QColor("lightblue")
        elif state == "success":
            color = QColor("lightgreen")
        elif state == "error":
            color = QColor("lightcoral")

        palette.setColor(QPalette.Button, color)
        self.launch_button.setAutoFillBackground(True)
        self.launch_button.setPalette(palette)
        self.launch_button.update()

    def run_computation(self):
        self.set_launch_color("running")
        self.output_display.clear()
        self.mfpt_label.setText("MFPT: ")
        self.duration_label.hide()

        # Validate inputs
        inputs = {}
        missing_fields = []
        for param, field in self.param_inputs.items():
            value = field.text().strip()
            if not value:
                missing_fields.append(param)
            else:
                inputs[param] = value

        if missing_fields:
            QMessageBox.warning(self.panel, "Missing Input", f"Please fill in: {', '.join(missing_fields)}")
            self.set_launch_color("error")
            return

        comp_type = self.comp_select.currentText()

        status = "completed"
        error_msg = None
        csv_paths, png_paths = [], []

        try:
            result = controller.run_selected_computation(comp_type, inputs)

            if not isinstance(result, dict):
                raise ValueError(f"Computation '{comp_type}' did not return a dictionary. Got: {type(result).__name__}")

            if "MFPT" in result:
                self.mfpt_label.setText(f"MFPT: {result['MFPT']:.6f}")
                self.output_display.append(f"Computation returned MFPT = {result['MFPT']:.6f}\n")
            if "duration" in result:
                self.duration_label.setText(f"Duration: {result['duration']:.6f} seconds")
                self.duration_label.show()

            if "output_dirs" in result:
                csv_paths, png_paths = aux_gui_funcs.extract_csv_and_png_paths(result["output_dirs"])
                self.panel.output_files_widget.update_display(csv_paths, png_paths)
                self.panel.png_preview_widget.update_png_list(png_paths)
                self.panel.output_files_widget.show()
                self.panel.png_preview_widget.show()
            else:
                self.panel.output_files_widget.hide()
                self.panel.png_preview_widget.hide()

            self.set_launch_color("success")

        except Exception as e:
            result = {}
            status = "failed"
            error_msg = str(e)
            QMessageBox.critical(self.panel, "Error", str(e))
            self.set_launch_color("error")

        record = computation_history_entry.ComputationRecord(
            comp_type=comp_type,
            params=inputs,
            mfpt=result.get("MFPT"),
            duration=result.get("duration"),
            csv_files=csv_paths,
            png_files=png_paths,
            status=status,
            error_msg=error_msg
        )

        history_cache.cache.add_entry(record)
        self.panel.history_dropdown.addItem(record.display_name())

    def enqueue_job(self):

        inputs = {param: field.text() for param, field in self.param_inputs.items()}
        comp_type = self.comp_select.currentText()

        job = computation_history_entry.ComputationRecord(
            comp_type=comp_type,
            params=inputs,
            status="pending",
            time_for_execution=0
        )

        job_queue.global_queue.enqueue(job)
        self.output_display.append(f"Job enqueued: {job.display_name()}")
