import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QPushButton, QMessageBox
from PyQt5.QtGui import QGuiApplication, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPoint
from . import views
from . import fp

from project_src_package_2025.gui_components.GUI_modular_plan.views_mod import ControlPanel


class GridOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.mouse_pos = QPoint()
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent")
        self.step = 40

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor(200, 200, 200, 100))
        pen.setWidth(1)
        painter.setPen(pen)

        width = self.width()
        height = self.height()

        for x in range(0, width, self.step):
            painter.drawLine(x, 0, x, height)
            painter.drawText(x + 2, 12, str(x))

        for y in range(0, height, self.step):
            painter.drawLine(0, y, width, y)
            painter.drawText(2, y + 12, str(y))

        painter.setPen(QPen(QColor(255, 0, 0, 200)))
        x, y = self.mouse_pos.x(), self.mouse_pos.y()
        painter.drawText(x + 10, y - 10, f"({x}, {y})")
        painter.drawEllipse(self.mouse_pos, 3, 3)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        debug_mode = False

        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.setGeometry(screen_geometry)
        self.setWindowTitle("GUI version 1.2")

        self.layout = QVBoxLayout()
        self.control_panel = views.ControlPanel(self)
        # self.control_panel = ControlPanel(self)
        #
        container = QWidget()
        container.setLayout(self.layout)
        self.layout.addWidget(self.control_panel)
        self.setCentralWidget(container)

        if debug_mode:
            self.grid_overlay = GridOverlay(self)
            self.grid_overlay.resize(self.size())
            self.grid_overlay.show()

    def resizeEvent(self, event):
        if hasattr(self, "grid_overlay"):
            self.grid_overlay.resize(self.size())
        super().resizeEvent(event)


def run_app():
    app = QApplication(sys.argv)

    from importlib import resources

    style_data = resources.files('project_src_package_2025.gui_components.styles') \
        .joinpath('style.qss') \
        .read_text()

    app.setStyleSheet(style_data)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
