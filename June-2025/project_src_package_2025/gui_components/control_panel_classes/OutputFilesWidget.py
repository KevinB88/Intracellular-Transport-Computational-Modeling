from . import QLabel, QVBoxLayout, QWidget, QTextEdit


class OutputFilesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("CSV Output Files:")
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.output_area)

    def display_outputs(self, file_list):
        if not file_list:
            self.output_area.setText("No output files.")
        else:
            self.output_area.setText("\\n".join(file_list))