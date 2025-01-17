from . import mfpt_comp, sup, datetime, tb, fp, mp, config, partial


'''
    ind_param:  independent parameter: the value that remains static across all MFPT solutions
    dep_param:  dependent parameter(s) : value that is being tested for MFPT dependence (contained within a set)
'''


def solve_mfpt_multi_process(N_param, rg_param, ry_param, dep_type, ind_param, dep_param):
    M = rg_param
    N = ry_param

    if dep_type == "W":
        w_param = dep_param
        v_param = ind_param
    elif dep_type == "V":
        v_param = dep_param
        w_param = ind_param
    else:
        raise f"{dep_type} not yet defined, must use either V or W"

    mfpt, duration = solve_mfpt(rg_param, ry_param, N_param, v_param, w_param, True)

    print(f"MxN={M}x{N}    Duration (sim time) : {duration}    Microtubule configuration: {N_param}"
          f"    W: {w_param}    V: {v_param}")

    if dep_type == "W":
        return {f'W: {w_param}', f'MFPT: {mfpt}'}
    elif dep_type == "V":
        return {f'V: {w_param}', f'MFPT: {mfpt}'}


def parallel_process_mfpt(N_list, rg_param, ry_param, dep_type, ind_type, ind_param, dep_list, cores=None):

    dep_type = dep_type.upper()
    if dep_type != "W" and dep_type != "V":
        raise(f"{dep_type} is an undefined dependent parameter. The current available "
              f"dependent parameters are Switch Rate (W), and Velocity (V)")

    print(f"{dep_type} list: {dep_list}")

    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    data_filepath = tb.create_directory(fp.general_output, current_time)

    if cores is not None and cores > 0:
        core_count = min(cores, config.core_amount)
    else:
        core_count = config.core_amount

    for n in range(len(N_list)):
        with mp.Pool(processes=core_count) as pool:
            mfpt_results = pool.map(partial(solve_mfpt_multi_process, N_list[n],
                                            rg_param, ry_param, dep_type, ind_param), dep_list)
        print(mfpt_results)
        tb.produce_csv_from_xy(mfpt_results, dep_type, "MFPT", data_filepath,
                               f'MFPT_Results_N={len(N_list[n])}_{ind_type}={ind_param}_')


def solve_mfpt(rg_param, ry_param, N_param, v_param, w_param, return_duration=False):
    diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)
    mfpt, duration = mfpt_comp.comp_mfpt_by_mass_loss(rg_param, ry_param, w_param, w_param,
                                                      v_param, N_param, diff_layer, adv_layer)
    if return_duration:
        return mfpt, duration
    else:
        return mfpt





