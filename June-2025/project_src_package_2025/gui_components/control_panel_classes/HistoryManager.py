from . import QComboBox, QPushButton, QVBoxLayout, QMessageBox, QLabel
from . import history_cache
from . import computation_history_entry


class HistoryManager:
    def __init__(self, parent_panel):
        self.panel = parent_panel
        self.dropdown = QComboBox()
        self.dropdown.addItem("Select Previous Computation: ")
        for label in history_cache.cache.get_labels():
            self.dropdown.addItem(label)
        self.dropdown.currentIndexChanged.connect(self.load_history_entry)

        self.clear_button = QPushButton("Clear History")
        self.clear_button.clicked.connect(self.clear_history)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.dropdown)
        self.layout.addWidget(self.clear_button)

    def load_history_entry(self, index):
        if index <= 0:
            return  # Ignore "Select Previous Computation"
        label = self.dropdown.currentText()
        record = history_cache.cache.get_entry(label)
        if record:
            self.panel.set_computation(record.comp_type)
            self.panel.set_parameters(record.params)
            self.panel.show_restored_message(record)

    def clear_history(self):
        confirm = QMessageBox.question(
            self.panel, "Confirm Clear",
            "Are you sure you want to clear all history records?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            history_cache.cache.clear()
            self.dropdown.clear()
            self.dropdown.addItem("Select Previous Computation: ")