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
from computational_tools import time_analysis as tim

from time import perf_counter


def run_main():

    print()

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
    solving for T in this case: 
    
    1 = floor(T / d_time)
    
    -> same as saying: 
    
    any value that is floored and equates to 1:
    
    1 = floor(A)
    
    A is between the range:   [1, 2) 
    
    T/d_time is between the range: [1, 2)
    
            1 <= T/d_time < 2
            d_time <= T < 2 * d_time
    
    in this case choose T = d_time             
'''