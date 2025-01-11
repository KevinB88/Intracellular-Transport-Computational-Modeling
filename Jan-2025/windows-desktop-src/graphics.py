import math
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
from matplotlib import cm
from matplotlib.colors import LogNorm, BoundaryNorm


'''
    The diffusive_layer and diffusive_layer_center refer to specific snapshots of the MxN 
    domain. diffusive_layer consists of all phi values for each M,N value within the domain 
    excluding the center phi value, and the diffusive_layer_center obviously refers to the center.
'''


def generate_polar_heatmap(diffusive_layer, diffusive_layer_center, toggle_border, w, v, MT_count, filepath, color_scheme='viridis', save_png=False, show_plot=True):
    # Include the center value as the first "ring" in the polar heatmap
    diffusive_layer_center = np.full((1, diffusive_layer.shape[1]), diffusive_layer_center)  # Expand the center value
    full_diffusive_layer = np.vstack([diffusive_layer_center, diffusive_layer])

    rings = full_diffusive_layer.shape[0]
    rays = full_diffusive_layer.shape[1]

    r = np.linspace(0, 1, rings + 1)
    theta = np.linspace(0, 2 * np.pi, rays + 1)

    R, Theta = np.meshgrid(r, theta)
    X, Y = R * np.cos(Theta), R * np.sin(Theta)

    log_min = 10**-7
    log_max = 10**0

    plt.figure(figsize=(8, 10))
    cmap = cm.get_cmap(color_scheme, 512)

    boundaries = [0] + list(np.logspace(np.log10(log_min), np.log10(log_max), num=512))

    # Use BoundaryNorm with custom boundaries
    norm_zero = BoundaryNorm(boundaries, ncolors=cmap.N, clip=True)

    if toggle_border:
        heatmap = plt.pcolormesh(X, Y, full_diffusive_layer.T, shading='flat', cmap=cmap, norm=norm_zero, edgecolors='k', linewidth=0.01)
    else:
        heatmap = plt.pcolormesh(X, Y, full_diffusive_layer.T, shading='flat', cmap=cmap, norm=norm_zero)

    cbar = plt.colorbar(heatmap, location='bottom', pad=0.08)

    # Set ticks on a log scale between 10^-7 and 10^0, with 8 segments
    cbar_ticks = [0] + list(np.logspace(-7, 0, num=8)[1:])
    cbar.set_ticks(cbar_ticks)

    # Set tick labels as powers of ten
    cbar.set_ticklabels([f'0' if tick == 0 else f'$10^{{{int(np.log10(tick))}}}$' for tick in cbar_ticks])
    cbar.ax.tick_params(labelsize=12, labelcolor='black')

    plt.title(f'N={MT_count}, w={w}, v={v}', fontdict={'weight': 'bold', 'font': 'Times New Roman', 'size': 20}, pad=20)

    plt.axis('off')

    if save_png:
        if filepath:
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            file = os.path.join(filepath, f'N={MT_count}_w={w}_MxN={rings}x{rays}_data{current_time}.png')
            plt.savefig(file, bbox_inches='tight', transparent=True)
    if show_plot:
        plt.show()
