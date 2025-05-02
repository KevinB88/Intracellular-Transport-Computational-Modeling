import pandas as pd

from . import mfpt_comp, sup, datetime, tb, fp, mp, config, partial, ant, np, os, plt
import time as clk
import math


'''
    ind_param:  independent parameter: the value that remains static across all MFPT solutions
    dep_param:  dependent parameter(s) : value that is being tested for MFPT dependence (contained within a set)
'''


def solve_mfpt_multi_process(N_param, rg_param, ry_param, dep_type, ind_param, dep_param):
    M = rg_param
    N = ry_param

    if dep_type == "W":
        w_param = dep_param
        v_param = ind_param
    elif dep_type == "V":
        v_param = dep_param
        w_param = ind_param
    else:
        raise f"{dep_type} not yet defined, must use either V or W"

    mfpt, duration = solve_mfpt(rg_param, ry_param, N_param, v_param, w_param, return_duration=True)

    print(f"MxN={M}x{N}    Duration (sim time) : {duration}    Microtubule configuration: {N_param}"
          f"    W: {w_param}    V: {v_param}")

    if dep_type == "W":
        return {f'W: {w_param}', f'MFPT: {mfpt}'}
    elif dep_type == "V":
        return {f'V: {w_param}', f'MFPT: {mfpt}'}


def parallel_process_mfpt(N_list, rg_param, ry_param, dep_type, ind_type, dep_param, ind_list, cores=None):

    dep_type = dep_type.upper()
    if dep_type != "W" and dep_type != "V":
        raise(f"{dep_type} is an undefined dependent parameter. The current available "
              f"dependent parameters are Switch Rate (W), and Velocity (V)")

    print(f"{ind_type} list: {ind_list}")

    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    data_filepath = tb.create_directory(fp.mfpt_results_output, current_time)

    if cores is not None and cores > 0:
        core_count = min(cores, config.core_amount)
    else:
        core_count = config.core_amount

    for n in range(len(N_list)):
        with mp.Pool(processes=core_count) as pool:
            mfpt_results = pool.map(partial(solve_mfpt_multi_process, N_list[n],
                                            rg_param, ry_param, dep_type, dep_param), ind_list)
        print(mfpt_results)
        tb.produce_csv_from_xy(mfpt_results, dep_type, "MFPT", data_filepath,
                               f'MFPT_Results_N={len(N_list[n])}_{ind_type}={dep_param}_')


def solve_mfpt(rg_param, ry_param, N_param, v_param, w_param, r=1.0, d=1.0, mass_checkpoint=10**6,
               mass_threshold=0.01, return_duration=False):
    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)
    mfpt, duration = mfpt_comp.comp_mfpt_by_mass_loss(rg_param, ry_param, w_param, w_param, v_param,
                                                      N_param, diff_layer, adv_layer, mass_checkpoint, r, d, mass_threshold)

    if return_duration:
        return mfpt, duration
    else:
        return mfpt


def output_time_until_mass_depletion(rg_param, ry_param, N_param, v_param, w_param, mass_threshold=0.01):
    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)
    duration = ant.comp_until_mass_depletion(rg_param, ry_param, w_param, w_param,
                                             v_param, N_param, diff_layer, adv_layer, mass_retention_threshold=mass_threshold)
    return duration


# produces a csv containing Phi versus Theta data relative to the specified approach
def collect_phi_ang_dep(rg_param, ry_param, N_param, v_param, w_param, approach, m_segment=0.5,
                        r=1, d=1, mass_retention_threshold=0.01, time_point_container=None, verbose=False, save_png=True, show_plt=False,
                        rect_config=False, rect_dist=2):
    if approach == 1:
        rows = 2
    elif approach == 2:
        rows = 4
    elif approach == 3:
        rows = len(time_point_container)
    elif approach == 4:
        rows = int(rg_param / 2)
    # approach 4 is temporary, and has been implemented to execute Task 2 from 2/11/25 6:02 PM
    else:
        raise ValueError(f"{approach} undefined, please use either approach 1, 2, or 3 (int).")

    phi_v_theta_container = np.zeros((rows, ry_param), dtype=np.float64)

    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)

    ant.comp_diffusive_angle_snapshots(rg_param, ry_param, w_param, w_param, v_param, N_param,
                                       diff_layer, adv_layer, phi_v_theta_container, approach, m_segment=m_segment, r=r, d=d,
                                       mass_retention_threshold=mass_retention_threshold, time_point_container=time_point_container, rect_config=rect_config, rect_dist=rect_dist)

    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    if rect_config:
        current_time += "-rect-config"
    else:
        current_time += "-original-config"

    data_filepath = os.path.abspath(tb.create_directory(fp.phi_v_theta_output, current_time))
    print(data_filepath)
    filename = f"phi_v_theta_V={v_param}_W={w_param}_{rg_param}x{ry_param}_approach={approach}_.csv"
    output_location = os.path.join(data_filepath, filename)
    # print(output_location)
    df = pd.DataFrame(phi_v_theta_container)
    df.to_csv(output_location, header=False, index=False)

    if verbose:
        print({filename})

    clk.sleep(2)

    plt.plot_phi_v_theta(output_location, v_param, w_param, N_param, approach, m_segment, data_filepath, save_png=save_png, show_plt=show_plt, time_point_container=time_point_container)


def collect_density_rad_depend(rg_param, ry_param, N_param, v_param, w_param, fixed_angle, time_point_container, r=1.0, d=1.0,
                               mass_retention_threshold=0.01, mass_checkpoint=10**6, save_png=True, show_plt=False, rect_config=False, rect_dist=2):

    phi_rad_container = np.zeros((3, rg_param+1), dtype=np.float64)
    rho_rad_container = np.zeros((3, rg_param), dtype=np.float64)
    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)

    ant.comp_diffusive_rad_snapshots(rg_param, ry_param, w_param, w_param, v_param, N_param, diff_layer, adv_layer,
                                     fixed_angle, phi_rad_container, rho_rad_container, time_point_container, r=r, d=d,
                                     mass_retention_threshold=mass_retention_threshold, mass_checkpoint=mass_checkpoint,
                                     rect_config=rect_config, rect_dist=rect_dist)

    # collecting raw results for diffusive-v-rad
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    if rect_config:
        current_time += "-rect-config"
    else:
        current_time += "-original-config"
    data_filepath = os.path.abspath(tb.create_directory(fp.radial_dependence_phi, current_time))
    print(data_filepath)
    filename = f"phi_v_rad_V={v_param}_W={w_param}_Domain={rg_param}x{ry_param}.csv"
    output_location = os.path.join(data_filepath, filename)
    df = pd.DataFrame(phi_rad_container)
    df.to_csv(output_location, header=False, index=False)

    plt.plot_dense_v_rad("Phi", output_location, v_param, w_param, len(N_param), rg_param, ry_param, fixed_angle,
                         time_point_container, data_filepath, save_png=save_png, show_plt=show_plt)

    # collecting raw results for rho-v-rad
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    if rect_config:
        current_time += "-rect-config"
    else:
        current_time += "-original-config"
    data_filepath = os.path.abspath(tb.create_directory(fp.radial_dependence_rho, current_time))
    print(data_filepath)
    filename = f"rho_v_rad_V={v_param}_W={w_param}_Domain={rg_param}x{ry_param}.csv"
    output_location = os.path.join(data_filepath, filename)
    df = pd.DataFrame(rho_rad_container)
    df.to_csv(output_location, header=False, index=False)

    plt.plot_dense_v_rad("Rho", output_location, v_param, w_param, len(N_param), rg_param, ry_param, fixed_angle,
                         time_point_container, data_filepath, save_png=save_png, show_plt=show_plt)


def collect_mass_analysis(rg_param, ry_param, N_param, v_param, w_param, T_param, collection_width, r=1.0, d=1.0,
                          mass_checkpoint=10**6, save_png=False, show_plt=True, rect_config=False, rect_dist=2):

    d_radius = r / rg_param
    d_theta = ((2 * math.pi) / ry_param)
    d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / (2 * d)
    K = math.floor(T_param / d_time)
    relative_k = math.floor(K / collection_width)

    print("Number of time-steps: ", K)
    print("Number of data-points to collect: ", relative_k)

    diffusive_mass_container = np.zeros([relative_k], dtype=np.float64)
    advective_mass_container = np.zeros([relative_k], dtype=np.float64)
    advective_over_total_container = np.zeros([relative_k], dtype=np.float64)

    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)

    ant.comp_mass_analysis_respect_to_time(rg_param, ry_param, w_param, w_param, v_param, T_param,
                                           N_param, diff_layer, adv_layer, diffusive_mass_container,
                                           advective_mass_container, advective_over_total_container, collection_width,
                                           mass_checkpoint, r, d, rect_config=rect_config, rect_dist=rect_dist)

    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    if rect_config:
        current_time += "-rect-config"
    else:
        current_time += "-original-config"
    data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_diffusive, current_time))
    print(data_filepath)
    filename = f"diffusive_mass_analysis_V={v_param}_W={w_param}_{rg_param}x{ry_param}_.csv"
    output_location = os.path.join(data_filepath, filename)
    df = pd.DataFrame(diffusive_mass_container)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_mass_analysis(output_location, v_param, w_param, N_param, T_param, rg_param, ry_param, "diffusive_mass", data_filepath, save_png, show_plt)

    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    if rect_config:
        current_time += "-rect-config"
    else:
        current_time += "-original-config"
    data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_advective, current_time))
    print(data_filepath)
    filename = f"advective_mass_analysis_V={v_param}_W={w_param}_{rg_param}x{ry_param}_.csv"
    output_location = os.path.join(data_filepath, filename)
    df = pd.DataFrame(advective_mass_container)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_mass_analysis(output_location, v_param, w_param, N_param, T_param, rg_param, ry_param, "advective_mass",
                           data_filepath, save_png, show_plt)

    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    # if rect_config:
    #     current_time += "-rect-config"
    # else:
    #     current_time += "-original-config"
    data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_advective_over_total, current_time))
    print(data_filepath)

    filename = f"advective_over_total_mass_analysis_V={v_param}_W={w_param}_{rg_param}x{ry_param}_.csv"
    output_location = os.path.join(data_filepath, filename)
    df = pd.DataFrame(advective_over_total_container)
    df.to_csv(output_location, header=False, index=False)

    plt.plot_mass_analysis(output_location, v_param, w_param, N_param, T_param, rg_param, ry_param, "adv_over_tot_mass",
                           data_filepath, save_png, show_plt)

    '''
        The following line above resulted in the following error: 
        
        FileNotFoundError: [Errno 2] No such file or directory: 'N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\April-2025\\project_src_package_2025\\data_output\\mass_analysis_results\\advective_over_total\\2025-04-10-07-52-46-rect-config\\adv_over_tot_mass_versus_T_W=1000_V=-10_N=4_16x16_2025-04-10_07-52-46.png'
    '''





