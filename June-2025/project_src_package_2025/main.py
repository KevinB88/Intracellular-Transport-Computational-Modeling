import sys
import os
# from datetime import datetime
# from contextlib import redirect_stdout
from project_src_package_2025.gui_components import main_gui as gui
# from project_src_package_2025.launch_functions import launch
# from project_src_package_2025.auxiliary_tools import validity_checks as val
# from project_src_package_2025.system_configuration import file_paths as fp
# from project_src_package_2025.computational_tools import analysis_tools as ant
# from project_src_package_2025.computational_tools import supplements as sup
# from project_src_package_2025.data_visualization import ani_evolution as evo
# from project_src_package_2025.experimental import test_anim
from multiprocessing import freeze_support
from pathlib import Path
# import time
# import numpy as np

if getattr(sys, 'frozen', False):
    base_dir = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(os.path.dirname(sys.executable))
    project_path = base_dir / 'project_src_package_2025'
    sys.path.insert(0, str(project_path.parent))
else:
    # Development mode
    current = Path(__file__).resolve()
    sys.path.insert(0, str(current.parent.parent))


freeze_support()


def run_main():

    # rg_param = 16
    # ry_param = 16
    # v_param = 10.0
    # w_param = 100
    # N_param = [0, 4, 8, 12]
    # T_param = 0.5
    # T_points = [0.25, 0.5]

    gui.run_app()

    # print(launch.launch_super_comp_I(rg_param, ry_param, w_param, v_param, T_param, N_param, Timestamp_List=T_points, d_tube=0, T_fixed_ring_seg=0.1, MA_collection_factor=5))
    # launch.collect_mass_analysis(rg_param, ry_param, v_param, w_param, T_param, N_param)
    # launch.collect_phi_ang_dep(rg_param, ry_param, v_param, w_param, T_param, N_param, T_points, T_fixed_ring_seg=0.5)

    # launch.collect_density_rad_depend(rg_param, ry_param, N_param, v_param, w_param, T_param, T_points)

    # print(launch.output_time_until_mass_depletion(rg_param, ry_param, N_param, v_param, w_param))


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

