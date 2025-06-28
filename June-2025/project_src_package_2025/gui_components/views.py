from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QFormLayout,
    QLineEdit, QMessageBox, QCheckBox, QTextEdit
)

from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt

from . import parmas_config
from . import controller
from . import stdout_redirector
from . import output_display_widget
from . import aux_gui_funcs

from . import computation_history_entry
from . import history_cache


class ControlPanel(QWidget):
    def __init__(self, history_dropdown, main_window, parent=None):
        super().__init__(parent)
        self.history_dropdown = history_dropdown
        self.main_window = main_window

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Dropdown to select computation
        self.comp_label = QLabel("Select Computation:")
        self.comp_select = QComboBox()
        self.comp_select.addItems(parmas_config.PARAMETER_SCHEMAS.keys())
        self.comp_select.currentTextChanged.connect(self.update_parameter_fields)

        # Parameter form
        self.param_form = QFormLayout()
        self.param_inputs = {}

        # Advanced toggle
        self.advanced_toggle = QCheckBox("Show Advanced Parameters")
        self.advanced_toggle.stateChanged.connect(self.toggle_advanced_fields)
        self.advanced_widgets = []

        # Output display for MFPT and other information
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)

        self.mfpt_label = QLabel("MFPT: ")
        self.duration_label = QLabel("")
        self.duration_label.hide()

        # Launch button with status color
        self.launch_button = QPushButton("Launch")
        self.launch_button.clicked.connect(self.run_computation)
        self.set_launch_color("idle")

        # Assemble layout
        self.layout.addWidget(self.comp_label)
        self.layout.addWidget(self.comp_select)
        self.layout.addLayout(self.param_form)
        self.layout.addWidget(self.advanced_toggle)
        self.layout.addWidget(self.launch_button)
        self.layout.addWidget(self.mfpt_label)
        self.layout.addWidget(self.output_display)

        self.output_files_widget = output_display_widget.OutputFilesWidget()
        self.layout.addWidget(self.output_files_widget)
        self.output_files_widget.hide()

        # Initialize parameter fields
        self.update_parameter_fields(self.comp_select.currentText())

    def update_parameter_fields(self, computation_name):
        # Clear previous inputs
        for i in reversed(range(self.param_form.count())):
            self.param_form.removeRow(i)

        self.param_inputs.clear()
        self.advanced_widgets.clear()

        schema = parmas_config.PARAMETER_SCHEMAS[computation_name]

        # Add required fields
        for param, default in schema.get("required", []):
            input_field = QLineEdit()
            self.param_form.addRow(f"{param}:", input_field)
            self.param_inputs[param] = input_field

        # Add default/advanced fields (initially hidden)
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

        try:
            inputs = {param: field.text() for param, field in self.param_inputs.items()}
            result = controller.run_selected_computation(self.comp_select.currentText(), inputs)
            print(f"Result: {result}")  # For now, log result in terminal

            if isinstance(result, dict):
                if "MFPT" in result:
                    self.mfpt_label.setText(f"MFPT: {result['MFPT']:.6f}")
                    self.output_display.append(f"Computation returned MFPT = {result['MFPT']:.6f}\n")
                if "duration" in result:
                    self.duration_label.setText(f"Duration: {result['duration']:.6f} seconds")
                    self.duration_label.show()
            self.set_launch_color("success")

            csv_paths = []
            png_paths = []

            if "output_dirs" in result:
                csv_paths, png_paths = aux_gui_funcs.extract_csv_and_png_paths(result["output_dirs"])
                if csv_paths or png_paths:
                    self.output_files_widget.update_display(csv_paths, png_paths)
                    self.output_files_widget.show()
                else:
                    self.output_files_widget.hide()
            else:
                self.output_files_widget.hide()

            record = computation_history_entry.ComputationRecord(
                comp_type=self.comp_select.currentText(),
                params=inputs,
                mfpt=result.get("MFPT"),
                duration=result.get("duration"),
                csv_files=csv_paths,
                png_files=png_paths
            )

            history_cache.cache.add_entry(record)
            self.history_dropdown.addItem(record.display_name())

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.set_launch_color("error")

    def load_entry(self, entry):
        # Update labels
        if entry.mfpt is not None:
            self.mfpt_label.setText(f"MFPT: {entry.mfpt:.6f}")
        else:
            self.mfpt_label.setText("MFPT: ")

        if entry.duration is not None:
            self.duration_label.setText(f"Duration: {entry.duration:.6f} seconds")
            self.duration_label.show()
        else:
            self.duration_label.hide()

        # Update output files
        self.output_files_widget.update_display(entry.csv_files or [], entry.png_files or [])
        self.output_files_widget.show()


