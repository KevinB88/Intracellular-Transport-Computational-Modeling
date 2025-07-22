import pandas as pd

from . import plt, os, np, datetime, cm, BoundaryNorm, Normalize, fp, ant, sup, tb, exc
from matplotlib.patches import Polygon
from matplotlib.collections import LineCollection
import time
import math


def generate_heatmaps(rg_param, ry_param, w_param, v_param, N_param, approach=2,
                      filepath=fp.heatmap_output, time_point_container=None, save_png=True, show_plot=False,
                      compute_mfpt=False, verbose=False, output_csv=False, rect_config=False,
                      d_tube=-1, r=1.0, d=1.0, mass_retention_threshold=0.01, mass_checkpoint=10 ** 6,
                      color_scheme='viridis',
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
            raise "Time point container must be non empty for collection approach #2."
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
            print(j_max_list)
            produce_heatmap_tool_rect(domain_snapshot_container[i], domain_center_snapshot_container[i],
                                      toggle_border, w_param, v_param, len(N_param), data_filepath, color_scheme,
                                      save_png,
                                      show_plot, approach=int(approach), pane=i, MFPT=MFPT, duration=duration,
                                      time_point=time_point,
                                      extraction_angle_list=N_param, boundary_of_extraction_list=j_max_list,
                                      display_extraction=display_extraction)

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
    # norm = Normalize(vmin=0, vmax=1)

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
                len(boundary_of_extraction_list) == rings - 1):

            ax = plt.gca()
            overlay_color = exc.extraction_overlay_colors.get(color_scheme, (0.5, 0.5, 0.5, 0.15))
            faint_color = (overlay_color[0], overlay_color[1], overlay_color[2], 0.08)

            for ring_idx in range(1, rings):
                angular_spread = boundary_of_extraction_list[ring_idx - 1]
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
                        color = faint_color if angular_spread == 0 else overlay_color
                        patch = Polygon(verts, closed=True, facecolor=color, edgecolor='black', linewidth=1.0)
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


def display_domain_grid(rings, rays, microtubules, d_tube, r=1, display_extract=True, toggle_border=True):

    j_max_list = []

    j_max_lim = sup.j_max_bef_overlap(rings, microtubules)
    max_d_tube = sup.solve_d_rect(r, rings, rays, j_max_lim, 0)

    microtubules = list(np.unique(microtubules))

    while d_tube < 0 or d_tube > max_d_tube:
        d_tube = float(
            input(f"Select d_tube within the range: [0, {max_d_tube}] to avoid DL extraction region overlap: "))

    d_radius = r / rings
    d_theta = ((2 * math.pi) / rays)

    for m in range(rings):
        j_max = math.ceil((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
        j_max_list.append(j_max)

    return build_domain_grid(rings, rays, j_max_list, microtubules, display_extract, toggle_border, max_d_tube)


def build_domain_grid(rings, rays, boundary_of_extraction_list=None,
                      extraction_angle_list=None, display_extraction=False, toggle_border=True, d_sup=0):

    assert isinstance(rings, int) and rings > 0
    assert isinstance(rays, int) and rays > 0
    assert (not display_extraction) or (
        boundary_of_extraction_list is not None
        and extraction_angle_list is not None
        and len(boundary_of_extraction_list) == rings)

    # +1 for including center, +1 for boundary edge
    r = np.linspace(0, 1, rings + 2)
    theta = np.linspace(0, 2 * np.pi, rays + 1)
    R, Theta = np.meshgrid(r, theta)
    X, Y = R * np.cos(Theta), R * np.sin(Theta)

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'aspect': 'equal'})

    ax.set_title(f"Discretized Polar Grid Preview: {rings}x{rays} N={len(extraction_angle_list)} d_sup={d_sup:.5f}")

    # Base greyscale grid (used only as placeholder shading)
    C = np.zeros((theta.shape[0]-1, r.shape[0]-1))

    if toggle_border:
        pcm = ax.pcolormesh(X, Y, C, shading='flat', cmap='Greys', edgecolors='k', linewidth=0.1)
    else:
        pcm = ax.pcolormesh(X, Y, C, shading='flat', cmap='Greys', edgecolors='k', linewidth=0)

    center_radius = r[1]
    # center_circle = plt.Circle((0, 0), radius=(center_radius - 0.0004), color='white', zorder=10)
    center_circle = plt.Circle(
        (0, 0),
        center_radius,
        facecolor='white',
        edgecolor='black',  # Border color
        linewidth=1.2,  # Border thickness
        zorder=10  # Ensure it overlays everything
    )
    ax.add_patch(center_circle)

    ax.axis('off')

    # Red outer boundary edges (absorbing boundary)
    for i in range(rays):
        t1, t2 = theta[i], theta[i + 1]
        r1, r2 = r[-2], r[-1]
        verts = [
            (r1 * np.cos(t1), r1 * np.sin(t1)),
            (r2 * np.cos(t1), r2 * np.sin(t1)),
            (r2 * np.cos(t2), r2 * np.sin(t2)),
            (r1 * np.cos(t2), r1 * np.sin(t2))
        ]
        patch = Polygon(verts, closed=True, facecolor='none', edgecolor='red', linewidth=1.5)
        ax.add_patch(patch)

    # Extraction overlays (only until before absorbing ring)
    if display_extraction:
        overlay_color = (0.6, 0.2, 0.2, 0.3)
        for ring_idx in range(rings - 1):  # exclude last ring (absorbing)
            angular_spread = boundary_of_extraction_list[ring_idx]
            r1, r2 = r[ring_idx + 1], r[ring_idx + 2]
            for angle_center in extraction_angle_list:
                for offset in range(-angular_spread, angular_spread + 1):
                    angle_idx = (angle_center + offset) % rays
                    t1 = theta[angle_idx]
                    t2 = theta[(angle_idx + 1) % rays]
                    verts = [
                        (r1 * np.cos(t1), r1 * np.sin(t1)),
                        (r2 * np.cos(t1), r2 * np.sin(t1)),
                        (r2 * np.cos(t2), r2 * np.sin(t2)),
                        (r1 * np.cos(t2), r1 * np.sin(t2))
                    ]
                    patch = Polygon(verts, closed=True, facecolor=overlay_color,
                                    edgecolor='black', linewidth=0.8)
                    ax.add_patch(patch)

    # Microtubules (green radial lines at specified angular indices)
    for angle_idx in extraction_angle_list or []:
        # angle = 0.5 * (theta[angle_idx] + theta[(angle_idx + 1) % rays])  # center of conic region

        r_start = r[1]
        r_end = r[-2]  # last valid ring before absorbing boundary

        angle = 0.5 * (theta[angle_idx] + theta[(angle_idx + 1) % rays])  # center of conic region
        x1, y1 = r_start * np.cos(angle), r_start * np.sin(angle)

        # Get angular endpoints of the conic wedge
        t1 = theta[angle_idx]
        t2 = theta[(angle_idx + 1) % rays]

        # Compute the *polygonal* endpoints of the absorbing ring arc
        xA, yA = r_end * np.cos(t1), r_end * np.sin(t1)
        xB, yB = r_end * np.cos(t2), r_end * np.sin(t2)

        # Take the midpoint between those endpoints — this lies *on the polygonal arc*
        x2, y2 = 0.5 * (xA + xB), 0.5 * (yA + yB)

        ax.plot([x1, x2], [y1, y2], color='green', linewidth=3)

    plt.tight_layout()
    # plt.show()
    return fig
