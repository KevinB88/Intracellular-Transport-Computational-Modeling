import matplotlib.pyplot as plt
import os
import pandas as pd
from datetime import datetime


def phi_versus_theta_plot(data_filepath, Velocity, SwitchRate, numMicrotubs, position, approachType, save_png=False,
                          filePath=None):
    data = pd.read_csv(data_filepath, header=None)

    # Prepare the x-axis as column indices starting from 1
    x = range(1, data.shape[1] + 1)

    if approachType == "#1":
        label_container = ["0.675 < m < 0.68", "0.45 < mass_retained < 0.46"
            , " 0.225 < mass_retained < 0.26", "0.015 < mass_retained < 0.02"]
    else:
        label_container = ["early time", "late time"]

    # Plot each row of data
    plt.figure(figsize=(10, 6))
    for i, row in data.iterrows():
        plt.plot(x, row, label=label_container[i])

    # Add labels, legend, and title
    plt.xlabel("Theta")
    plt.ylabel("Phi")
    title = f"Phi versus Theta    V={Velocity}    W={SwitchRate}    N={numMicrotubs}    Approach{approachType}  Position={position}"
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_png:
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if filePath:
            if not os.path.exists(filePath):
                os.makedirs(filePath)
            file = os.path.join(filePath, f'{title}_date{current_time}.png')
            plt.savefig(file, bbox_inches='tight')
            print(f'Plot saved to {filePath}')
    plt.show()


def plot_all_csv_in_directory_manual(file_list, N_labels, filepath, title, save_png=False, show_plt=True,
                                     transparent=False):
    plt.figure(figsize=(12, 8))

    for i in range(len(file_list)):
        df = pd.read_csv(file_list[i])
        plt.scatter(df['W'], df['MFPT'], label=f'{len(N_labels[i])}', linewidth=(10 / (i + 1)))
        plt.yscale('log')
        plt.xscale('log')

    plt.xlabel('W', fontsize=30, fontname='Times New Roman')
    plt.ylabel('MFPT', fontsize=30, fontname='Times New Roman')
    plt.title(title, fontsize=40, fontname='Times New Roman')

    plt.xticks(fontsize=30, fontname='Times New Roman')
    plt.yticks(fontsize=25, fontname='Times New Roman')

    plt.legend(fontsize=22, frameon=True, edgecolor='black', loc='best')
    plt.ylim(10 ** -1, 10 ** 1)

    if save_png:
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if filepath:
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            file = os.path.join(filepath, f'{title}_date{current_time}.png')
            plt.savefig(file, bbox_inches='tight', transparent=transparent)
            print(f'Plot saved to {filepath}')
    plt.show()


def plot_all_csv_in_directory(directory_path, N_labels, filepath, title, save_png=False, show_plt=True,
                              transparent=False):
    plt.figure(figsize=(12, 8))

    i = 0
    for filename in os.listdir(directory_path):

        if filename.endswith('.csv'):
            file_path = os.path.join(directory_path, filename)
            df = pd.read_csv(file_path)

            if 'W' in df.columns and 'MFPT' in df.columns:
                plt.scatter(df['W'], df['MFPT'], label=f'{len(N_labels[i])}', linewidth=(10 / (i + 1)))
                plt.yscale('log')
                plt.xscale('log')
                i += 1

    plt.xlabel('W', fontsize=30, fontname='Times New Roman')
    plt.ylabel('MFPT', fontsize=30, fontname='Times New Roman')
    plt.title(title, fontsize=40, fontname='Times New Roman')

    plt.xticks(fontsize=30, fontname='Times New Roman')
    plt.yticks(fontsize=25, fontname='Times New Roman')

    plt.legend(fontsize=22, frameon=True, edgecolor='black', loc='best')
    plt.ylim(10 ** -1, 10 ** 1)

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
