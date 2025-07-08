from . import (QWidget, QVBoxLayout, QPushButton, QCheckBox,
               QGroupBox, QHBoxLayout, QSizePolicy, QMessageBox)
from . import FigureCanvas
from . import plt
from . import ast
from . import ani


class DomainDisplayWidget(QWidget):
    def __init__(self, param_inputs, animation_panel=None, parent=None):
        super().__init__(parent)
        self.param_inputs = param_inputs
        self.animation_panel = animation_panel  # For coordination

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.checkbox_group = QGroupBox("Domain Grid Options")
        self.checkbox_group.setStyleSheet("font-weight: bold;")
        checkbox_layout = QVBoxLayout()

        self.display_extract_checkbox = QCheckBox("Display Extraction Region")
        self.toggle_border_checkbox = QCheckBox("Display Internal Borders")
        self.toggle_border_checkbox.setChecked(True)

        checkbox_layout.addWidget(self.display_extract_checkbox)
        checkbox_layout.addWidget(self.toggle_border_checkbox)

        self.display_button = QPushButton("Display Domain")
        self.display_button.clicked.connect(self.display_domain)

        self.close_button = QPushButton("Close Domain")
        self.close_button.clicked.connect(self.close_domain)
        self.close_button.setVisible(False)

        checkbox_layout.addSpacing(15)
        checkbox_layout.addWidget(self.display_button)
        checkbox_layout.addWidget(self.close_button)

        self.checkbox_group.setLayout(checkbox_layout)
        self.layout.addWidget(self.checkbox_group)

        self.plot_layout = QVBoxLayout()
        self.layout.addLayout(self.plot_layout)

        self.canvas = None

    def display_domain(self):
        try:
            if self.animation_panel:
                self.animation_panel.pause_animation()
                self.animation_panel.hide()

            self.show()

            plt.close('all')

            rings = int(self.param_inputs["rg_param"].text())
            rays = int(self.param_inputs["ry_param"].text())
            d_tube = float(self.param_inputs["d_tube"].text())

            try:
                microtubules_input = self.param_inputs["N_param"].text()
                parsed = ast.literal_eval(microtubules_input)
                microtubules = list(parsed) if isinstance(parsed, (list, tuple)) else [int(parsed)]
            except Exception:
                microtubules = []

            display_extract = self.display_extract_checkbox.isChecked()
            toggle_border = self.toggle_border_checkbox.isChecked()

            fig = ani.display_domain_grid(
                rings=rings,
                rays=rays,
                microtubules=microtubules,
                d_tube=d_tube,
                display_extract=display_extract,
                toggle_border=toggle_border
            )

            self._update_canvas(fig)
            self.close_button.setVisible(True)
            self.display_button.setText("Update Domain")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display domain: {str(e)}")

    def _update_canvas(self, fig):
        self._clear_canvas()
        self.canvas = FigureCanvas(fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_layout.addWidget(self.canvas)
        self.canvas.draw()

    def _clear_canvas(self):
        if self.canvas:
            self.plot_layout.removeWidget(self.canvas)
            self.canvas.setParent(None)
            self.canvas = None

    def close_domain(self):
        self._clear_canvas()
        self.close_button.setVisible(False)
        self.display_button.setText("Display Domain")
        # self.hide()

    def pause_if_active(self):
        self.close_domain()
