import func_calc_mfpt_optimzied as calc_op
import func_tab as tb
import func_plots as plt
import graphics as gc

import multiprocessing as mp
import filepaths as fp
from datetime import datetime
from functools import partial
import time as clk
import pandas as pd
import numpy as np
import math
import os


def solve(N_param, rg_param, ry_param, v_param, w_param):
    M = rg_param
    N = ry_param
    d_c = 1
    radius = 1
    v = v_param

    diffusive, advective = calc_op.initialize_layers(M, N)

    # original code
    mfpt, duration = calc_op.solve_mass_retained_2T(M, N, radius, d_c, w_param, w_param, v, N_param, diffusive, advective)
    # mfpt = calc_op.solve_mass_retained_2T(M, N, radius, d_c, w_param, w_param, v, N_param, diffusive, advective)

    print(f'Duration (simulation time): {duration}    Microtubule Configuration: {N_param}')
    print()
    return {f'W: {w_param}', f'MFPT: {mfpt}'}


# Solving for velocity
def solve_velocity(N_param, rg_param, ry_param, w_param, v_param):
    M = rg_param
    N = ry_param
    d_c = 1
    radius = 1

    diffusive, advective = calc_op.initialize_layers(rg_param, ry_param)

    mfpt, duration = calc_op.solve_mass_retained_2T(rg_param, ry_param, radius, d_c, w_param, w_param, v_param, N_param, diffusive, advective)

    print(f'MFPT: {mfpt}    Velocity={v_param}      MxN : {M}x{N}      W={w_param}     Sim-time={duration}')

    # phi_v_theta_container = np.zeros((4, N), dtype=np.float64)
    #
    # mfpt, duration = calc_op.solve_mass_retained_2T_theta_phi(M, N, radius, d_c, w_param, w_param, v_param,
    #                         N_param, diffusive, advective, phi_v_theta_container, 0.5, True)
    #
    # current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    # data_filepath = tb.create_directory(fp.mfpt_data_fp, current_time)
    # output_file = os.path.join(data_filepath, f"phi_v_theta_comp_V={v_param}_W={w_param}_{rg_param}x{ry_param}_.csv")
    #
    # df = pd.DataFrame(phi_v_theta_container)
    #
    # df.to_csv(output_file, header=False, index=False)
    # print(f"Phi versus Theta information has been saved to: {data_filepath}")

    print(f'Microtubule Configuration: {N_param}')
    print()
    return{f'V: {v_param}', f'MFPT: {mfpt}'}


def parallel_process_velocity(N_list, rg_param, ry_param, w_param, v_list, cores):

    print("Velocity list: ", v_list)

    if len(v_list) < cores:
        process_count = len(v_list)
    else:
        process_count = cores

    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    data_filepath = tb.create_directory(fp.mfpt_data_fp, current_time)

    for n in range(len(N_list)):
        with mp.Pool(processes=process_count) as pool:
            mfpt_results = pool.map(partial(solve_velocity, N_list[n], rg_param, ry_param, w_param), v_list)
        print(mfpt_results)

    #     tb.data_extraction_pandas(mfpt_results, data_filepath, f'MFPT_Results_N={len(N_list[n])}_W={w_param}')
    #     clk.sleep(1)
    # plt.plot_all_csv_in_directory(data_filepath, N_list, data_filepath, f'MFPT_versus_v_W={w_param}_', True)


def parallel_process(rg_param, ry_param, v_param, N_list, w_low_bound, w_high_bound, process_count):
    w_list = []
    lower_bound = w_low_bound
    upper_bound = w_high_bound
    for x in range(lower_bound, upper_bound+1):
        w_list.append(10 ** x)

    print(w_list)

    if process_count > 6:
        process_count = 6
    else:
        process_count = len(w_list)

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    data_filepath = tb.create_directory(fp.mfpt_data_fp, current_time)

    for n in range(len(N_list)):
        with mp.Pool(processes=process_count) as pool:
            mfpt_results = pool.map(partial(solve, N_list[n], rg_param, ry_param, v_param), w_list)
        print(mfpt_results)

        tb.data_extraction_pandas(mfpt_results, data_filepath, f'MFPT_Results_N={len(N_list[n])}_v={v_param}_')
        clk.sleep(1)
    plt.plot_all_csv_in_directory(data_filepath, N_list, data_filepath, f'MFPT_versus_W_v={v_param}_', True, show_plt=False)


def validate_contents(file_1, file_2):

    df1 = pd.read_csv(file_1)
    df2 = pd.read_csv(file_2)

    print(df1.equals(df2))


def microtubule_configure_tool(dim, den):
    return [j for j in range(0, dim, den)]


def simulation_time_conversion(M, N, time_steps):
    d_radius = 1 / M
    d_theta = ((2 * math.pi) / N)
    d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / 2
    return time_steps * d_time


def clustered_configuration(rg_param, ry_param, v, N_config):
    parallel_process(rg_param, ry_param, v, N_config, -2, 4, fp.core_amount)


def multiple_domain_config(domain_config_list, microtubule_count, v, w_low_bound, w_high_bound):

    N = microtubule_count

    for i in range(len(domain_config_list)):
        rg_param = domain_config_list[i]
        ry_param = domain_config_list[i]

        N_configs = [
            microtubule_configure_tool(rays, domain_config_list[i] // N)
        ]

        parallel_process(rg_param, ry_param, v, N_configs, w_low_bound, w_high_bound, fp.core_amount)


def heat_map_generation(rg_param, ry_param, approach, w_param, v_param, N_param, filepath=None, output_peak=False, time_point_container=None, save_png=False):

    panes = 0
    if approach == "1":
        panes = 2
    elif approach == "2":
        panes = 4
    domain_snapshot_container = np.zeros((panes, rg_param, ry_param), dtype=np.float64)
    domain_center_snapshot_container = np.zeros([panes], dtype=np.float64)
    diffusive, advective = calc_op.initialize_layers(rg_param, ry_param)

    mfpt, duration = calc_op.solve_mass_retained_2T_domain_snapshot(rg_param, ry_param, 1, 1, w_param, w_param, v_param,
                                                                    N_param, diffusive, advective,
                                                                    domain_snapshot_container, domain_center_snapshot_container,

                                                                    approach, time_point_container,False)
    print(domain_center_snapshot_container)

    print(f"MFPT: {mfpt}    Duration in sim-time: {duration}")
    for i in range(panes):
        gc.generate_polar_heatmap(domain_snapshot_container[i], domain_center_snapshot_container[i],
                                  True, w_param, v_param, len(N_param), filepath, save_png=save_png, show_plot=False)


if __name__ == "__main__":

    rings = 64
    rays = 64
    microtubule_configs = [
        [0, 4, 8, 12],
        [0, 2, 4, 6, 8, 10, 12, 14],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
         16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
    ]

    temp_save_path = 'N:\\QueensCollege2024\\Research\\Theoretical-Biophysics\\Fall-Semester\\Version-F1.0\\Python\\MFPT-exclusive\\data-output\\Jan-Content\\Microtubule-Clustering-Heatmaps'

    for i in range(len(microtubule_configs)):
        heat_map_generation(rings, rays, "1", 10**4, -10, microtubule_configs[i], filepath=temp_save_path, save_png=True)
        clk.sleep(2)

    rings = 48
    rays = 48
    w = 10 ** 4

    microtubule_configs = [
        [0, 6, 12, 18, 24, 30, 36, 42]
    ]

    # velocity values to compute
    # still need to compute the following points
    # -660, -720, -800, -880, -960, -1020, -1080
    # parallel_process_velocity(microtubule_configs, rings, rays, w, [-540, -560, -580, -600], fp.core_amount)

    v_list = [-560, -580, -600, -660, -720, -800, -880, -960, -1020, -1080]

    # -560, -580, -600, -660, -720, -800, -880, -960, -1020, -1080

    # parallel_process_velocity(microtubule_configs, rings, rays, w, v_list, fp.core_amount)


'''
    generating a heatmap of a domain at certain timestamps:
    
    using the container from the diffusive layer,
    including the center point.
    
'''

