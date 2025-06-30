from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFormLayout,
    QLineEdit, QMessageBox, QCheckBox, QTextEdit, QGroupBox, QSpinBox, QDoubleSpinBox,
    QSizePolicy
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt

from . import parmas_config
from . import controller
from . import stdout_redirector
from . import output_display_widget
from . import aux_gui_funcs

from . import computation_history_entry
from . import history_cache
from . import ani

import ast

import matplotlib.pyplot as plt


class ControlPanel(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.left_panel = QVBoxLayout()

        # Domain display

        # checkbox_group = QGroupBox("Domain Grid Options")

        title_label = QLabel("Domain Grid Options")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-weight: bold;")

        checkbox_group = QGroupBox()
        checkbox_layout = QVBoxLayout()
        checkbox_layout.setContentsMargins(10, 15, 10, 10)

        checkbox_layout.addWidget(title_label)

        self.display_extract_checkbox = QCheckBox("Display Extraction Region")
        self.toggle_border_checkbox = QCheckBox("Display Internal Borders")
        self.toggle_border_checkbox.setChecked(True)

        checkbox_layout.addWidget(self.display_extract_checkbox)
        checkbox_layout.addWidget(self.toggle_border_checkbox)

        checkbox_layout.addSpacing(15)

        # Now add the buttons below the checkboxes, in the same layout
        self.display_domain_button = QPushButton("Preview Domain")
        self.display_domain_button.clicked.connect(self.handle_display_domain)
        checkbox_layout.addWidget(self.display_domain_button)

        self.close_domain_button = QPushButton("Close Domain")
        self.close_domain_button.clicked.connect(self.close_domain)
        self.close_domain_button.hide()
        checkbox_layout.addWidget(self.close_domain_button)

        checkbox_group.setLayout(checkbox_layout)

        # Add the whole group box (checkbox + buttons) to the left panel
        self.left_panel.addWidget(checkbox_group)

        # History management

        self.history_dropdown = QComboBox()
        self.history_dropdown.addItem("Select Previous Computation: ")
        self.history_dropdown.currentIndexChanged.connect(self.load_history_entry)
        self.left_panel.addWidget(self.history_dropdown)

        for label in history_cache.cache.get_labels():
            self.history_dropdown.addItem(label)

        self.reset_params_button = QPushButton("Reset Parameters")
        self.reset_params_button.clicked.connect(self.clear_parameter_fields)
        self.left_panel.addWidget(self.reset_params_button)

        self.clear_button = QPushButton("Clear History")
        self.clear_button.clicked.connect(self.clear_history)
        self.left_panel.addWidget(self.clear_button)

        self.right_panel = QVBoxLayout()

        self.main_layout.addLayout(self.left_panel, stretch=2)
        self.main_layout.addLayout(self.right_panel, stretch=3)

        # Clearing outputs

        self.clear_output_button = QPushButton("Clear Outputs")
        self.clear_output_button.clicked.connect(self.clear_displayed_results)
        self.left_panel.addWidget(self.clear_output_button)

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
        self.left_panel.addWidget(self.comp_label)
        self.left_panel.addWidget(self.comp_select)
        self.left_panel.addLayout(self.param_form)
        self.left_panel.addWidget(self.advanced_toggle)
        self.left_panel.addWidget(self.launch_button)
        self.left_panel.addWidget(self.mfpt_label)
        self.left_panel.addWidget(self.output_display)

        self.png_preview_widget = output_display_widget.PNGPreviewWidget()
        self.right_panel.addWidget(self.png_preview_widget)
        # self.layout.addWidget(self.png_preview_widget)
        self.png_preview_widget.hide()

        self.output_files_widget = output_display_widget.OutputFilesWidget()
        self.right_panel.addWidget(self.output_files_widget)
        self.output_files_widget.hide()

        self.restored_label = QLabel("")
        self.restored_label.setStyleSheet("Color: blue; font-weight: bold;")
        self.restored_label.hide()

        self.right_panel.addWidget(self.restored_label, alignment=Qt.AlignRight)
        self.plot_layout = QVBoxLayout()
        self.right_panel.addLayout(self.plot_layout)
        self.right_panel.addStretch()

        # Initialize parameter fields
        self.update_parameter_fields(self.comp_select.currentText())

        # real time update of domain preview relative to updates of the microtubules
        # self.param_inputs["N_param"].textChanged.connect(self.update_microtubules_live)

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
                    self.png_preview_widget.update_png_list(png_paths)
                    self.png_preview_widget.show()
                else:
                    self.output_files_widget.hide()
                    self.png_preview_widget.hide()
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

    def set_computation(self, computation_name):
        self.comp_select.setCurrentText(computation_name)
        self.update_parameter_fields(computation_name)

    def set_parameters(self, params: dict):
        for key, val in params.items():
            if key in self.param_inputs:
                self.param_inputs[key].setText(str(val))

    def show_restored_message(self, record):
        label_text = f"Restored: {record.comp_type} ({record.timestamp})"
        self.restored_label.setText(label_text)
        self.restored_label.show()

    def clear_history(self):
        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            "Are you sure you want to delete all saved history?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            history_cache.cache.clear()
            self.history_dropdown.clear()
            self.history_dropdown.addItem("Select Previous Computation: ")
            self.clear_displayed_results()
            self.clear_parameter_fields()

    def clear_parameter_fields(self):
        self.update_parameter_fields(self.comp_select.currentText())
        self.mfpt_label.setText("MFPT: ")
        self.output_display.clear()

    def clear_displayed_results(self):
        self.output_files_widget.hide()
        self.png_preview_widget.hide()
        self.restored_label.hide()
        # self.png_preview_widget.update_png_list()

    def load_history_entry(self, index):
        if index == 0:
            return  # Ignore placeholder

        entry = history_cache.cache.get_entry(index - 1)
        if not entry:
            return

        self.set_computation(entry.comp_type)
        self.set_parameters(entry.params)

        if entry.mfpt is not None:
            self.mfpt_label.setText(f"MFPT: {entry.mfpt:.6f}")
        if entry.duration is not None:
            self.duration_label.setText(f"Duration: {entry.duration:.6f} seconds")
            self.duration_label.show()
        else:
            self.duration_label.hide()

        self.output_files_widget.update_display(entry.csv_files or [], entry.png_files or [])
        self.output_files_widget.show()

        self.show_restored_message(entry)
        self.png_preview_widget.update_png_list(entry.png_files or [])
        self.png_preview_widget.show()

    def handle_display_domain(self):

        try:
            plt.close('all')

            rings = int(self.param_inputs["rg_param"].text())
            rays = int(self.param_inputs["ry_param"].text())
            d_tube = float(self.param_inputs["d_tube"].text())

            try:
                microtubules_input = self.param_inputs["N_param"].text()
                parsed = ast.literal_eval(microtubules_input)
                microtubules = list(parsed) if isinstance(parsed, (list, tuple)) else [int(parsed)]
            except (ValueError, SyntaxError):
                print("[Error] Invalid microtubule input. Please enter a list like [0,1,2] or comma-separated values.")
                microtubules = []

            display_extract = self.display_extract_checkbox.isChecked()
            toggle_border = self.toggle_border_checkbox.isChecked()

            fig = ani.display_domain_grid(
                rings=rings,
                rays=rays,
                microtubules=microtubules,
                d_tube=d_tube,
                display_extract=display_extract,
                toggle_border=toggle_border
            )

            self.display_matplotlib_figure(fig)

            self.close_domain_button.show()
            self.display_domain_button.setText("Update Domain")

            # self.close_domain_button.show()
        except Exception as e:
            print(f"[Error] Failed to display domain grid: {e}")

    def close_domain(self):
        if hasattr(self, "plot_layout"):
            for i in reversed(range(self.plot_layout.count())):
                widget = self.plot_layout.itemAt(i).widget()
                if widget is not None:
                    widget.setParent(None)

        self.close_domain_button.hide()
        self.display_domain_button.setText("Display Domain")
    def display_matplotlib_figure(self, fig):
        for i in reversed(range(self.plot_layout.count())):
            widget_to_remove = self.plot_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
                widget_to_remove.deleteLater()
        canvas = FigureCanvas(fig)
        canvas.setParent(self)

        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas.updateGeometry()

        self.plot_layout.addWidget(canvas)
        canvas.draw()
        canvas.show()

    # def update_microtubules_live(self):
    #     try:
    #         plt.close('all')
    #
    #         rings = int(self.param_inputs["rg_param"].text())
    #         rays = int(self.param_inputs["ry_param"].text())
    #         d_tube = float(self.param_inputs["d_tube"].text())
    #
    #         microtubules_text = self.param_inputs["N_param"].text()
    #         cleaned = ''.join(c for c in microtubules_text if c.isdigit() or c in [','])
    #         candidate_strs = cleaned.split(',')
    #         microtubules = []
    #
    #         for val in candidate_strs:
    #             if val.strip().isdigit():
    #                 v = int(val.strip())
    #                 if 0 <= v < rays:
    #                     microtubules.append(v)
    #                 else:
    #                     print(f"[Warning] Microtubule index {v} is out of range [0, {rays-1}]")
    #
    #         display_extract = self.display_extract_checkbox.isChecked()
    #         toggle_border = self.toggle_border_checkout.isChecked()
    #
    #         ani.display_domain_grid(
    #             rings=rings,
    #             rays=rays,
    #             microtubules=microtubules,
    #             d_tube=d_tube,
    #             display_extract=display_extract,
    #             toggle_border=toggle_border
    #         )
    #     except Exception as e:
    #         print(f"[Live Update Error] Could not update microtubules: {e}")


