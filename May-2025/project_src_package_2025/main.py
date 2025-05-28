import sys
import os
from datetime import datetime
from contextlib import redirect_stdout

from launch_functions import launch
from computational_tools import analysis_tools as an
from data_visualization import animation_functions as ani, plot_functions as plt
from auxiliary_tools import unit_conversion_functions as uni
from system_configuration import file_paths as fp
from computational_tools import analysis_tools as ant, numerical_tools as num, supplements as sup
import time as clk
import math
import numpy as np


def run_main():
    rg_param = 36
    ry_param = 36
    v_param = -10
    N_param = [0, 9, 18, 27]
    w_param = 10 ** 3

    # mfpt, time = launch.solve_mfpt(rg_param, ry_param, N_param, v_param, w_param, mixed_config=True, return_duration=True, mx_cn_rrange=3)
    # print(mfpt, time)
    # mfpt, time = launch.solve_mfpt(rg_param, ry_param, N_param, v_param, w_param, mixed_config=False, return_duration=True)
    # print(mfpt, time)
    launch.collect_mass_analysis(rg_param, ry_param, N_param, v_param, w_param, T_param=1, collection_width=5,
                                 mixed_config=True, save_png=True, show_plt=False, mx_cn_rrange=36, init_j_max=-1)
    # diff, adv = sup.initialize_layers(rg_param, ry_param)

    # print(sup.j_max_bef_overlap(ry_param, N_param))

    # ant.comp_until_mass_depletion(rg_param, ry_param, w_param, w_param, v_param, N_param, diff, adv, mixed_config=True, mx_cn_rrange=5, init_j_max=-1)

    # launch.collect_phi_ang_dep(rg_param, ry_param, N_param, v_param, w_param, 3, time_point_container=[0.1, 0.2])
    # launch.collect_density_rad_depend(rg_param, ry_param, N_param, v_param, w_param, 0, [0.1, 0.2, 0.3], mixed_config=True)


if __name__ == "__main__":

    today_str = datetime.now().strftime("%Y-%m-%d")

    log_dir = os.path.join(os.getcwd(), fp.rect_logs)

    output_filename = os.path.join(log_dir, f"output_{today_str}.txt")

    class Tee:
        def __init__(self, *streams):
            self.streams = streams

        def write(self, data):
            for s in self.streams:
                s.write(data)

        def flush(self):
            for s in self.streams:
                s.flush()


    with open(output_filename, "w") as f:
        tee = Tee(sys.stdout, f)
        with redirect_stdout(tee):
            run_main()
