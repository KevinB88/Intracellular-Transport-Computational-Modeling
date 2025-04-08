from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QLineEdit, QTabWidget, QLabel, QTextEdit, QMessageBox
)
import importlib
from project_src_package_2025 import launch_functions
import inspect


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.func_dict = None
        self.setWindowTitle("PDE-Solver GUI")
        self.setGeometry(100, 100, 1200, 700)

        self.main_layout = QHBoxLayout()

        # Left Panel: Launch Functions
        self.launch_panel = QWidget()
        self.launch_layout = QVBoxLayout()
        self.dropdown = QComboBox()
        self.param_input_widgets = {}  # Map from param name -> QLineEdit
        self.param_container = QWidget()
        self.param_container_layout = QVBoxLayout()
        self.param_container.setLayout(self.param_container_layout)
        self.run_button = QPushButton("Run Function")

        self.populate_dropdown()
        self.dropdown.currentIndexChanged.connect(self.load_params)
        self.run_button.clicked.connect(self.run_selected_function)

        self.launch_layout.addWidget(QLabel("Select Launch Function:"))
        self.launch_layout.addWidget(self.dropdown)
        self.launch_layout.addWidget(QLabel("Enter Parameters:"))
        self.launch_layout.addWidget(self.param_container)
        self.launch_layout.addWidget(self.run_button)
        self.launch_panel.setLayout(self.launch_layout)

        # Right Panel: Output Tabs
        self.output_tabs = QTabWidget()
        self.output_tabs.addTab(QLabel("Run a function to view outputs here."), "Welcome")

        # Combine both panels
        self.main_layout.addWidget(self.launch_panel, 2)
        self.main_layout.addWidget(self.output_tabs, 5)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def populate_dropdown(self):
        self.func_dict = {name: fn for name, fn in inspect.getmembers(launch_functions, inspect.isfunction)}
        for fn_name in self.func_dict:
            self.dropdown.addItem(fn_name)

    def load_params(self):
        # Clear existing widgets
        for i in reversed(range(self.param_container_layout.count())):
            self.param_container_layout.itemAt(i).widget().setParent(None)

        self.param_input_widgets.clear()

        fn_name = self.dropdown.currentText()
        fn = self.func_dict[fn_name]
        sig = inspect.signature(fn)

        for param in sig.parameters.values():
            label = QLabel(f"{param.name} ({param.annotation.__name__ if param.annotation != inspect.Parameter.empty else 'str'}):")
            line_edit = QLineEdit()
            self.param_container_layout.addWidget(label)
            self.param_container_layout.addWidget(line_edit)
            self.param_input_widgets[param.name] = line_edit

    def run_selected_function(self):
        fn_name = self.dropdown.currentText()
        fn = self.func_dict[fn_name]
        sig = inspect.signature(fn)

        kwargs = {}
        try:
            for param in sig.parameters.values():
                input_widget = self.param_input_widgets[param.name]
                input_text = input_widget.text()

                # Basic type inference
                if param.annotation == int:
                    kwargs[param.name] = int(input_text)
                elif param.annotation == float:
                    kwargs[param.name] = float(input_text)
                else:
                    kwargs[param.name] = input_text  # fallback as string

            result = fn(**kwargs)
            self.output_tabs.addTab(QLabel(f"Function `{fn_name}` executed successfully."), fn_name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run `{fn_name}`:\n{e}")
