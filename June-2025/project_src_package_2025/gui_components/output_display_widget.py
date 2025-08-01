from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGroupBox, QComboBox, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl
# from PyQt5.QtGui import QTextCursor
import os
import subprocess


import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class PNGPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.dropdown = QComboBox()
        self.dropdown.currentIndexChanged.connect(self.update_image)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setMinimumSize(600, 600)
        # self.image_label.setScaledContents(True)

        self.layout.addWidget(self.dropdown)
        self.layout.addWidget(self.image_label)

        self.png_paths = []

    def update_png_list(self, png_paths):
        self.png_paths = png_paths or []
        self.dropdown.clear()

        for path in self.png_paths:
            filename = os.path.basename(path)
            self.dropdown.addItem(filename)

        if self.png_paths:
            self.update_image(0)
        else:
            self.image_label.clear()

    def update_image(self, index):
        if 0 <= index < len(self.png_paths):
            path = self.png_paths[index]
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap.scaled(
                    self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                print(f"Warning: failed to load image {path}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image(self.dropdown.currentIndex())


class OutputFilesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.csv_container = QWidget()
        self.csv_layout = QVBoxLayout()
        self.csv_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.csv_container.setLayout(self.csv_layout)

        self.csv_scroll = QScrollArea()
        self.csv_scroll.setWidgetResizable(True)
        self.csv_scroll.setWidget(self.csv_container)

        self.layout.addWidget(self.csv_scroll)

    @staticmethod
    def open_in_file_explorer(file_path):
        folder = os.path.dirname(file_path)
        if os.name == "nt":
            os.startfile(folder)
        elif os.name == "posix":
            if "Darwin" in os.uname().sysname:
                subprocess.run(["open", folder])
            else:
                subprocess.run(["xdg-open", folder])

    def update_display(self, csv_paths, png_paths=None):
        # Clear previous displays

        while self.csv_layout.count():
            item = self.csv_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for path in csv_paths:
            label = QLabel(f'<a href="{path}">{os.path.basename(path)}</a>')
            label.setTextInteractionFlags(Qt.TextBrowserInteraction)
            label.setOpenExternalLinks(False)
            label.linkActivated.connect(lambda file_path=path: self.open_in_file_explorer(file_path))
            label.setStyleSheet("padding: 4px;")
            self.csv_layout.addWidget(label)