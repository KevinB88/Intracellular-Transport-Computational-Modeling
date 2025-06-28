import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QPushButton, QMessageBox
from . import views
from . import history_cache


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GUI version 1.0")
        self.setFixedSize(1000, 800)
        self.layout = QVBoxLayout()

        self.history_dropdown = QComboBox()
        self.history_dropdown.addItem("Select Previous Computation: ")
        self.history_dropdown.currentIndexChanged.connect(self.load_history_entry)
        self.layout.addWidget(self.history_dropdown)

        self.clear_button = QPushButton("Clear History")
        self.clear_button.clicked.connect(self.confirm_clear_history)
        self.layout.addWidget(self.clear_button)

        # Populate history dropdown with saved entries
        for label in history_cache.cache.get_labels():
            self.history_dropdown.addItem(label)

        self.control_panel = views.ControlPanel(self.history_dropdown, self)

        container = QWidget()
        container.setLayout(self.layout)
        self.layout.addWidget(self.control_panel)
        self.setCentralWidget(container)

    def confirm_clear_history(self):
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

    def load_history_entry(self, index):
        if index == 0:
            return  # Ignore the placeholder option

        entry = history_cache.cache.get_entry(index - 1)
        if entry:
            self.control_panel.load_entry(entry)


def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
