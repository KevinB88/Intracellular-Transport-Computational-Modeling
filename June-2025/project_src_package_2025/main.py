import sys
import os
from datetime import datetime
from contextlib import redirect_stdout
from project_src_package_2025.gui_components import main_gui as gui
from project_src_package_2025.launch_functions import launch
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
    launch.launch_super_comp_I(rg_param, ry_param, w_param, v_param, T_param, N_param)


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

