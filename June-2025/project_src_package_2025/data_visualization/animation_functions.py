import pandas as pd

from . import plt, os, np, datetime, cm, BoundaryNorm, Normalize, fp, ant, sup, tb
from matplotlib.patches import Polygon
from extraction_colors import extraction_overlay_colors
import time
import math


def generate_heatmaps(rg_param, ry_param, w_param, v_param, N_param, approach=2,
                      filepath=fp.heatmap_output, time_point_container=None, save_png=True, show_plot=False,
                      compute_mfpt=False, verbose=False, output_csv=False, rect_config=False,
                      d_tube=-1, r=1.0, d=1.0, mass_retention_threshold=0.01, mass_checkpoint=10 ** 6, color_scheme='viridis',
                      toggle_border=False, display_extraction=True):
    j_max_list = []
    if rect_config:
        j_max_lim = sup.j_max_bef_overlap(ry_param, N_param)
        max_d_tube = sup.solve_d_rect(r, ry_param, rg_param, j_max_lim, 0)

        while d_tube < 0 or d_tube > max_d_tube:
            d_tube = float(
                input(f"Select d_tube within the range: [0, {max_d_tube}] to avoid DL extraction region overlap: "))

        d_radius = r / rg_param
        d_theta = ((2 * math.pi) / ry_param)

        for m in range(rg_param):
            j_max = math.ceil((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
            j_max_list.append(j_max)

    duration = False
    time_point = -1

    if approach == 1:
        panes = 4
    elif approach == 2:
        if time_point_container is None:
            raise "Time point container must be non empty for collection approach #1."
        panes = len(time_point_container)
        duration = True
    else:
        raise f"Approach: {approach} has not been defined, please provide either 1 or 2 as input. (int)"

    domain_snapshot_container = np.zeros((panes, rg_param, ry_param), dtype=np.float64)
    domain_center_snapshot_container = np.zeros([panes], dtype=np.float64)
    sim_time_container = np.zeros([panes], dtype=np.float64)
    mfpt_container = np.zeros([panes], dtype=np.float64)
    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)

    ant.comp_diffusive_snapshots(rg_param, ry_param, w_param, w_param, v_param, N_param, diff_layer, adv_layer,
                                 domain_snapshot_container,
                                 domain_center_snapshot_container, sim_time_container, approach, r=r, d=d,
                                 mass_retention_threshold=mass_retention_threshold,
                                 time_point_container=time_point_container, compute_mfpt=compute_mfpt,
                                 mfpt_container=mfpt_container, mass_checkpoint=mass_checkpoint,
                                 rect_config=rect_config, d_tube=d_tube)

    if verbose:
        print(f"Values from within the center snapshot container: {domain_snapshot_container}")

    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    if rect_config:
        current_time += "_rect_config"
    else:
        current_time += "_polar_config"

    data_filepath = tb.create_directory(filepath, current_time)

    microtubule_count = len(N_param)

    for i in range(panes):
        if verbose:
            print(f"Looking at pane {i}")

        if compute_mfpt:
            MFPT = mfpt_container[i]
        else:
            MFPT = -1.0

        if output_csv:
            csv_filename = f"density_snapshot_#{i}_V={v_param}_W={w_param}_N={microtubule_count}_D={rg_param}x{ry_param}_.csv"
            output_csv_location = os.path.join(data_filepath, csv_filename)
            df = pd.DataFrame(domain_snapshot_container[i])
            df.to_csv(output_csv_location, header=False, index=False)

        if duration:
            time_point = time_point_container[i]

        if rect_config:
            produce_heatmap_tool_rect(domain_snapshot_container[i], domain_center_snapshot_container[i],
                                      toggle_border, w_param, v_param, len(N_param), data_filepath, color_scheme, save_png,
                                      show_plot, approach=int(approach), pane=i, MFPT=MFPT, duration=duration, time_point=time_point,
                                      extraction_angle_list=N_param, boundary_of_extraction_list=j_max_list, display_extraction=display_extraction)

        else:
            produce_heatmap_tool(domain_snapshot_container[i], domain_center_snapshot_container[i],
                                 toggle_border, w_param, v_param, len(N_param), data_filepath,
                                 save_png=save_png, show_plot=show_plot, approach=int(approach), pane=i,
                                 MFPT=MFPT, duration=duration, time_point=time_point, color_scheme=color_scheme)
        if verbose:
            if save_png:
                print(f"File saved at: {data_filepath}")
        time.sleep(3)


def produce_heatmap_tool(diffusive_layer, diffusive_layer_center, toggle_border, w, v, MT_count, filepath,
                         color_scheme='viridis',
                         save_png=False, show_plot=True, transparent=False, approach=-1, pane=None, MFPT=-1.0,
                         duration=False, time_point=-1.0):
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

    norm = Normalize(vmin=full_diffusive_layer.min(), vmax=full_diffusive_layer.max())

    if toggle_border:
        heatmap = plt.pcolormesh(X, Y, full_diffusive_layer.T, shading='flat', cmap=cmap, norm=norm, edgecolors='k',
                                 linewidth=0.01)
    else:
        heatmap = plt.pcolormesh(X, Y, full_diffusive_layer.T, shading='flat', cmap=cmap, norm=norm)

    cbar = plt.colorbar(heatmap, location='bottom', pad=0.08)

    cbar.set_ticks(np.linspace(full_diffusive_layer.min(), full_diffusive_layer.max(), num=8))
    cbar.set_ticklabels(
        [f'{tick:.3f}' for tick in np.linspace(full_diffusive_layer.min(), full_diffusive_layer.max(), num=8)])

    cbar.ax.tick_params(labelsize=12, labelcolor='black')

    title = f'N={MT_count}, w={w:.2e}, v={v}'

    if MFPT >= 0:
        title += f', MFPT={MFPT:.3f}'
    if duration:
        print(time_point)
        title += f', T={time_point:.3f}'

    plt.title(title, fontdict={'weight': 'bold', 'font': 'Times New Roman', 'size': 20}, pad=20)

    plt.axis('off')

    if save_png:
        if filepath:
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"N={MT_count}_w={w}_MxN={rings}x{rays}_data{current_time}"
            if approach > 0:
                filename += f"_app={approach}"
            filename += f'_pane={pane}'
            file = os.path.join(filepath, filename + ".png")
            plt.savefig(file, bbox_inches='tight', transparent=transparent)
    if show_plot:
        plt.show()
    plt.close()


def produce_heatmap_tool_rect(diffusive_layer, diffusive_layer_center, toggle_border, w, v, MT_count, filepath,
                              color_scheme='viridis',
                              save_png=False, show_plot=True, transparent=False, approach=-1, pane=None, MFPT=-1.0,
                              duration=False, time_point=-1.0,
                              extraction_angle_list=None,
                              boundary_of_extraction_list=None,
                              display_extraction=False):
    diffusive_layer_center = np.full((1, diffusive_layer.shape[1]), diffusive_layer_center)
    full_diffusive_layer = np.vstack([diffusive_layer_center, diffusive_layer])
    rings, rays = full_diffusive_layer.shape

    r = np.linspace(0, 1, rings + 1)
    theta = np.linspace(0, 2 * np.pi, rays + 1)
    R, Theta = np.meshgrid(r, theta)
    X, Y = R * np.cos(Theta), R * np.sin(Theta)

    plt.figure(figsize=(8, 10))
    cmap = cm.get_cmap(color_scheme, 512)
    norm = Normalize(vmin=full_diffusive_layer.min(), vmax=full_diffusive_layer.max())

    if toggle_border:
        heatmap = plt.pcolormesh(X, Y, full_diffusive_layer.T, shading='flat', cmap=cmap, norm=norm, edgecolors='k',
                                 linewidth=0.01)
    else:
        heatmap = plt.pcolormesh(X, Y, full_diffusive_layer.T, shading='flat', cmap=cmap, norm=norm)

    cbar = plt.colorbar(heatmap, location='bottom', pad=0.08)
    ticks = np.linspace(full_diffusive_layer.min(), full_diffusive_layer.max(), num=8)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f'{tick:.3f}' for tick in ticks])
    cbar.ax.tick_params(labelsize=12, labelcolor='black')

    title = f'N={MT_count}, w={w:.2e}, v={v}'
    if MFPT >= 0:
        title += f', MFPT={MFPT:.3f}'
    if duration:
        title += f', T={time_point:.3f}'
    plt.title(title, fontdict={'weight': 'bold', 'font': 'Times New Roman', 'size': 20}, pad=20)
    plt.axis('off')

    if display_extraction:
        if (boundary_of_extraction_list is not None and
                extraction_angle_list is not None and
                len(boundary_of_extraction_list) == rings):
            ax = plt.gca()
            overlay_color = extraction_overlay_colors.get(color_scheme, (0.5, 0.5, 0.5, 0.4))

            for ring_idx in range(rings):
                angular_spread = boundary_of_extraction_list[ring_idx]
                for angle_center in extraction_angle_list:
                    for offset in range(-angular_spread, angular_spread + 1):
                        angle_idx = (angle_center + offset) % rays
                        r1, r2 = r[ring_idx], r[ring_idx + 1]
                        t1, t2 = theta[angle_idx], theta[angle_idx + 1]
                        verts = [
                            (r1 * np.cos(t1), r1 * np.sin(t1)),
                            (r2 * np.cos(t1), r2 * np.sin(t1)),
                            (r2 * np.cos(t2), r2 * np.sin(t2)),
                            (r1 * np.cos(t2), r1 * np.sin(t2))
                        ]
                        patch = Polygon(verts, closed=True, facecolor=overlay_color, edgecolor=None)
                        ax.add_patch(patch)
        else:
            print("[Warning] Extraction overlay skipped due to boundary list mismatch or missing input.")

    if save_png:
        if filepath:
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"N={MT_count}_w={w}_MxN={rings}x{rays}_data{current_time}"
            if approach > 0:
                filename += f"_app={approach}"
            filename += f'_pane={pane}'
            file = os.path.join(filepath, filename + ".png")
            plt.savefig(file, bbox_inches='tight', transparent=transparent)

    if show_plot:
        plt.show()
    plt.close()
