from . import np
from . import sup
from . import num
from . import plt
from . import njit
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
from matplotlib import cm
from matplotlib.colors import Normalize
from . import sys
from time import perf_counter

ENABLE_JIT = sys.ENABLE_NJIT


def evolve_layers_for_animation(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer, T,
                                r=1.0, d=1.0, d_tube=-1):
    # Set up geometry
    d_radius = r / rings
    d_theta = ((2 * np.pi) / rays)
    d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / (2 * d)
    K = int(np.floor(T / d_time))

    phi_center = 1 / (np.pi * (d_radius * d_radius))

    d_list = []

    if d_tube < 0:
        d_tube = sup.solve_d_rect(1, rings, rays, sup.j_max_bef_overlap(rays, tube_placements), 0)

    for m in range(rings):
        j_max = np.ceil((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
        keys = sup.mod_range_flat(tube_placements, j_max, rays, False)
        dict_ = sup.dict_gen(keys, tube_placements)
        d_list.append(dict_)

    for k in range(K):
        m = 0
        aIdx = 0

        while m < rings:
            n = 0
            while n < rays:
                if m == rings - 1:
                    diffusive_layer[1][m][n] = 0
                else:
                    if n in d_list[m]:
                        diffusive_layer[1][m][n] = num.u_density_rect(diffusive_layer, 0, m, n, d_radius, d_theta,
                                                                      d_time, phi_center, rings, advective_layer,
                                                                      int(d_list[m][n]), a, b, d_tube)
                    else:
                        diffusive_layer[1][m][n] = num.u_density(diffusive_layer, 0, m, n, d_radius, d_theta,
                                                                 d_time, phi_center, rings, advective_layer,
                                                                 aIdx, a, b, tube_placements)
                    if n == tube_placements[aIdx]:
                        advective_layer[1][m][n] = num.u_tube_rect(advective_layer, diffusive_layer, 0, m, n, a,
                                                                   b, v, d_time, d_radius, d_theta, d_tube)
                        if aIdx < len(tube_placements) - 1:
                            aIdx += 1
                n += 1
            m += 1

        # Swap & update
        phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center,
                                  advective_layer, tube_placements, v)
        num.update_layer_inplace(diffusive_layer[0], diffusive_layer[1], rays, rings)
        num.update_layer_inplace(advective_layer[0], advective_layer[1], rays, rings)

        yield diffusive_layer[0].copy(), advective_layer[0].copy(), phi_center, k * d_time


@njit(nopython=ENABLE_JIT)
def collect_stamps_for_animation(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer, K,
                                 r=1.0, d=1.0, d_tube=-1):
    d_radius = r / rings
    d_theta = ((2 * np.pi) / rays)
    d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / (2 * d)

    phi_center = 1 / (np.pi * (d_radius * d_radius))

    d_list = []

    if d_tube < 0:
        d_tube = sup.solve_d_rect(1, rings, rays, sup.j_max_bef_overlap(rays, tube_placements), 0)

    for m in range(rings):
        j_max = np.ceil((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
        keys = sup.mod_range_flat(tube_placements, j_max, rays, False)
        dict_ = sup.dict_gen(keys, tube_placements)
        d_list.append(dict_)

    for k in range(K - 1):
        m = 0
        aIdx = 0

        while m < rings:
            n = 0
            while n < rays:
                if m == rings - 1:
                    diffusive_layer[k + 1][m][n] = 0
                else:
                    if n in d_list[m]:
                        diffusive_layer[k + 1][m][n] = num.u_density_rect(diffusive_layer, k, m, n, d_radius, d_theta,
                                                                          d_time, phi_center, rings, advective_layer,
                                                                          int(d_list[m][n]), a, b, d_tube)
                    else:
                        diffusive_layer[k + 1][m][n] = num.u_density(diffusive_layer, k, m, n, d_radius, d_theta,
                                                                     d_time, phi_center, rings, advective_layer,
                                                                     aIdx, a, b, tube_placements)
                    if n == tube_placements[aIdx]:
                        advective_layer[k + 1][m][n] = num.u_tube_rect(advective_layer, diffusive_layer, k, m, n, a,
                                                                       b, v, d_time, d_radius, d_theta, d_tube)
                        if aIdx < len(tube_placements) - 1:
                            aIdx += 1
                n += 1
            m += 1

        phi_center = num.u_center(diffusive_layer, k, d_radius, d_theta, d_time, phi_center,
                                  advective_layer, tube_placements, v)

    return diffusive_layer, advective_layer, phi_center


def animate_diffusion(
        rings, rays, diffusive_layer_gen,
        interval_ms=1, steps_per_frame=10,
        color_scheme='viridis'
):
    # Create polar grid
    r = np.linspace(0, 1, rings + 1)  # rings+1 edges
    theta = np.linspace(0, 2 * np.pi, rays + 1)  # rays+1 edges
    R, Theta = np.meshgrid(r, theta)
    X, Y = R * np.cos(Theta), R * np.sin(Theta)

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), subplot_kw=dict(polar=True))
    fig.suptitle("Real-Time Diffusion/Advection Animation", fontsize=16)

    # Create placeholder data using the same logic as produce_heatmap_tool_rect
    empty_layer = np.zeros((1, rays))  # single central patch row
    layer_base = np.zeros((rings - 1, rays))  # placeholder for remaining rings
    full_diff = np.vstack([empty_layer, layer_base])
    full_diff_T = full_diff.T

    cmap = cm.get_cmap(color_scheme, 512)
    norm = Normalize(vmin=0, vmax=1)

    # pcolormesh expects C.shape == (rays, rings), which matches full_diff_T
    heatmap1 = ax1.pcolormesh(X, Y, full_diff_T, shading='flat', cmap=cmap, norm=norm)
    heatmap2 = ax2.pcolormesh(X, Y, full_diff_T, shading='flat', cmap='plasma', norm=norm)

    def update(frame):
        for _ in range(steps_per_frame):
            try:
                diff_layer, adv_layer, phi_center, t = next(diffusive_layer_gen)
            except StopIteration:
                return heatmap1, heatmap2

        # Compose full layer: add center row
        center_row = np.full((1, diff_layer.shape[1]), phi_center)
        full_diff = np.vstack([center_row, diff_layer])
        full_adv = np.vstack([center_row, adv_layer])

        # Transpose to match heatmap grid shape: (rays, rings)
        heatmap1.set_array(full_diff.T.ravel())
        heatmap2.set_array(full_adv.T.ravel())

        ax1.set_title(f"Diffusive Layer\nT={t:.3f}")
        ax2.set_title(f"Advective Layer\nT={t:.3f}")
        return heatmap1, heatmap2

    ani = FuncAnimation(fig, update, interval=interval_ms, blit=False)
    plt.show()


def run_realtime_simulation(rg_param, ry_param, w_param, v_param, N_param, K_param):
    advective_layer = np.zeros((K_param, rg_param, ry_param), dtype=np.float64)
    diffusive_layer = np.zeros((K_param, rg_param, ry_param), dtype=np.float64)

    diff, adv, central = collect_stamps_for_animation(rg_param, ry_param, w_param, w_param, v_param, N_param, diffusive_layer, advective_layer, 0)

    estimated_memory = K_param * rg_param * ry_param * 8

    print(f"Memory expenditure/footprint: {estimated_memory} bytes = {(estimated_memory / 10**7)}% of a GB")

    start = perf_counter()
    diff, adv, central = collect_stamps_for_animation(rg_param, ry_param, w_param, w_param, v_param, N_param, diffusive_layer, advective_layer, K_param)
    end = perf_counter()

    print(f"{end - start:.5f}")

    # generator = evolve_layers_for_animation(rg_param, ry_param, w_param, w_param, v_param, N_param, diffusive_layer,
    #                                         advective_layer, T_param)
    # animate_diffusion(rg_param, ry_param, generator)
