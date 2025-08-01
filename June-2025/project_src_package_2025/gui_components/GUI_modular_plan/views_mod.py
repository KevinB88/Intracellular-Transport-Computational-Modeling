from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTextEdit,
    QListWidget, QGroupBox, QSplitter, QFrame, QStackedWidget
)

from project_src_package_2025.gui_components.GUI_modular_plan.parameter_section import ParameterSection
from project_src_package_2025.gui_components.GUI_modular_plan.computation_section import ComputationSection
from project_src_package_2025.gui_components.GUI_modular_plan.computation_executor_mixin import ComputationExecutorMixin

# import parmas_config
from project_src_package_2025.gui_components import parmas_config

class ControlPanel(QWidget, ComputationExecutorMixin):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # === Core Data Structures ===
        self.history = {}
        self.pending_jobs = []
        self.current_job = None

        # === Layout ===
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # === Computation Selection ===
        comp_layout = QHBoxLayout()
        self.comp_label = QLabel("Select Computation:")
        self.comp_select = QComboBox()
        self.comp_select.addItems(parmas_config.PARAMETER_SCHEMAS.keys())
        self.comp_select.currentTextChanged.connect(self.update_parameter_fields)
        comp_layout.addWidget(self.comp_label)
        comp_layout.addWidget(self.comp_select)
        self.main_layout.addLayout(comp_layout)

        # === Parameter Section ===
        self.parameter_section = ParameterSection(self)
        self.main_layout.addWidget(self.parameter_section)

        # === Job Queue Section ===
        self.computation_section = ComputationSection(self)
        self.main_layout.addWidget(self.computation_section)

        # === History Dropdown ===
        history_layout = QHBoxLayout()
        self.history_label = QLabel("Computation History:")
        self.history_dropdown = QComboBox()
        history_layout.addWidget(self.history_label)
        history_layout.addWidget(self.history_dropdown)
        self.main_layout.addLayout(history_layout)

        # === Output Console ===
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        self.output_console.setFixedHeight(120)
        self.main_layout.addWidget(self.output_console)

        # === Output Display Widgets (for CSV and PNG) ===
        self.output_display_panel = QStackedWidget()
        self.output_display_panel.setFrameShape(QFrame.StyledPanel)
        self.main_layout.addWidget(self.output_display_panel)

        # === Job Queue Widget (needed by mixin) ===
        self.job_queue_widget = self.computation_section.job_queue_widget

        # === Build initial form ===
        self.parameter_section.build_parameter_fields(self.comp_select.currentText())

    def update_parameter_fields(self, computation_name):
        self.parameter_section.build_parameter_fields(computation_name)

    def run_selected_computation(self, computation_name, parameters):
        self.run_computation_mp(computation_name, parameters)
