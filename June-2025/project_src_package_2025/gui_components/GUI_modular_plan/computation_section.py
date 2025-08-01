from PyQt5.QtWidgets import (
    QVBoxLayout, QWidget, QPushButton, QListWidget, QListWidgetItem,
    QHBoxLayout, QMessageBox
)

from PyQt5.QtCore import Qt
from project_src_package_2025.auxiliary_tools.prints import return_timestamp

class ComputationSection(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Buttons
        self.add_job_button = QPushButton("Add to Queue")
        self.remove_job_button = QPushButton("Remove Selected Job")
        self.edit_job_button = QPushButton("Edit Selected Job")
        self.move_up_button = QPushButton("Move Up")
        self.move_down_button = QPushButton("Move Down")
        self.launch_button = QPushButton("Launch Computation")

        # Queue list
        self.job_queue_widget = QListWidget()

        # Connect signals
        self.add_job_button.clicked.connect(self.add_job_to_queue)
        self.remove_job_button.clicked.connect(self.remove_selected_job)
        self.edit_job_button.clicked.connect(self.edit_selected_job)
        self.move_up_button.clicked.connect(self.move_selected_job_up)
        self.move_down_button.clicked.connect(self.move_selected_job_down)
        self.launch_button.clicked.connect(self.launch_computation)

        # Layout
        self.layout.addWidget(self.add_job_button)
        self.layout.addWidget(self.remove_job_button)
        self.layout.addWidget(self.edit_job_button)
        self.layout.addWidget(self.move_up_button)
        self.layout.addWidget(self.move_down_button)
        self.layout.addWidget(self.job_queue_widget)
        self.layout.addWidget(self.launch_button)

    def add_job_to_queue(self):
        valid, msg = self.parent.parameter_section.validate_parameters()
        if not valid:
            QMessageBox.warning(self, "Invalid Parameters", msg)
            return

        parameters = self.parent.parameter_section.get_parameter_values()
        computation = self.parent.comp_select.currentText()
        timestamp = return_timestamp()

        job_str = f"{computation} | {timestamp} | {parameters}"
        item = QListWidgetItem(job_str)
        item.setData(Qt.UserRole, {"computation": computation, "parameters": parameters})
        self.job_queue_widget.addItem(item)

    def remove_selected_job(self):
        row = self.job_queue_widget.currentRow()
        if row >= 0:
            self.job_queue_widget.takeItem(row)

    def edit_selected_job(self):
        row = self.job_queue_widget.currentRow()
        if row >= 0:
            item = self.job_queue_widget.item(row)
            job_data = item.data(Qt.UserRole)
            self.parent.comp_select.setCurrentText(job_data["computation"])
            self.parent.parameter_section.build_parameter_fields(job_data["computation"])

            for param, value in job_data["parameters"].items():
                widget = self.parent.parameter_section.param_inputs.get(param)
                if widget:
                    if hasattr(widget, "setValue"):
                        widget.setValue(value)
                    elif hasattr(widget, "setText"):
                        widget.setText(str(value))

    def move_selected_job_up(self):
        row = self.job_queue_widget.currentRow()
        if row > 0:
            item = self.job_queue_widget.takeItem(row)
            self.job_queue_widget.insertItem(row - 1, item)
            self.job_queue_widget.setCurrentRow(row - 1)

    def move_selected_job_down(self):
        row = self.job_queue_widget.currentRow()
        if row < self.job_queue_widget.count() - 1:
            item = self.job_queue_widget.takeItem(row)
            self.job_queue_widget.insertItem(row + 1, item)
            self.job_queue_widget.setCurrentRow(row + 1)

    def launch_computation(self):
        if self.job_queue_widget.count() == 0:
            QMessageBox.information(self, "No Jobs", "No jobs in the queue.")
            return

        for i in range(self.job_queue_widget.count()):
            item = self.job_queue_widget.item(i)
            job_data = item.data(Qt.UserRole)
            computation = job_data["computation"]
            parameters = job_data["parameters"]
            # Delegate to controller/main_window
            self.parent.run_selected_computation(computation, parameters)
