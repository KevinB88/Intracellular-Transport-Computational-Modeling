import multiprocessing
from gui_components import main_gui as gui
from launch_functions import launch
from computational_tools import numerical_tools as num

def run_main():
    gui.run_app()


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    # print(launch.solve_mfpt_mass_(16, 16, [0, 4, 8, 12], 1, 1))
    run_main()


"""
    Tasks:
        1) Adjust the user visibility of the GUI.
        2) Include submenu for determining an approach for certain methods:
            Submenus for approach 1 and approach 2: 
                phi-v-theta, phi/rho v radius, full-analysis, MFPT computation
"""


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

