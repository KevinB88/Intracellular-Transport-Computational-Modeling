
from . import (QWidget, QVBoxLayout, QPushButton, QSlider,
               QLabel, Qt, QMessageBox)
from . import FigureCanvas
from . import plt
from . import ast
from . import ani


class AnimationDisplayWidget(QWidget):
    def __init__(self, param_inputs, parent=None):
        super().__init__(parent)
        self.param_inputs = param_inputs
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.fps_label = QLabel("Frames per Second: 50")
        self.fps_slider = QSlider(Qt.Horizontal)
        self.fps_slider.setMinimum(5)
        self.fps_slider.setMaximum(100)
        self.fps_slider.setValue(50)
        self.fps_slider.setTickInterval(5)
        self.fps_slider.setTickPosition(QSlider.TicksBelow)
        self.fps_slider.valueChanged.connect(self.update_fps_label)

        self.launch_button = QPushButton("Launch Animation")
        self.launch_button.clicked.connect(self.launch_animation)

        self.pause_button = QPushButton("Pause Animation")
        self.pause_button.clicked.connect(self.pause_animation)
        self.pause_button.setVisible(False)

        self.clear_button = QPushButton("Clear Animation")
        self.clear_button.clicked.connect(self.clear_animation)
        self.clear_button.setVisible(False)

        self.layout.addWidget(self.fps_label)
        self.layout.addWidget(self.fps_slider)
        self.layout.addWidget(self.launch_button)
        self.layout.addWidget(self.pause_button)
        self.layout.addWidget(self.clear_button)

        self.canvas = None
        self.anim = None

    def update_fps_label(self):
        fps = self.fps_slider.value()
        self.fps_label.setText(f"Frames per Second: {fps}")

    def launch_animation(self):
        try:
            self.hide_animation_controls(False)
            if hasattr(self.parent(), 'domain_panel'):
                self.parent().domain_panel.pause_if_active()

            plt.close('all')
            fps = self.fps_slider.value()

            rings = int(self.param_inputs["rg_param"].text())
            rays = int(self.param_inputs["ry_param"].text())
            w_param = float(self.param_inputs["w_param"].text())
            v_param = float(self.param_inputs["v_param"].text())
            N_param = self.param_inputs["N_param"].text()
            K_param = float(self.param_inputs["K_param"].text())
            T_param = float(self.param_inputs["T_param"].text())
            d_tube = float(self.param_inputs["d_tube"].text())

            fig, anim = ani.animate_diffusion(
                rings, rays, w_param, v_param, N_param,
                K_param, T_param, d_tube,
                steps_per_frame=10,
                interval_ms=int(1000 / fps)
            )

            self.anim = anim
            self._update_canvas(fig)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Animation failed: {str(e)}")

    def _update_canvas(self, fig):
        self.clear_animation()
        self.canvas = FigureCanvas(fig)
        self.layout.addWidget(self.canvas)
        self.canvas.draw()
        self.pause_button.setVisible(True)
        self.clear_button.setVisible(True)

    def pause_animation(self):
        if self.anim:
            self.anim.event_source.stop()
            self.pause_button.setVisible(False)

    def hide_animation_controls(self, hide=True):
        self.pause_button.setVisible(not hide)
        self.clear_button.setVisible(not hide)
        if self.canvas:
            self.canvas.setVisible(not hide)

    def clear_animation(self):
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.setParent(None)
            self.canvas = None
        self.anim = None
        self.hide_animation_controls(True)