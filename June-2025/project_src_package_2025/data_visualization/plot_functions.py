from . import plt, os, pd, datetime, Fraction, math, np


def plot_general(file_list, labels, xlab, ylab, title, filepath, xlog=False, ylog=False, ylims=None,
                 continuous=False, dynamic_pts=False, save_png=True, show_plt=True, transparent=False,
                 figsize=(12, 8), lab_fontsize=30, title_fontsize=40, legend_fontsize=22,
                 fontname='Times New Roman'):

    plt.figure(figsize=figsize)

    for i in range(len(file_list)):
        df = pd.read_csv(file_list[i])

        if continuous:
            plt.plot(df[xlab], df[ylab], label=labels[i])
        else:
            if dynamic_pts:
                plt.scatter(df[xlab], df[ylab], label=labels[i], linewidth=(10 / (i + 1)))
            else:
                    plt.scatter(df[xlab], df[ylab], label=labels[i], linewidth=(10 / (i + 1)))

        if xlog:
            plt.xscale('log')

        if ylog:
            plt.yscale('log')

    plt.xlabel(xlab, fontsize=lab_fontsize, fontname=fontname)
    plt.ylabel(ylab, fontsize=lab_fontsize, fontname=fontname)
    plt.title(title, fontsize=title_fontsize, fontname=fontname)

    plt.xticks(fontsize=30, fontname=fontname)
    plt.yticks(fontsize=25, fontname=fontname)

    plt.legend(fontsize=legend_fontsize, frameon=True, edgecolor='black', loc='best')

    if ylims is not None:
        if len(ylims) < 0 or len(ylims) > 2:
            raise ValueError("There can only be two values provided for the y-axis limits, "
                             "a lower bound and an upper bound.")
        else:
            plt.ylim(ylims[0], ylims[1])
    if save_png:
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if filepath:
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            file = os.path.join(filepath, f'{title}_date{current_time}.png')
            plt.savefig(file, bbox_inches='tight', transparent=transparent)
            print(f'Plot saved to {filepath}')

    if show_plt:
        plt.show()
    plt.close()


def plot_mfpt_v_checkpoints(data_filepath, x_label, rg_param, ry_param, w_param, v_param, N_LIST, file_path, save_png=True, show_plt=True):
    data = pd.read_csv(data_filepath)
    x = data[x_label]
    y = data['MFPT']
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y)
    plt.xlabel(x_label)
    plt.ylabel('MFPT')
    plt.grid(True)
    plt.tight_layout()
    plt.title(f'MFPT({x_label}) W={w_param:.2e}   V={v_param}   N={len(N_LIST)}    Domain={rg_param}x{ry_param}')

    if save_png:
        if file_path:
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            file = os.path.join(file_path, f"MFPT_v_{x_label}.png")
            plt.savefig(file, bbox_inches='tight')
            print(f'Plot saved to {file_path}')
    if show_plt:
        plt.show()
    plt.close()


def plot_phi_v_theta(data_filepath, v, w, N, approach, position, file_path, checkpoint_collect_container, save_png=True, show_plt=True):

    data = pd.read_csv(data_filepath, header=None)

    # Prepare the x-axis as column indices starting from 1
    x = range(1, data.shape[1] + 1)

    label_container = []

    if approach == 1:
        for i in range(len(checkpoint_collect_container)):
            label_container.append(f"Mass ~ {checkpoint_collect_container[i]}")

    elif approach == 2:
        for i in range(len(checkpoint_collect_container)):
            label_container.append(f"T ~ {checkpoint_collect_container[i]}")
    else:
        raise ValueError(f"Invalid approach: {approach}. Use approach 1 (mass-point collection) or approach 2 (time-point collection).")

    # Plot each row of data
    plt.figure(figsize=(10, 6))
    for i, row in data.iterrows():
        plt.plot(x, row, label=label_container[i])

    # Add labels, legend, and title
    plt.xlabel("Theta")
    plt.ylabel("Phi")

    # if approach == 4:
    #     title = f'Phi_versus_Theta_V={v}_W={w}_N={N}_Approach{approach}'
    # else:
    #     title = f'Phi_versus_Theta_V={v}_W={w}_N={N}_Approach{approach}_Position={position}'

    title = f" Phi(theta)  W={w:.2e}   V={v}   N={len(N)} Position={position}"

    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_png:
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if file_path:
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            # file = os.path.join(file_path, f'phi_v_theta_v={v}_w={w}_app={approach}_pos={position}_{current_time}.png')
            file = os.path.join(file_path, "phi_v_theta.png")
            plt.savefig(file, bbox_inches='tight')
            print(f'Plot saved to {file_path}')

    if show_plt:
        plt.show()
    plt.close()


def plot_dense_v_rad(y_lab, data_filepath, v, w, N, rings, rays, fixed_angle, checkpoint_collect_container, file_path, approach, save_png=True, show_plt=True):

    data = pd.read_csv(data_filepath, header=None)

    if y_lab.lower() == "phi":
        x = np.linspace(0, 1, rings+1)
    elif y_lab.lower() == "rho":
        x = np.linspace(1/rings, 1, rings)

    label_container = []

    title = f"{y_lab.lower()}(R) W={w:.2e}  V={v}   N={N}  fixed_angle={fixed_angle} Domain={rings}x{rays}"

    if approach == 1:
        for i in range(len(checkpoint_collect_container)):
            label_container.append(f"Mass ~ {checkpoint_collect_container[i]}")

    elif approach == 2:
        for i in range(len(checkpoint_collect_container)):
            label_container.append(f"T ~ {checkpoint_collect_container[i]}")
    else:
        raise ValueError(f"Invalid approach: {approach}. Use approach 1 (mass-point collection) or approach 2 (time-point collection).")
    # Plot each row of data
    plt.figure(figsize=(10, 6))
    for i, row in data.iterrows():
        plt.plot(x, row, label=label_container[i])

    # Add labels, legend, and title
    plt.xlabel("(R) Radius")
    plt.ylabel(y_lab)

    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_png:
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if file_path:
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            # file = os.path.join(file_path, f'{y_lab}_v_theta_V={v}_W={w}_N={N}_Angle={fixed_angle}_{current_time}.png')
            file = os.path.join(file_path, f'{y_lab.lower()}_v_radius.png')
            plt.savefig(file, bbox_inches='tight')
            print(f'Plot saved to {file_path}')

    if show_plt:
        plt.show()
    plt.close()


def plot_mass_analysis(data_filepath, v, w, N, T, rings, rays, mass_type, file_name_mass_type, file_path, save_png=True, show_plt=True):

    data = pd.read_csv(data_filepath, header=None)

    # Plot each row of data
    plt.figure(figsize=(10, 6))

    y = data
    discretization = len(data)
    x = np.linspace(0, T, discretization)

    plt.plot(x, y)

    # Add labels, legend, and title
    plt.xlabel("(T) Time")
    plt.ylabel("(m) Mass")

    title = f" Mass ({mass_type}) v. Time   W={w:.2e}   V={v}   N={len(N)}  Domain={rings}x{rays}"

    plt.title(title)
    # plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_png:
        # current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if file_path:
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            # file = os.path.join(file_path, f'{mass_type}_versus_T_W={w}_V={v}_N={len(N)}_{rings}x{rays}_{current_time}.png')

            filename_ = "MA_" + file_name_mass_type + ".png"
            file = os.path.join(file_path, filename_)
            plt.savefig(file, bbox_inches='tight')
            print(f'Plot saved to {file_path}')
    if show_plt:
        plt.show()
    plt.close()


# ================================================= UNDER INSPECTION/REQUIRES UPDATES =================================================
# def plot_dense_v_rad_mul(y_lab, data_filepaths, v, w, N, rings, rays, fixed_angle, time_point_container, file_path,
#                      save_png=False, show_plt=True):
#     """
#     Plots the same indexed row (trajectory) across multiple CSV datasets for comparison.
#
#     Parameters:
#         y_lab (str): Label for y-axis.
#         data_filepaths (list): List of CSV file paths (same format expected).
#         v, w, N, rings, rays, fixed_angle: Parameters for title.
#         time_point_container (list): Time values corresponding to each row.
#         file_path (str): Directory to save PNG if enabled.
#         save_png (bool): If True, saves PNG to file_path.
#         show_plt (bool): If True, displays the plot.
#     """
#
#     # Load all datasets into a list of DataFrames
#     datasets = [pd.read_csv(fp, header=None) for fp in data_filepaths]
#
#     # Determine x-axis values
#     if y_lab.lower() == "phi":
#         x = np.linspace(0, 1, rings + 1)
#     elif y_lab.lower() == "rho":
#         x = np.linspace(1 / rings, 1, rings)
#     else:
#         raise ValueError("y_lab must be either 'phi' or 'rho'.")
#
#     converted_container = [f"T={T:.3f}" for T in time_point_container]
#
#     num_trajectories = len(converted_container)
#     num_datasets = len(datasets)
#
#     plt.figure(figsize=(12, 6 * num_trajectories))
#
#     for i in range(num_trajectories):
#         plt.subplot(num_trajectories, 1, i + 1)
#         for j, df in enumerate(datasets):
#             label = f"{converted_container[i]} - Dataset {j + 1}"
#             plt.plot(x, df.iloc[i], label=label)
#
#         plt.xlabel("(R) Radius")
#         plt.ylabel(y_lab)
#         plt.title(f"Trajectory {i + 1} at {converted_container[i]}")
#         plt.legend()
#         plt.grid(True)
#
#     full_title = f"{y_lab}_comparison_V={v}_W={w:.2e}_N={N}_Angle={fixed_angle}_Domain={rings}x{rays}"
#     plt.suptitle(full_title, fontsize=14)
#     plt.tight_layout(rect=[0, 0, 1, 0.96])
#
#     if save_png:
#         current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#         if file_path:
#             os.makedirs(file_path, exist_ok=True)
#             filename = f"{y_lab}_comparison_V={v}_W={w}_N={N}_Angle={fixed_angle}_{current_time}.png"
#             save_path = os.path.join(file_path, filename)
#             plt.savefig(save_path, bbox_inches='tight')
#             print(f'Plot saved to {save_path}')
#
#     if show_plt:
#         plt.show()
#     plt.close()
#
#
# def plot_phi_v_theta_mult(data_filepaths, v, w, N, approach, position, file_path, save_png=False, show_plt=True,
#                      time_point_container=None):
#     """
#     Plots corresponding phi-vs-theta rows across multiple CSV files.
#     Labeling is based on the approach used.
#
#     Parameters:
#         data_filepaths (list): List of file paths (all should have same row count).
#         v, w, N, approach, position: Plot parameters.
#         file_path (str): Directory to save figure if save_png=True.
#         save_png (bool): Save figure to file if True.
#         show_plt (bool): Show figure if True.
#         time_point_container (list): Used only if approach == 3.
#     """
#
#     # Load all datasets
#     datasets = [pd.read_csv(fp, header=None) for fp in data_filepaths]
#
#     # Assume all files have the same number of rows
#     num_curves = datasets[0].shape[0]
#     x = range(1, datasets[0].shape[1] + 1)  # theta values (1-based index)
#
#     # Determine label strategy based on approach
#     if approach == 2:
#         label_container = ["0.675 < m < 0.68", "0.45 < mass_retained < 0.46",
#                            "0.225 < mass_retained < 0.26", "0.015 < mass_retained < 0.02"]
#     elif approach == 1:
#         label_container = ["early time", "late time"]
#     elif approach == 3:
#         if time_point_container is None:
#             raise ValueError("time_point_container must be provided for approach == 3")
#         label_container = [f"T={T:.3f}" for T in time_point_container]
#     elif approach == 4:
#         label_container = [f"ring={i * 2}" for i in range(num_curves)]
#     else:
#         raise ValueError(f'{approach} is not a valid argument. Choose 1, 2, 3, or 4.')
#
#     # Plot each row (trajectory) as a subplot comparing all datasets
#     plt.figure(figsize=(12, 6 * num_curves))
#
#     for i in range(num_curves):
#         plt.subplot(num_curves, 1, i + 1)
#         for j, df in enumerate(datasets):
#             label = f"{label_container[i]} - Dataset {j + 1}"
#             plt.plot(x, df.iloc[i], label=label)
#
#         plt.xlabel("Theta")
#         plt.ylabel("Phi")
#         plt.title(f"Trajectory {i + 1}: {label_container[i]}")
#         plt.legend()
#         plt.grid(True)
#
#     # Overall title
#     if approach == 4:
#         suptitle = f'Phi_vs_Theta_V={v}_W={w}_N={N}_Approach{approach}'
#     else:
#         suptitle = f'Phi_vs_Theta_V={v}_W={w}_N={N}_Approach{approach}_Position={position}'
#
#     plt.suptitle(suptitle, fontsize=14)
#     plt.tight_layout(rect=[0, 0, 1, 0.96])
#
#     if save_png:
#         current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#         if file_path:
#             os.makedirs(file_path, exist_ok=True)
#             filename = f'phi_v_theta_v={v}_w={w}_app={approach}_pos={position}_{current_time}.png'
#             save_path = os.path.join(file_path, filename)
#             plt.savefig(save_path, bbox_inches='tight')
#             print(f'Plot saved to {save_path}')
#
#     if show_plt:
#         plt.show()
#     plt.close()