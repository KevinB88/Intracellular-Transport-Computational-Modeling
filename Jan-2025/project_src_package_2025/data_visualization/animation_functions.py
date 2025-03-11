import pandas as pd

from . import plt, os, np, datetime, cm, BoundaryNorm, Normalize, fp, ant, sup, tb, Axes3D, LogNorm
import time

'''
    The diffusive_layer and diffusive_layer_center refer to specific snapshots of the MxN 
    domain. diffusive_layer consists of all diffusive values for each M,N value within the domain 
    excluding the center diffusive value, and the diffusive_layer_center obviously refers to the center.
'''

'''
    The time_point_container is constructed relative to the "early" and "late"
    times collected from the global max values from the J(t) function. 
'''


def generate_heatmaps(rg_param, ry_param, w_param, v_param, N_param, approach=2,
                      filepath=fp.heatmap_output, time_point_container=None, save_png=True, show_plot=False,
                      compute_mfpt=False, verbose=False, output_csv=False, log_scale=False, toggleBorder=False,
                      colorScheme='viridis', topological=False):
    panes = 0
    mfpt = None
    # duration refers to the dimensionless time from the mfpt computation
    duration = None

    if approach == 2:
        panes = 4
    elif approach == 1:
        if time_point_container is None:
            raise ("The time_point_container cannot be empty for approach #1, "
                   "you must provide 2 values for the early interval, and 2 for the late interval."
                   "You can use the 'comp_mass_loss_glb_pk()' function from the 'analysis_tools.py' file to approximate these values.")
        panes = 1
    else:
        raise f"Approach: {approach} has not been defined, please provide either 1 or 2 as input. (int)"

    domain_snapshot_container = np.zeros((panes, rg_param, ry_param), dtype=np.float64)
    domain_center_snapshot_container = np.zeros([panes], dtype=np.float64)
    sim_time_container = np.zeros([panes], dtype=np.float64)
    mfpt_container = np.zeros([panes], dtype=np.float64)
    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)

    ant.comp_diffusive_snapshots(rg_param, ry_param, w_param, w_param, v_param, N_param, diff_layer, adv_layer,
                                 domain_snapshot_container, domain_center_snapshot_container, sim_time_container,
                                 approach,
                                 time_point_container=time_point_container, compute_mfpt=compute_mfpt,
                                 mfpt_container=mfpt_container)

    if verbose:
        print(f"Values from within the center snapshot container: {domain_snapshot_container}")

    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    data_filepath = tb.create_directory(filepath, current_time)

    microtubule_count = len(N_param)

    for i in range(panes):
        if verbose:
            print(f"Looking at pane {i}")

        if compute_mfpt:
            mfpt = mfpt_container[i]
        else:
            mfpt = None

        if output_csv:
            csv_filename = f"density_snapshot_V={v_param}_W={w_param}_N={microtubule_count}_Domain={rg_param}x{ry_param}.csv"
            output_csv_location = os.path.join(data_filepath, csv_filename)
            df = pd.DataFrame(domain_snapshot_container[i])
            df.to_csv(output_csv_location, header=False, index=False)

        if topological:
            produce_3D_heatmap_tool(domain_snapshot_container[i], domain_center_snapshot_container[i],
                                    toggleBorder, w_param, v_param, len(N_param), data_filepath, colorScheme, save_png,
                                    approach=int(approach), pane=i, mfpt=mfpt, duration=sim_time_container[i])
        else:
            produce_heatmap_tool(domain_snapshot_container[i], domain_center_snapshot_container[i],
                                 toggleBorder, w_param, v_param, len(N_param), data_filepath,
                                 save_png=save_png, show_plot=show_plot, approach=int(approach), pane=i,
                                 mfpt=mfpt, duration=sim_time_container[i], log_scale=log_scale)
        if verbose:
            if save_png:
                print(f"File saved at: {data_filepath}")
        time.sleep(3)


def produce_heatmap_tool(diffusive_layer, diffusive_layer_center, toggle_border, w, v, MT_count, filepath,
                         color_scheme='viridis',
                         save_png=False, show_plot=True, transparent=False, approach=None, pane=None, mfpt=None,
                         duration=None,
                         log_scale=True):  # Add log_scale toggle

    # Include the center value as the first "ring" in the polar heatmap
    diffusive_layer_center = np.full((1, diffusive_layer.shape[1]), diffusive_layer_center)  # Expand the center value
    full_diffusive_layer = np.vstack([diffusive_layer_center, diffusive_layer])

    rings = full_diffusive_layer.shape[0]
    rays = full_diffusive_layer.shape[1]

    r = np.linspace(0, 1, rings + 1)
    theta = np.linspace(0, 2 * np.pi, rays + 1)

    R, Theta = np.meshgrid(r, theta)
    X, Y = R * np.cos(Theta), R * np.sin(Theta)

    plt.figure(figsize=(8, 10))
    cmap = cm.get_cmap(color_scheme, 512)

    if log_scale:
        log_min, log_max = 10 ** -7, 10 ** 0
        boundaries = [0] + list(np.logspace(np.log10(log_min), np.log10(log_max), num=512))
        norm = BoundaryNorm(boundaries, ncolors=cmap.N, clip=True)
    else:
        norm = Normalize(vmin=full_diffusive_layer.min(), vmax=full_diffusive_layer.max())

    if toggle_border:
        heatmap = plt.pcolormesh(X, Y, full_diffusive_layer.T, shading='flat', cmap=cmap, norm=norm, edgecolors='k',
                                 linewidth=0.01)
    else:
        heatmap = plt.pcolormesh(X, Y, full_diffusive_layer.T, shading='flat', cmap=cmap, norm=norm)

    cbar = plt.colorbar(heatmap, location='bottom', pad=0.08)

    if log_scale:
        cbar_ticks = [0] + list(np.logspace(-7, 0, num=8)[1:])
        cbar.set_ticks(cbar_ticks)
        cbar.set_ticklabels([f'0' if tick == 0 else f'$10^{{{int(np.log10(tick))}}}$' for tick in cbar_ticks])
    else:
        cbar.set_ticks(np.linspace(full_diffusive_layer.min(), full_diffusive_layer.max(), num=8))
        cbar.set_ticklabels(
            [f'{tick:.3f}' for tick in np.linspace(full_diffusive_layer.min(), full_diffusive_layer.max(), num=8)])

    cbar.ax.tick_params(labelsize=12, labelcolor='black')

    title = f'N={MT_count}, w={w:.2e}, v={v}'

    if mfpt is not None:
        title += f', MFPT={mfpt:.3f}'
    if duration is not None:
        title += f', T={duration:.3f}'
    if pane is not None:
        title += f', pane={pane}'

    if approach is not None:
        if approach != 1 and approach != 2:
            raise ValueError(f"Approach {approach} doesn't exist, must use either approach 1 or 2 (int value)")
        else:
            title += f', approach={approach}'

    plt.title(title, fontdict={'weight': 'bold', 'font': 'Times New Roman', 'size': 20}, pad=20)

    plt.axis('off')

    if save_png:
        if filepath:
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"N={MT_count}_w={w}_MxN={rings}x{rays}_data{current_time}"
            if approach is not None:
                filename += f"_app={approach}"
            filename += f'_pane={pane}'
            file = os.path.join(filepath, filename + ".png")
            plt.savefig(file, bbox_inches='tight', transparent=transparent)
    if show_plot:
        plt.show()
    plt.close()


def produce_3D_heatmap_tool(diffusive_layer, diffusive_layer_center, toggle_border, w, v, MT_count, filepath,
                            color_scheme='viridis', save_png=False, show_plot=True, transparent=False,
                            approach=None, pane=None, mfpt=None, duration=None, log_scale=True):
    """
    Produces a 3D topological density plot with angular and radial positions as the first two dimensions
    and density as the third (Z-axis).

    Parameters:
    - diffusive_layer (numpy array): The density values in a radial grid.
    - diffusive_layer_center (float): The central density value.
    - toggle_border (bool): Toggle borders on the plot.
    - w, v, MT_count: Parameters for title annotations.
    - filepath (str): Directory to save the image.
    - color_scheme (str): Colormap for visualization.
    - save_png (bool): Whether to save the plot as a PNG.
    - show_plot (bool): Whether to display the plot.
    - transparent (bool): Save PNG with transparency.
    - approach, pane, mfpt, duration: Additional metadata for the title.
    - log_scale (bool): Whether to use a logarithmic scale.
    """

    # Include the center value as the first "ring" in the polar heatmap
    diffusive_layer_center = np.full((1, diffusive_layer.shape[1]), diffusive_layer_center)
    full_diffusive_layer = np.vstack([diffusive_layer_center, diffusive_layer])

    rings = full_diffusive_layer.shape[0]
    rays = full_diffusive_layer.shape[1]

    # Generate radial and angular grid
    r = np.linspace(0, 1, rings)
    theta = np.linspace(0, 2 * np.pi, rays)

    R, Theta = np.meshgrid(r, theta)
    X, Y = R * np.cos(Theta), R * np.sin(Theta)
    Z = full_diffusive_layer.T  # Density values

    # Apply log scale or normalization
    if log_scale:
        norm = LogNorm(vmin=np.max([1e-7, Z.min()]), vmax=Z.max())  # Avoid log(0)
    else:
        norm = Normalize(vmin=Z.min(), vmax=Z.max())

    # Set up figure and 3D axis
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the surface
    cmap = cm.get_cmap(color_scheme, 512)
    surf = ax.plot_surface(X, Y, Z, cmap=cmap, norm=norm, edgecolor='k' if toggle_border else 'none')

    # Add color bar
    cbar = fig.colorbar(surf, shrink=0.5, aspect=10)
    cbar.ax.tick_params(labelsize=12, labelcolor='black')

    # Title
    title = f'N={MT_count}, w={w:.2e}, v={v}'
    if mfpt is not None:
        title += f', MFPT={mfpt:.3f}'
    if duration is not None:
        title += f', T={duration:.3f}'
    if pane is not None:
        title += f', pane={pane}'
    if approach is not None:
        if approach not in [1, 2]:
            raise ValueError(f"Approach {approach} doesn't exist, must use either 1 or 2")
        title += f', approach={approach}'

    ax.set_title(title, fontdict={'weight': 'bold', 'fontsize': 16}, pad=20)

    # Axis labels
    ax.set_xlabel('X-axis (Cosine Projection)', fontsize=12)
    ax.set_ylabel('Y-axis (Sine Projection)', fontsize=12)
    ax.set_zlabel('Density', fontsize=12)

    # Hide axes for a cleaner visualization
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    # Save plot if required
    if save_png and filepath:
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"N={MT_count}_w={w}_MxN={rings}x{rays}_data{current_time}"
        if approach is not None:
            filename += f"_app={approach}"
        filename += f'_pane={pane}.png'
        plt.savefig(os.path.join(filepath, filename), bbox_inches='tight', transparent=transparent)

    if show_plot:
        plt.show()
    else:
        plt.close()
