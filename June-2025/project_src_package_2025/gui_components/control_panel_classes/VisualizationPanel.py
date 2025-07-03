from . import QWidget, QVBoxLayout, QTabWidget
from . import DomainDisplayWidget
from . import AnimationDisplayWidget


class VisualizationPanel(QWidget):
    def __init__(self, param_inputs, png_preview_widget, output_files_widget, parent=None):
        super().__init__(parent)
        self.param_inputs = param_inputs
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Create Tab Widget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # --- Tab 1: Results ---
        self.result_display_tab = QWidget()
        self.result_layout = QVBoxLayout()
        self.result_display_tab.setLayout(self.result_layout)
        self.result_layout.addWidget(png_preview_widget)
        self.result_layout.addWidget(output_files_widget)
        png_preview_widget.hide()
        output_files_widget.hide()
        self.tab_widget.addTab(self.result_display_tab, "Results")

        # --- Tab 2: Visualization (Domain/Animation) ---
        self.visualization_tab = QWidget()
        self.visualization_layout = QVBoxLayout()
        self.visualization_tab.setLayout(self.visualization_layout)

        self.domain_panel = DomainDisplayWidget(self.param_inputs)
        self.animation_panel = AnimationDisplayWidget(self.param_inputs)

        # Cross-reference for mutual exclusion
        self.domain_panel.animation_panel = self.animation_panel
        self.animation_panel.setParent(self)
        self.animation_panel.domain_panel = self.domain_panel

        self.visualization_layout.addWidget(self.domain_panel)
        self.visualization_layout.addWidget(self.animation_panel)

        # Start with both hidden
        self.domain_panel.hide()
        self.animation_panel.hide()

        self.tab_widget.addTab(self.visualization_tab, "Visualization")

    def show_domain_display(self):
        """Show domain display and hide animation."""
        self.domain_panel.show()
        self.animation_panel.pause_animation()
        self.animation_panel.hide()

    def show_animation_display(self):
        """Show animation display and hide domain."""
        self.domain_panel.pause_if_active()
        self.domain_panel.hide()
        self.animation_panel.show()

    def reset(self):
        """Hide both displays and clear animation."""
        self.domain_panel.hide()
        self.animation_panel.clear_animation()
        self.animation_panel.hide()