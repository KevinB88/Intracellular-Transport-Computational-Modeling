import sys
import os
from datetime import datetime
from contextlib import redirect_stdout
from project_src_package_2025.gui_components import main_gui as gui
from project_src_package_2025.launch_functions import launch
from project_src_package_2025.auxiliary_tools import validity_checks as val
from project_src_package_2025.system_configuration import file_paths as fp
from project_src_package_2025.computational_tools import analysis_tools as ant
from project_src_package_2025.computational_tools import supplements as sup
from project_src_package_2025.data_visualization import ani_evolution as evo
from project_src_package_2025.experimental import test_anim
from multiprocessing import freeze_support
from pathlib import Path
import time
import numpy as np

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

    rg_param = 16
    ry_param = 16
    v_param = 10.0
    w_param = 100
    N_param = [0, 4, 8, 12]
    T_param = 0.06
    T_points = [0.03, 0.04]

    gui.run_app()

    # launch.launch_super_comp_I(rg_param, ry_param, w_param, v_param, T_param, N_param, Timestamp_List=T_points, d_tube=0, T_fixed_ring_seg=0.1)

    # Include simulation time onto mass analysis csv
    # Clarify which methods are robust and which are experimental/require extensive testing

    '''
        Tasks for the week:
        
        -Justify the asymmetry from previous typo in the code (refer to ani_evolution.py) 
        
        -Remain on standby for results from Ankush (so that I can compare my PDE results with)
        -performance with multiprocessing capabilities (running the GUI on one process, and launching the animation on another)  
        -Complete development of the software package 
        -Test new calc_mass() from numerical_tools.py
        -Develop a function to automate a results comparison (by comparing csvs automatically) 
    '''


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

