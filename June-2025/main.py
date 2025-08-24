import multiprocessing
from  project_src_package_2025.gui_components import main_gui as gui
from project_src_package_2025.launch_functions import launch
from project_src_package_2025.computational_tools import numerical_tools as num
from project_src_package_2025.computational_tools import time_analysis as tim
from project_src_package_2025.computational_tools import supplements as sup
from project_src_package_2025.auxiliary_tools import unit_conversion_functions

"""
Version 2.1  (August 8 2025)

personal notes/tasks:
    - Include version information onto documentation
    - Read upon professional/software engineer version control tips/how to name or properly archive previous versions of the codebase
    - Write a script to automatically delete all data contents [ def delete_ALL_output_() ]
    - Write a script to save all data contents onto the cloud (Google Drive API), then call delete_ALL_output_ [ def upload_to_cloud_() ] 
    - Incorporate delete_ALL_output_() and def upload_to_cloud_() onto GUI
    - Include custom plot options onto GUI (first by selecting the appropriate data file [.csv] to analyze ) 
@Kevin
"""

'''
    Bugs: 8/23/25
    
    d_tube message continues to stack.

'''


def run_main():
    gui.run_app()


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    run_main()

    # tim._launch_time_analysis_MFPT(75, 256, 1, 10**4, 2, [0, 64, 128, 192], 0.01, SingleStep=True, unit_conversion=False, iters=10**4)
    # tim._launch_time_analysis_MFPT(75, 128, 1, 10**4, 2, [0, 32, 64, 96], 0.01, SingleStep=True, unit_conversion=False, iters=10**4)

    # d_tube_max = sup.solve_d_rect(1, 75, 256, sup.j_max_bef_overlap(256, [0, 64, 128, 192]), 0)
    # d_tube_max = sup.solve_d_rect(1, 75, 128, sup.j_max_bef_overlap(128, [0, 32, 64, 96]), 0)
    # print(d_tube_max)

    # print(num.compute_K(75, 128, 2))
    # print(unit_conversion_functions.convert_seconds(1.2132784053129344e-07 * 93377602 * 75 * 128))

    # print(d_tube_max)

    # ~ 1.25 days (computation #1)
    # ~ 1.42 weeks (computation #2) 75, 256

# today_str = datetime.now().strftime("%Y-%m-%d")
#
# log_dir = os.path.join(os.getcwd(), fp.rect_logs)
#
# os.makedirs(log_dir,  exist_ok=True)
#
# output_filename = os.path.join(log_dir, f"output_{today_str}.txt")
#
# class Tee:
#     def __init__(self, *streams):
#         self.streams = streams
#
#     def write(self, data):
#         for s in self.streams:
#             s.write(data)
#
#     def flush(self):
#         for s in self.streams:
#             s.flush()
#
#
# with open(output_filename, "w") as f:
#     tee = Tee(sys.stdout, f)
#     with redirect_stdout(tee):
#         run_main()

