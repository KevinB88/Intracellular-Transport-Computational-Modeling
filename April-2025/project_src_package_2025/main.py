from launch_functions import launch
from data_visualization import animation_functions as ani, plot_functions as plt
from auxiliary_tools import unit_conversion_functions as uni
from system_configuration import file_paths as fp
from computational_tools import analysis_tools as ant, numerical_tools as num, supplements as sup, mfpt_comp_functions as mf
import time as clk
import math
import numpy as np

if __name__ == "__main__":

    rg_param = 32
    ry_param = 32
    v_param = -10
    N_param = [0, 8, 16, 24]
    w_param = 10**4

    diff, adv = sup.initialize_layers(rg_param, ry_param)

    mfpt_base = mf.comp_mfpt_by_mass_loss(rg_param, ry_param, w_param, w_param, v_param, N_param, diff, adv)
    mfpt_rec = mf.comp_mfpt_by_mass_loss_rect(rg_param, ry_param, w_param, w_param, v_param, N_param, diff, adv, rect_dist=2)

    print(f'MFPT under DL/AL updates in polar geometry: ', mfpt_base)
    print(f'MFPT under DL/AL updates in rectangular geometry: ', mfpt_rec)

    launch.collect_mass_analysis(rg_param, ry_param, N_param, v_param, w_param, 1.0, 100)
    launch.collect_mass_analysis(rg_param, ry_param, N_param, v_param, w_param, 1.0, 100, rect_config=True)

    launch.collect_density_rad_depend(rg_param, ry_param, N_param, v_param, w_param, 8, [0.1, 0.5, 0.9])
    launch.collect_density_rad_depend(rg_param, ry_param, N_param, v_param, w_param, 8, [0.1, 0.5, 0.9], rect_config=True)

    launch.collect_phi_ang_dep(rg_param, ry_param, N_param, v_param, w_param, approach=3, time_point_container=[0.1, 0.5, 0.9])
    launch.collect_phi_ang_dep(rg_param, ry_param, N_param, v_param, w_param, approach=3, time_point_container=[0.1, 0.5, 0.9], rect_config=True)

    ani.generate_heatmaps(rg_param, ry_param, w_param, v_param, N_param, approach=3, time_point_container=[0.1, 0.5, 0.9], verbose=True)
    ani.generate_heatmaps(rg_param, ry_param, w_param, v_param, N_param, approach=3, time_point_container=[0.1, 0.5, 0.9], verbose=True, rect_config=True)
