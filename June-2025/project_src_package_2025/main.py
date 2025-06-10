import sys
import os
from datetime import datetime
from contextlib import redirect_stdout

from data_visualization import animation_functions as ani, plot_functions as plt
from computational_tools import analysis_tools as an
from computational_tools import analysis_tools as ant, numerical_tools as num, supplements as sup, error_analysis as err
from auxiliary_tools import unit_conversion_functions as uni
from auxiliary_tools import format_conversion as form
from system_configuration import file_paths as fp
from launch_functions import launch


def run_main():

    x16_d0 = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\results\\6-10-2025\\MFPT-saturation-analysis-d_tube=0\\16x16\\MFPT_N=4_v=1_T=5_16x16_6-10-2025.csv"
    x16 = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\results\\6-7-2025\\MFPT-saturation-analysis\\16x16\\MFPT_N=4_v=1_T=5_16x16_6-7-2025.csv"

    x32_d0 = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\results\\6-10-2025\\MFPT-saturation-analysis-d_tube=0\\32x32\\MFPT_N=4_v=1_T=5_32x32_6-10-2025.csv"
    x32 = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\results\\6-7-2025\\MFPT-saturation-analysis\\32x32\\MFPT_N=4_v=1_T=5_32x32_6-7-2025.csv"

    x48_d0 = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\results\\6-10-2025\\MFPT-saturation-analysis-d_tube=0\\48x48\\MFPT_N=4_v=1_T=5_48x48_6-10-2025.csv"
    x48 = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\results\\6-7-2025\\MFPT-saturation-analysis\\48x48\\MFPT_N=4_v=1_T=5_48x48_6-7-2025.csv"

    x64_d0 = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\results\\6-10-2025\\MFPT-saturation-analysis-d_tube=0\\64x64\\MFPT_N=4_v=1_T=5_64x64_6-10-2025.csv"
    x64 = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\results\\6-7-2025\\MFPT-saturation-analysis\\64x64\\MFPT_N=4_v=1_T=5_64x64_6-7-2025.csv"

    # plt.plot_general(file_list, labels, "W", "MFPT", "MFPT(W) N=4 V=-1 T=5", fp.general_output, xlog=True, ylog=True, dynamic_pts=False, save_png=True)
    err.compute_percent_diff(x64_d0, x64, fp.general_output, "W", "MFPT(d=0)", "MFPT(d=0.01)", output_filename="64x64_%diff_6_10_25.csv")


if __name__ == "__main__":

    today_str = datetime.now().strftime("%Y-%m-%d")

    log_dir = os.path.join(os.getcwd(), fp.rect_logs)

    output_filename = os.path.join(log_dir, f"output_{today_str}.txt")

    class Tee:
        def __init__(self, *streams):
            self.streams = streams

        def write(self, data):
            for s in self.streams:
                s.write(data)

        def flush(self):
            for s in self.streams:
                s.flush()


    with open(output_filename, "w") as f:
        tee = Tee(sys.stdout, f)
        with redirect_stdout(tee):
            run_main()
