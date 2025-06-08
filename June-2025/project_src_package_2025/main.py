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
    rg_param = 48
    ry_param = 48
    T_param = 5
    v_param = -1
    d_tube = 0.01
    w_param = 10**-4
    N_param = [0, 12, 24, 36]


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


'''
    Produce a plot from the resulting MFPT data
    Construct an automatic MFPT(W) plotting function, allowing the user the option to specify for a number of domain sizes or number of microtubules.
    Next steps, port the codebase onto the mac book pro
    Write a function that automatically zips a file after it exceeds a file size threshold (for data output)
'''