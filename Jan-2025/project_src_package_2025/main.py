from launch_functions import launch
from data_visualization import animation_functions as ani, plot_functions as plt
from auxiliary_tools import unit_conversion_functions as uni
# from system_configuration import file_paths as fp
# from computational_tools import analysis_tools as ant

import time as clk

if __name__ == "__main__":

    # Task no. 1 : Collecting results for phi-v-theta amplitude radial dependence when 10% of the mass has exited from the domain.
    rg_param = 48
    ry_param = 48
    N_param = [0, 12, 24, 36]
    v_param = -10
    w_param = 10 ** 4

    start = clk.time()
    T = launch.output_time_until_mass_depletion(rg_param, ry_param, N_param, v_param, w_param, mass_threshold=0.90005)
    print("<**********> Time until approx. 10% of mass exited: (sim time)", T)
    end = clk.time()
    print("Real time until approx. 10% of mass exited: ", uni.convert_seconds(end - start))

    start = clk.time()
    launch.collect_phi_v_theta(rg_param, ry_param, N_param, v_param, w_param, 4, verbose=True,
                               mass_retention_threshold=0.90005, time_point_container=[1])
    end = clk.time()
    print("Real time until phi-v-theta amplitude results have been successfully collected: ", uni.convert_seconds(end - start))

    # Task no. 2, Produce heatmap for 128x128, v=-10, w=10**4, N=4, using an adjusted approach 2.
    '''
        Approach 2 collection points:
        
          pane0 ->  0.985 < mass_retained < 0.99
          pane1 ->  0.45 < mass_retained < 0.46
          pane2 ->  0.225 < mass_retained < 0.26
          pane3 ->  0.015 < mass_retained < 0.02
    '''

    rg_param = 128
    ry_param = 128
    N_param = [0, 32, 64, 96]
    v_param = -10
    w_param = 10 ** 4

    start = clk.time()
    ani.generate_heatmaps(rg_param, ry_param, w_param, v_param, N_param, approach=2, save_png=True, show_plot=False, compute_mfpt=True, verbose=True)
    end = clk.time()
    print("Real time until heatmap generation for 128x128 domain using slightly modified approach 2: ", uni.convert_seconds(end - start))




