from PyQt5.QtWidgets import (
    QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QFormLayout,
    QCheckBox, QTextEdit, QMessageBox, QWidget, QHBoxLayout, QGroupBox,
    QSizePolicy, QSlider, QTabWidget
)

from PyQt5.QtGui import QColor, QPalette, QPixmap
from PyQt5.QtCore import Qt

from project_src_package_2025.gui_components import computation_history_entry
from project_src_package_2025.gui_components import history_cache
from project_src_package_2025.gui_components import controller
from project_src_package_2025.gui_components import aux_gui_funcs
from project_src_package_2025.job_queuing_system import job_queue
from project_src_package_2025.data_visualization import animation_functions as ani
from project_src_package_2025.data_visualization import ani_evolution as evo

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import ast


__all__ = [
    "QVBoxLayout", "QLabel", "QComboBox", "QLineEdit", "QPushButton", "QFormLayout",
    "QCheckBox", "QTextEdit", "QMessageBox", "QWidget", "QHBoxLayout", "QColor",
    "QPalette", "Qt", "computation_history_entry", "history_cache", "controller",
    "aux_gui_funcs", "job_queue", "QGroupBox", "FigureCanvas", "plt", "ast", "ani",
    "evo", "QSlider", "QSizePolicy", "QTabWidget", "QPixmap"
]

