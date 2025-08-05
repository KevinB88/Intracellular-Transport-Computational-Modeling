import sys
import os
from gui_components import main_gui as gui


def run_main():

    rg_param = 16
    ry_param = 16
    v_param = 10.0
    w_param = 100
    N_LIST = [0, 4, 8, 12]
    T_param = 2
    T_points = [0.75, 0.5, 0.25]

    gui.run_app()


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

