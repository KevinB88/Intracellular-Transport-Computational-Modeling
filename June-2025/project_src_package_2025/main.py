import sys
import os
import numpy as np
from time import perf_counter
from datetime import datetime
from contextlib import redirect_stdout
from data_visualization import animation_functions as ani, plot_functions as plt
from computational_tools import analysis_tools as an
from computational_tools import struct_init as struct
from computational_tools import analysis_tools as ant, numerical_tools as num, supplements as sup, error_analysis as err
from auxiliary_tools import unit_conversion_functions as uni
from auxiliary_tools import format_conversion as form
from system_configuration import file_paths as fp
from launch_functions import launch
from computational_tools import time_analysis as tim
from project_src_package_2025.gui_components import main_gui as gui
from project_src_package_2025.data_visualization import ani_evolution as evo

# from . import gui, datetime, os, fp, sys, redirect_stdout
from multiprocessing import freeze_support

"""
Main entry point for the PyQt5 GUI application.
Includes output redirection and multiprocessing freeze support.
"""


def run_main():

    freeze_support()
    gui.run_app()


if __name__ == "__main__":

    """
    Log content produced by the terminal from relevant executions. 
    """

    today_str = datetime.now().strftime("%Y-%m-%d")

    log_dir = os.path.join(os.getcwd(), fp.rect_logs)

    os.makedirs(log_dir,  exist_ok=True)

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