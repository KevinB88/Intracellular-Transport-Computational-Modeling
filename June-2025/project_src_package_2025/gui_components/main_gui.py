import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QPushButton, QMessageBox
from PyQt5.QtGui import QGuiApplication
from . import views
from . import history_cache
from . import fp


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        self.control_panel = views.ControlPanel

        width = int(screen_width * 0.8)
        height = int(screen_height * 0.8)

        self.resize(width, height)
        self.move(
            (screen_width - width) // 2,
            (screen_height - height) // 2
        )

        self.setWindowTitle("GUI version 1.0")
        # self.setFixedSize(2000, 1000)
        self.layout = QVBoxLayout()

        self.control_panel = views.ControlPanel(self)
        container = QWidget()
        container.setLayout(self.layout)
        self.layout.addWidget(self.control_panel)
        self.setCentralWidget(container)


def run_app():
    app = QApplication(sys.argv)

    with open(fp.styles_location, "r") as file:
        app.setStyleSheet(file.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
