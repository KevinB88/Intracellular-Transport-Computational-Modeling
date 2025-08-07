from project_src_package_2025.gui_components import controller

def compute_and_send(queue, computation_name, param_dict):
    try:
        result = controller.run_selected_computation(computation_name, param_dict)
        queue.put({"status": "ok", "result": result})
    except Exception as e:
        queue.put({"status": "error", "message": str(e)})


# @staticmethod
#     def compute_and_send(queue, computation_name, param_dict):
#         try:
#             result = controller.run_selected_computation(computation_name, param_dict)
#             queue.put({"status": "ok", "result": result})
#         except Exception as e:
#             queue.put({"status": "error", "message": str(e)})

# def check_for_computation_results(self, computation_name):
#     if not self.mp_queue.empty():
#         response = self.mp_queue.get()
#         self.poll_timer.stop()
#         self.mp_process.join()
#
#         if response[ "status" ] == "ok":
#
#             self.output_display.append(
#                 f"Computation {computation_name} executed successfully.  [{self.produce_timestamp()}]")
#             self.process_result(response[ "result" ])
#         else:
#             QMessageBox.critical(self, "Error", response[ "message" ])
#             self.output_display.append(f"Computation {computation_name} failed.     [{self.produce_timestamp()}]")
#             self.set_launch_color("error")
#         self.launch_button.setEnabled(True)
#         self.spinner_movie.stop()
#         self.spinner_label.setVisible(False)

# def run_computation_mp(self):
#     self.set_launch_color("running")
#     self.launch_button.setEnabled(False)
#     self.spinner_label.setVisible(True)
#     self.spinner_movie.start()
#
#     try:
#         inputs = {param: field.text() for param, field in self.param_inputs.items()}
#         # print(inputs)
#         if not any(inputs.values()):
#             raise ValueError("No input parameters were provided.")
#
#         computation_name = self.comp_select.currentText()
#         if not computation_name:
#             raise ValueError("No computation type selected.")
#
#         self.output_display.append(
#             f"Launching computation: {computation_name}...       [{self.produce_timestamp()}]")
#
#         self.mp_queue = Queue()
#         self.mp_process = Process(target=self.compute_and_send, args=(self.mp_queue, computation_name, inputs))
#         self.mp_process.start()
#
#         # Start polling for results
#         self.poll_timer = QTimer()
#         self.poll_timer.timeout.connect(lambda: self.check_for_computation_results(computation_name))
#         self.poll_timer.start(100)
#     except Exception as e:
#
#         self.set_launch_color("error")
#         self.output_display.append(f"Computation {computation_name} failed.     [{self.produce_timestamp()}]")
#         QMessageBox.critical(self, "Input Error", str(e))
#         self.spinner_label.setVisible(False)
#         self.spinner_movie.stop()
#         self.launch_button.setEnabled(True)


# def process_result(self, result):
#     self.set_launch_color("success")
#
#     if "MFPT" in result:
#         # self.mfpt_label.setText(f"MFPT: {result['MFPT']:.6f}")
#         self.output_display.append(
#             f"Computation returned MFPT = {result[ 'MFPT' ]:.6f}       [{self.produce_timestamp()}]")
#
#     if "duration" in result:
#         self.output_display.append(
#             f"Dimensionless time duration: {result[ 'duration' ]:.6f}      [{self.produce_timestamp()}]")
#         # self.duration_label.setText(f"Duration: {result['duration']:.6f}")
#         # self.duration_label.show()
#
#     csv_paths = [ ]
#     png_paths = [ ]
#
#     if "output_dirs" in result:
#         csv_paths, png_paths = aux_gui_funcs.extract_csv_and_png_paths(result[ "output_dirs" ])
#         if csv_paths or png_paths:
#             self.output_files_widget.update_display(csv_paths, png_paths)
#             self.output_files_widget.show()
#             self.png_preview_widget.update_png_list(png_paths)
#             self.png_preview_widget.show()
#         else:
#             self.output_files_widget.hide()
#             self.png_preview_widget.hide()
#     else:
#         self.output_files_widget.hide()
#
#     record = computation_history_entry.ComputationRecord(
#         comp_type=self.comp_select.currentText(),
#         params={param: field.text() for param, field in self.param_inputs.items()},
#         mfpt=result.get("MFPT"),
#         duration=result.get("duration"),
#         csv_files=csv_paths,
#         png_files=png_paths,
#         status="completed",
#         error_msg=None
#     )
#
#     history_cache.cache.add_entry(record)
#     self.history_dropdown.addItem(record.display_name())
#     self.update_history_dropdown_visibility()
