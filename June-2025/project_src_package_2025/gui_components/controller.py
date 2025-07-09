# GUI_components/controller.py

import ast
import os
from . import launch
from multiprocessing import Process


COMPUTATION_FUNCTIONS = {
    "Solve MFPT": launch.solve_mfpt_,
    "Time Until Mass Depletion": launch.output_time_until_mass_depletion,
    "Phi Angular Dependence": launch.collect_phi_ang_dep,
    "Density Radial Dependence": launch.collect_density_rad_depend,
    "Mass Analysis": launch.collect_mass_analysis
}


def parse_input(value):
    """
    Attempts to convert a string input into its appropriate Python type.
    Supports float, int, bool, list, None, etc.
    """
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value.strip()


def run_selected_computation(computation_name, param_dict):
    """
    Dispatches the selected computation function with the parsed parameters.
    Returns whatever the backend function returns, formatted into a consistent output.
    """
    if computation_name not in COMPUTATION_FUNCTIONS:
        raise ValueError(f"Unknown computation: {computation_name}")

    func = COMPUTATION_FUNCTIONS[computation_name]

    # Parse inputs
    parsed_inputs = {
        key: parse_input(val)
        for key, val in param_dict.items()
        if val.strip() != ""
    }

    result = func(**parsed_inputs)

    # --- Case 1: Solve MFPT ---
    if computation_name == "Solve MFPT":
        output = {}
        if isinstance(result, tuple):
            output["MFPT"] = result[0]
            output["duration"] = result[1]
        elif isinstance(result, dict):
            output["MFPT"] = result.get("MFPT")
            if "duration" in result and isinstance(result["duration"], (int, float)):
                output["duration"] = result["duration"]
        else:
            output["MFPT"] = result
        return output

    # --- Case 2: Time Until Mass Depletion ---
    if computation_name == "Time Until Mass Depletion":
        return {"duration": result}

    # --- Case 3: Plot-producing functions (return list of paths) ---
    if computation_name in {
        "Mass Analysis",
        "Density Radial Dependence",
        "Phi Angular Dependence",
    }:
        if isinstance(result, list) and all(isinstance(p, str) for p in result):
            return {"output_dirs": [os.path.dirname(p) for p in result]}
        elif isinstance(result, dict):
            # Backward compatibility if returning a dict of lists
            output = {}
            for key, val in result.items():
                if isinstance(val, list) and all(isinstance(p, str) for p in val):
                    output["output_dirs"] = [os.path.dirname(p) for p in val]
                    break
            return output

    # --- Fallback: return as-is ---
    return result


def _dummy_compile_run():
    try:
        launch.solve_mfpt_(1,1,[0], 0, 0, 0, d_tube=0)
        launch.output_time_until_mass_depletion(1, 1, [0], 0, 0, d_tube=0, mass_threshold=1)
        # a = launch.collect_phi_ang_dep(1, 1, [0], 0, 0, approach=3, m_segment=0, time_point_container=[0], d_tube=0)
        # b = launch.collect_density_rad_depend(1, 1, [0], 0, 0, 0, [0], d_tube=0)
        c = launch.collect_mass_analysis(1, 1,[0],0,0,0,1, d_tube=0, save_png=False, show_plt=False, collect_plots=False)
        print("[Numba Compilation] Compilation complete.")
    except Exception as e:
        print(f"[Numba Compilation] Warning: {e}")


def initiate_compilation():
    p = Process(target=_dummy_compile_run)
    p.start()
    return p
