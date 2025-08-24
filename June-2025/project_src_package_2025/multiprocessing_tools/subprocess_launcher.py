import os
import subprocess


def launch_subprocess(args):

    project_root = "N:\\QueensCollege2025\\research\\computational_biophysics\\remote-clone\\June-2025"
    env = os.environ.copy()

    return subprocess.Popen(
        args,
        cwd=project_root,
        env=env
    )


if __name__ == "__main__":
    from project_src_package_2025.multiprocessing_tools.compute_worker import compute_and_send
    import sys
    import json

    computation_name = sys.argv[1]
    inputs = json.loads(sys.argv[2])
    compute_and_send(computation_name, inputs)
