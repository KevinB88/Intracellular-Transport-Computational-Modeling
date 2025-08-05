from PyQt5.QtWidgets import (
    QFormLayout, QCheckBox, QPushButton, QLineEdit,
    QDoubleSpinBox, QSpinBox, QLabel, QHBoxLayout, QWidget
)
from PyQt5.QtCore import Qt

from project_src_package_2025.gui_components import params_config

class ParameterSection(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.layout = QFormLayout()
        self.setLayout(self.layout)

        self.param_inputs = {}
        self.advanced_widgets = [ ]

        # Advanced toggle
        self.advanced_toggle = QCheckBox("Show Advanced Parameters")
        self.advanced_toggle.stateChanged.connect(self.toggle_advanced_fields)
        self.layout.addRow(self.advanced_toggle)

        # Reset button
        self.reset_button = QPushButton("Reset Parameters")
        self.reset_button.clicked.connect(self.clear_parameter_fields)
        self.layout.addRow(self.reset_button)

    def build_parameter_fields(self, schema_name):
        self.clear_layout()

        schema = parmas_config.PARAMETER_SCHEMAS[ schema_name ]
        self.param_inputs = {}
        self.advanced_widgets = [ ]

        # Required fields: visible by default
        for param_name, _ in schema.get("required", [ ]):
            input_field = QLineEdit()
            self.param_inputs[ param_name ] = input_field
            self.layout.addRow(QLabel(f"{param_name}:"), input_field)

        # Default fields: considered "advanced"
        for param_name, value in schema.get("default", [ ]):
            input_field = QLineEdit(str(value))
            self.param_inputs[ param_name ] = input_field
            label = QLabel(f"{param_name}:")
            label.setVisible(False)
            input_field.setVisible(False)
            self.layout.addRow(label, input_field)
            self.advanced_widgets.append((label, input_field))

        self.layout.addRow(self.advanced_toggle)
        self.layout.addRow(self.reset_button)

    def toggle_advanced_fields(self, state):
        show = state == Qt.Checked
        for label, widget in self.advanced_widgets:
            label.setVisible(show)
            widget.setVisible(show)

    def get_parameter_values(self):
        return {
            name: (
                widget.text() if isinstance(widget, QLineEdit)
                else widget.value()
            )
            for name, widget in self.param_inputs.items()
        }

    def clear_parameter_fields(self):
        for name, widget in self.param_inputs.items():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.setValue(widget.minimum())

    def validate_parameters(self):
        # Basic numeric validation already handled by Qt spinboxes.
        # Add custom validation logic if needed here.
        for name, widget in self.param_inputs.items():
            if isinstance(widget, QLineEdit):
                if not widget.text().strip():
                    return False, f"Field '{name}' cannot be empty."
        return True, ""

    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.setParent(None)
