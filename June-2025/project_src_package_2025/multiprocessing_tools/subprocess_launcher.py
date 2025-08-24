import os
import subprocess


def launch_subprocess(args):

    project_root = "/Users/kbedoya88/Desktop/QC25-Summer/Research/Computational-Biophysics/Comp-Bio-Summer/June-2025"
    env = os.environ.copy()

    return subprocess.Popen(
        args,
        cwd=project_root,
        env=env
    )


if __name__ == "__main__":
    from multiprocessing_tools.compute_worker import compute_and_send
    import sys
    import json

    computation_name = sys.argv[1]
    inputs = json.loads(sys.argv[2])
    compute_and_send(computation_name, inputs)
