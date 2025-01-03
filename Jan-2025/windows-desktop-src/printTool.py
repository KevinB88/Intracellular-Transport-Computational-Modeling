import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime


def plt_v_mfpt(filepath, w, N, convg=False, convg_bar=None, discrete=True):
    plt.figure(figsize=(12, 8))
    df = pd.read_csv(filepath)

    if discrete:
        plt.scatter(df['V'], df['MFPT'], linewidth=2)
    else:
        plt.plot(df['V'], df['MFPT'], linewidth=2)

    plt.xlabel('velocity', fontsize=30, fontname='Times New Roman')
    plt.ylabel('MFPT', fontsize=30, fontname='Times New Roman')

    if convg:
        plt.axhline(y=convg_bar, color='red', linestyle='-', linewidth=2, label=f'MFPT={convg_bar}')

    counter = 0
    while w > 1:
        w /= 10
        counter += 1

    if w != 1:
        w_string = rf"{w}x$10^{{{counter}}}$"
    else:
        w_string = rf"$10^{{{counter}}}$"

    plt.legend()
    plt.title(f'MFPT vs Velocity w/params   :   W={w_string}   N={N}', fontsize=20, fontname='Times New Roman')
    plt.show()


def overlap_results(file_list, N_labels, title, filepath=None, save_png=False, show_plt=True, transparent=False, log_scale=False, discrete=True, dest_filename=None):
    plt.figure(figsize=(12, 8))
    for i in range(len(file_list)):
        df = pd.read_csv(file_list[i])
        if discrete:
            plt.scatter(df['V'], df['MFPT'], label=f'{N_labels[i]}', linewidth=(5/(i+1)))
        else:
            plt.plot(df['V'], df['MFPT'], label=f'{N_labels[i]}', linewidth=(5 / (i + 1)))

        if log_scale:
            plt.yscale('log')
            plt.xscale('log')
    plt.xlabel('Velocity', fontsize=25, fontname='Times New Roman')
    plt.ylabel('MFPT', fontsize=25, fontname='Times New Roman')
    plt.title(title, fontsize=40, fontname='Times New Roman')

    plt.xticks(fontsize=20, fontname='Times New Roman')
    plt.yticks(fontsize=20, fontname='Times New Roman')
    plt.legend(fontsize=22, frameon=True, edgecolor='black', loc='best')

    if save_png:
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if filepath:
            if not os.path.exists(filepath):
                os.makedirs(filepath)
                if dest_filename:
                    file = os.path.join(filepath, f'{dest_filename}_data{current_time}.png')
                else:
                    file = os.path.join(filepath, f'{title}_data{current_time}.png')
                print(file)
                plt.savefig(file, bbox_inches='tight', transparent=transparent)
            print(f'Plot saved to {filepath}')
    plt.show()


