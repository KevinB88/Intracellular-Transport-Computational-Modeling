from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGroupBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl
# from PyQt5.QtGui import QTextCursor
import os
import subprocess


class OutputFilesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.csv_group = QGroupBox("CSV Outputs")
        self.csv_layout = QVBoxLayout()
        self.csv_group.setLayout(self.csv_layout)

        self.png_group = QGroupBox("PNG Outputs")
        self.png_layout = QVBoxLayout()
        self.png_group.setLayout(self.png_layout)

        self.csv_scroll = QScrollArea()
        self.csv_scroll.setWidget(self.csv_group)
        self.csv_scroll.setWidgetResizable(True)

        self.png_scroll = QScrollArea()
        self.png_scroll.setWidget(self.png_group)
        self.png_scroll.setWidgetResizable(True)

        self.layout.addWidget(self.csv_scroll)
        self.layout.addWidget(self.png_scroll)

    def open_in_file_explorer(self, file_path):
        folder = os.path.dirname(file_path)
        if os.name == "nt":
            os.startfile(folder)
        elif os.name == "posix":
            if "Darwin" in os.uname().sysname:
                subprocess.run(["open", folder])
            else:
                subprocess.run(["xdg-open", folder])

    def update_display(self, csv_paths, png_paths):
        # Clear previous displays
        for layout in [self.csv_layout, self.png_layout]:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        for path in csv_paths:
            label = QLabel(f'<a href="{path}">{os.path.basename(path)}</a>')
            label.setTextInteractionFlags(Qt.TextBrowserInteraction)
            label.setOpenExternalLinks(False)
            label.linkActivated.connect(lambda file_path=path: self.open_in_file_explorer(file_path))
            self.csv_layout.addWidget(label)

        for path in png_paths:
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    scaled = pixmap.scaledToWidth(300)
                    image_label = QLabel()
                    image_label.setPixmap(scaled)
                    self.png_layout.addWidget(image_label)


