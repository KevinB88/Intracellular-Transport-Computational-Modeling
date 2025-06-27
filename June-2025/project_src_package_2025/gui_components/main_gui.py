import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from . import views


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GUI version 1.0")
        self.setFixedSize(600, 500)

        layout = QVBoxLayout()
        self.control_panel = views.ControlPanel(self)

        container = QWidget()
        container.setLayout(layout)
        layout.addWidget(self.control_panel)

        self.setCentralWidget(container)


def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
