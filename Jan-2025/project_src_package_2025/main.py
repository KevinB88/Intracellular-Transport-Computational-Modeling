from launch_functions import launch
from data_visualization import animation_functions as ani, plot_functions as plt
from auxiliary_tools import unit_conversion_functions as uni
# from system_configuration import file_paths as fp
# from computational_tools import analysis_tools as ant

import time as clk

if __name__ == "__main__":

    # Computational configuration for 2/18/25

    # Task no. 1 : Collecting results for phi-v-theta amplitude radial dependence when 10% of the mass has exited from the domain.
    rg_param = 48
    ry_param = 48
    N_param = [0, 12, 24, 36]
    v_param = -1
    # w_param = 10 ** 4
    w_list = [10**-7, 10**-6, 10**-5, 10**-4, 10**-3, 10**-2, 10**-1, 10**0, 10, 10**2, 10**3, 10**4]
    launch.parallel_process_mfpt([N_param], rg_param, ry_param, "W", "V", v_param, w_list, cores=3)

'''

Just in case, can you also make some runs that start at smaller w?  Say, starting from w=10^(-7).  Try this for v=1 and v=10 for N=4.  I don't think there will be a transition at a lower w, but let's check.
'''


