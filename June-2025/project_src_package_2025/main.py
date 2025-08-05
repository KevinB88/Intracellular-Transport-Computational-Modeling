import sys
import os
# from datetime import datetime
# from contextlib import redirect_stdout
from project_src_package_2025.gui_components import main_gui as gui
from project_src_package_2025.launch_functions import launch
# from project_src_package_2025.auxiliary_tools import validity_checks as val
# from project_src_package_2025.system_configuration import file_paths as fp
# from project_src_package_2025.computational_tools import analysis_tools as ant
from project_src_package_2025.computational_tools import supplements as sup
# from project_src_package_2025.data_visualization import ani_evolution as evo
from project_src_package_2025.experimental.computational_test import numerical_methods as test
from multiprocessing import freeze_support
from pathlib import Path


def run_main():

    rg_param = 16
    ry_param = 16
    v_param = 10.0
    w_param = 100
    N_LIST = [0, 4, 8, 12]
    T_param = 2
    T_points = [0.75, 0.5, 0.25]

    gui.run_app()


if __name__ == "__main__":
    run_main()


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

