
import func_calc_mfpt as calc
import func_calc_mfpt_optimzied as calc_op
import func_tab as tb
import func_plots as plt
import printTool

import multiprocessing as mp
import filepaths as fp
from datetime import datetime
from functools import partial
import time as clk
import pandas as pd
import numpy as np
import math
import os

op_test_directory = 'N:\\QueensCollege2024\\Research\\Theoretical-Biophysics\\Fall-Semester\\Version-F1.0\\Python\\MFPT-exclusive\\Optimization_Tests'


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

    phi_v_theta_container = np.zeros((4, N), dtype=np.float64)

    mfpt, duration = calc_op.solve_mass_retained_2T_theta_phi(M, N, radius, d_c, w_param, w_param, v_param,
                            N_param, diffusive, advective, phi_v_theta_container, 0.5, True)

    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    data_filepath = tb.create_directory(fp.mfpt_data_fp, current_time)
    output_file = os.path.join(data_filepath, f"phi_v_theta_comp_V={v_param}_W={w_param}_{rg_param}x{ry_param}_.csv")

    df = pd.DataFrame(phi_v_theta_container)

    df.to_csv(output_file, header=False, index=False)
    print(f"Phi versus Theta information has been saved to: {data_filepath}")

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


def validate_contents():
    file_1 = 'N:\\QueensCollege2024\\Research\\Theoretical-Biophysics\\Fall-Semester\\Version-F1.0\\Python\\MFPT-exclusive\\Optimization_Tests\\2024-11-03_20-13-28\\base.csv'
    file_2 = 'N:\\QueensCollege2024\\Research\\Theoretical-Biophysics\\Fall-Semester\\Version-F1.0\\Python\\MFPT-exclusive\\Optimization_Tests\\2024-11-03_20-13-28\\optimized.csv'

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


if __name__ == "__main__":

    multiple_domain_config = False

    rings = 48
    rays = 48
    w = 10 ** 4

    '''
        Parameters for the Phi versus Theta computations:
    
        MxN=48x48
        N=4
        W=10^4
        V=[-240, -560, -880]
        
        MxN=48x48
        N=8
        W=10^4
        V=[-480, -800, -1020]
    '''

    microtubule_configs = [
        [0, 6, 12, 18, 24, 30, 36, 42]
    ]

    v = [-480, -800, -1020]

    # print(simulation_time_conversion(rings, rays, 438598))

    # parallel_process_velocity(microtubule_configs, rings, rays, w, v, cores=fp.core_amount)

    destination = 'N:\\QueensCollege2024\\Research\\Theoretical-Biophysics\\Fall-Semester\\Version-F1.0\\Python\\MFPT-exclusive\\data-output\\Phi-versus-Theta-N=8_48x48\\approach_#1\\0.5'
    origin = 'N:\\QueensCollege2024\\Research\\Theoretical-Biophysics\\Fall-Semester\\Version-F1.0\\Python\\MFPT-exclusive\\data-output\\Phi-versus-Theta-N=8_48x48\\approach_#1\\0.5\\phi_v_theta_comp_V=-1020_W=10000_48x48_.csv'

    plt.phi_versus_theta_plot(origin, -1020, "10^4", 8, 0.5, "#1", save_png=True, filePath=destination)

    # still need to compute the following points
    # -660, -720, -800, -880, -960, -1020, -1080
    # parallel_process_velocity(microtubule_configs, rings, rays, w, [-540, -560, -580, -600], fp.core_amount)

    # parallel_process(rings, rays, -10, microtubule_configs, -2, 4, 6)

    if multiple_domain_config:

        domain_config_list = [52]

        N = 4

        for i in range(len(domain_config_list)):

            rings = domain_config_list[i]
            rays = domain_config_list[i]
            # w = 10 ** 4

            microtubule_configs = [
                microtubule_configure_tool(rays, domain_config_list[i] // N)
            ]

            # still need to compute the following points
            # -660, -720, -800, -880, -960, -1020, -1080
            # parallel_process_velocity(microtubule_configs, rings, rays, w, [-540, -560, -580, -600], fp.core_amount)

            parallel_process(rings, rays, -10, microtubule_configs, -2, 4, 6)


'''
Parameters for the J versus k computations:

For the N-dependence examinations (verifying the behavior of the mass loss (J) across the last ring of the domain across time (k * d_time))

MxN=64x64
W=10^4  
V=-10
For varying N=[2, 4, 8, 16, 32, 64]
'''




'''
    
    Number of time-steps it took in order to reach the global max at different velocity values:
    
    V=-240, -560, -880
    
    -240: 371356
    
    -560: 379484
    
    -880: 382576
'''