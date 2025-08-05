from project_src_package_2025.system_configuration import file_paths as fp
from project_src_package_2025.auxiliary_tools import prints, tabulate_functions as tb
from project_src_package_2025.data_visualization import plot_functions as plt
from project_src_package_2025.data_visualization import animation_functions as ani
import pandas as pd
import time
import os


def process_PvT_DL(PvT_DL_snapshots, v_param, w_param, N_LIST, T_fixed_ring_seg, save_png, show_plt, Timestamp_List, approach):

    output_location_list = []

    timestamp = prints.return_timestamp()
    data_filepath = os.path.abspath(tb.create_directory(fp.phi_v_theta_output, timestamp))
    filename = "PvT_Dl.csv"
    output_location = os.path.join(data_filepath, filename)

    df = pd.DataFrame(PvT_DL_snapshots)
    df.to_csv(output_location, header=False, index=False)

    time.sleep(1)
    plt.plot_phi_v_theta(output_location, v_param, w_param, N_LIST, approach, T_fixed_ring_seg,
                         data_filepath, Timestamp_List, save_png=save_png, show_plt=show_plt)

    output_location_list.append(output_location)

    return output_location_list


def process_MA_results(MA_DL_timeseries, MA_AL_timeseries, MA_TM_timeseries, MA_ALoT_timeseries,
                       MA_ALoI_timeseries, v_param, w_param, N_LIST, T_param, rg_param, ry_param,
                       save_png, show_plt):

    output_location_list = []

    # Diffusive mass analysis
    timestamp = prints.return_timestamp()
    data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_diffusive, timestamp))
    filename = f"MA_DL.csv"
    output_location = os.path.join(data_filepath, filename)

    df = pd.DataFrame(MA_DL_timeseries)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_mass_analysis(output_location, v_param, w_param, N_LIST, T_param, rg_param, ry_param,
                           "DL", "DL", data_filepath, save_png, show_plt)
    output_location_list.append(output_location)

    # Advective mass analysis
    timestamp = prints.return_timestamp()
    data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_advective, timestamp))
    filename = f"MA_AL.csv"
    output_location = os.path.join(data_filepath, filename)

    df = pd.DataFrame(MA_AL_timeseries)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_mass_analysis(output_location, v_param, w_param, N_LIST, T_param, rg_param, ry_param,
                           "AL", "AL", data_filepath, save_png, show_plt)
    output_location_list.append(output_location)

    # Total mass analysis
    timestamp = prints.return_timestamp()
    data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_total, timestamp))
    filename = f"MA_total.csv"
    output_location = os.path.join(data_filepath, filename)

    df = pd.DataFrame(MA_TM_timeseries)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_mass_analysis(output_location, v_param, w_param, N_LIST, T_param, rg_param, ry_param,
                           "Total", "Total", data_filepath, save_png, show_plt)
    output_location_list.append(output_location)

    # Advective/running total mass analysis
    timestamp = prints.return_timestamp()
    data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_advective_over_total, timestamp))
    filename = f"MA_AL_running_total.csv"
    output_location = os.path.join(data_filepath, filename)

    df = pd.DataFrame(MA_ALoT_timeseries)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_mass_analysis(output_location, v_param, w_param, N_LIST, T_param, rg_param, ry_param,
                           "AL/running total", "Al_running_total", data_filepath, save_png, show_plt)
    output_location_list.append(output_location)

    # Advective/initial total mass analysis
    timestamp = prints.return_timestamp()
    data_filepath = os.path.abspath(tb.create_directory(fp.mass_analysis_advective_over_initial, timestamp))
    filename = f"MA_AL_initial_total.csv"
    output_location = os.path.join(data_filepath, filename)

    df = pd.DataFrame(MA_ALoI_timeseries)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_mass_analysis(output_location, v_param, w_param, N_LIST, T_param, rg_param, ry_param,
                           "AL/initial total", "AL_initial_total", data_filepath, save_png, show_plt)
    output_location_list.append(output_location)

    return output_location_list


def process_DvR_results(PvR_DL_snapshots, RvR_AL_snapshots, v_param, w_param, N_LIST, rg_param,
                        ry_param, R_fixed_angle, Timestamp_List, save_png, show_plt, approach):
    # Processing results for Phi v. Radius & Rho v. Radius

    output_location_list = []

    timestamp = prints.return_timestamp()
    data_filepath = os.path.abspath(tb.create_directory(fp.radial_dependence_phi, timestamp))
    filename = "PvR_DL_snapshots.csv"
    output_location = os.path.join(data_filepath, filename)
    df = pd.DataFrame(PvR_DL_snapshots)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_dense_v_rad("Phi", output_location, v_param, w_param,
                         len(N_LIST), rg_param, ry_param, R_fixed_angle, Timestamp_List,
                         data_filepath, approach, save_png=save_png, show_plt=show_plt)
    output_location_list.append(output_location)

    # RvR_AL_snapshots = np.zeros((Timestamp_enum, rg_param), dtype=np.float64)

    timestamp = prints.return_timestamp()
    data_filepath = os.path.abspath(tb.create_directory(fp.radial_dependence_rho, timestamp))
    filename = "RvR_AL_snapshots.csv"
    output_location = os.path.join(data_filepath, filename)
    df = pd.DataFrame(RvR_AL_snapshots)
    df.to_csv(output_location, header=False, index=False)
    plt.plot_dense_v_rad("Rho", output_location, v_param, w_param,
                         len(N_LIST), rg_param, ry_param, R_fixed_angle, Timestamp_List,
                         data_filepath, approach, save_png=save_png, show_plt=show_plt)
    output_location_list.append(output_location)

    return output_location_list


def process_static_HM_results(HM_DL_snapshots, HM_C_snapshots, MFPT_snapshots, checkpoint_collect_container,
                              heat_plot_border, w_param, v_param, N_LIST, heatplot_colorscheme,
                              save_png, show_plt, j_max_list, display_extraction, approach):

    output_location_list = []
    timestamp = prints.return_timestamp()
    data_filepath = tb.create_directory(fp.heatmap_output, timestamp)

    N_LIST_count = len(N_LIST)

    for t in range(len(checkpoint_collect_container)):

        MFPT = MFPT_snapshots[t]
        curr_DL_snapshot = HM_DL_snapshots[t]
        curr_C_snapshot = HM_C_snapshots[t]
        check_point = checkpoint_collect_container[t]

        csv_filename = f"HM_DL_snapshot_T={check_point}.csv"
        output_csv_loc = os.path.join(data_filepath, csv_filename)
        # print(output_csv_loc)
        df = pd.DataFrame(curr_DL_snapshot)
        df.to_csv(output_csv_loc, header=False, index=False)

        ani.produce_heatmap_tool_rect(curr_DL_snapshot, curr_C_snapshot, w_param, v_param, N_LIST_count,
                                      approach, t, data_filepath, MFPT, check_point, N_LIST, j_max_list, display_extraction,
                                      save_png, show_plt, transparent=False, toggle_border=heat_plot_border, color_scheme=heatplot_colorscheme)
        time.sleep(1)

    csv_filename = f"HM_C_snapshot.csv"
    column_labels = ['T', 'Phi(center)']

    data_dict = {
        column_labels[0]: checkpoint_collect_container,
        column_labels[1]: HM_C_snapshots
    }

    output_csv_loc = os.path.join(data_filepath, csv_filename)
    df = pd.DataFrame(data_dict)
    df.to_csv(output_csv_loc, index=False)
    output_location_list.append(output_csv_loc)

    return output_location_list


def process_MFPT_results(MFPT_snapshots, checkpoint_collect_container, approach,
                         rg_param, ry_param, w_param, v_param, N_LIST, save_png=True,
                         show_plt=True):

    output_location_list = []

    timestamp = prints.return_timestamp()
    data_filepath = tb.create_directory(fp.mfpt_results_output, timestamp)

    csv_filename = f"MFPT_timestamp.csv"

    if approach == 1:
        x_label = 'TM'
    elif approach == 2:
        x_label = 'T'
    else:
        raise ValueError(f'{approach} is not a valid argument, use either collection approach "1" or "2" (must be an int)')

    column_labels = [x_label, 'MFPT']

    data_dict = {
        column_labels[0]: checkpoint_collect_container,
        column_labels[1]: MFPT_snapshots
    }

    output_csv_loc = os.path.join(data_filepath, csv_filename)
    df = pd.DataFrame(data_dict)
    df.to_csv(output_csv_loc, index=False)
    plt.plot_mfpt_v_checkpoints(output_csv_loc, x_label, rg_param, ry_param, w_param, v_param, N_LIST, data_filepath,
                                save_png, show_plt)
    output_location_list.append(output_csv_loc)

    return output_location_list
