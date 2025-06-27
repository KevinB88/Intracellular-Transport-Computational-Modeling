from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QFormLayout,
    QLineEdit, QMessageBox, QCheckBox
)

from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt

from . import parmas_config
from . import controller
from . import stdout_redirector


class ControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

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
        try:
            inputs = {param: field.text() for param, field in self.param_inputs.items()}
            result = controller.run_selected_computation(self.comp_select.currentText(), inputs)
            print(f"Result: {result}")  # For now, log result in terminal
            self.set_launch_color("success")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.set_launch_color("error")
