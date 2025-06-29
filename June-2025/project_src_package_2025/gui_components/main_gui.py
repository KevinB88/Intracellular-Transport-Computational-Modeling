import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QPushButton, QMessageBox
from . import views
from . import history_cache
from . import fp


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GUI version 1.0")
        self.setFixedSize(2000, 1000)
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

    # def load_history_entry(self, index):
    #     if index == 0:
    #         return  # Ignore the placeholder option
    #
    #     entry = history_cache.cache.get_entry(index - 1)
    #     if entry:
    #         self.control_panel.load_entry(entry)

    def load_history_entry(self, index):
        if index == 0:
            return  # Ignore placeholder

        entry = history_cache.cache.get_entry(index - 1)
        if not entry:
            return

        # Update the selected computation type in dropdown
        self.control_panel.set_computation(entry.comp_type)

        # Fill input fields with parameters
        self.control_panel.set_parameters(entry.params)

        # Update MFPT/Duration labels
        if entry.mfpt is not None:
            self.control_panel.mfpt_label.setText(f"MFPT: {entry.mfpt:.6f}")
        if entry.duration is not None:
            self.control_panel.duration_label.setText(f"Duration: {entry.duration:.6f} seconds")
            self.control_panel.duration_label.show()
        else:
            self.control_panel.duration_label.hide()

        # Update file output display
        self.control_panel.output_files_widget.update_display(entry.csv_files or [], entry.png_files or [])
        self.control_panel.output_files_widget.show()
        self.control_panel.show_restored_message(entry)

        self.control_panel.png_preview_widget.update_png_list(entry.png_files or [])
        self.control_panel.png_preview_widget.show()


def run_app():
    app = QApplication(sys.argv)

    with open(fp.styles_location, "r") as file:
        app.setStyleSheet(file.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
