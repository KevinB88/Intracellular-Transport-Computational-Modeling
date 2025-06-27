# GUI_components/controller.py

import ast
from . import launch


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
    Returns whatever the backend function returns.
    """
    if computation_name not in COMPUTATION_FUNCTIONS:
        raise ValueError(f"Unknown computation: {computation_name}")

    func = COMPUTATION_FUNCTIONS[computation_name]

    parsed_inputs = {
        key: parse_input(val)
        for key, val in param_dict.items()
        if val.strip() != ""
    }

    result = func(**parsed_inputs)
    return result
