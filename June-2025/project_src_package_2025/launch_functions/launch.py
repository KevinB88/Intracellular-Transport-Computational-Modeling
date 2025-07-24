import pandas as pd

from . import mfpt_comp, sup, datetime, tb, fp, mp, config, partial, ant, np, os, plt, ani, num, super
import time as clk
import math

from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QMessageBox

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
            mfpt_results = pool.map(partial(solve_mfpt_multi_process, N_list[n],
                                            rg_param, ry_param, dep_type, dep_param), ind_list)
        print(mfpt_results)
        tb.produce_csv_from_xy(mfpt_results, dep_type, "MFPT", data_filepath,
                               f'MFPT_Results_N={len(N_list[n])}_{ind_type}={dep_param}_')


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


def solve_mfpt_(rg_param, ry_param, N_param, v_param, w_param, T_param, r=1.0, d=1.0, mass_checkpoint=10 ** 6,
                d_tube=-1, return_duration=False):
    j_max_lim = sup.j_max_bef_overlap(ry_param, N_param)
    max_d_tube = sup.solve_d_rect(r, ry_param, rg_param, j_max_lim, 0)

    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)
    MFPT, duration = mfpt_comp.comp_mfpt_by_time_rect(rg_param, ry_param, w_param, w_param,
                                                      v_param * -1, N_param, diff_layer, adv_layer, T_param,
                                                      mass_checkpoint=mass_checkpoint, r=r, d=d, d_tube=d_tube)
    if return_duration:
        return MFPT, duration
    else:
        return MFPT


# MFPT as a function of W saturation analysis

# under construction
def mfpt_of_W_sat_analysis(domain_list, N_param_list, v_param, w_param_list, T_param, r=1.0, d=1.0,
                           mass_checkpoint=10 ** 6, d_tube=-1):
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


def output_time_until_mass_depletion(rg_param, ry_param, N_param, v_param, w_param, mass_threshold=0.01,
                                     mixed_config=False, d_tube=-1):
    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)

    if mixed_config:
        # This variable denotes the maximum j_max value with respect to microtubule configuration on the first ring
        j_max_lim = sup.j_max_bef_overlap(ry_param, N_param)
        max_d_tube = sup.solve_d_rect(1, ry_param, rg_param, j_max_lim, 0)

    duration = ant.comp_until_mass_depletion(rg_param, ry_param, w_param, w_param,
                                             v_param * -1, N_param, diff_layer, adv_layer,
                                             mass_retention_threshold=mass_threshold, mixed_config=mixed_config,
                                             d_tube=d_tube)
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

    v_param *= -1

    ant.comp_diffusive_angle_snapshots(rg_param, ry_param, w_param, w_param, v_param, N_param,
                                       diff_layer, adv_layer, phi_v_theta_container, approach, m_segment=m_segment, r=r,
                                       d=d,
                                       mass_retention_threshold=mass_retention_threshold,
                                       time_point_container=time_point_container, mixed_config=mixed_config,
                                       d_tube=d_tube)

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

    ant.comp_diffusive_rad_snapshots(rg_param, ry_param, w_param, w_param, v_param * -1, N_param, diff_layer, adv_layer,
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
                          mass_checkpoint=10 ** 6, save_png=False, show_plt=True, mixed_config=False, d_tube=-1,
                          collect_MFPT=False, collect_plots=True):
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

    ant.comp_mass_analysis_respect_to_time(rg_param, ry_param, w_param, w_param, v_param * -1, T_param, N_param,
                                           diff_layer,
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
        plt.plot_mass_analysis(output_location, v_param, w_param, N_param, T_param, rg_param, ry_param,
                               "diffusive_mass", "diff",
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
        plt.plot_mass_analysis(output_location, v_param, w_param, N_param, T_param, rg_param, ry_param,
                               "advective_mass", "adv",
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
        plt.plot_mass_analysis(output_location, v_param, w_param, N_param, T_param, rg_param, ry_param, "adv_over_tot", "adv_over_tot",
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
        plt.plot_mass_analysis(output_location, v_param, w_param, N_param, T_param, rg_param, ry_param, "total_mass", "total",
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

        plt.plot_mass_analysis(output_location, v_param, w_param, N_param, T_param, rg_param, ry_param, "adv_over_init", "adv_over_init",
                               data_filepath, save_png, show_plt)

        clk.sleep(2)
        return [diff_output, adv_output, adv_over_initial_output, adv_over_total_output, total_mass_output]
    else:
        print('Plots have not been printed because "collect_plots" has been set to False.')


def heatmap_production(rg_param, ry_param, w_param, v_param, N_param, filepath=fp.heatmap_output,
                       time_point_container=None,
                       save_png=True, show_plot=True, compute_MFPT=True, verbose=False, output_csv=True,
                       rect_config=False,
                       d_tube=-1, r=1.0, d=1.0, mass_retention_threshold=0.01, mass_checkpoint=10 ** 6,
                       color_scheme='viridis',
                       toggle_border=False, display_extraction=True, approach=2):

    ani.generate_heatmaps(rg_param=rg_param, ry_param=ry_param, w_param=w_param, v_param=v_param, N_param=N_param,
                          approach=approach,
                          filepath=filepath, time_point_container=time_point_container, save_png=save_png,
                          show_plot=show_plot, compute_mfpt=compute_MFPT,
                          verbose=verbose, output_csv=output_csv, rect_config=rect_config, d_tube=d_tube, r=r, d=d,
                          mass_retention_threshold=mass_retention_threshold,
                          mass_checkpoint=mass_checkpoint, color_scheme=color_scheme, toggle_border=toggle_border,
                          display_extraction=display_extraction)

    '''
        If approach 2 is selected, only run the diffusive snapshot collection function until the last/maximum time point in the time-point container.
        The list of time-points should always be sorted in increasing order. 
    '''


def launch_super_comp_I(rg_param, ry_param, w_param, v_param, T_param, N_LIST, d_tube=0, Timestamp_List=None,
                        MA_collection_factor=5, MA_collection_factor_limit=10 ** 3,
                        D=1.0, domain_radius=1.0, mass_checkpoint=10 ** 6, T_fixed_ring_seg=0.5, R_fixed_angle=-1,
                        save_png=True, save_csv=True, show_plt=False, heat_plot_border=False, heatplot_colorscheme='viridis',
                        display_extraction=True):

    T_param = float(T_param)

    if Timestamp_List is None:
        # Default timestamps
        Timestamp_List = [T_param * 0.25, T_param * 0.5, T_param * 0.75, T_param]

    for t in range(len(Timestamp_List)):
        if Timestamp_List[t] < 0.0 or Timestamp_List[t] > T_param:
            raise ValueError(f"Timestamp-point: {Timestamp_List[t]} falls outside of the legal timestamp-point range: [0, {T_param} (T_param) ] (T_param = your input solution time duration)")

    dT = num.compute_dT(rg_param, ry_param, domain_radius=domain_radius, D=D)
    T_param += dT
    Timestamp_enum = len(Timestamp_List)

    # Initialize mass analysis time series collection containers

    K = T_param / dT
    relative_k = math.floor(K / MA_collection_factor)

    MA_DL_timeseries = np.zeros([relative_k], dtype=np.float64)
    MA_AL_timeseries = np.zeros([relative_k], dtype=np.float64)
    MA_TM_timeseries = np.zeros([relative_k], dtype=np.float64)
    MA_ALoT_timeseries = np.zeros([relative_k], dtype=np.float64)
    MA_ALoI_timeseries = np.zeros([relative_k], dtype=np.float64)

    # Initialize Phi v. Theta diffusive layer snapshot container

    PvT_DL_snapshots = np.zeros((Timestamp_enum, ry_param), dtype=np.float64)

    # Initialize Density v. Radius snapshot containers

    PvR_DL_snapshots = np.zeros((Timestamp_enum, rg_param + 1), dtype=np.float64)
    RvR_AL_snapshots = np.zeros((Timestamp_enum, rg_param), dtype=np.float64)

    # Prepare for heatmap collection

    j_max_list = []
    j_max_lim = sup.j_max_bef_overlap(ry_param, N_LIST)
    max_d_tube = sup.solve_d_rect(domain_radius, ry_param, rg_param, j_max_lim, 0)

    if d_tube < 0 or d_tube > max_d_tube:
        d_tube = max_d_tube

    dRad = domain_radius / rg_param
    dThe = (2 * np.pi) / ry_param

    for m in range(rg_param):
        j_max = int(np.ceil((d_tube / ((m + 1) * dRad * dThe)) - 0.5))
        j_max_list.append(j_max)

    HM_DL_snapshots = np.zeros((Timestamp_enum, rg_param, ry_param), dtype=np.float64)
    HM_C_snapshots = np.zeros([Timestamp_enum], dtype=np.float64)
    MFPT_snapshots = np.zeros([Timestamp_enum], dtype=np.float64)

    # Initialize layers
    D_LAYER, A_LAYER = sup.initialize_layers(rg_param, ry_param)

    # Release the Kraken.. (execute super_comp_type_I)
    super.super_comp_type_I(rg_param, ry_param, w_param, w_param, T_param, v_param, N_LIST, D_LAYER, A_LAYER,
                            Timestamp_List, HM_DL_snapshots, HM_C_snapshots, PvT_DL_snapshots, T_fixed_ring_seg,
                            MA_DL_timeseries, MA_AL_timeseries, MA_ALoI_timeseries, MA_ALoT_timeseries,
                            MA_TM_timeseries,
                            MA_collection_factor, PvR_DL_snapshots, RvR_AL_snapshots, R_fixed_angle, MFPT_snapshots,
                            d_tube, D, domain_radius, mass_checkpoint, MA_collection_factor_limit)

    # Process results: Produce CSVs, PNGs (plots and heatmaps) (log results to filepath_log<timestamp>.txt)
    # Parameter chart (relative to the computation) is also included in the result
    # Desired output: a package containing all results categorized by type

    # Processing results for Mass-Analysis

    # Diffusive mass analysis

    timestamp = datetime.now().strftime("%I-%M_%p_%m-%d-%Y")
    data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_diffusive, timestamp))
    filename = f"MA_DL.csv"
    output_location = os.path.join(data_filepath, filename)

    df = pd.DataFrame(MA_DL_timeseries)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_mass_analysis(output_location, v_param, w_param, N_LIST, T_param, rg_param, ry_param,
                           "DL", "DL", data_filepath, save_png, show_plt)

    # Advective mass analysis
    timestamp = datetime.now().strftime("%I-%M_%p_%m-%d-%Y")
    data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_advective, timestamp))
    filename = f"MA_AL.csv"
    output_location = os.path.join(data_filepath, filename)

    df = pd.DataFrame(MA_AL_timeseries)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_mass_analysis(output_location, v_param, w_param, N_LIST, T_param, rg_param, ry_param,
                           "AL", "AL", data_filepath, save_png, show_plt)

    # Total mass analysis
    timestamp = datetime.now().strftime("%I-%M_%p_%m-%d-%Y")
    data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_total, timestamp))
    filename = f"MA_total.csv"
    output_location = os.path.join(data_filepath, filename)

    df = pd.DataFrame(MA_TM_timeseries)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_mass_analysis(output_location, v_param, w_param, N_LIST, T_param, rg_param, ry_param,
                           "Total", "Total", data_filepath, save_png, show_plt)

    # Advective/running total mass analysis
    timestamp = datetime.now().strftime("%I-%M_%p_%m-%d-%Y")
    data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_advective_over_total, timestamp))
    filename = f"MA_AL_running_total.csv"
    output_location = os.path.join(data_filepath, filename)

    df = pd.DataFrame(MA_ALoT_timeseries)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_mass_analysis(output_location, v_param, w_param, N_LIST, T_param, rg_param, ry_param,
                           "AL/running total", "Al_running_total", data_filepath, save_png, show_plt)

    # Advective/initial total mass analysis
    timestamp = datetime.now().strftime("%I-%M_%p_%m-%d-%Y")
    data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_advective_over_initial, timestamp))
    filename = f"MA_AL_initial_total.csv"
    output_location = os.path.join(data_filepath, filename)

    df = pd.DataFrame(MA_AL_timeseries)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_mass_analysis(output_location, v_param, w_param, N_LIST, T_param, rg_param, ry_param,
                           "AL/initial total", "AL_initial_total", data_filepath, save_png, show_plt)

    # Processing results for Phi v. Theta

    timestamp = datetime.now().strftime("%I-%M_%p_%m-%d-%Y")
    data_filepath = os.path.abspath(tb.create_directory(fp.phi_v_theta_output, timestamp))
    filename = "PvT_Dl.csv"
    output_location = os.path.join(data_filepath, filename)
    df = pd.DataFrame(PvT_DL_snapshots)
    df.to_csv(output_location, header=False, index=False)

    clk.sleep(1)
    plt.plot_phi_v_theta(output_location, v_param, w_param, N_LIST, 3, T_fixed_ring_seg,
                         data_filepath, save_png=save_png, show_plt=show_plt, time_point_container=Timestamp_List)

    # Processing results for Phi v. Radius & Rho v. Radius

    timestamp = datetime.now().strftime("%I-%M_%p_%m-%d-%Y")
    data_filepath = os.path.abspath(tb.create_directory(fp.radial_dependence_phi, timestamp))
    filename = "PvR_DL_snapshots.csv"
    output_location = os.path.join(data_filepath, filename)
    df = pd.DataFrame(PvR_DL_snapshots)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_dense_v_rad("Phi", output_location, v_param, w_param,
                         len(N_LIST), rg_param, ry_param, R_fixed_angle, Timestamp_List,
                         data_filepath, save_png=save_png, show_plt=show_plt)

    # RvR_AL_snapshots = np.zeros((Timestamp_enum, rg_param), dtype=np.float64)

    timestamp = datetime.now().strftime("%I-%M_%p_%m-%d-%Y")
    data_filepath = os.path.abspath(tb.create_directory(fp.radial_dependence_rho, timestamp))
    filename = "RvR_AL_snapshots.csv"
    output_location = os.path.join(data_filepath, filename)
    df = pd.DataFrame(RvR_AL_snapshots)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_dense_v_rad("Rho", output_location, v_param, w_param,
                         len(N_LIST), rg_param, ry_param, R_fixed_angle, Timestamp_List,
                         data_filepath, save_png=save_png, show_plt=show_plt)

    # Processing static heat-plots

    timestamp = datetime.now().strftime("%I-%M_%p_%m-%d-%Y")
    data_filepath = tb.create_directory(fp.heatmap_output, timestamp)

    for t in range(len(Timestamp_List)):
        MFPT = MFPT_snapshots[t]
        curr_DL_snapshot = HM_DL_snapshots[t]
        curr_C_snapshot = HM_C_snapshots[t]
        time_point = Timestamp_List[t]

        csv_filename = f"HM_DL_snapshot_T={time_point}.csv"
        output_csv_loc = os.path.join(data_filepath, csv_filename)
        df = pd.DataFrame(curr_DL_snapshot)
        df.to_csv(output_csv_loc, header=False, index=False)

        ani.produce_heatmap_tool_rect(curr_DL_snapshot, curr_C_snapshot,
                                      heat_plot_border, w_param, v_param,
                                      len(N_LIST), data_filepath, heatplot_colorscheme, save_png,
                                      show_plt, pane=t, MFPT=MFPT, duration=True, time_point=time_point, approach=2,
                                      extraction_angle_list=N_LIST, boundary_of_extraction_list=j_max_list,
                                      display_extraction=display_extraction, )
        clk.sleep(1)

    csv_filename = f"HM_C_snapshot.csv"

    column_labels = ['T', 'Phi(center)']

    data_dict = {
        column_labels[0]: Timestamp_List,
        column_labels[1]: HM_C_snapshots
    }

    output_csv_loc = os.path.join(data_filepath, csv_filename)
    df = pd.DataFrame(data_dict)
    df.to_csv(output_csv_loc, index=False)

    print("Successfully completed super-function. View results in project_src_package_2025/data_output.")









