from project_src_package_2025.system_configuration import file_paths as fp
from project_src_package_2025.auxiliary_tools import prints, tabulate_functions as tb
from project_src_package_2025.data_visualization import plot_functions as plt
import pandas as pd
import time
import os


def process_PvT_DL(PvT_DL_snapshots, v_param, w_param, N_LIST, T_fixed_ring_seg, save_png, show_plt, Timestamp_List):

    timestamp = prints.return_timestamp()
    data_filepath = os.path.abspath(tb.create_directory(fp.phi_v_theta_output, timestamp))
    filename = "PvT_Dl.csv"
    output_location = os.path.join(data_filepath, filename)
    df = pd.DataFrame(PvT_DL_snapshots)
    df.to_csv(output_location, header=False, index=False)

    time.sleep(1)
    plt.plot_phi_v_theta(output_location, v_param, w_param, N_LIST, 3, T_fixed_ring_seg,
                         data_filepath, save_png=save_png, show_plt=show_plt, time_point_container=Timestamp_List)
