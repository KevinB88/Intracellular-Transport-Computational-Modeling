from launch_functions import launch
from data_visualization import animation_functions as ani, plot_functions as plt
from auxiliary_tools import unit_conversion_functions as uni
from system_configuration import file_paths as fp
import time as clk

# The following computation below is from a heatmap generation computation
if __name__ == "__main__":

    rg_param = 48
    ry_param = 48
    w_param = 10**4
    N_param = [0, 12, 24, 36]
    approach = 2
    v_list = [-50, -100, -950, -1000]

    start = clk.time()

    for v in range(len(v_list)):
        ani.compute_heatmap(rg_param, ry_param, w_param, v_list[v], N_param, 2, save_png=True, show_plot=False, verbose=True)
        clk.sleep(5)
        launch.collect_phi_v_theta(rg_param, ry_param, N_param, v_list[v], w_param, 2)
        clk.sleep(5)

    end = clk.time()

    elapsed = uni.convert_seconds(end - start)
    print(f'Time elapsed: {elapsed}')
