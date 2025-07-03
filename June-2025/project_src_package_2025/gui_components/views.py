from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QGroupBox

from project_src_package_2025.gui_components.control_panel_classes import ComputationControls
from project_src_package_2025.gui_components.control_panel_classes import HistoryManager
from project_src_package_2025.gui_components.control_panel_classes import VisualizationPanel
from project_src_package_2025.gui_components.control_panel_classes import OutputFilesWidget
from project_src_package_2025.gui_components.control_panel_classes import PNGPreviewWidget
from . import parmas_config as params


class ControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.comp_schemas = params.PARAMETER_SCHEMAS

        # Tabs: Results & Visualization
        self.tab_widget = QTabWidget()
        self.result_display_tab = QWidget()
        self.result_layout = QVBoxLayout()
        self.result_display_tab.setLayout(self.result_layout)

        self.visualization_tab = QWidget()
        self.visualization_layout = QVBoxLayout()
        self.visualization_tab.setLayout(self.visualization_layout)

        self.tab_widget.addTab(self.result_display_tab, "Results")
        self.tab_widget.addTab(self.visualization_tab, "Visualization")
        self.main_layout.addWidget(self.tab_widget)

        # Shared output widgets
        self.png_preview_widget = PNGPreviewWidget.PNGPreviewWidget()
        self.output_files_widget = OutputFilesWidget.OutputFilesWidget()

        self.result_layout.addWidget(self.png_preview_widget)
        self.result_layout.addWidget(self.output_files_widget)

        self.png_preview_widget.hide()
        self.output_files_widget.hide()

        # Bottom section: Computation + History
        self.bottom_layout = QHBoxLayout()

        # ↓↓↓ PASSING SELF as parent_panel
        self.computation_controls = ComputationControls.ComputationalControls(parent_panel=self)
        self.history_manager = HistoryManager.HistoryManager(parent_panel=self)

        # Visualization logic (domain/animation switch)
        self.visualization_panel = VisualizationPanel.VisualizationPanel(
            png_preview_widget=self.png_preview_widget,
            output_files_widget=self.output_files_widget,
            param_inputs=self.computation_controls.param_inputs
        )
        self.visualization_layout.addWidget(self.visualization_panel)

        self.bottom_layout.addWidget(self.computation_controls)
        self.bottom_layout.addWidget(self.history_manager)

        self.main_layout.addLayout(self.bottom_layout)
