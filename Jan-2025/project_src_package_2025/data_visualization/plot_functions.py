from . import plt, os, pd, datetime


def plot_general(file_list, N_labels, xlab, ylab, title, filepath, xlog=False, ylog=False, ylims=None,
                 continuous=False, dynamic_pts=False, save_png=False, show_plt=True, transparent=False,
                 figsize=(12, 8), lab_fontsize=30, title_fontsize=40, legend_fontsize=22,
                 fontname='Times New Roman'):

    plt.figure(figsize)

    for i in range(len(file_list)):
        df = pd.read_csv(file_list[i])

        if continuous:
            plt.plot(df[xlab], df[ylab], label=f'{len(N_labels[i])}')
        else:
            if dynamic_pts:
                plt.scatter(df[xlab], df[ylab], label=f'{len(N_labels[i])}', linewidth=(10 / (i + 1)))
            else:
                plt.scatter(df[xlab], df[ylab], label=f'{len(N_labels[i])}', linewidth=(10 / (i + 1)))
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


def plot_phi_v_theta(data_filepath, v, w, N, approach, position, file_path, save_png=False, show_plt=True, time_point_container=None):

    data = pd.read_csv(data_filepath, header=None)

    # Prepare the x-axis as column indices starting from 1
    x = range(1, data.shape[1] + 1)

    if approach == 2:
        label_container = ["0.675 < m < 0.68", "0.45 < mass_retained < 0.46",
                           " 0.225 < mass_retained < 0.26", "0.015 < mass_retained < 0.02"]
    elif approach == 1:
        label_container = ["early time", "late time"]
    elif approach == 3:
        converted_container = [f"T={T:.3f}" for T in time_point_container]
        label_container = converted_container
    elif approach == 4:
        label_container = [f"ring={i*2}" for i in range(24)]
    else:
        raise ValueError(f'{approach} is not a valid argument, use either approach2 "1" or "2" (must be an int)')

    # Plot each row of data
    plt.figure(figsize=(10, 6))
    for i, row in data.iterrows():
        plt.plot(x, row, label=label_container[i])

    # Add labels, legend, and title
    plt.xlabel("Theta")
    plt.ylabel("Phi")

    if approach == 4:
        title = f'Phi_versus_Theta_V={v}_W={w}_N={N}_Approach{approach}'
    else:
        title = f'Phi_versus_Theta_V={v}_W={w}_N={N}_Approach{approach}_Position={position}'

    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_png:
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if file_path:
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            file = os.path.join(file_path, f'phi_v_theta_v={v}_w={w}_app={approach}_pos={position}_{current_time}.png')
            plt.savefig(file, bbox_inches='tight')
            print(f'Plot saved to {file_path}')

    if show_plt:
        plt.show()
    plt.close()
