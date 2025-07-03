from . import QLabel, QVBoxLayout, QWidget, QPixmap


class PNGPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("No image loaded.")
        self.layout.addWidget(self.label)

    def display_image(self, image_path):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.label.setText("Failed to load image.")
        else:
            self.label.setPixmap(pixmap)
            self.label.setScaledContents(True)