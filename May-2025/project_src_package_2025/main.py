import sys
import os
from datetime import datetime
from contextlib import redirect_stdout

from launch_functions import launch
from computational_tools import analysis_tools as an
from data_visualization import animation_functions as ani, plot_functions as plt
from auxiliary_tools import unit_conversion_functions as uni
from system_configuration import file_paths as fp
from computational_tools import analysis_tools as ant, numerical_tools as num, supplements as sup, \
    mfpt_comp_functions as mf
import time as clk
import math
import numpy as np


def run_main():
    rg_param = 36
    ry_param = 36
    v_param = -10
    N_param = [0, 9, 18, 27]
    w_param = 10 ** 3

    launch.collect_mass_analysis(rg_param, ry_param, N_param, v_param, w_param, T_param=0.1, collection_width=100, mixed_config=False)


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

