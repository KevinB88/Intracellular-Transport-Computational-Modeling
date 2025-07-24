import sys
import os
from datetime import datetime
from contextlib import redirect_stdout
from project_src_package_2025.gui_components import main_gui as gui
from project_src_package_2025.launch_functions import launch
from project_src_package_2025.auxiliary_tools import validity_checks as val
from project_src_package_2025.system_configuration import file_paths as fp
from multiprocessing import freeze_support
from pathlib import Path


if getattr(sys, 'frozen', False):
    base_dir = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(os.path.dirname(sys.executable))
    project_path = base_dir / 'project_src_package_2025'
    sys.path.insert(0, str(project_path.parent))
else:
    # Development mode
    current = Path(__file__).resolve()
    sys.path.insert(0, str(current.parent.parent))


# dist/Biophysics-app-1.0.app/Contents/MacOS/Biophysics-app-1.0

freeze_support()


def run_main():

    rg_param = 16
    ry_param = 16
    v_param = 10.0
    w_param = 100.0
    N_param = [0, 4, 8, 12]
    T_param = 1.0

    # gui.run_app()
    # launch.launch_super_comp_I(rg_param, ry_param, w_param, v_param, T_param, N_param)
    # launch.collect_mass_analysis(rg_param, ry_param, N_param, v_param, w_param, T_param, 5, save_png=True, show_plt=False)

    adv_super = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\project_src_package_2025\\data_output\\mass_analysis_results\\advective\\08-20_PM_07-22-2025\\MA_AL.csv"
    adv_og = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\project_src_package_2025\\data_output\\mass_analysis_results\\advective\\2025-07-22-20-20-15-original-config\\advective_mass_analysis_V=10.0_W=100.0_16x16_.csv"

    diff_super = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\project_src_package_2025\\data_output\\mass_analysis_results\\diffusive\\08-20_PM_07-22-2025\\MA_DL.csv"
    diff_og = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\project_src_package_2025\\data_output\\mass_analysis_results\\diffusive\\2025-07-22-20-20-15-original-config\\diffusive_mass_analysis_V=10.0_W=100.0_16x16_.csv"

    total_super = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\project_src_package_2025\\data_output\\mass_analysis_results\\total\\08-20_PM_07-22-2025\\MA_total.csv"
    total_og = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\project_src_package_2025\\data_output\\mass_analysis_results\\total\\08-20_PM_07-22-2025\\MA_total.csv"

    adv_o_total_super = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\project_src_package_2025\\data_output\\mass_analysis_results\\advective_over_total\\08-20_PM_07-22-2025\\MA_AL_running_total.csv"
    adv_o_total_og = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\project_src_package_2025\\data_output\\mass_analysis_results\\advective_over_total\\2025-07-22-20-20-15\\advective_over_total_mass_analysis_V=10.0_W=100.0_16x16_.csv"

    adv_o_initial_super = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\project_src_package_2025\\data_output\\mass_analysis_results\\advective_over_initial\\08-20_PM_07-22-2025\\MA_AL_initial_total.csv"
    adv_o_initial_og = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025\\project_src_package_2025\\data_output\\mass_analysis_results\\advective_over_initial\\2025-07-22-20-20-16\\advective_over_initial_mass_analysis_V=10.0_W=100.0_16x16_.csv"

    val.validate_contents(adv_super, adv_og)
    val.validate_contents(diff_super, diff_og)
    val.validate_contents(total_super, total_og)
    val.validate_contents(adv_o_total_super, adv_o_total_og)
    val.validate_contents(adv_o_initial_super, adv_o_initial_og)

    # Include simulation time onto mass analysis csv
    # Clarify which methods are robust and which are experimental/require extensive testing

    '''
        Tasks for the week:
        
        -Remain on standby for results from Ankush (so that I can compare my PDE results with)
        -Fix up the heatplot video, and performance with multiprocessing capabilities (running the GUI on one process, and launching the animation on another)  
        -Complete development on the super function 
        -Complete development of the software package 
        -Test new calc_mass() from numerical_tools.py
        -Develop a function to automate a results comparison (by comparing csvs automatically) 
    '''


if __name__ == "__main__":
    run_main()

    # today_str = datetime.now().strftime("%Y-%m-%d")
    #
    # log_dir = os.path.join(os.getcwd(), fp.rect_logs)
    #
    # os.makedirs(log_dir,  exist_ok=True)
    #
    # output_filename = os.path.join(log_dir, f"output_{today_str}.txt")
    #
    # class Tee:
    #     def __init__(self, *streams):
    #         self.streams = streams
    #
    #     def write(self, data):
    #         for s in self.streams:
    #             s.write(data)
    #
    #     def flush(self):
    #         for s in self.streams:
    #             s.flush()
    #
    #
    # with open(output_filename, "w") as f:
    #     tee = Tee(sys.stdout, f)
    #     with redirect_stdout(tee):
    #         run_main()

