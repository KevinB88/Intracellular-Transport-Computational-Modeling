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

    MFPT_16 = launch.solve_mfpt_(16, 16, [0, 4, 8, 12], -1, 10**-4, 5, d_tube=0.01)
    print("MFPT(10^-4) 16x16: ", MFPT_16)
    MFPT_16 = launch.solve_mfpt_(16, 16, [0, 4, 8, 12], -1, 1, 5, d_tube=0.01)
    print("MFPT(1) 16x16: ", MFPT_16)
    MFPT_16 = launch.solve_mfpt_(16, 16, [0, 4, 8, 12], -1, 100, 5, d_tube=0.01)
    print("MFPT(100) 16x16: ", MFPT_16)

    launch.heatmap_production(16, 16, 10**-4, -1, [0, 4, 8, 12], time_point_container=[0.25, 0.5, 0.75],
                              rect_config=True, d_tube=0.01, show_plot=False)

    MFPT_32 = launch.solve_mfpt_(32, 32, [0, 8, 16, 24], -1, 10**-4, 5, d_tube=0.01)
    print("MFPT(10^-4) 32x32: ", MFPT_32)
    MFPT_32 = launch.solve_mfpt_(32, 32, [0, 8, 16, 24], -1, 1, 5, d_tube=0.01)
    print("MFPT(1) 32x32: ", MFPT_32)
    MFPT_32 = launch.solve_mfpt_(32, 32, [0, 8, 16, 24], -1, 100, 5, d_tube=0.01)
    print("MFPT(100) 32x32: ", MFPT_32)

    launch.heatmap_production(32, 32, 10 ** -4, -1, [0, 8, 16, 24], time_point_container=[0.25, 0.5, 0.75],
                              rect_config=True, d_tube=0.01, show_plot=False)

    MFPT_48 = launch.solve_mfpt_(48, 48, [0, 12, 24, 36], -1, 10**-4, 5, d_tube=0.01)
    print("MFPT(10^-4) 48x48: ", MFPT_48)
    MFPT_48 = launch.solve_mfpt_(48, 48, [0, 12, 24, 36], -1, 1, 5, d_tube=0.01)
    print("MFPT(1) 48x48: ", MFPT_48)
    MFPT_48 = launch.solve_mfpt_(48, 48, [0, 12, 24, 36], -1, 100, 5, d_tube=0.01)
    print("MFPT(100) 48x48: ", MFPT_48)

    launch.heatmap_production(48, 48, 10 ** -4, -1, [0, 12, 24, 36], time_point_container=[0.25, 0.5, 0.75],
                              rect_config=True, d_tube=0.01, show_plot=False)

    MFPT_64 = launch.solve_mfpt_(64, 64, [0, 16, 32, 48], -1, 10**-4, 5, d_tube=0.01)
    print("MFPT(10^-4) 64x64: ", MFPT_64)
    MFPT_64 = launch.solve_mfpt_(64, 64, [0, 16, 32, 48], -1, 1, 5, d_tube=0.01)
    print("MFPT(1) 64x64: ", MFPT_64)
    MFPT_64 = launch.solve_mfpt_(64, 64, [0, 16, 32, 48], -1, 100, 5, d_tube=0.01)
    print("MFPT(100) 64x64: ", MFPT_64)

    launch.heatmap_production(64, 64, 10 ** -4, -1, [0, 16, 32, 48], time_point_container=[0.25, 0.5, 0.75],
                              rect_config=True, d_tube=0.01, show_plot=False)


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
