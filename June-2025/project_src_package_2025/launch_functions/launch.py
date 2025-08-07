from . import mfpt_comp, sup, datetime, tb, fp, mp, config, partial, ant, np, os, plt, ani, num, super

from project_src_package_2025.computational_tools import struct_init
from project_src_package_2025.data_processing import data_process_functions as pro
import pandas as pd


# (****) (****)
def collect_phi_ang_dep(rg_param, ry_param, v_param, w_param, T_param, N_LIST, checkpoint_collect_container, approach=2,
                        T_fixed_ring_seg=0.5,
                        d_tube=0.0, domain_radius=1, D=1, mass_retention_threshold=0.01, mass_checkpoint=10 ** 6,
                        save_png=True, show_plt=False):
    if len(N_LIST) > ry_param:
        raise IndexError(
            f'Too many angular indices supplied for microtubule positions: {len(N_LIST)} > {ry_param} (number of angular positions in domain).'
        )

    for i in range(len(N_LIST)):
        if N_LIST[i] < 0 or N_LIST[i] > ry_param:
            raise IndexError(
                f'Angular index: {N_LIST[i]} falls outside of the legal index range: [0,{ry_param - 1}) under ry_param={ry_param}')
    N_LIST.sort()

    if int(approach) != 1 and int(approach) != 2:
        raise ValueError(
            f"Approach: {approach} is undefined. Must supply approach 1 (Mass-point collection) or approach 2 (Time-point collection).")

    if T_fixed_ring_seg < 0 or T_fixed_ring_seg > 1:
        print("T_fixed_ring_seg automatically adjusted to legal range.")
        T_fixed_ring_seg = 0.5

    if approach == 1:
        checkpoint_collect_container.sort(reverse=True)
    elif approach == 2:
        for t in range(len(checkpoint_collect_container)):
            if checkpoint_collect_container[t] < 0.0 or checkpoint_collect_container[t] > T_param:
                raise ValueError(
                    f"Timestamp-point: {checkpoint_collect_container[t]} falls outside of the legal timestamp-point range: [0, {T_param} (T_param) ] (T_param = your input solution time duration)")
            dT = num.compute_dT(rg_param, ry_param, domain_radius=domain_radius, D=D)
            T_param += dT
        checkpoint_collect_container.sort()
    else:
        raise ValueError(
            f'{approach} is not a valid argument, use either collection approach "1" or "2" (must be an int)')

    checkpoint_collect_container = [float(item) for item in checkpoint_collect_container]

    # d_tube_max is with respect to the non-overlapping microtubule extraction region implementation.
    d_tube_max = sup.solve_d_rect(domain_radius, rg_param, ry_param, sup.j_max_bef_overlap(ry_param, N_LIST), 0)

    if d_tube < 0 or d_tube > d_tube_max:
        raise ValueError(f"d_tube: {d_tube} is outside of the legal range: [0, {d_tube_max}")

    collection_stamp_enum = len(checkpoint_collect_container)

    PvT_DL_snapshots = np.zeros((collection_stamp_enum, ry_param), dtype=np.float64)

    D_LAYER, A_LAYER = sup.initialize_layers(rg_param, ry_param)

    ant.comp_diffusive_angle_snapshots(rg_param, ry_param, w_param, w_param, T_param, v_param, N_LIST, D_LAYER, A_LAYER,
                                       PvT_DL_snapshots, checkpoint_collect_container, approach, T_fixed_ring_seg,
                                       d_tube, domain_radius,
                                       D, mass_retention_threshold, mass_checkpoint)

    return pro.process_PvT_DL(PvT_DL_snapshots, v_param, w_param, N_LIST, T_fixed_ring_seg, save_png, show_plt,
                              checkpoint_collect_container, approach)


# (****) (****)
def collect_mass_analysis(rg_param, ry_param, v_param, w_param, T_param, N_LIST, MA_collection_factor=5,
                          domain_radius=1.0, D=1.0,
                          mass_checkpoint=10 ** 6, d_tube=0.0, MA_collection_factor_limit=10 ** 3, save_png=True,
                          show_plt=False):

    if len(N_LIST) > ry_param:
        raise IndexError(
            f'Too many angular indices supplied for microtubule positions: {len(N_LIST)} > {ry_param} (number of angular positions in domain).'
        )

    for i in range(len(N_LIST)):
        if N_LIST[i] < 0 or N_LIST[i] > ry_param:
            raise IndexError(
                f'Angular index: {N_LIST[i]} falls outside of the legal index range: [0,{ry_param - 1}) under ry_param={ry_param}')
    N_LIST.sort()

    d_tube_max = sup.solve_d_rect(domain_radius, rg_param, ry_param, sup.j_max_bef_overlap(ry_param, N_LIST), 0)

    if d_tube < 0 or d_tube > d_tube_max:
        raise ValueError(f"d_tube: {d_tube} is outside of the legal range: [0, {d_tube_max}")

    if MA_collection_factor < 1 or MA_collection_factor > MA_collection_factor_limit:
        print("MA_collection_factor automatically adjusted to legal range.")
        MA_collection_factor = 100

    K = num.compute_K(rg_param, ry_param, T_param, domain_radius, D)
    relative_k = int(np.floor(K / MA_collection_factor))

    D_LAYER, A_LAYER = sup.initialize_layers(rg_param, ry_param)

    MA_DL_timeseries = np.zeros([relative_k], dtype=np.float64)
    MA_AL_timeseries = np.zeros([relative_k], dtype=np.float64)
    MA_ALoT_timeseries = np.zeros([relative_k], dtype=np.float64)
    MA_ALoI_timeseries = np.zeros([relative_k], dtype=np.float64)
    MA_TM_timeseries = np.zeros([relative_k], dtype=np.float64)

    ant.comp_mass_analysis_respect_to_time(rg_param, ry_param, w_param, w_param, v_param, T_param, N_LIST, D_LAYER,
                                           A_LAYER, MA_DL_timeseries, MA_AL_timeseries, MA_ALoI_timeseries,
                                           MA_ALoT_timeseries, MA_TM_timeseries, MA_collection_factor,
                                           relative_k, d_tube, domain_radius, D, mass_checkpoint)

    return pro.process_MA_results(MA_DL_timeseries, MA_AL_timeseries, MA_TM_timeseries, MA_ALoT_timeseries,
                                  MA_ALoI_timeseries,
                                  v_param, w_param, N_LIST, T_param, rg_param, ry_param, save_png, show_plt, MA_collection_factor, domain_radius, D)


# (****) (****)
def launch_super_comp_I(rg_param, ry_param, w_param, v_param, T_param, N_LIST, d_tube=0.0, Timestamp_List=None,
                        MA_collection_factor=5, MA_collection_factor_limit=10 ** 3,
                        D=1.0, domain_radius=1.0, mass_checkpoint=10 ** 6, T_fixed_ring_seg=0.5, R_fixed_angle=-1,
                        save_png=True, save_csv=True, show_plt=False, heat_plot_border=False,
                        heatplot_colorscheme='viridis',
                        display_extraction=True):
    if len(N_LIST) > ry_param:
        raise IndexError(
            f'Too many angular indices supplied for microtubule positions: {len(N_LIST)} > {ry_param} (number of angular positions in domain).'
        )

    for i in range(len(N_LIST)):
        if N_LIST[i] < 0 or N_LIST[i] > ry_param:
            raise IndexError(
                f'Angular index: {N_LIST[i]} falls outside of the legal index range: [0,{ry_param - 1}) under ry_param={ry_param}')
    N_LIST.sort()


    if T_fixed_ring_seg < 0 or T_fixed_ring_seg > 1:
        print("T_fixed_ring_seg automatically adjusted to legal range.")
        T_fixed_ring_seg = 0.5

    if R_fixed_angle < 0 or R_fixed_angle > ry_param - 1:
        print("R_fixed_angle automatically adjusted to legal range.")
        R_fixed_angle = N_LIST[0]

    if MA_collection_factor < 1 or MA_collection_factor > MA_collection_factor_limit:
        print("MA_collection_factor automatically adjusted to legal range.")
        MA_collection_factor = 100

    d_tube_max = sup.solve_d_rect(domain_radius, rg_param, ry_param, sup.j_max_bef_overlap(ry_param, N_LIST), 0)

    if d_tube < 0 or d_tube > d_tube_max:
        raise ValueError(f"d_tube: {d_tube} is outside of the legal range: [0, {d_tube_max}")

    T_param = float(T_param)

    if Timestamp_List is None:
        # Default timestamps
        Timestamp_List = [T_param * 0.25, T_param * 0.5, T_param * 0.75, T_param]
    else:
        Timestamp_List.sort()

    Timestamp_List = [float(item) for item in Timestamp_List]

    for t in range(len(Timestamp_List)):
        if Timestamp_List[t] < 0.0 or Timestamp_List[t] > T_param:
            raise ValueError(
                f"Timestamp-point: {Timestamp_List[t]} falls outside of the legal timestamp-point range: [0, {T_param} (T_param) ] (T_param = your input solution time duration)")

    dT = num.compute_dT(rg_param, ry_param, domain_radius=domain_radius, D=D)
    T_param += dT
    Timestamp_enum = len(Timestamp_List)

    # Initialize mass analysis time series collection containers

    K = T_param / dT
    relative_k = int(np.floor(K / MA_collection_factor))

    MA_DL_timeseries = np.zeros([relative_k], dtype=np.float64)
    MA_AL_timeseries = np.zeros([relative_k], dtype=np.float64)
    MA_TM_timeseries = np.zeros([relative_k], dtype=np.float64)
    MA_ALoT_timeseries = np.zeros([relative_k], dtype=np.float64)
    MA_ALoI_timeseries = np.zeros([relative_k], dtype=np.float64)

    # Initialize Phi v. Theta diffusive layer snapshot container

    PvT_DL_snapshots = np.zeros((Timestamp_enum, ry_param), dtype=np.float64)

    # Initialize Density v. Radius snapshot containers

    PvR_DL_snapshots = np.zeros((Timestamp_enum, rg_param + 1), dtype=np.float64)
    RvR_AL_snapshots = np.zeros((Timestamp_enum, rg_param), dtype=np.float64)

    # Prepare for heatmap collection

    j_max_list = struct_init.build_j_max_list(rg_param, ry_param, N_LIST, d_tube, domain_radius)

    HM_DL_snapshots = np.zeros((Timestamp_enum, rg_param, ry_param), dtype=np.float64)
    HM_C_snapshots = np.zeros([Timestamp_enum], dtype=np.float64)
    MFPT_snapshots = np.zeros([Timestamp_enum], dtype=np.float64)

    # Initialize layers
    D_LAYER, A_LAYER = sup.initialize_layers(rg_param, ry_param)

    # Release the Kraken.. (execute super_comp_type_I)
    super.super_comp_type_I(rg_param, rg_param, w_param, w_param, T_param, v_param, N_LIST, D_LAYER, A_LAYER,
                            Timestamp_List,
                            HM_DL_snapshots, HM_C_snapshots, PvT_DL_snapshots, T_fixed_ring_seg, MA_DL_timeseries,
                            MA_AL_timeseries,
                            MA_ALoI_timeseries, MA_ALoT_timeseries, MA_TM_timeseries, MA_collection_factor, relative_k,
                            PvR_DL_snapshots,
                            RvR_AL_snapshots, R_fixed_angle, MFPT_snapshots, d_tube, D, domain_radius, mass_checkpoint)

    # Process results: Produce CSVs, PNGs (plots and heatmaps) (log results to filepath_log<timestamp>.txt)
    # Parameter chart (relative to the computation) is also included in the result
    # Desired output: a package containing all results categorized by type

    # Processing MFPT results

    MFPT_results = pro.process_MFPT_results(MFPT_snapshots, Timestamp_List, 2, rg_param, ry_param, w_param, v_param, N_LIST, save_png, show_plt)

    # Processing results for Mass-Analysis

    # Diffusive mass analysis
    MA_results = pro.process_MA_results(MA_DL_timeseries, MA_AL_timeseries, MA_TM_timeseries, MA_ALoT_timeseries,
                                        MA_ALoI_timeseries, v_param, w_param, N_LIST, T_param, rg_param, ry_param,
                                        save_png, show_plt)

    # Processing results for Phi v. Theta

    PvT_DL_results = pro.process_PvT_DL(PvT_DL_snapshots, v_param, w_param, N_LIST, T_fixed_ring_seg, save_png,
                                        show_plt, Timestamp_List, 2)

    # Processing results for Phi v. Radius & Rho v. Radius

    DvR_results = pro.process_DvR_results(PvR_DL_snapshots, RvR_AL_snapshots, v_param, w_param, N_LIST, rg_param,
                                          ry_param, R_fixed_angle, Timestamp_List, save_png, show_plt, 2)

    # Processing static heat-plots

    static_HM_results = pro.process_static_HM_results(HM_DL_snapshots, HM_C_snapshots, MFPT_snapshots, Timestamp_List,
                                                      heat_plot_border, w_param, v_param, N_LIST, heatplot_colorscheme,
                                                      save_png, show_plt, j_max_list, display_extraction, 2)

    print("Successfully completed super-function. View results in project_src_package_2025/data_output.")

    output_list = MFPT_results + MA_results + PvT_DL_results + DvR_results + static_HM_results
    return output_list


# (****) (****)
def collect_MFPT_snapshots(rg_param, ry_param, N_LIST, v_param, w_param, T_param, approach, checkpoint_collect_container,
                           domain_radius=1.0, D=1.0, mass_checkpoint=10 ** 6, d_tube=0.0, save_png=True,
                           show_plt=False):
    if len(N_LIST) > ry_param:
        raise IndexError(
            f'Too many angular indices supplied for microtubule positions: {len(N_LIST)} > {ry_param} (number of angular positions in domain).'
        )

    for i in range(len(N_LIST)):
        if N_LIST[i] < 0 or N_LIST[i] > ry_param:
            raise IndexError(
                f'Angular index: {N_LIST[i]} falls outside of the legal index range: [0,{ry_param - 1}) under ry_param={ry_param}')
    N_LIST.sort()

    if approach == 1:
        checkpoint_collect_container.sort(reverse=True)
    elif approach == 2:
        for t in range(len(checkpoint_collect_container)):
            if checkpoint_collect_container[t] < 0.0 or checkpoint_collect_container[t] > T_param:
                raise ValueError(
                    f"Timestamp-point: {checkpoint_collect_container[t]} falls outside of the legal timestamp-point range: [0, {T_param} (T_param) ] (T_param = your input solution time duration)")
            dT = num.compute_dT(rg_param, ry_param, domain_radius=domain_radius, D=D)
            T_param += dT
        checkpoint_collect_container.sort()
    else:
        raise ValueError(
            f'{approach} is not a valid argument, use either collection approach "1" or "2" (must be an int)')

    checkpoint_collect_container = [float(item) for item in checkpoint_collect_container]

    checkpoint_enum = len(checkpoint_collect_container)

    d_tube_max = sup.solve_d_rect(domain_radius, rg_param, ry_param, sup.j_max_bef_overlap(ry_param, N_LIST), 0)

    if d_tube < 0 or d_tube > d_tube_max:
        raise ValueError(f"d_tube: {d_tube} is outside of the legal range: [0, {d_tube_max}")

    T_param = float(T_param)

    D_LAYER, A_LAYER = sup.initialize_layers(rg_param, ry_param)
    MFPT_snapshots = np.zeros([checkpoint_enum], dtype=np.float64)

    mfpt_comp.comp_mfpt_by_time_points(rg_param, ry_param, w_param, w_param, v_param, N_LIST, D_LAYER, A_LAYER,
                                       checkpoint_collect_container, MFPT_snapshots, T_param, approach, mass_checkpoint, domain_radius, D,
                                       d_tube)

    return pro.process_MFPT_results(MFPT_snapshots, checkpoint_collect_container, approach, rg_param, ry_param, w_param, v_param, N_LIST,
                                    save_png, show_plt)


# (****) (****)
def output_time_until_mass_depletion(rg_param, ry_param, N_LIST, v_param, w_param, domain_radius=1.0, D=1.0,
                                     d_tube=0, mass_threshold=0.01):
    D_LAYER, A_LAYER = sup.initialize_layers(rg_param, ry_param)

    if len(N_LIST) > ry_param:
        raise IndexError(
            f'Too many microtubules requested: {len(N_LIST)}, within domain of {ry_param} angular rays.')

    for i in range(len(N_LIST)):
        if N_LIST[i] < 0 or N_LIST[i] > ry_param:
            raise IndexError(f'Angle {N_LIST[i]} is out of bounds, your range should be [0, {ry_param - 1}]')
    N_LIST.sort()

    duration = ant.comp_until_mass_depletion(rg_param, ry_param, w_param, w_param,
                                             v_param, N_LIST, D_LAYER, A_LAYER, domain_radius, D, mass_threshold,
                                             d_tube)
    return duration


# (****) (****)
def collect_density_rad_depend(rg_param, ry_param, N_LIST, v_param, w_param, T_param, checkpoint_collect_container,
                               R_fixed_angle=-1, approach=2, domain_radius=1.0, D=1.0,
                               d_tube=0.0, mass_retention_threshold=0.01, mass_checkpoint=10 ** 6, save_png=True,
                               show_plt=False):

    if len(N_LIST) > ry_param:
        raise IndexError(
            f'Too many angular indices supplied for microtubule positions: {len(N_LIST)} > {ry_param} (number of angular positions in domain).'
        )

    for i in range(len(N_LIST)):
        if N_LIST[i] < 0 or N_LIST[i] > ry_param:
            raise IndexError(
                f'Angular index: {N_LIST[i]} falls outside of the legal index range: [0,{ry_param - 1}) under ry_param={ry_param}')

    N_LIST.sort()

    if approach == 1:
        checkpoint_collect_container.sort(reverse=True)
    elif approach == 2:
        for t in range(len(checkpoint_collect_container)):
            if checkpoint_collect_container[t] < 0.0 or checkpoint_collect_container[t] > T_param:
                raise ValueError(
                    f"Timestamp-point: {checkpoint_collect_container[t]} falls outside of the legal timestamp-point range: [0, {T_param} (T_param) ] (T_param = your input solution time duration)")
            dT = num.compute_dT(rg_param, ry_param, domain_radius=domain_radius, D=D)
            T_param += dT
        checkpoint_collect_container.sort()
    else:
        raise ValueError(
            f'{approach} is not a valid argument, use either collection approach "1" or "2" (must be an int)')

    checkpoint_collect_container = [float(item) for item in checkpoint_collect_container]

    d_tube_max = sup.solve_d_rect(domain_radius, rg_param, ry_param, sup.j_max_bef_overlap(ry_param, N_LIST), 0)

    if d_tube < 0 or d_tube > d_tube_max:
        raise ValueError(f"d_tube: {d_tube} is outside of the legal range: [0, {d_tube_max}")

    if R_fixed_angle < 0 or R_fixed_angle > ry_param - 1:
        print("R_fixed_angle automatically adjusted to legal range.")
        R_fixed_angle = N_LIST[0]

    collection_stamp_enum = len(checkpoint_collect_container)

    PvR_DL_snapshots = np.zeros((collection_stamp_enum, rg_param + 1), dtype=np.float64)
    RvR_AL_snapshots = np.zeros((collection_stamp_enum, rg_param), dtype=np.float64)

    D_LAYER, A_LAYER = sup.initialize_layers(rg_param, ry_param)

    ant.comp_diffusive_rad_snapshots(rg_param, ry_param, w_param, w_param, v_param, T_param, N_LIST, D_LAYER, A_LAYER,
                                     R_fixed_angle, PvR_DL_snapshots, RvR_AL_snapshots, checkpoint_collect_container,
                                     approach,
                                     domain_radius, D, mass_retention_threshold, mass_checkpoint, d_tube)

    output_list = pro.process_DvR_results(PvR_DL_snapshots, RvR_AL_snapshots, v_param, w_param, N_LIST, rg_param,
                                          ry_param, R_fixed_angle,
                                          checkpoint_collect_container, save_png, show_plt, approach)

    return output_list


# (****) (****)
def solve_mfpt_time_(rg_param, ry_param, N_LIST, v_param, w_param, T_param, domain_radius=1.0, D=1.0,
                mass_checkpoint=10 ** 6,
                d_tube=0.0):
    if len(N_LIST) > ry_param:
        raise IndexError(
            f'Too many angular indices supplied for microtubule positions: {len(N_LIST)} > {ry_param} (number of angular positions in domain).'
        )

    for i in range(len(N_LIST)):
        if N_LIST[i] < 0 or N_LIST[i] > ry_param:
            raise IndexError(
                f'Angular index: {N_LIST[i]} falls outside of the legal index range: [0,{ry_param - 1}) under ry_param={ry_param}')

    N_LIST.sort()

    d_tube_max = sup.solve_d_rect(domain_radius, rg_param, ry_param, sup.j_max_bef_overlap(ry_param, N_LIST), 0)

    if d_tube < 0 or d_tube > d_tube_max:
        raise ValueError(f"d_tube: {d_tube} is outside of the legal range: [0, {d_tube_max}")

    D_LAYER, A_LAYER = sup.initialize_layers(rg_param, ry_param)
    MFPT = mfpt_comp.comp_mfpt_by_time(rg_param, ry_param, w_param, w_param, v_param, N_LIST,
                                       D_LAYER, A_LAYER, T_param, mass_checkpoint, domain_radius, D, d_tube)
    return MFPT


def solve_mfpt_mass_(rg_param, ry_param, N_LIST, v_param, w_param, domain_radius=1.0, D=1.0, mass_checkpoint=10**6, mass_retention_threshold=0.01, d_tube=0.0):
    if len(N_LIST) > ry_param:
        raise IndexError(
            f'Too many angular indices supplied for microtubule positions: {len(N_LIST)} > {ry_param} (number of angular positions in domain).'
        )

    for i in range(len(N_LIST)):
        if N_LIST[i] < 0 or N_LIST[i] > ry_param:
            raise IndexError(
                f'Angular index: {N_LIST[i]} falls outside of the legal index range: [0,{ry_param - 1}) under ry_param={ry_param}')

    N_LIST.sort()

    d_tube_max = sup.solve_d_rect(domain_radius, rg_param, ry_param, sup.j_max_bef_overlap(ry_param, N_LIST), 0)

    if d_tube < 0 or d_tube > d_tube_max:
        raise ValueError(f"d_tube: {d_tube} is outside of the legal range: [0, {d_tube_max}")

    D_LAYER, A_LAYER = sup.initialize_layers(rg_param, ry_param)
    MFPT, sim_time = mfpt_comp.comp_mfpt_by_mass_loss_rect(rg_param, ry_param, w_param, w_param, v_param, N_LIST, D_LAYER, A_LAYER,
                                                           mass_checkpoint, domain_radius, D, mass_retention_threshold, d_tube)
    return MFPT, sim_time


# (****) (****)
def heatmap_production(rg_param, ry_param, N_LIST, v_param, w_param, T_param, checkpoint_collect_container, approach,
                       domain_radius=1.0, D=1.0, mass_checkpoint=10 ** 6, d_tube=0.0, mass_retention_threshold=0.01,
                       heatplot_border=False, heatplot_colorscheme='viridis', save_png=True,
                       show_plt=True, display_extraction=True):

    if len(N_LIST) > ry_param:
        raise IndexError(
            f'Too many angular indices supplied for microtubule positions: {len(N_LIST)} > {ry_param} (number of angular positions in domain).'
        )

    for i in range(len(N_LIST)):
        if N_LIST[i] < 0 or N_LIST[i] > ry_param:
            raise IndexError(
                f'Angular index: {N_LIST[i]} falls outside of the legal index range: [0,{ry_param - 1}) under ry_param={ry_param}')

    N_LIST.sort()

    d_tube_max = sup.solve_d_rect(domain_radius, rg_param, ry_param, sup.j_max_bef_overlap(ry_param, N_LIST), 0)

    if d_tube < 0 or d_tube > d_tube_max:
        raise ValueError(f"d_tube: {d_tube} is outside of the legal range: [0, {d_tube_max}")

    checkpoint_enum = len(checkpoint_collect_container)

    if approach == 1:
        checkpoint_collect_container.sort(reverse=True)
    elif approach == 2:
        for t in range(len(checkpoint_collect_container)):
            if checkpoint_collect_container[t] < 0.0 or checkpoint_collect_container[t] > T_param:
                raise ValueError(
                    f"Timestamp-point: {checkpoint_collect_container[t]} falls outside of the legal timestamp-point range: [0, {T_param} (T_param) ] (T_param = your input solution time duration)")
            dT = num.compute_dT(rg_param, ry_param, domain_radius=domain_radius, D=D)
            T_param += dT
        checkpoint_collect_container.sort()
    else:
        raise ValueError(
            f'{approach} is not a valid argument, use either collection approach "1" or "2" (must be an int)')

    checkpoint_collect_container = [float(item) for item in checkpoint_collect_container]

    j_max_list = struct_init.build_j_max_list(rg_param, ry_param, N_LIST, d_tube, domain_radius)

    # Initialize layers
    D_LAYER, A_LAYER = sup.initialize_layers(rg_param, ry_param)

    HM_DL_snapshots = np.zeros((checkpoint_enum, rg_param, ry_param), dtype=np.float64)
    HM_C_snapshots = np.zeros([checkpoint_enum], dtype=np.float64)
    MFPT_snapshots = np.zeros([checkpoint_enum], dtype=np.float64)

    ant.comp_diffusive_snapshots(rg_param, ry_param, w_param, w_param, v_param, T_param, N_LIST,
                                 D_LAYER, A_LAYER, HM_DL_snapshots, HM_C_snapshots, MFPT_snapshots, approach, checkpoint_collect_container, domain_radius, D, mass_retention_threshold,
                                 mass_checkpoint, d_tube)

    return pro.process_static_HM_results(HM_DL_snapshots, HM_C_snapshots, MFPT_snapshots, checkpoint_collect_container, heatplot_border, w_param, v_param,
                                         N_LIST, heatplot_colorscheme, save_png, show_plt, j_max_list, display_extraction, approach)


# (****> Requires non-numerical updates <****)
# def heatmap_production(rg_param, ry_param, w_param, v_param, N_LIST, filepath=fp.heatmap_output,
#                        time_point_container=None,
#                        save_png=True, show_plot=True, compute_MFPT=True, verbose=False, output_csv=True,
#                        rect_config=False,
#                        d_tube=-1, r=1.0, d=1.0, mass_retention_threshold=0.01, mass_checkpoint=10 ** 6,
#                        color_scheme='viridis',
#                        toggle_border=False, display_extraction=True, approach=2):
#
#     ani.generate_heatmaps(rg_param=rg_param, ry_param=ry_param, w_param=w_param, v_param=v_param, N_param=N_LIST,
#                           approach=approach,
#                           filepath=filepath, time_point_container=time_point_container, save_png=save_png,
#                           show_plot=show_plot, compute_mfpt=compute_MFPT,
#                           verbose=verbose, output_csv=output_csv, rect_config=rect_config, d_tube=d_tube, r=r, d=d,
#                           mass_retention_threshold=mass_retention_threshold,
#                           mass_checkpoint=mass_checkpoint, color_scheme=color_scheme, toggle_border=toggle_border,
#                           display_extraction=display_extraction)


# <***************************** UNDER DEVELOPMENT/REQUIRES MORE TESTING *****************************>

# MFPT as a function of W saturation analysis
# under construction
# def mfpt_of_W_sat_analysis(domain_list, N_param_list, v_param, w_param_list, T_param, r=1.0, d=1.0,
#                            mass_checkpoint=10 ** 6, d_tube=-1):
#     '''
#     Produces a visualization for a saturation of analysis as MFPT as a function of W (switching rate a=b) for varying domain sizes)
#     In addition, this current implementation only functions for a single microtubule configuration.
#
#     We are interested in saturation of MFPT across varying domain sizes under fixed number of microtubules, d_tube, velocity, and time.
#
#     Args:
#         domain_list: (2-Dimensional list: a list of domain dimensions, i.e. MxN, Rings x Rays)
#         N_param_list: (2-Dimensional list: a list of microtubule configurations corresponding to the dimensions in the above list)
#         v_param:
#         w_param_list: (1-dimensional list: a list of desired w_values in sorted order)
#         T_param:
#         r:
#         d:
#         mass_checkpoint:
#         d_tube:
#
#     Returns:
#     '''
#
#     # Throw an error if the sizes of the domain_list, N_param_list, and the w_param_list do not match
#
#     # In the case of non overlap, the current selection of d_tube (assuming it is non-zero) needs to be verified if it functions properly across all domain sizes and microtubule configurations.
#
#     output_file_list = []
#     for i in range(len(domain_list)):
#         MFPT_list = []
#         for j in range(len(w_param_list)):
#             MFPT = solve_mfpt_(domain_list[i][0], domain_list[i][1], N_param_list[i], v_param, w_param_list[j], T_param,
#                                r=r, d=d, mass_checkpoint=mass_checkpoint, d_tube=d_tube)
#             MFPT_list.append(MFPT)
#
#         # store the data and save the data to csv
#         # store a pointer to the csv data file
#         # append this pointer to a list of csv data files
#     # Configure a plot to display the saturation of results by overlapping the results contained in the list of csv data files.
#
#
# '''
#     Configure a launch function to produce an analysis on MFPT as a function of W for varying amounts of N
# '''

# <***************************** UNDER DEVELOPMENT/REQUIRES MORE TESTING *****************************>


# <**********************************************************> REQUIRES REVIEW (These functions have not been used since 2024)

# ind_param:  independent parameter: the value that remains static across all MFPT solutions
# dep_param:  dependent parameter(s) : value that is being tested for MFPT dependence (contained within a set)
#
#

# def solve_mfpt_multi_process(N_param, rg_param, ry_param, dep_type, ind_param, dep_param):
#     M = rg_param
#     N = ry_param
#
#     if dep_type == "W":
#         w_param = dep_param
#         v_param = ind_param
#     elif dep_type == "V":
#         v_param = dep_param
#         w_param = ind_param
#     else:
#         raise f"{dep_type} not yet defined, must use either V or W"
#
#     mfpt, duration = solve_mfpt(rg_param, ry_param, N_param, v_param, w_param, return_duration=True)
#
#     print(f"MxN={M}x{N}    Duration (sim time) : {duration}    Microtubule configuration: {N_param}"
#           f"    W: {w_param}    V: {v_param}")
#
#     if dep_type == "W":
#         return {f'W: {w_param}', f'MFPT: {mfpt}'}
#     elif dep_type == "V":
#         return {f'V: {w_param}', f'MFPT: {mfpt}'}
#
#
# # Will require further inspection
# def parallel_process_mfpt(N_list, rg_param, ry_param, dep_type, ind_type, dep_param, ind_list, cores=None):
#     dep_type = dep_type.upper()
#     if dep_type != "W" and dep_type != "V":
#         raise (f"{dep_type} is an undefined dependent parameter. The current available "
#                f"dependent parameters are Switch Rate (W), and Velocity (V)")
#
#     print(f"{ind_type} list: {ind_list}")
#
#     current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
#     data_filepath = tb.create_directory(fp.mfpt_results_output, current_time)
#
#     if cores is not None and cores > 0:
#         core_count = min(cores, config.core_amount)
#     else:
#         core_count = config.core_amount
#
#     for n in range(len(N_list)):
#         with mp.Pool(processes=core_count) as pool:
#             mfpt_results = pool.map(partial(solve_mfpt_multi_process, N_list[n],
#                                             rg_param, ry_param, dep_type, dep_param), ind_list)
#         print(mfpt_results)
#         tb.produce_csv_from_xy(mfpt_results, dep_type, "MFPT", data_filepath,
#                                f'MFPT_Results_N={len(N_list[n])}_{ind_type}={dep_param}_')
#
#
# # Will require further inspection
# def solve_mfpt(rg_param, ry_param, N_param, v_param, w_param, r=1.0, d=1.0, mass_checkpoint=10 ** 6,
#                mass_threshold=0.01, return_duration=False, mixed_config=False, mx_cn_rrange=1):
#     diff_layer, adv_layer = sup.initialize_layers(rg_param, ry_param)
#     mfpt, duration = mfpt_comp.comp_mfpt_by_mass_loss_rect(rg_param, ry_param, w_param, w_param, v_param,
#                                                            N_param, diff_layer, adv_layer, mass_checkpoint, r, d,
#                                                            mass_threshold, mixed_config, mx_cn_rrange)
#
#     if return_duration:
#         return mfpt, duration
#     else:
#         return mfpt

# <**********************************************************> REQUIRES REVIEW (These functions have not been used since 2024)
