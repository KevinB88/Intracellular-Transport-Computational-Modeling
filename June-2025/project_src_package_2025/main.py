import sys
import os
import numpy as np
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


def run_main():

    RG_PARAM = 48
    RY_PARAM = 48
    N_PARAM = [0, 6, 12, 18, 24, 30, 36, 42]
    D_TUBE = 0.01
    # D_tube should range between (0,1)

    D_THETA = (2 * np.pi) / RY_PARAM
    D_RADIUS = 1 / RG_PARAM

    struct.export_rect_config_structure_to_csv(RG_PARAM, RY_PARAM, N_PARAM,
                                               D_THETA, D_RADIUS, D_TUBE, fp.general_output)


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

