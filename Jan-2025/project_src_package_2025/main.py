from launch_functions import launch
from data_visualization import animation_functions as ani, plot_functions as plt
from auxiliary_tools import unit_conversion_functions as uni
from system_configuration import file_paths as fp
# from computational_tools import analysis_tools as ant
import time as clk

if __name__ == "__main__":

    # rho_data = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\Jan-2025\\project_src_package_2025\\data_output\\density-results\\radial-dependence\\rho\\2025-03-01-18-05-37\\rho_v_rad_V=-10_W=0.0001_Domain=48x48.csv"
    #
    # plt.plot_dense_v_rad("rho", rho_data, -10, 10**-4, 4, 48, 48, 12, [0.1, 0.5, 0.9], fp.radial_dependence_rho)

    ani.generate_heatmaps(16, 16, 10, -50, [0, 4, 8, 12], log_scale=False, show_plot=True, save_png=False)

    # T_fixed = [0.1, 0.5, 0.9]
    #
    # rg_param = 48
    # ry_param = 48
    # N_param = [0, 12, 24, 36]
    # V_param = -10
    #
    # launch.collect_density_rad_depend(rg_param, ry_param, N_param, V_param, 10 ** -4, 12, T_fixed)
    # launch.collect_density_rad_depend(rg_param, ry_param, N_param, V_param, 0, 12, T_fixed)
    # launch.collect_density_rad_depend(rg_param, ry_param, N_param, V_param, 10 ** 0, 12, T_fixed)
    # launch.collect_density_rad_depend(rg_param, ry_param, N_param, V_param, 10 ** 4, 12, T_fixed)
    #
    # clk.sleep(10)
    #
    # # Task 2.
    # rg_param = 128
    # ry_param = 128
    # N_param = [0, 32, 64, 96]
    # V_param = -10
    # W_param = 10 ** 4
    # ani.generate_heatmaps(rg_param, ry_param, W_param, V_param, N_param, log_scale=False, output_csv=True)

    # Task 1.

    # # W=10**-4, until 99% depletion tim+e
    # T1 = 0.8646698582027904
    # T1_points = [T1 * 0.1, T1 * 0.5, T1 * 1.15]
    #
    # # W=10**0, until 99% depletion time
    # T2 = 0.8763514454129948
    # T2_points = [T2 * 0.1, T2 * 0.5, T2 * 1.15]
    #
    # # W=10**4, until 99% depletion time
    # T3 = 1.1471980528857275
    # T3_points = [T3 * 0.1, T3 * 0.5, T3 * 1.15]
    #
