from . import QWidget, QVBoxLayout, QTabWidget, QComboBox, QStackedLayout


class VisualizationPanel(QWidget):
    def __init__(self, domain_display_widget, animation_display_widget):
        super().__init__()

        self.domain_display_widget = domain_display_widget
        self.animation_display_widget = animation_display_widget

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Dropdown to choose between domain and animation
        self.view_selector = QComboBox()
        self.view_selector.addItems(["Domain Display", "Animation"])
        self.view_selector.currentIndexChanged.connect(self.switch_view)
        self.layout.addWidget(self.view_selector)

        # Stack layout for both visualizations
        self.view_stack = QStackedLayout()
        self.view_stack.addWidget(self.domain_display_widget)
        self.view_stack.addWidget(self.animation_display_widget)
        self.layout.addLayout(self.view_stack)

    def switch_view(self, index):
        if index == 0:
            self.show_domain_display()
        elif index == 1:
            self.show_animation_display()

    def show_domain_display(self):
        self.view_stack.setCurrentIndex(0)

        # Attempt to pause animation if possible
        if hasattr(self.animation_display_widget, "pause_animation"):
            try:
                self.animation_display_widget.clear_animation()
            except Exception:
                pass

        self.domain_display_widget.show()

    def show_animation_display(self):
        self.view_stack.setCurrentIndex(1)
        self.domain_display_widget.hide()
        self.animation_display_widget.show()

    def pause_animation(self):
        if hasattr(self.animation_display_widget, "pause_animation"):
            try:
                self.animation_display_widget.pause_animation()
            except Exception:
                pass

    def stop_animation(self):
        if hasattr(self.animation_display_widget, "clear_animation"):
            try:
                self.animation_display_widget.clear_animation()
            except Exception:
                pass
        self.animation_display_widget.hide()
