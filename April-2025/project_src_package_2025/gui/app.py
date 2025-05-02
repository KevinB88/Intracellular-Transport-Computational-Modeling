from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QLineEdit, QTabWidget, QLabel, QTextEdit, QMessageBox,
    QTableWidgetItem, QTableWidget
)
from PyQt6.QtCore import QThread
from worker import Worker
import importlib

from project_src_package_2025 import launch_functions
import inspect

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


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
                    kwargs[param.name] = input_text

            self.statusBar().showMessage(f"Running `{fn_name}`...")

            # Set up thread and worker
            self.thread = QThread()
            self.worker = Worker(fn, fn_name, kwargs)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.on_function_finished)
            self.worker.error.connect(self.on_function_error)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Parameter error:\n{e}")

    def on_function_finished(self, result, fn_name):
        self.statusBar().showMessage(f"{fn_name} finished successfully.")

        if isinstance(result, str):
            # If the function returns a status string
            self.output_tabs.addTab(QLabel(result), f"{fn_name} Output")
        elif isinstance(result, list):
            for i, path in enumerate(result):
                tab_name = f"{fn_name} [{i + 1}]"
                ext = os.path.splitext(path)[1].lower()

                if ext == ".csv":
                    table_widget = self.create_table_from_csv(path)
                    self.output_tabs.addTab(table_widget, tab_name)
                elif ext in [".png", ".jpg", ".jpeg"]:
                    canvas = self.create_canvas_from_image(path)
                    self.output_tabs.addTab(canvas, tab_name)
                elif ext == ".pdf":
                    self.output_tabs.addTab(QLabel(f"PDF saved: {path}"), tab_name)
                else:
                    self.output_tabs.addTab(QLabel(f"Output saved: {path}"), tab_name)
        else:
            self.output_tabs.addTab(QLabel("Unknown output format"), f"{fn_name} Output")

    def on_function_error(self, error_msg, fn_name):
        QMessageBox.critical(self, f"Error in `{fn_name}`", error_msg)
        self.statusBar().showMessage(f"{fn_name} failed.")

    def create_table_from_csv(self, file_path):
        df = pd.read_csv(file_path)
        table = QTableWidget(df.shape[0], df.shape[1])
        table.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                table.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))

        table.setMinimumSize(800, 400)
        return table

    def create_canvas_from_image(self, file_path):
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        img = plt.imread(file_path)
        ax.imshow(img)
        ax.axis('off')
        canvas = FigureCanvas(fig)
        return canvas

