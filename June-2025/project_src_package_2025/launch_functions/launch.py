import pandas as pd

from . import mfpt_comp, sup, datetime, tb, fp, mp, config, partial, ant, np, os, plt, ani
import time as clk
import math

'''
    ind_param:  independent parameter: the value that remains static across all MFPT solutions
    dep_param:  dependent parameter(s) : value that is being tested for MFPT dependence (contained within a set)
'''


# Will require further inspection
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


# Will require further inspection
def parallel_process_mfpt(N_list, rg_param, ry_param, dep_type, ind_type, dep_param, ind_list, cores=None):
    dep_type = dep_type.upper()
    if dep_type != "W" and dep_type != "V":
        raise (f"{dep_type} is an undefined dependent parameter. The current available "
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
            mfpt_results = pool.map(partial(solve_mfpt_multi_process, N_list[ n ],
                                            rg_param, ry_param, dep_type, dep_param), ind_list)
        print(mfpt_results)
        tb.produce_csv_from_xy(mfpt_results, dep_type, "MFPT", data_filepath,
                               f'MFPT_Results_N={len(N_list[ n ])}_{ind_type}={dep_param}_')


# Will require further inspection
def solve_mfpt(rg_param, ry_param, N_param, v_param, w_param, r=1.0, d=1.0, mass_checkpoint=10 ** 6,
               mass_threshold=0.01, return_duration=False, mixed_config=False, mx_cn_rrange=1):
    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)
    mfpt, duration = mfpt_comp.comp_mfpt_by_mass_loss_rect(rg_param, ry_param, w_param, w_param, v_param,
                                                           N_param, diff_layer, adv_layer, mass_checkpoint, r, d,
                                                           mass_threshold, mixed_config, mx_cn_rrange)

    if return_duration:
        return mfpt, duration
    else:
        return mfpt


def solve_mfpt_(rg_param, ry_param, N_param, v_param, w_param, T_param, r=1.0, d=1.0, mass_checkpoint=10**6, d_tube=-1, return_duration=False):
    j_max_lim = sup.j_max_bef_overlap(ry_param, N_param)
    max_d_tube = sup.solve_d_rect(r, ry_param, rg_param, j_max_lim, 0)

    while d_tube < 0 or d_tube > max_d_tube:
        d_tube = float(
            input(f"Select d_tube within the range: [0, {max_d_tube}] to avoid DL extraction region overlap: "))
    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)
    MFPT, duration = mfpt_comp.comp_mfpt_by_time_rect(rg_param, ry_param, w_param, w_param,
                                                      v_param*-1, N_param, diff_layer, adv_layer, T_param,
                                                      mass_checkpoint=mass_checkpoint, r=r, d=d, d_tube=d_tube)
    if return_duration:
        return MFPT, duration
    else:
        return MFPT


# MFPT as a function of W saturation analysis

# under construction
def mfpt_of_W_sat_analysis(domain_list, N_param_list, v_param, w_param_list,  T_param, r=1.0, d=1.0, mass_checkpoint=10**6, d_tube=-1):

    '''
    Produces a visualization for a saturation of analysis as MFPT as a function of W (switching rate a=b) for varying domain sizes)
    In addition, this current implementation only functions for a single microtubule configuration.

    We are interested in saturation of MFPT across varying domain sizes under fixed number of microtubules, d_tube, velocity, and time.

    Args:
        domain_list: (2-Dimensional list: a list of domain dimensions, i.e. MxN, Rings x Rays)
        N_param_list: (2-Dimensional list: a list of microtubule configurations corresponding to the dimensions in the above list)
        v_param:
        w_param_list: (1-dimensional list: a list of desired w_values in sorted order)
        T_param:
        r:
        d:
        mass_checkpoint:
        d_tube:

    Returns:
    '''

    # Throw an error if the sizes of the domain_list, N_param_list, and the w_param_list do not match

    # In the case of non overlap, the current selection of d_tube (assuming it is non-zero) needs to be verified if it functions properly across all domain sizes and microtubule configurations.

    output_file_list = []
    for i in range(len(domain_list)):
        MFPT_list = []
        for j in range(len(w_param_list)):
            MFPT = solve_mfpt_(domain_list[i][0], domain_list[i][1], N_param_list[i], v_param, w_param_list[j], T_param,
                               r=r, d=d, mass_checkpoint=mass_checkpoint, d_tube=d_tube)
            MFPT_list.append(MFPT)

        # store the data and save the data to csv
        # store a pointer to the csv data file
        # append this pointer to a list of csv data files
    # Configure a plot to display the saturation of results by overlapping the results contained in the list of csv data files.

'''
    Configure a launch function to produce an analysis on MFPT as a function of W for varying amounts of N 
'''


def output_time_until_mass_depletion(rg_param, ry_param, N_param, v_param, w_param, mass_threshold=0.01, mixed_config=False, d_tube=-1):

    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)

    if mixed_config:
        # This variable denotes the maximum j_max value with respect to microtubule configuration on the first ring
        j_max_lim = sup.j_max_bef_overlap(ry_param, N_param)
        max_d_tube = sup.solve_d_rect(1, ry_param, rg_param, j_max_lim, 0)

        while d_tube <= 0 or d_tube > max_d_tube:
            d_tube = float(
                input(f"Select d_tube within the range: (0, {max_d_tube}] to avoid DL extraction region overlap: "))

    duration = ant.comp_until_mass_depletion(rg_param, ry_param, w_param, w_param,
                                             v_param*-1, N_param, diff_layer, adv_layer,
                                             mass_retention_threshold=mass_threshold, mixed_config=mixed_config, d_tube=d_tube)
    return duration


# produces a csv containing Phi versus Theta data relative to the specified approach
def collect_phi_ang_dep(rg_param, ry_param, N_param, v_param, w_param, approach=3, m_segment=0.5,
                        r=1, d=1, mass_retention_threshold=0.01, time_point_container=None, verbose=False,
                        save_png=True, show_plt=False,
                        mixed_config=False, d_tube=-1):
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

    if mixed_config:
        # This variable denotes the maximum j_max value with respect to microtubule configuration on the first ring
        j_max_lim = sup.j_max_bef_overlap(ry_param, N_param)
        max_d_tube = sup.solve_d_rect(r, ry_param, rg_param, j_max_lim, 0)

        while d_tube <= 0 or d_tube > max_d_tube:
            d_tube = float(input(f"Select d_tube within the range: (0, {max_d_tube}] to avoid DL extraction region overlap: "))

    ant.comp_diffusive_angle_snapshots(rg_param, ry_param, w_param, w_param, v_param*-1, N_param,
                                       diff_layer, adv_layer, phi_v_theta_container, approach, m_segment=m_segment, r=r,
                                       d=d,
                                       mass_retention_threshold=mass_retention_threshold,
                                       time_point_container=time_point_container, mixed_config=mixed_config, d_tube=d_tube)

    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    if mixed_config:
        current_time += "-mixed-config"
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

    plt.plot_phi_v_theta(output_location, v_param, w_param, N_param, approach, m_segment, data_filepath,
                         save_png=save_png, show_plt=show_plt, time_point_container=time_point_container)


def collect_density_rad_depend(rg_param, ry_param, N_param, v_param, w_param, fixed_angle, time_point_container, r=1.0,
                               d=1.0,
                               mass_retention_threshold=0.01, mass_checkpoint=10 ** 6, save_png=True, show_plt=False,
                               mixed_config=False, d_tube=-1):
    phi_rad_container = np.zeros((3, rg_param + 1), dtype=np.float64)
    rho_rad_container = np.zeros((3, rg_param), dtype=np.float64)
    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)

    if mixed_config:
        # This variable denotes the maximum j_max value with respect to microtubule configuration on the first ring
        j_max_lim = sup.j_max_bef_overlap(ry_param, N_param)
        max_d_tube = sup.solve_d_rect(r, ry_param, rg_param, j_max_lim, 0)

        while d_tube <= 0 or d_tube > max_d_tube:
            d_tube = float(
                input(f"Select d_tube within the range: (0, {max_d_tube}] to avoid DL extraction region overlap: "))

    ant.comp_diffusive_rad_snapshots(rg_param, ry_param, w_param, w_param, v_param*-1, N_param, diff_layer, adv_layer,
                                     fixed_angle, phi_rad_container, rho_rad_container, time_point_container, r=r, d=d,
                                     mass_retention_threshold=mass_retention_threshold, mass_checkpoint=mass_checkpoint,
                                     mixed_config=mixed_config)

    # collecting raw results for diffusive-v-rad
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    if mixed_config:
        current_time += "-mixed-config"
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
    if mixed_config:
        current_time += "-mixed-config"
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
                          mass_checkpoint=10 ** 6, save_png=False, show_plt=True, mixed_config=False, d_tube=-1, collect_MFPT=False, collect_plots=True):
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
    advective_over_initial_container = np.zeros([relative_k], dtype=np.float64)
    total_mass_container = np.zeros([relative_k], dtype=np.float64)

    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)

    # This conditional block is temporary while overlap of extraction regions are avoided
    if mixed_config:
        # This variable denotes the maximum j_max value with respect to microtubule configuration on the first ring
        j_max_lim = sup.j_max_bef_overlap(ry_param, N_param)
        max_d_tube = sup.solve_d_rect(r, ry_param, rg_param, j_max_lim, 0)

        while d_tube < 0 or d_tube > max_d_tube:
            d_tube = float(input(f"Select d_tube within the range: [0, {max_d_tube}] to avoid DL extraction region overlap: "))

    ant.comp_mass_analysis_respect_to_time(rg_param, ry_param, w_param, w_param, v_param*-1, T_param, N_param, diff_layer,
                                           adv_layer, diffusive_mass_container, advective_mass_container,
                                           advective_over_total_container, advective_over_initial_container,
                                           total_mass_container, collection_width, mass_checkpoint, r, d,
                                           mixed_config=mixed_config, d_tube=d_tube, collect_MFPT=collect_MFPT)

    if collect_plots:

        # Computing plot for only diffusive mass in the domain

        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        if mixed_config:
            current_time += "-mixed-config"
        else:
            current_time += "-original-config"

        data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_diffusive, current_time))
        print("Diffusive mass:", data_filepath)

        filename = f"diffusive_mass_analysis_V={v_param}_W={w_param}_{rg_param}x{ry_param}_.csv"
        output_location = os.path.join(data_filepath, filename)
        diff_output = output_location
        df = pd.DataFrame(diffusive_mass_container)
        df.to_csv(output_location, header=False, index=False)
        plt.plot_mass_analysis(output_location, v_param, w_param, N_param, T_param, rg_param, ry_param, "diffusive_mass",
                               data_filepath, save_png, show_plt)
        print()

        # Computing plot for only advective mass in domain

        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        if mixed_config:
            current_time += "-mixed-config"
        else:
            current_time += "-original-config"

        data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_advective, current_time))
        print("Advective mass:", data_filepath)

        filename = f"advective_mass_analysis_V={v_param}_W={w_param}_{rg_param}x{ry_param}_.csv"
        output_location = os.path.join(data_filepath, filename)
        adv_output = output_location
        df = pd.DataFrame(advective_mass_container)
        df.to_csv(output_location, header=False, index=False)
        plt.plot_mass_analysis(output_location, v_param, w_param, N_param, T_param, rg_param, ry_param, "advective_mass",
                               data_filepath, save_png, show_plt)

        print()
        # Computing plot for advective mass over current total mass

        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_advective_over_total, current_time))
        print("Advective over total:", data_filepath)

        filename = f"advective_over_total_mass_analysis_V={v_param}_W={w_param}_{rg_param}x{ry_param}_.csv"
        output_location = os.path.join(data_filepath, filename)
        adv_over_total_output = output_location
        df = pd.DataFrame(advective_over_total_container)
        df.to_csv(output_location, header=False, index=False)
        plt.plot_mass_analysis(output_location, v_param, w_param, N_param, T_param, rg_param, ry_param, "adv_over_tot",
                               data_filepath, save_png, show_plt)
        print()

        # Computing plot for total mass

        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        if mixed_config:
            current_time += "-mixed-config"
        else:
            current_time += "-original-config"

        data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_total, current_time))
        print("Total mass: ", data_filepath)

        filename = f"total_mass_analysis_V={v_param}_W={w_param}_{rg_param}x{ry_param}_.csv"
        output_location = os.path.join(data_filepath, filename)
        total_mass_output = output_location
        df = pd.DataFrame(total_mass_container)
        df.to_csv(output_location, header=False, index=False)
        plt.plot_mass_analysis(output_location, v_param, w_param, N_param, T_param, rg_param, ry_param, "total_mass",
                               data_filepath, save_png, show_plt)
        print()

        # Computing plot for advective mass over initial mass

        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_advective_over_initial, current_time))
        print("Advective over initial: ", data_filepath)

        filename = f"advective_over_initial_mass_analysis_V={v_param}_W={w_param}_{rg_param}x{ry_param}_.csv"
        output_location = os.path.join(data_filepath, filename)
        adv_over_initial_output = output_location
        df = pd.DataFrame(advective_over_initial_container)
        df.to_csv(output_location, header=False, index=False)

        plt.plot_mass_analysis(output_location, v_param, w_param, N_param, T_param, rg_param, ry_param, "adv_over_init",
                               data_filepath, save_png, show_plt)

        clk.sleep(2)
        return [diff_output, adv_output, adv_over_initial_output, adv_over_total_output, total_mass_output]
    else:
        print('Plots have not been printed because "collect_plots" has been set to False.')


def heatmap_production(rg_param, ry_param, w_param, v_param, N_param, filepath=fp.heatmap_output, time_point_container=None,
                       save_png=True, show_plot=True, compute_MFPT=True, verbose=False, output_csv=True, rect_config=False,
                       d_tube=-1, r=1.0, d=1.0, mass_retention_threshold=0.01, mass_checkpoint=10**6, color_scheme='viridis',
                       toggle_border=False, display_extraction=True, approach=2):
    v_param *= -1

    ani.generate_heatmaps(rg_param=rg_param, ry_param=ry_param, w_param=w_param, v_param=v_param, N_param=N_param, approach=approach,
                          filepath=filepath, time_point_container=time_point_container, save_png=save_png, show_plot=show_plot, compute_mfpt=compute_MFPT,
                          verbose=verbose, output_csv=output_csv, rect_config=rect_config, d_tube=d_tube, r=r, d=d, mass_retention_threshold=mass_retention_threshold,
                          mass_checkpoint=mass_checkpoint, color_scheme=color_scheme, toggle_border=toggle_border, display_extraction=display_extraction)

    '''
        If approach 2 is selected, only run the diffusive snapshot collection function until the last/maximum time point in the time-point container.
        The list of time-points should always be sorted in increasing order. 
    '''


