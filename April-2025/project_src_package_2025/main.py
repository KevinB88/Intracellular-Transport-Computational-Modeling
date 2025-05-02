import sys
import os
from datetime import datetime
from contextlib import redirect_stdout

from launch_functions import launch
from data_visualization import animation_functions as ani, plot_functions as plt
from auxiliary_tools import unit_conversion_functions as uni
from system_configuration import file_paths as fp
from computational_tools import analysis_tools as ant, numerical_tools as num, supplements as sup, mfpt_comp_functions as mf
import time as clk
import math
import numpy as np


def run_main():
    rg_param = 32
    ry_param = 32
    v_param = -10
    N_param = [0, 8, 16, 24]
    w_param = 1000
    rect_dist = 2

    # testing params
    # rg_param = 16
    # ry_param = 16
    # v_param = -10
    # N_param = [0, 4, 8, 12]
    # w_param = 1000
    # rect_dist = 0.05

    '''
        Try out for d=0.05
        
        N=4, W=1000 
        
        On 64x64 
        
        Updates to make to launch functions: 
        
        Plotting comparisons between trajectories, for instance,
        making comparisons between polar and rectangular trajectories on over lay plots.
        
        create a launch function to execute this operation. Other ideas, construct a python notebook
        
        create a full-analysis function that will compute the differences between two given configurations of the same domain size: 
        
        rect-config versus polar-config 
        
    '''

    start = clk.time()

    diff, adv = sup.initialize_layers(rg_param, ry_param)

    # mfpt_p = mf.comp_mfpt_by_mass_loss(rg_param, ry_param, w_param, w_param, v_param, N_param, diff, adv)
    mfpt = mf.comp_mfpt_by_mass_loss_rect(rg_param, ry_param, w_param, w_param, v_param, N_param, diff, adv, rect_dist)

    # print("MFPT from polar collection region config:", mfpt_p)
    print("MFPT from rectified collection region config:", mfpt)

    launch.collect_phi_ang_dep(rg_param, ry_param, N_param, v_param, w_param, 3, time_point_container=[0.1, 0.5, 0.9], rect_config=True, rect_dist=rect_dist, show_plt=False)
    # launch.collect_phi_ang_dep(rg_param, ry_param, N_param, v_param, w_param, 3, time_point_container=[0.1, 0.5, 0.9], rect_config=False, rect_dist=rect_dist, show_plt=False)

    launch.collect_density_rad_depend(rg_param, ry_param, N_param, v_param, w_param, 4, time_point_container=[0.1, 0.5, 0.9], rect_config=True, rect_dist=rect_dist, show_plt=False)
    # launch.collect_density_rad_depend(rg_param, ry_param, N_param, v_param, w_param, 4, time_point_container=[0.1, 0.5, 0.9], rect_config=False, rect_dist=rect_dist, show_plt=False)

    ani.generate_heatmaps(rg_param, ry_param, w_param, v_param, N_param, approach=3, time_point_container=[0.1, 0.5, 0.9], rect_config=True, rect_dist=rect_dist, show_plot=False)
    ani.generate_heatmaps(rg_param, ry_param, w_param, v_param, N_param, approach=3, time_point_container=[0.1, 0.5, 0.9], rect_config=False, rect_dist=rect_dist, show_plot=False)

    launch.collect_mass_analysis(rg_param, ry_param, N_param, v_param, w_param, 0.5, 100, rect_config=True, rect_dist=rect_dist, show_plt=False, save_png=True)
    launch.collect_mass_analysis(rg_param, ry_param, N_param, v_param, w_param, 0.5, 100, rect_config=False, rect_dist=rect_dist, show_plt=False, save_png=True)

    end = clk.time()

    f'Full analysis duration: {end - start:.3f}'


if __name__ == "__main__":

    # p1 = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\April-2025\\rect_polar_comparisons_4_8_25\\ang-dep\\polar\\2025-04-06-19-03-24_polar\\phi_v_theta_V=-10_W=1000_64x64_approach=3_.csv"
    # p2 = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\April-2025\\rect_polar_comparisons_4_8_25\\ang-dep\\rect\\2025-04-06-18-38-48_rect\\phi_v_theta_V=-10_W=1000_64x64_approach=3_.csv"
    #
    # phi_v_theta_list = [p1, p2]
    #
    # plt.plot_phi_v_theta_mult(phi_v_theta_list, -10, 1000, [0, 16, 32, 48], 3, 0.5, fp.general_output, True, time_point_container=[0.1, 0.5, 0.9])
    # plt.plot_dense_v_rad_mul()

    today_str = datetime.now().strftime("%Y-%m-%d")

    log_dir = os.path.join(os.getcwd(), fp.rect_logs)

    output_filename = os.path.join(log_dir, f"output_{today_str}.txt")

    # Optional: Print to both terminal and file
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