import multiprocessing
from PyQt5.QtCore import QTimer
from datetime import datetime
import traceback
import os


def compute_and_send(computation_name, parameters, queue):
    """Worker function executed inside a multiprocessing.Process."""
    try:
        # from launch_functions.launch import run_computation  # Your existing computation function
        from project_src_package_2025.gui_components import controller
        # result = run_computation(computation_name, parameters)
        result = controller.run_selected_computation(computation_name, parameters)
        queue.put(result)
    except Exception as e:
        queue.put(("error", str(e), traceback.format_exc()))

class ComputationExecutorMixin:
    def run_computation_mp(self, computation_name, parameters):
        """Start a multiprocessing computation and poll result."""
        self.output_console.append(f"Launching: {computation_name}")
        self.mp_queue = multiprocessing.Queue()
        self.process = multiprocessing.Process(
            target=compute_and_send,
            args=(computation_name, parameters, self.mp_queue)
        )
        self.process.start()
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.check_for_computation_results(computation_name))
        self.timer.start(100)

    def run_job_queue_mp(self):
        """Run all jobs in the job queue using multiprocessing."""
        self.pending_jobs = []
        for i in range(self.job_queue_widget.count()):
            item = self.job_queue_widget.item(i)
            job_data = item.data(0)
            self.pending_jobs.append(job_data)

        if not self.pending_jobs:
            self.output_console.append("No jobs to run.")
            return

        self.current_job = self.pending_jobs.pop(0)
        self.run_computation_mp(
            self.current_job["computation"],
            self.current_job["parameters"]
        )

    def check_for_computation_results(self, computation_name):
        """Check if the multiprocessing job is complete and handle result."""
        if self.mp_queue is not None and not self.mp_queue.empty():
            result = self.mp_queue.get()
            self.timer.stop()
            self.process_result(result, computation_name)

            # Launch next job if available
            if self.pending_jobs:
                self.current_job = self.pending_jobs.pop(0)
                self.run_computation_mp(
                    self.current_job["computation"],
                    self.current_job["parameters"]
                )

    def process_result(self, result):
        self.set_launch_color("success")

        if "MFPT" in result:
            self.output_console.append(
                f"Computation returned MFPT = {result[ 'MFPT' ]:.6f}       [{self.produce_timestamp()}]"
            )

        if "duration" in result:
            self.output_console.append(
                f"Dimensionless time duration: {result[ 'duration' ]:.6f}      [{self.produce_timestamp()}]"
            )

        csv_paths, png_paths = [ ], [ ]

        if "output_dirs" in result:
            # from auxiliary_tools import aux_gui_funcs  # ensure this is a top-level import in your module
            from project_src_package_2025.gui_components import aux_gui_funcs
            csv_paths, png_paths = aux_gui_funcs.extract_csv_and_png_paths(result[ "output_dirs" ])
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

        # from auxiliary_tools import computation_history_entry, history_cache  # safe for inline import
        from project_src_package_2025.gui_components import computation_history_entry, history_cache
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
