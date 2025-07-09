from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFormLayout,
    QLineEdit, QMessageBox, QCheckBox, QTextEdit, QGroupBox, QSpinBox, QDoubleSpinBox,
    QSizePolicy, QSlider, QStackedWidget, QTabWidget, QListWidget, QListWidgetItem, QDialogButtonBox,
    QDialog
)

from project_src_package_2025.job_queuing_system import job_queue

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QEvent

from . import parmas_config
from . import controller
# from . import stdout_redirector
from . import output_display_widget
from . import aux_gui_funcs

from . import computation_history_entry
from . import history_cache
from . import ani
from . import evo

import re
import ast

# loading spinner animation
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel


from datetime import datetime

import matplotlib.pyplot as plt

from multiprocessing import Process, Queue
from PyQt5.QtCore import QTimer


class ToggleSelectListWidget(QListWidget):
    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        current_item = self.currentItem()

        if item and item == current_item:
            self.clearSelection()
            self.clearFocus()
            # self.parent().toggle_move_buttons_visibility()
        else:
            super().mousePressEvent(event)

        self.parent().toggle_move_buttons_visibility()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clearSelection()
            self.clearFocus()
            # self.parent().toggle_move_buttons_visibility()
        else:
            super().keyPressEvent(event)

        self.parent().toggle_move_buttons_visibility()


class ControlPanel(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.jit_timer = None
        self.jit_compile_process = None
        self.job_timer = None
        self.job_process = None
        self.job_queue = None
        self.current_job = None
        self.pending_jobs = None
        self.mp_process = None
        self.poll_timer = None
        self.mp_queue = None
        self.current_canvas = None
        self.main_window = main_window

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.left_panel = QVBoxLayout()

        # Parameter form
        self.param_form = QFormLayout()
        self.param_inputs = {}

        # Advanced toggle
        self.advanced_toggle = QCheckBox("Show Advanced Parameters")
        self.advanced_toggle.stateChanged.connect(self.toggle_advanced_fields)
        self.advanced_widgets = []

        # Central Display area; to swap between results and visualization

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

        # History management

        self.history_dropdown = QComboBox()
        self.history_dropdown.addItem("Select Previous Computation: ")
        self.history_dropdown.currentIndexChanged.connect(self.load_history_entry)
        self.left_panel.addWidget(self.history_dropdown)

        for label in history_cache.cache.get_labels():
            self.history_dropdown.addItem(label)

        self.reset_params_button = QPushButton("Reset Parameters")
        self.reset_params_button.clicked.connect(self.clear_parameter_fields)
        self.left_panel.addWidget(self.reset_params_button)

        self.clear_hist_button = QPushButton("Clear History")
        self.clear_hist_button.clicked.connect(self.clear_history)
        self.left_panel.addWidget(self.clear_hist_button)

        self.right_panel = QVBoxLayout()

        self.main_layout.addLayout(self.left_panel, stretch=2)
        self.main_layout.addLayout(self.right_panel, stretch=3)

        # Clearing outputs

        self.clear_output_button = QPushButton("Clear Outputs")
        self.clear_output_button.clicked.connect(self.clear_displayed_results)
        self.left_panel.addWidget(self.clear_output_button)

        # Dropdown to select computation
        self.comp_label = QLabel("Select Computation:")
        self.comp_select = QComboBox()
        self.comp_select.addItems(parmas_config.PARAMETER_SCHEMAS.keys())
        self.comp_select.currentTextChanged.connect(self.update_parameter_fields)

        # Output display for MFPT and other information
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        # self.output_display.setFixedHeight(1)

        # self.mfpt_label = QLabel("MFPT: ")
        # self.duration_label = QLabel("")
        # self.duration_label.hide()

        # Launch button with status color

        button_row = QHBoxLayout()
        #
        # initializing the spinner
        self.spinner_label = QLabel()
        self.spinner_label.setVisible(False)

        spinner_location = "gui_components/visual_materials/gifs/spinner_100x100.gif"

        self.spinner_movie = QMovie(spinner_location)
        self.spinner_label.setMovie(self.spinner_movie)

        self.launch_button = QPushButton("Launch")
        self.launch_button.clicked.connect(self.run_computation_mp)
        # self.launch_button.clicked.connect(self.run_computation)
        self.set_launch_color("idle")

        self.enqueue_button = QPushButton("+")
        self.enqueue_button.setToolTip("Add this computation to the job queue")
        self.enqueue_button.clicked.connect(self.enqueue_job)

        self.run_queue_button = QPushButton("Execute Queue")
        self.run_queue_button.setToolTip("Start running enqueued computations")
        self.run_queue_button.clicked.connect(self.run_job_queue_mp)

        button_row.addWidget(self.launch_button)
        button_row.addWidget(self.spinner_label)
        button_row.addWidget(self.enqueue_button)
        button_row.addWidget(self.run_queue_button)

        self.left_panel.addLayout(button_row)

        # === Job Queue Display Panel ===
        self.queue_list_label = QLabel("Queued Jobs:")
        self.queue_list_widget = ToggleSelectListWidget()
        self.queue_list_widget.setFixedWidth(300)  # adjust size as needed
        self.queue_list_widget.itemSelectionChanged.connect(self.toggle_move_buttons_visibility)

        for job in job_queue.global_queue.jobs:
            item = QListWidgetItem(job.display_name())
            item.setData(Qt.UserRole, job)
            self.queue_list_widget.addItem(item)

        queue_panel = QVBoxLayout()
        queue_panel.addWidget(self.queue_list_label)
        queue_panel.addWidget(self.queue_list_widget)

        self.main_layout.addLayout(queue_panel)

        # Buttons for job manipulation
        self.edit_job_button = QPushButton("Edit Job")
        self.move_up_button = QPushButton("Move Up")
        self.move_down_button = QPushButton("Move Down")
        self.remove_job_button = QPushButton("Remove Job")
        self.clear_queue_button = QPushButton("Clear Queue")

        # Connect buttons
        self.edit_job_button.clicked.connect(self.edit_selected_job)
        self.move_up_button.clicked.connect(self.move_selected_job_up)
        self.move_down_button.clicked.connect(self.move_selected_job_down)
        self.remove_job_button.clicked.connect(self.remove_selected_job)
        self.clear_queue_button.clicked.connect(self.clear_entire_queue)

        # Add to layout
        queue_button_layout = QHBoxLayout()
        queue_button_layout.addWidget(self.edit_job_button)
        queue_button_layout.addWidget(self.move_up_button)
        queue_button_layout.addWidget(self.move_down_button)
        queue_button_layout.addWidget(self.remove_job_button)
        queue_button_layout.addWidget(self.clear_queue_button)

        queue_panel.addLayout(queue_button_layout)

        # Assemble layout
        self.left_panel.addWidget(self.comp_label)
        self.left_panel.addWidget(self.comp_select)
        self.left_panel.addLayout(self.param_form)
        self.left_panel.addWidget(self.advanced_toggle)
        self.left_panel.addWidget(self.launch_button)
        # self.left_panel.addWidget(self.mfpt_label)
        self.right_panel.addWidget(self.output_display)

        self.png_preview_widget = output_display_widget.PNGPreviewWidget()
        # self.right_panel.addWidget(self.png_preview_widget)
        self.result_layout.addWidget(self.png_preview_widget)
        self.png_preview_widget.hide()

        self.output_files_widget = output_display_widget.OutputFilesWidget()
        # self.right_panel.addWidget(self.output_files_widget)
        self.result_layout.addWidget(self.output_files_widget)
        self.output_files_widget.hide()

        self.restored_label = QLabel("")
        self.restored_label.setStyleSheet("Color: blue; font-weight: bold;")
        self.restored_label.hide()

        self.right_panel.addWidget(self.restored_label, alignment=Qt.AlignRight)
        self.plot_layout = QVBoxLayout()
        self.right_panel.addLayout(self.plot_layout)
        self.right_panel.addStretch()

        # Initialize parameter fields
        self.update_parameter_fields(self.comp_select.currentText())
        for line_edit in self.param_inputs.values():
            line_edit.installEventFilter(self)

        # real time update of domain preview relative to updates of the microtubules
        # self.param_inputs["N_param"].textChanged.connect(self.update_microtubules_live)

        # --- Visualization Dropdown Group ---

        viz_group = QGroupBox()
        viz_layout = QVBoxLayout()
        viz_group.setLayout(viz_layout)

        viz_label = QLabel("Select Visualization: ")
        viz_label.setStyleSheet("font-weight: bold;")
        self.visualization_select = QComboBox()
        self.visualization_select.addItems(["Show Domain", "Animate Diffusion"])
        self.visualization_select.currentTextChanged.connect(self.handle_visualization_mode_change)

        viz_layout.addWidget(viz_label)
        viz_layout.addWidget(self.visualization_select)

        # self.right_panel.addWidget(viz_group)
        self.visualization_layout.addWidget(viz_group)

        self.visualization_mode = "Show Domain"

        # --- Domain Visualization UI Group ---
        self.domain_checkbox_group = QGroupBox("Domain Grid Options")
        self.domain_checkbox_group.setStyleSheet("font-weight: bold;")

        checkbox_layout = QVBoxLayout()
        checkbox_layout.setContentsMargins(10, 15, 10, 10)

        self.display_extract_checkbox = QCheckBox("Display Extraction Region")
        self.toggle_border_checkbox = QCheckBox("Display Internal Borders")
        self.toggle_border_checkbox.setChecked(True)

        checkbox_layout.addWidget(self.display_extract_checkbox)
        checkbox_layout.addWidget(self.toggle_border_checkbox)

        # checkbox_layout.addSpacing(20)

        self.display_domain_button = QPushButton("Preview Domain")
        self.display_domain_button.clicked.connect(self.handle_display_domain)

        self.close_domain_button = QPushButton("Close Domain")
        self.close_domain_button.clicked.connect(self.close_domain)
        self.close_domain_button.hide()

        checkbox_layout.addWidget(self.display_domain_button)
        checkbox_layout.addWidget(self.close_domain_button)

        self.domain_checkbox_group.setLayout(checkbox_layout)
        center = self.get_widget_center_global(self.domain_checkbox_group)
        print(center)
        dims = self.get_widget_dimensions(self.domain_checkbox_group)
        print(dims)

        # Add this group to the right panel
        # self.right_panel.addWidget(self.domain_checkbox_group)
        self.visualization_layout.addWidget(self.domain_checkbox_group)
        # self.visualization_layout.setContentsMargins(0, 861, 0, 0)

        # --- Animation Mode UI ---
        self.animation_controls_group = QGroupBox("Animation Controls")
        self.animation_controls_group.setVisible(False)
        self.anim_layout = QVBoxLayout()

        # Steps per frame slider
        self.steps_slider = QSlider(Qt.Horizontal)
        self.steps_slider.setMinimum(1)
        self.steps_slider.setMaximum(150)
        self.steps_slider.setValue(10)
        self.steps_slider.setTickInterval(10)
        self.steps_slider.setTickPosition(QSlider.TicksBelow)

        self.steps_label = QLabel("Steps per Frame: 10")
        self.steps_slider.valueChanged.connect(
            lambda val: self.steps_label.setText(f"Steps per Frame: {val}")
        )

        # Frames per second slider
        self.interval_slider = QSlider(Qt.Horizontal)
        self.interval_slider.setMinimum(10)
        self.interval_slider.setMaximum(60)
        self.interval_slider.setValue(50)
        self.interval_slider.setTickInterval(5)
        self.interval_slider.setTickPosition(QSlider.TicksBelow)

        self.interval_label = QLabel("Frames per second: 50")
        self.interval_slider.valueChanged.connect(
            lambda val: self.interval_label.setText(f"Frames per Second: {val}")
        )

        # Launch button

        self.launch_animation_button = QPushButton("Launch Animation")
        self.launch_animation_button.setEnabled(False)
        self.launch_animation_button.setStyleSheet("background-color : lightgray")

        # Connect all relevant QLineEdit fields to validation
        for key in ["rg_param", "ry_param", "w_param", "v_param", "N_param", "T_param", "d_tube"]:
            if key in self.param_inputs:
                self.param_inputs[key].textChanged.connect(self.validate_animation)

        self.launch_animation_button.clicked.connect(self.handle_launch_animation)

        # Animation evolution display
        self.visualization_area = QStackedWidget()
        self.visualization_area.setMinimumSize(600, 600)
        # self.right_panel.addWidget(self.visualization_area)
        self.visualization_layout.addWidget(self.visualization_area)

        # Animation evolution buttons

        self.pause_button = QPushButton("Pause")
        self.pause_button.setEnabled(True)
        self.pause_button.clicked.connect(self.pause_animation)

        self.clear_ani_button = QPushButton("Clear Animation")
        self.clear_ani_button.setEnabled(True)
        self.clear_ani_button.clicked.connect(self.clear_animation)

        # print("Dropdown count:", self.history_dropdown.count())

        self.anim_layout.addWidget(self.pause_button)
        self.anim_layout.addWidget(self.clear_ani_button)

        # add to layout
        self.anim_layout.addWidget(self.steps_label)
        self.anim_layout.addWidget(self.steps_slider)
        self.anim_layout.addSpacing(10)
        self.anim_layout.addWidget(self.interval_label)
        # anim_layout.addWidget(self.fps_slider)
        self.anim_layout.addWidget(self.interval_slider)
        self.anim_layout.addSpacing(10)
        self.anim_layout.addWidget(self.launch_animation_button)

        self.animation_controls_group.setLayout(self.anim_layout)
        # self.animation_controls_group.setContentsMargins(0, 861, 0, 0)

        # <**> right panel
        # self.right_panel.addWidget(self.animation_controls_group)
        self.visualization_layout.addWidget(self.animation_controls_group)

        # for move button visibility
        self.toggle_move_buttons_visibility()
        self.update_queue_controls_visibility()
        self.update_history_dropdown_visibility()
        self.update_queue_execute_button_visibility()

        # experimental feature
        # self.initiate_JIT_compilation()

    '''
        For a future enqueue_job() method:

    job = ComputationRecord(
    comp_type=self.comp_select.currentText(),
    params=inputs,
    status="pending",
    time_for_execution=0
)
    '''
    def initiate_JIT_compilation(self):
        self.launch_button.setEnabled(False)
        self.enqueue_button.setEnabled(False)
        self.run_queue_button.setEnabled(False)
        self.launch_animation_button.setEnabled(False)

        self.output_display.append("Initiating JIT numba compilation...")
        self.output_display.append("Computational options will be temporarily disabled.")
        
        self.jit_compile_process = controller.initiate_compilation()
        
        self.jit_timer = QTimer()
        self.jit_timer.timeout.connect(self.check_jit_compilation_done)
        self.jit_timer.start(200)

    def check_jit_compilation_done(self):
        if self.jit_compile_process is not None and not self.jit_compile_process.is_alive():
            self.jit_timer.stop()
            self.jit_compile_process = None

            self.output_display.append("JIT numba compilation successfully executed.")
            self.output_display.append("Computational options are now enabled for usage.")

            self.launch_button.setEnabled(True)
            self.enqueue_button.setEnabled(True)
            self.run_queue_button.setEnabled(True)
            self.launch_animation_button.setEnabled(True)

    @staticmethod
    def get_widget_center_global(widget):
        geom = widget.geometry()
        center_local = geom.center()
        center_global = widget.mapToGlobal(center_local)
        return {"Center of widget in global coorindates: ": center_global}

    @staticmethod
    def get_widget_corners_global(widget):
        rect = widget.rect()

        top_left = widget.mapToGlobal(rect.topLeft())
        top_right = widget.mapToGlobal(rect.topRight())
        bottom_left = widget.mapToGlobal(rect.bottomLeft())
        bottom_right = widget.mapToGlobal(rect.bottomRight())

        return {
            "top_left": top_left,
            "top_right": top_right,
            "bottom_left": bottom_left,
            "bottom_right": bottom_right
        }

    @staticmethod
    def get_widget_dimensions(widget):
        width = widget.width()
        height = widget.height()
        return {"width:": width, "height": height}

    def update_queue_execute_button_visibility(self):
        has_jobs = self.queue_list_widget.count() > 0
        self.run_queue_button.setVisible(has_jobs)

    def update_history_dropdown_visibility(self):
        count = self.history_dropdown.count()
        has_real_items = count > 1  # Or adjust depending on placeholder logic
        # print(has_real_items)

        self.history_dropdown.setVisible(has_real_items)
        self.clear_hist_button.setVisible(has_real_items)

    # def update_history_dropdown_visibility(self):
    #     has_history = self.history_dropdown.count() > 1
    #
    #     self.history_dropdown.setVisible(has_history)
    #
    #     if has_history:
    #         if self.clear_button not in [self.anim_layout.itemAt(i).widget() for i in range(self.anim_layout.count())]:
    #             self.anim_layout.addWidget(self.clear_button)
    #         self.clear_button.show()
    #     else:
    #         self.anim_layout.removeWidget(self.clear_button)
    #         self.clear_button.hide()

    def update_queue_controls_visibility(self):
        has_jobs = self.queue_list_widget.count() > 0
        self.clear_queue_button.setVisible(has_jobs)

    def toggle_move_buttons_visibility(self):
        selected = len(self.queue_list_widget.selectedItems()) > 0

        self.move_up_button.setVisible(selected)
        self.move_down_button.setVisible(selected)
        self.remove_job_button.setVisible(selected)
        self.edit_job_button.setVisible(selected)

    def pause_animation(self):
        canvas = self.current_canvas
        if not hasattr(canvas, 'ani') or canvas.ani is None:
            return

        if canvas.ani_paused:
            canvas.ani.event_source.start()
            canvas.ani_paused = False
            self.pause_button.setText("Pause Animation")
        else:
            canvas.ani.event_source.stop()
            canvas.ani_paused = True
            self.pause_button.setText("Resume Animation")

    def clear_animation(self):
        canvas = self.current_canvas
        if canvas is not None:
            # Stop animation
            if hasattr(canvas, 'ani') and canvas.ani is not None:
                canvas.ani.event_source.stop()
                canvas.ani = None

            # Remove canvas from layout
            self.right_panel.removeWidget(canvas)
            canvas.setParent(None)

            # Clean up reference
            self.current_canvas= None

    def handle_launch_animation(self):
        try:
            rg = int(self.param_inputs["rg_param"].text())
            ry = int(self.param_inputs["ry_param"].text())
            w = float(self.param_inputs["w_param"].text())
            v = float(self.param_inputs["v_param"].text())
            N_raw = self.param_inputs["N_param"].text()
            N = list(map(int, re.findall(r'\d+', N_raw))) if N_raw else []
            T = float(self.param_inputs["T_param"].text())
            d_tube = float(self .param_inputs["d_tube"].text())

            steps_per_frame = self.steps_slider.value()
            fps = self.interval_slider.value()
            interval_ms = int(1000 / fps)
            K_param = 1000
            color_scheme = 'viridis'
            canvas = evo.animate_diffusion(rg, ry, w, v, N, K_param,
                                  T, d_tube, steps_per_frame=steps_per_frame,
                                  interval_ms=interval_ms,
                                  color_scheme=color_scheme)
            if hasattr(self, 'current_canvas') and self.current_canvas:
                self.visualization_area.removeWidget(self.current_canvas)
                self.current_canvas.setParent(None)

            self.current_canvas = canvas
            self.visualization_area.addWidget(canvas)
            self.visualization_area.setCurrentWidget(canvas)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch animation: \n{str(e)}")

    def handle_visualization_mode_change(self, mode):
        self.visualization_mode = mode

        if mode == "Show Domain":
            self.show_domain_ui()
        elif mode == "Animate Diffusion":
            self.show_animation_ui()

    def show_domain_ui(self):
        self.domain_checkbox_group.show()
        self.display_domain_button.show()
        self.close_domain_button.show()

        self.animation_controls_group.hide()

    def show_animation_ui(self):
        self.domain_checkbox_group.hide()
        self.display_domain_button.hide()
        self.close_domain_button.hide()

        self.animation_controls_group.show()
        self.validate_animation()

    def validate_animation(self):
        required_keys = ["rg_param", "ry_param", "w_param", "v_param",
                         "N_param", "T_param", "d_tube"]
        inputs_filled = all(
            key in self.param_inputs and self.param_inputs[key].text().strip() != ""
            for key in required_keys
        )

        if inputs_filled:
            self.launch_animation_button.setEnabled(True)
            self.launch_animation_button.setStyleSheet("background-color: lightgreen")
        else:
            self.launch_animation_button.setEnabled(False)
            self.launch_animation_button.setStyleSheet("background-color: lightgray")

    def update_parameter_fields(self, computation_name):
        # Clear previous inputs
        for i in reversed(range(self.param_form.count())):
            self.param_form.removeRow(i)

        self.param_inputs.clear()
        self.advanced_widgets.clear()

        schema = parmas_config.PARAMETER_SCHEMAS[computation_name]

        # Add required fields
        for param, default in schema.get("required", []):
            input_field = QLineEdit()
            self.param_form.addRow(f"{param}:", input_field)
            self.param_inputs[param] = input_field

        # Add default/advanced fields (initially hidden)
        for param, value in schema.get("default", []):
            input_field = QLineEdit(str(value))
            self.param_inputs[param] = input_field
            label = QLabel(f"{param}:")
            label.setVisible(False)
            input_field.setVisible(False)
            self.param_form.addRow(label, input_field)
            self.advanced_widgets.append((label, input_field))

    def toggle_advanced_fields(self, state):
        show = state == Qt.Checked
        for label, field in self.advanced_widgets:
            label.setVisible(show)
            field.setVisible(show)

    def set_launch_color(self, state):
        palette = self.launch_button.palette()
        color = QColor("lightgray")
        if state == "running":
            color = QColor("green")
        elif state == "success":
            color = QColor("lightgreen")
        elif state == "error":
            color = QColor("lightcoral")

        palette.setColor(QPalette.Button, color)
        self.launch_button.setAutoFillBackground(True)
        self.launch_button.setPalette(palette)
        self.launch_button.update()

    @staticmethod
    def compute_and_send(queue, computation_name, param_dict):
        try:
            result = controller.run_selected_computation(computation_name, param_dict)
            queue.put({"status": "ok", "result": result})
        except Exception as e:
            queue.put({"status": "error", "message": str(e)})

    @staticmethod
    def produce_timestamp():
        timestamp = datetime.now().strftime("%I:%M %p %m/%d/%Y")
        timestamp = timestamp.replace(" 0", " ").replace("/0", "/")
        return timestamp

    def check_for_computation_results(self, computation_name):
        if not self.mp_queue.empty():
            response = self.mp_queue.get()
            self.poll_timer.stop()
            self.mp_process.join()

            if response["status"] == "ok":

                self.output_display.append(f"Computation {computation_name} executed successfully.  [{self.produce_timestamp()}]")
                self.process_result(response["result"])
            else:
                QMessageBox.critical(self, "Error", response["message"])
                self.output_display.append(f"Computation {computation_name} failed.     [{self.produce_timestamp()}]")
                self.set_launch_color("error")
            self.launch_button.setEnabled(True)
            self.spinner_movie.stop()
            self.spinner_label.setVisible(False)

    def run_computation_mp(self):
        self.set_launch_color("running")
        # self.output_display.clear()
        # self.mfpt_label.setText("MFPT: ")
        # self.duration_label.hide()
        self.launch_button.setEnabled(False)
        self.spinner_label.setVisible(True)
        self.spinner_movie.start()

        try:
            inputs = {param: field.text() for param, field in self.param_inputs.items()}
            print(inputs)
            if not any(inputs.values()):
                raise ValueError("No input parameters were provided.")

            computation_name = self.comp_select.currentText()
            if not computation_name:
                raise ValueError("No computation type selected.")

            self.output_display.append(f"Launching computation: {computation_name}...       [{self.produce_timestamp()}]")

            self.mp_queue = Queue()
            self.mp_process = Process(target=self.compute_and_send, args=(self.mp_queue, computation_name, inputs))
            self.mp_process.start()

            # Start polling for results
            self.poll_timer = QTimer()
            self.poll_timer.timeout.connect(lambda: self.check_for_computation_results(computation_name))
            self.poll_timer.start(100)
        except Exception as e:

            self.set_launch_color("error")
            self.output_display.append(f"Computation {computation_name} failed.     [{self.produce_timestamp()}]")
            QMessageBox.critical(self, "Input Error", str(e))
            self.spinner_label.setVisible(False)
            self.spinner_movie.stop()
            self.launch_button.setEnabled(True)

    def process_result(self, result):
        self.set_launch_color("success")

        if "MFPT" in result:
            # self.mfpt_label.setText(f"MFPT: {result['MFPT']:.6f}")
            self.output_display.append(f"Computation returned MFPT = {result['MFPT']:.6f}       [{self.produce_timestamp()}]")

        if "duration" in result:
            self.output_display.append(f"Dimensionless time duration: {result['duration']:.6f}      [{self.produce_timestamp()}]")
            # self.duration_label.setText(f"Duration: {result['duration']:.6f}")
            # self.duration_label.show()

        csv_paths = []
        png_paths = []

        if "output_dirs" in result:
            csv_paths, png_paths = aux_gui_funcs.extract_csv_and_png_paths(result["output_dirs"])
            if csv_paths or png_paths:
                self.output_files_widget.update_display(csv_paths, png_paths)
                self.output_files_widget.show()
                self.png_preview_widget.update_png_list(png_paths)
                self.png_preview_widget.show()
            else:
                self.output_files_widget.hide()
                self.png_preview_widget.hide()
        else:
            self.output_files_widget.hide()

        record = computation_history_entry.ComputationRecord(
            comp_type=self.comp_select.currentText(),
            params={param: field.text() for param, field in self.param_inputs.items()},
            mfpt=result.get("MFPT"),
            duration=result.get("duration"),
            csv_files=csv_paths,
            png_files=png_paths,
            status="completed",
            error_msg=None
        )

        history_cache.cache.add_entry(record)
        self.history_dropdown.addItem(record.display_name())
        self.update_history_dropdown_visibility()

    def run_computation(self):
        self.set_launch_color("running")
        self.output_display.clear()
        # self.mfpt_label.setText("MFPT: ")
        self.duration_label.hide()

        try:
            inputs = {param: field.text() for param, field in self.param_inputs.items()}
            result = controller.run_selected_computation(self.comp_select.currentText(), inputs)
            print(f"Result: {result}")  # For now, log result in terminal

            if isinstance(result, dict):
                if "MFPT" in result:
                    # self.mfpt_label.setText(f"MFPT: {result['MFPT']:.6f}")
                    self.output_display.append(f"Computation returned MFPT = {result['MFPT']:.6f}\n")
                if "duration" in result:
                    self.duration_label.setText(f"Duration: {result['duration']:.6f} seconds")
                    self.duration_label.show()
            self.set_launch_color("success")

            csv_paths = []
            png_paths = []

            if "output_dirs" in result:
                csv_paths, png_paths = aux_gui_funcs.extract_csv_and_png_paths(result["output_dirs"])
                if csv_paths or png_paths:
                    self.output_files_widget.update_display(csv_paths, png_paths)
                    self.output_files_widget.show()
                    self.png_preview_widget.update_png_list(png_paths)
                    self.png_preview_widget.show()
                else:
                    self.output_files_widget.hide()
                    self.png_preview_widget.hide()
            else:
                self.output_files_widget.hide()

            status = "completed"
            error_msg = None

            try:
                result = controller.run_selected_computation(self.comp_select.currentText(), inputs)
            except Exception as e:
                result = {}
                status = "failed"
                error_msg = str(e)
                QMessageBox.critical(self, "Error", str(e))
                self.set_launch_color("error")

            record = computation_history_entry.ComputationRecord(
                comp_type=self.comp_select.currentText(),
                params=inputs,
                mfpt=result.get("MFPT"),
                duration=result.get("duration"),
                csv_files=csv_paths,
                png_files=png_paths,
                status=status,
                error_msg=error_msg
            )

            history_cache.cache.add_entry(record)
            self.history_dropdown.addItem(record.display_name())
            self.update_history_dropdown_visibility()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.set_launch_color("error")

    def load_entry(self, entry):

        if entry.duration is not None:
            # self.duration_label.setText(f"Duration: {entry.duration:.6f}")
            self.output_display.append(f"<RESTORED> Dimensionless time: {entry.duration:.6f}    [{self.produce_timestamp()}]")
            # self.duration_label.show()

        # Update output files
        self.output_files_widget.update_display(entry.csv_files or [], entry.png_files or [])
        self.output_files_widget.show()

    def set_computation(self, computation_name):
        self.comp_select.setCurrentText(computation_name)
        self.update_parameter_fields(computation_name)

    def set_parameters(self, params: dict):
        for key, val in params.items():
            if key in self.param_inputs:
                self.param_inputs[key].setText(str(val))

    def show_restored_message(self, record):
        label_text = f"Restored: {record.comp_type} ({record.timestamp})"
        self.restored_label.setText(label_text)
        self.restored_label.show()

    def clear_history(self):
        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            "Are you sure you want to delete all saved history?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            history_cache.cache.clear()
            self.history_dropdown.clear()
            self.history_dropdown.addItem("Select Previous Computation: ")
            self.clear_displayed_results()
            self.clear_parameter_fields()
        self.update_history_dropdown_visibility()

    def clear_parameter_fields(self):
        self.update_parameter_fields(self.comp_select.currentText())
        # self.mfpt_label.setText("MFPT: ")
        self.output_display.clear()

    def clear_displayed_results(self):
        self.output_files_widget.hide()
        self.png_preview_widget.hide()
        self.restored_label.hide()
        # self.png_preview_widget.update_png_list()

    def load_history_entry(self, index):
        if index == 0:
            return  # Ignore placeholder

        entry = history_cache.cache.get_entry(index - 1)
        if not entry:
            return

        self.set_computation(entry.comp_type)
        self.set_parameters(entry.params)

        if entry.duration is not None:
            # self.duration_label.setText(f"Duration: {entry.duration:.6f} seconds")
            self.output_display.append(
                f"<RESTORED> Dimensionless time: {entry.duration:.6f}     [{self.produce_timestamp()}]")

        self.output_files_widget.update_display(entry.csv_files or [], entry.png_files or [])
        self.output_files_widget.show()

        self.show_restored_message(entry)
        self.png_preview_widget.update_png_list(entry.png_files or [])
        self.png_preview_widget.show()
        self.update_history_dropdown_visibility()

    def handle_display_domain(self):
        try:
            self.clear_animation()  # Automatically stop animation if active

            rings = int(self.param_inputs["rg_param"].text())
            rays = int(self.param_inputs["ry_param"].text())
            d_tube = float(self.param_inputs["d_tube"].text())

            try:
                microtubules_input = self.param_inputs["N_param"].text()
                parsed = ast.literal_eval(microtubules_input)
                microtubules = list(parsed) if isinstance(parsed, (list, tuple)) else [int(parsed)]
            except (ValueError, SyntaxError):
                print("[Error] Invalid microtubule input. Please enter a list like [0,1,2] or comma-separated values.")
                microtubules = []

            display_extract = self.display_extract_checkbox.isChecked()
            toggle_border = self.toggle_border_checkbox.isChecked()

            # Get domain figure
            fig = ani.display_domain_grid(
                rings=rings,
                rays=rays,
                microtubules=microtubules,
                d_tube=d_tube,
                display_extract=display_extract,
                toggle_border=toggle_border
            )

            # Clear previous canvas if any
            if hasattr(self, 'current_canvas') and self.current_canvas:
                self.visualization_area.removeWidget(self.current_canvas)
                self.current_canvas.setParent(None)

            # Add new domain canvas
            canvas = FigureCanvas(fig)
            self.current_canvas = canvas
            self.visualization_area.addWidget(canvas)
            self.visualization_area.setCurrentWidget(canvas)

            self.close_domain_button.show()
            self.display_domain_button.setText("Update Domain")

        except Exception as e:
            print(f"[Error] Failed to display domain grid: {e}")

    def close_domain(self):
        if hasattr(self, "plot_layout"):
            for i in reversed(range(self.plot_layout.count())):
                widget = self.plot_layout.itemAt(i).widget()
                if widget is not None:
                    widget.setParent(None)

        self.close_domain_button.hide()
        self.display_domain_button.setText("Display Domain")

    def display_matplotlib_figure(self, fig):
        for i in reversed(range(self.plot_layout.count())):
            widget_to_remove = self.plot_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
                widget_to_remove.deleteLater()
        canvas = FigureCanvas(fig)
        canvas.setParent(self)

        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas.updateGeometry()

        self.plot_layout.addWidget(canvas)
        canvas.draw()
        canvas.show()

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress:
            if isinstance(source, QLineEdit):
                keys = list(self.param_inputs.values())
                idx = keys.index(source)

                if event.key() == Qt.Key_Up:
                    prev_idx = (idx - 1) % len(keys)
                    keys[prev_idx].setFocus()
                    return True
                elif event.key() == Qt.Key_Down:
                    next_idx = (idx + 1) % len(keys)
                    keys[next_idx].setFocus()
                    return True
        return super().eventFilter(source, event)

    def enqueue_job(self):
        inputs = {param: field.text() for param, field in self.param_inputs.items()}
        comp_type = self.comp_select.currentText()

        job = computation_history_entry.ComputationRecord(
            comp_type=comp_type,
            params=inputs,
            status="pending",
            time_for_execution=0
        )

        job_queue.global_queue.enqueue(job)
        self.output_display.append(f"Job enqueued: {job.display_name()}     [{self.produce_timestamp()}]")
        # self.queue_list_widget.addItem(job.display_name())

        item = QListWidgetItem(job.display_name())
        item.setData(Qt.UserRole, job)
        self.queue_list_widget.addItem(item)
        self.update_queue_controls_visibility()
        self.update_queue_execute_button_visibility()

    def run_job_queue_mp(self):
        self.pending_jobs = job_queue.global_queue.get_jobs()
        if not self.pending_jobs:
            QMessageBox.information(self, "Job Queue", "No jobs in the queue")
            return
        self.output_display.append(f"Starting {len(self.pending_jobs)} queued job(s) ...        [{self.produce_timestamp()}]")
        self.queue_list_widget.clear()
        self.run_next_job()

    def run_next_job(self):

        if not self.pending_jobs:
            self.output_display.append(f"Job queue finished.     [{self.produce_timestamp()}]")
            job_queue.global_queue.clear_queue()
            self.update_history_dropdown_visibility()
            return

        self.spinner_label.setVisible(True)
        self.spinner_movie.start()

        self.current_job = self.pending_jobs.pop(0)
        job = self.current_job

        self.output_display.append(f"Running: {job.display_name()}      [{self.produce_timestamp()}]")
        self.set_launch_color("running")
        # self.duration_label.hide()
        # self.mfpt_label.setText("MFPT: ")
        self.output_display.repaint()

        self.job_queue = Queue()
        self.job_process = Process(target=self.compute_and_send, args=(self.job_queue, job.comp_type, job.params))
        self.job_process.start()
        
        self.job_timer = QTimer()
        self.job_timer.timeout.connect(self.check_job_result)
        self.job_timer.start(100)

    def check_job_result(self):
        if not self.job_queue.empty():
            self.job_timer.stop()
            response = self.job_queue.get()
            self.job_process.join()

            if response["status"] == "ok":
                self.handle_completed_job(response["result"])
            else:
                self.handle_failed_job(response["message"])

    def handle_completed_job(self, result):
        job = self.current_job
        job.status = "completed"
        job.error_msg = None

        job.mfpt = result.get("MFPT")
        job.duration = result.get("duration")

        output_dirs = result.get("output_dirs")
        if output_dirs:
            # self.output_display.append("Content stored")
            job.csv_files, job.png_files = aux_gui_funcs.extract_csv_and_png_paths(output_dirs)

        if job.mfpt:
            self.output_display.append(f"Computation returned MFPT = {job.mfpt:.6f}     [{self.produce_timestamp()}]")

        if job.duration:
            self.output_display.append(
                f"Dimensionless time: {job.duration}:.6f     [{self.produce_timestamp()}]")

        if job.csv_files or job.png_files:
            self.output_files_widget.update_display(job.csv_files, job.png_files)
            self.output_files_widget.show()
            self.png_preview_widget.update_png_list(job.png_files)
            self.png_preview_widget.show()
        else:
            self.output_files_widget.hide()
            self.png_preview_widget.hide()

        self.output_display.append(f"Job: {job_queue.global_queue.getComputationType(job)} executed successfully.       [{self.produce_timestamp()}]")

        # Record and clean up
        self.set_launch_color("success")
        history_cache.cache.add_entry(job)
        self.history_dropdown.addItem(job.display_name())
        self.remove_visual_job(job)
        self.spinner_label.setVisible(False)
        self.spinner_movie.stop()
        self.run_next_job()

    def handle_failed_job(self, error_msg):
        job = self.current_job
        job.status = "failed"
        job.error_msg = error_msg

        self.set_launch_color("error")
        self.output_display.append(f"Job failed: {error_msg}        [{self.produce_timestamp()}]")
        QMessageBox.critical(self, "Job Failed", f"Job {job.display_name()} failed:\n{error_msg}")

        history_cache.cache.add_entry(job)
        self.history_dropdown.addItem(job.display_name())
        self.remove_visual_job(job)

        self.spinner_label.setVisible(False)
        self.spinner_movie.stop()
        self.run_next_job()

    def run_job_queue(self):
        jobs = job_queue.global_queue.get_jobs()
        if not jobs:
            QMessageBox.information(self, "Job Queue", "No jobs in the queue.")
            return

        self.output_display.append(f"Starting {len(jobs)} queued job(s)...      [{self.produce_timestamp()}]")
        self.spinner_label.setVisible(True)
        self.spinner_movie.start()

        while jobs:
            job = jobs.pop(0)

            self.output_display.append(f"Running: {job.display_name()}")

            try:
                result = controller.run_selected_computation(job.comp_type, job.params)

                job.mfpt = result.get("MFPT")
                job.duration = result.get("duration")
                job.status = "completed"
                job.error_msg = None

                output_dirs = result.get("output_dirs")
                if output_dirs:
                    job.csv_files, job.png_files = aux_gui_funcs.extract_csv_and_png_paths(output_dirs)

                # Update display like in run_computation()
                if job.mfpt:
                    self.mfpt_label.setText(f"MFPT: {job.mfpt:.6f}")
                    self.output_display.append(f"Computation returned MFPT = {job.mfpt:.6f}         [{self.produce_timestamp()}]")
                if job.duration:
                    # self.duration_label.setText(f"Duration: {job.duration:.6f} seconds")
                    self.output_display.append(
                        f"Dimensionless time: {job.duration}:.6f     [{self.produce_timestamp()}]")
                    # self.duration_label.show()

                if job.csv_files or job.png_files:
                    self.output_files_widget.update_display(job.csv_files, job.png_files)
                    self.png_preview_widget.update_png_list(job.png_files)
                    self.output_files_widget.show()
                    self.png_preview_widget.show()
                else:
                    self.output_files_widget.hide()
                    self.png_preview_widget.hide()

            except Exception as e:
                job.status = "failed"
                job.error_msg = str(e)
                QMessageBox.critical(self, "Error", f"Job {job.display_name()} failed:\n{str(e)}")
                self.output_display.append(f"Job failed: {str(e)}       [{self.produce_timestamp()}]")

            # Save and archive job
            history_cache.cache.add_entry(job)
            self.history_dropdown.addItem(job.display_name())
            self.remove_visual_job(job)
            self.spinner_label.setVisible(False)
            self.spinner_movie.stop()

        # Clear queue after finishing
        job_queue.global_queue.clear_queue()
        self.output_display.append(f"Job queue finished.     [{self.produce_timestamp()}]")
        self.queue_list_widget.clear()
        self.update_history_dropdown_visibility()

    def remove_visual_job(self, job):
        for i in range(self.queue_list_widget.count()):
            item = self.queue_list_widget.item(i)
            if item.data(Qt.UserRole) == job:
                self.queue_list_widget.takeItem(i)
                break

    def edit_selected_job(self):
        item = self.queue_list_widget.currentItem()
        if not item:
            return

        job = item.data(Qt.UserRole)

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Job Parameters")
        layout = QFormLayout(dialog)

        fields = {}
        for key, val in job.params.items():
            line = QLineEdit(str(val))
            layout.addRow(QLabel(key), line)
            fields[ key ] = line

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)

        def on_accept():
            for key in job.params:
                job.params[ key ] = fields[ key ].text()
            item.setText(job.display_name())  # Update label if needed
            dialog.accept()

        button_box.accepted.connect(on_accept)
        button_box.rejected.connect(dialog.reject)

        dialog.exec_()

    def move_selected_job_up(self):
        row = self.queue_list_widget.currentRow()
        if row <= 0:
            return

        item = self.queue_list_widget.takeItem(row)
        self.queue_list_widget.insertItem(row - 1, item)
        self.queue_list_widget.setCurrentRow(row - 1)

        job_queue.global_queue.jobs[ row ], job_queue.global_queue.jobs[ row - 1 ] = \
            job_queue.global_queue.jobs[ row - 1 ], job_queue.global_queue.jobs[ row ]

    def move_selected_job_down(self):
        row = self.queue_list_widget.currentRow()
        if row < 0 or row >= self.queue_list_widget.count() - 1:
            return

        item = self.queue_list_widget.takeItem(row)
        self.queue_list_widget.insertItem(row + 1, item)
        self.queue_list_widget.setCurrentRow(row + 1)

        job_queue.global_queue.jobs[ row ], job_queue.global_queue.jobs[ row + 1 ] = \
            job_queue.global_queue.jobs[ row + 1 ], job_queue.global_queue.jobs[ row ]

    def remove_selected_job(self):
        item = self.queue_list_widget.currentItem()
        if not item:
            return

        job = item.data(Qt.UserRole)
        # print(job_queue.global_queue.getComputationType(job))
        self.output_display.append(f"Removed job: '{job_queue.global_queue.getComputationType(job)}' from queue.      [{self.produce_timestamp()}]")
        # Remove from GUI
        job_queue.global_queue.remove(job)
        self.queue_list_widget.takeItem(self.queue_list_widget.currentRow())
        self.update_queue_controls_visibility()
        self.update_queue_execute_button_visibility()

    def clear_entire_queue(self):
        # Clear job queue
        job_queue.global_queue.clear_queue()

        # Clear GUI
        self.queue_list_widget.clear()
        self.update_queue_controls_visibility()
        self.update_queue_execute_button_visibility()
        self.output_display.clear()








