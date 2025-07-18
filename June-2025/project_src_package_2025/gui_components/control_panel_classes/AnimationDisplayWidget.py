from . import (QWidget, QVBoxLayout, QPushButton, QSlider,
               QLabel, Qt, QMessageBox)
from . import FigureCanvas
from . import plt
from . import evo
import re


class AnimationDisplayWidget(QWidget):
    def __init__(self, param_inputs, parent=None):
        super().__init__(parent)
        self.param_inputs = param_inputs
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Controls
        self.fps_label = QLabel("Frames per Second: 50")
        self.fps_slider = QSlider(Qt.Horizontal)
        self.fps_slider.setMinimum(5)
        self.fps_slider.setMaximum(100)
        self.fps_slider.setValue(50)
        self.fps_slider.setTickInterval(5)
        self.fps_slider.setTickPosition(QSlider.TicksBelow)
        self.fps_slider.valueChanged.connect(self.update_fps_label)

        self.steps_slider = QSlider(Qt.Horizontal)
        self.steps_slider.setMinimum(1)
        self.steps_slider.setMaximum(100)
        self.steps_slider.setValue(10)
        self.steps_slider.setTickInterval(5)
        self.steps_slider.setTickPosition(QSlider.TicksBelow)
        self.steps_slider.valueChanged.connect(self.update_steps_label)
        self.steps_label = QLabel("Steps per Frame: 10")

        self.launch_button = QPushButton("Launch Animation")
        self.launch_button.clicked.connect(self.launch_animation)

        self.pause_button = QPushButton("Pause Animation")
        self.pause_button.clicked.connect(self.pause_animation)
        self.pause_button.setVisible(False)

        self.resume_button = QPushButton("Resume Animation")
        self.resume_button.clicked.connect(self.resume_animation)
        self.resume_button.setVisible(False)

        self.clear_button = QPushButton("Clear Animation")
        self.clear_button.clicked.connect(self.clear_animation)
        self.clear_button.setVisible(False)

        # Layout
        self.layout.addWidget(self.fps_label)
        self.layout.addWidget(self.fps_slider)
        self.layout.addWidget(self.steps_label)
        self.layout.addWidget(self.steps_slider)
        self.layout.addWidget(self.launch_button)
        self.layout.addWidget(self.pause_button)
        self.layout.addWidget(self.resume_button)
        self.layout.addWidget(self.clear_button)

        # Animation state
        self.canvas = None
        self.anim = None

    def update_fps_label(self):
        self.fps_label.setText(f"Frames per Second: {self.fps_slider.value()}")

    def update_steps_label(self, value):
        self.steps_label.setText(f"Steps per Frame: {value}")

    def launch_animation(self):
        try:
            self.clear_animation()
            plt.close('all')

            fps = self.fps_slider.value()
            steps_per_frame = self.steps_slider.value()
            K_param = 1000

            rings = int(self.param_inputs["rg_param"].text())
            rays = int(self.param_inputs["ry_param"].text())
            w_param = float(self.param_inputs["w_param"].text())
            v_param = float(self.param_inputs["v_param"].text())
            N_param = self.param_inputs["N_param"].text()
            N_param = list(map(int, re.findall(r'\d+', N_param))) if N_param else []
            T_param = float(self.param_inputs["T_param"].text())
            d_tube = float(self.param_inputs["d_tube"].text())

            canvas = evo.animate_diffusion(
                rings, rays, w_param, v_param, N_param,
                K_param, T_param, d_tube,
                steps_per_frame=steps_per_frame,
                interval_ms=int(1000 / fps)
            )

            self.canvas = canvas
            self.anim = getattr(canvas, "ani", None)
            if self.canvas:
                self.layout.addWidget(self.canvas)
                self.canvas.draw()

            self.pause_button.setVisible(True)
            self.resume_button.setVisible(False)
            self.clear_button.setVisible(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Animation failed: {str(e)}")

    def pause_animation(self):
        try:
            if self.canvas and hasattr(self.canvas, "ani") and self.canvas.ani:
                self.canvas.ani.event_source.stop()
                self.pause_button.setVisible(False)
                self.resume_button.setVisible(True)
        except Exception as e:
            QMessageBox.critical(self, "Pause Error", f"Could not pause animation: {str(e)}")

    def resume_animation(self):
        try:
            if self.canvas and hasattr(self.canvas, "ani") and self.canvas.ani:
                self.canvas.ani.event_source.start()
                self.resume_button.setVisible(False)
                self.pause_button.setVisible(True)
        except Exception as e:
            QMessageBox.critical(self, "Resume Error", f"Could not resume animation: {str(e)}")

    def clear_animation(self):
        try:
            if self.canvas:
                if hasattr(self.canvas, "ani") and self.canvas.ani:
                    self.canvas.ani.event_source.stop()
                    self.canvas.ani = None

                self.layout.removeWidget(self.canvas)
                self.canvas.setParent(None)
                self.canvas.deleteLater()
                self.canvas = None

            self.pause_button.setVisible(False)
            self.resume_button.setVisible(False)
            self.clear_button.setVisible(False)
        except Exception as e:
            QMessageBox.critical(self, "Clear Error", f"Could not clear animation: {str(e)}")
