from launch_functions import launch
from data_visualization import animation_functions as ani, plot_functions as plt
from auxiliary_tools import unit_conversion_functions as uni
from system_configuration import file_paths as fp
from computational_tools import analysis_tools as ant, numerical_tools as num, supplements as sup
import time as clk
import math
import numpy as np

if __name__ == "__main__":

    rg_param = 48
    ry_param = 48
    v_param = -10
    N_param = [0, 12, 24, 36]
    T_param = 5

    launch.collect_mass_analysis(rg_param, ry_param, N_param, v_param, 0, T_param, collection_width=100, save_png=True)
    launch.collect_mass_analysis(rg_param, ry_param, N_param, v_param, 10 ** -4, T_param, collection_width=100, save_png=True)
    launch.collect_mass_analysis(rg_param, ry_param, N_param, v_param, 10 ** 0, T_param, collection_width=100, save_png=True)
    launch.collect_mass_analysis(rg_param, ry_param, N_param, v_param, 10**4, T_param, collection_width=100, save_png=True)