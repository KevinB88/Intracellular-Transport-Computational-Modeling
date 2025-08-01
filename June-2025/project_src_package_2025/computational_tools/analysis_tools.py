from . import math, njit, numerical_tools as num, sys_config, supplements as sup, np, struct_init as strc
from numba.typed import List
from numba import int64
from project_src_package_2025.computational_tools import struct_init

ENABLE_JIT = sys_config.ENABLE_NJIT
ENABLE_CACHE = sys_config.ENABLE_NUMBA_CACHING


# Methods used to collect numerical results (via PDE solver) to conduct analyses on, e.g, mass(t), Phi(theta), Phi(rad), Rho(rad), ect.
# All methods below implement the space efficient two-step approach (in terms of how numerical data is stored across updates), i.e, [0][m][n] refers to the current (step k), and [1][m][n] refers to next (step k+1).


# (****) (****)
@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def comp_mass_analysis_respect_to_time(rg_param, ry_param, switch_param_a, switch_param_b, v_param, T_param,
                                       N_LIST, D_LAYER, A_LAYER, MA_DL_timeseries, MA_AL_timeseries, MA_ALoI_timeseries,
                                       MA_ALoT_timeseries, MA_TM_timeseries, MA_collection_factor,
                                       relative_k, d_tube=0, domain_radius=1.0, D=1.0, mass_checkpoint=10 ** 6):
    if ENABLE_JIT:
        print("Running optimized version.")

    # Initialize constants
    dRad = num.compute_dRad(rg_param, domain_radius)
    dThe = num.compute_dThe(ry_param)
    dT = num.compute_dT(rg_param, ry_param, domain_radius, D)
    K = num.compute_K(rg_param, ry_param, T_param, domain_radius, D)
    central_patch = num.compute_init_cond_cent(rg_param, domain_radius)
    v_param *= -1

    # Initialize the ring position (m) dependent extraction range dictionary
    d_list = struct_init.build_d_tube_mapping_no_overlap(rg_param, ry_param, N_LIST, d_tube, domain_radius)

    # Initialize layer masses
    dl_mass = 1
    al_mass = 0

    # Mass data collection iterator
    MA_k_step = 0

    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k < K:

        num.comp_DL_AL_kp1_2step(ry_param, rg_param, d_list, D_LAYER, central_patch, A_LAYER, N_LIST, dRad, dThe, dT, switch_param_a, switch_param_b, v_param, d_tube)

        # <<<< ------------- Updating DL and AL for the K+1-th step ------------- >>>>
        # m = 0
        #
        # while m < rg_param:
        #
        #     # The advective angle index 'aIdx'
        #     aIdx = 0
        #     n = 0
        #
        #     while n < ry_param:
        #         if m == rg_param - 1:
        #             D_LAYER[1][m][n] = 0
        #         else:
        #             if n in d_list[m]:
        #                 D_LAYER[1][m][n] = num.u_density_rect(D_LAYER, 0, m, n, dRad,
        #                                                       dThe, dT, central_patch, rg_param,
        #                                                       A_LAYER, int(d_list[m][n]), switch_param_a,
        #                                                       switch_param_b, d_tube)
        #             else:
        #                 D_LAYER[1][m][n] = num.u_density(D_LAYER, 0, m, n, dRad, dThe,
        #                                                  dT, central_patch, rg_param, A_LAYER,
        #                                                  aIdx, switch_param_a, switch_param_b, N_LIST)
        #             if n == N_LIST[aIdx]:
        #
        #                 A_LAYER[1][m][n] = num.u_tube_rect(A_LAYER, D_LAYER, 0, m, n,
        #                                                    switch_param_a, switch_param_b,
        #                                                    v_param, dT, dRad, dThe, d_tube)
        #                 if aIdx < len(N_LIST) - 1:
        #                     aIdx += 1
        #         n += 1
        #     m += 1
        # <<<< ------------- Updating DL and AL for the K+1-th step ------------- >>>>

        if k > 0 and k % mass_checkpoint == 0:
            print("Current timestep: ", k, "Current simulation time: ", k * dT, "Current DL mass: ", dl_mass,
                  "Current AL mass: ", al_mass)
            print("Velocity (v): ", v_param, "Diffusive to Advective switch rate (a): ", switch_param_a,
                  "Advective to Diffusive switch rate (b): ", switch_param_b)

        # Collect mass
        if MA_k_step < relative_k and k % MA_collection_factor == 0:
            MA_DL_timeseries[MA_k_step] = dl_mass
            MA_AL_timeseries[MA_k_step] = al_mass
            MA_TM_timeseries[MA_k_step] = dl_mass + al_mass
            MA_ALoT_timeseries[MA_k_step] = al_mass / MA_TM_timeseries[MA_k_step]
            MA_ALoI_timeseries[MA_k_step] = al_mass / D
            MA_k_step += 1

        # Update mass for the next step
        dl_mass = num.calc_mass_diff(D_LAYER, 0, dRad, dThe, central_patch, rg_param, ry_param)
        al_mass = num.calc_mass_adv(A_LAYER, 0, dRad, dThe, rg_param, N_LIST)
        central_patch = num.u_center(D_LAYER, 0, dRad, dThe, dT, central_patch, A_LAYER, N_LIST, v_param)

        D_LAYER[0] = D_LAYER[1]
        A_LAYER[0] = A_LAYER[1]
        k += 1
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# (****) (****)
@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def comp_diffusive_angle_snapshots(rg_param, ry_param, switch_param_a, switch_param_b, T_param, v_param, N_LIST,
                                   D_LAYER, A_LAYER,
                                   PvT_DL_snapshots, checkpoint_collect_container, approach, T_fixed_ring_seg=0.5,
                                   d_tube=0,
                                   domain_radius=1.0, D=1.0, mass_retention_threshold=0.01, mass_checkpoint=10 ** 6):
    if ENABLE_JIT:
        print("Running optimized version.")

    if len(N_LIST) > ry_param:
        raise IndexError(
            f'Too many angular indices supplied for microtubule positions: {len(N_LIST)} > {ry_param} (number of angular positions in domain).')

    for i in range(len(N_LIST)):
        if N_LIST[i] < 0 or N_LIST[i] > ry_param:
            raise IndexError(
                f'Angular index: {N_LIST[i]} falls outside of the legal index range: [0,{ry_param - 1}) under ry_param={ry_param}')

    dRad = num.compute_dRad(ry_param, domain_radius)
    dThe = num.compute_dThe(ry_param)
    dT = num.compute_dT(rg_param, ry_param, domain_radius, D)
    K = num.compute_K(rg_param, ry_param, T_param, domain_radius, D)
    v_param *= -1

    central_patch = num.compute_init_cond_cent(rg_param, domain_radius)
    mass_retained = 0

    d_list = struct_init.build_d_tube_mapping_no_overlap(rg_param, ry_param, N_LIST, d_tube, domain_radius)

    checkpoint_iter = 0

    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or (k < K and mass_retained > mass_retention_threshold):

        num.comp_DL_AL_kp1_2step(ry_param, rg_param, d_list, D_LAYER, central_patch, A_LAYER, N_LIST, dRad, dThe, dT,
                                 switch_param_a, switch_param_b, v_param, d_tube)

        # <<<< ------------- Updating DL and AL for the K+1-th step ------------- >>>>
        # m = 0
        # while m < rg_param:
        #
        #     # The advective angle index 'aIdx'
        #     aIdx = 0
        #     n = 0
        #
        #     while n < ry_param:
        #         if m == rg_param - 1:
        #             D_LAYER[1][m][n] = 0
        #         else:
        #
        #             if n in d_list[m]:
        #
        #                 D_LAYER[1][m][n] = num.u_density_rect(D_LAYER, 0, m, n, dRad, dThe, dT,
        #                                                       central_patch, rg_param, A_LAYER, int(d_list[m][n]),
        #                                                       switch_param_a, switch_param_b, d_tube)
        #
        #             else:
        #                 D_LAYER[1][m][n] = num.u_density(D_LAYER, 0, m, n, dRad, dThe,
        #                                                  dT,
        #                                                  central_patch, rg_param, A_LAYER,
        #                                                  aIdx,
        #                                                  switch_param_a, switch_param_b,
        #                                                  N_LIST)
        #             if n == N_LIST[aIdx]:
        #                 A_LAYER[1][m][n] = num.u_tube_rect(A_LAYER, D_LAYER, 0, m, n, switch_param_a, switch_param_b,
        #                                                    v_param, dT, dRad, dThe, d_tube)
        #                 if aIdx < len(N_LIST) - 1:
        #                     aIdx += 1
        #         n += 1
        #     m += 1
        # <<<< ------------- Updating DL and AL for the K+1-th step ------------- >>>>

        if k > 0 and k % mass_checkpoint == 0:
            print("Current timestep: ", k, "Current simulation time: ", k * dT, "Current DL mass: ", mass_retained)
            print("Velocity (v): ", v_param, "Diffusive to Advective switch rate (a): ", switch_param_a,
                  "Advective to Diffusive switch rate (b): ", switch_param_b)

        if int(approach) == 1:

            if checkpoint_iter < len(checkpoint_collect_container):
                curr_mass_stamp = checkpoint_collect_container[checkpoint_iter]
                if curr_mass_stamp * 0.99 < mass_retained < curr_mass_stamp * 1.01:
                    PvT_DL_snapshots[checkpoint_iter] = D_LAYER[0][int(np.floor(rg_param * T_fixed_ring_seg))]
                    checkpoint_iter += 1
            else:
                return

        elif int(approach) == 2:

            if checkpoint_iter < len(checkpoint_collect_container):
                curr_stamp = np.floor(checkpoint_collect_container[checkpoint_iter] / dT)
                if k == curr_stamp:
                    PvT_DL_snapshots[checkpoint_iter] = D_LAYER[0][int(np.floor(rg_param * T_fixed_ring_seg))]
                    checkpoint_iter += 1
            else:
                return

        mass_retained = num.calc_mass(D_LAYER, A_LAYER, 0, dRad, dThe, central_patch, rg_param, ry_param, N_LIST)
        central_patch = num.u_center(D_LAYER, 0, dRad, dThe, dT, central_patch, A_LAYER, N_LIST, v_param)
        D_LAYER[0] = D_LAYER[1]
        A_LAYER[0] = A_LAYER[1]
        k += 1


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# (****) (****)
@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def comp_diffusive_rad_snapshots(rg_param, ry_param, switch_param_a, switch_param_b, v_param, T_param, N_LIST, D_LAYER,
                                 A_LAYER,
                                 R_fixed_angle, PvR_DL_snapshots, RvR_AL_snapshots, checkpoint_collect_container,
                                 approach, domain_radius=1.0, D=1.0,
                                 mass_retention_threshold=0.01, mass_checkpoint=10 ** 6, d_tube=0):
    if ENABLE_JIT:
        print("Running optimized version.")

    R_fixed_angle = int(R_fixed_angle)

    dRad = num.compute_dRad(rg_param, domain_radius)
    dThe = num.compute_dThe(ry_param)
    dT = num.compute_dT(rg_param, ry_param, domain_radius, D)
    central_patch = num.compute_init_cond_cent(rg_param, domain_radius)
    K = num.compute_K(rg_param, ry_param, T_param, domain_radius, D)

    v_param *= -1

    d_list = struct_init.build_d_tube_mapping_no_overlap(rg_param, ry_param, N_LIST, d_tube, domain_radius)

    checkpoint_iter = 0

    mass_retained = 0

    k = 0
    while k == 0 or (k < K and mass_retained > mass_retention_threshold):

        num.comp_DL_AL_kp1_2step(ry_param, rg_param, d_list, D_LAYER, central_patch, A_LAYER, N_LIST, dRad, dThe, dT,
                                 switch_param_a, switch_param_b, v_param, d_tube)

        # <<<< ------------- Updating DL and AL for the K+1-th step ------------- >>>>
        # m = 0
        #
        # while m < rg_param:
        #
        #     # The advective angle index 'aIdx'
        #     aIdx = 0
        #     n = 0
        #
        #     while n < ry_param:
        #         if m == rg_param - 1:
        #             D_LAYER[1][m][n] = 0
        #         else:
        #             if n in d_list[m]:
        #                 D_LAYER[1][m][n] = num.u_density_rect(D_LAYER, 0, m, n, dRad, dThe,
        #                                                       dT,
        #                                                       central_patch, rg_param, A_LAYER,
        #                                                       int(d_list[m][n]), switch_param_a, switch_param_b, d_tube)
        #             else:
        #                 D_LAYER[1][m][n] = num.u_density(D_LAYER, 0, m, n, dRad, dThe,
        #                                                  dT,
        #                                                  central_patch, rg_param, A_LAYER,
        #                                                  aIdx,
        #                                                  switch_param_a, switch_param_b,
        #                                                  N_LIST)
        #             if n == N_LIST[aIdx]:
        #
        #                 A_LAYER[1][m][n] = num.u_tube_rect(A_LAYER, D_LAYER, 0, m,
        #                                                    n, switch_param_a, switch_param_b, v_param, dT, dRad, dThe,
        #                                                    d_tube)
        #
        #                 if aIdx < len(N_LIST) - 1:
        #                     aIdx += 1
        #         n += 1
        #     m += 1
        # <<<< ------------- Updating DL and AL for the K+1-th step ------------- >>>>

        if k > 0 and k % mass_checkpoint == 0:
            print("Velocity (V)= ", v_param, "Time step: ", k, "Simulation time: ", k * dT, "Current mass: ",
                  mass_retained,
                  "a=", switch_param_a, "b=", switch_param_b)

        if int(approach) == 1:

            if checkpoint_iter < len(checkpoint_collect_container):
                curr_mass_stamp = checkpoint_collect_container[checkpoint_iter]
                if curr_mass_stamp * 0.99 < mass_retained < curr_mass_stamp * 1.01:
                    PvR_DL_snapshots[checkpoint_iter][0] = central_patch
                    for m in range(rg_param):
                        PvR_DL_snapshots[checkpoint_iter][m + 1] = D_LAYER[0][m][R_fixed_angle]
                        RvR_AL_snapshots[checkpoint_iter][m] = A_LAYER[0][m][R_fixed_angle]
                    checkpoint_iter += 1

            else:
                return

        elif int(approach) == 2:

            if checkpoint_iter < len(checkpoint_collect_container):
                curr_stamp = np.floor(checkpoint_collect_container[checkpoint_iter] / dT)
                if k == curr_stamp:
                    PvR_DL_snapshots[checkpoint_iter][0] = central_patch
                    for m in range(rg_param):
                        PvR_DL_snapshots[checkpoint_iter][m + 1] = D_LAYER[0][m][R_fixed_angle]
                        RvR_AL_snapshots[checkpoint_iter][m] = A_LAYER[0][m][R_fixed_angle]
                    checkpoint_iter += 1
            else:
                return

        mass_retained = num.calc_mass(D_LAYER, A_LAYER, 0, dRad, dThe, central_patch, rg_param, ry_param,
                                      N_LIST)
        central_patch = num.u_center(D_LAYER, 0, dRad, dThe, dT, central_patch, A_LAYER,
                                     N_LIST, v_param)
        D_LAYER[0] = D_LAYER[1]
        A_LAYER[0] = A_LAYER[1]
        k += 1


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# (****) (****)
@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def comp_until_mass_depletion(rg_param, ry_param, switch_param_a, switch_param_b, v_param, N_LIST, D_LAYER, A_LAYER,
                              domain_radius=1.0, D=1.0,
                              mass_retention_threshold=0.01, d_tube=0.0):
    if ENABLE_JIT:
        print("Running optimized version.")

    dRad = num.compute_dRad(rg_param, D)
    dThe = num.compute_dThe(ry_param)
    dT = num.compute_dT(rg_param, ry_param, domain_radius, D)
    central_patch = num.compute_init_cond_cent(rg_param, domain_radius)
    v_param *= -1

    d_list = struct_init.build_d_tube_mapping_no_overlap(rg_param, ry_param, N_LIST, d_tube, domain_radius)

    mass_retained = 0

    k = 0

    while k == 0 or mass_retained > mass_retention_threshold:
        num.comp_DL_AL_kp1_2step(ry_param, rg_param, d_list, D_LAYER, central_patch, A_LAYER, N_LIST, dRad, dThe, dT, switch_param_a, switch_param_b, v_param, d_tube)
        # <<<< ------------- Updating DL and AL for the K+1-th step ------------- >>>>
        # m = 0
        # while m < rg_param:
        #
        #     # The advective angle index 'aIdx'
        #     aIdx = 0
        #     n = 0
        #
        #     while n < ry_param:
        #         if m == rg_param - 1:
        #             D_LAYER[1][m][n] = 0
        #         else:
        #             if n in d_list[m]:
        #
        #                 D_LAYER[1][m][n] = num.u_density_rect(D_LAYER, 0, m, n, dRad, dThe,
        #                                                       dT,
        #                                                       central_patch, rg_param, A_LAYER,
        #                                                       int(d_list[m][n]), switch_param_a, switch_param_b, d_tube)
        #             else:
        #                 D_LAYER[1][m][n] = num.u_density(D_LAYER, 0, m, n, dRad, dThe,
        #                                                  dT,
        #                                                  central_patch, rg_param, A_LAYER,
        #                                                  aIdx,
        #                                                  switch_param_a, switch_param_b,
        #                                                  N_LIST)
        #
        #             if n == N_LIST[aIdx]:
        #                 A_LAYER[1][m][n] = num.u_tube_rect(A_LAYER, D_LAYER, 0, m, n,
        #                                                    switch_param_a, switch_param_b, v_param, dT, dRad, dThe,
        #                                                    d_tube)
        #
        #                 if aIdx < len(N_LIST) - 1:
        #                     aIdx += 1
        #         n += 1
        #     m += 1
        # <<<< ------------- Updating DL and AL for the K+1-th step ------------- >>>>

        mass_retained = num.calc_mass(D_LAYER, A_LAYER, 0, dRad, dThe, central_patch, rg_param, ry_param,
                                      N_LIST)
        central_patch = num.u_center(D_LAYER, 0, dRad, dThe, dT, central_patch, A_LAYER,
                                  N_LIST, v_param)

        D_LAYER[0] = D_LAYER[1]
        A_LAYER[0] = A_LAYER[1]

        k += 1

    return k * dT


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# (****> Requires non-numerical updates <****)
@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
# Collecting DL, central-patch, and AL snapshots for static heat-plot visualization.
def comp_diffusive_snapshots(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer,
                             domain_snapshot_container, domain_center_container, sim_time_container, approach, r=1.0,
                             d=1.0,
                             mass_retention_threshold=0.01, time_point_container=None, compute_mfpt=False,
                             mfpt_container=None, mass_checkpoint=10 ** 6, rect_config=False, d_tube=-1):
    if ENABLE_JIT:
        print("Running optimized version.")

    if len(tube_placements) > rays:
        raise IndexError(
            f'Too many microtubules requested: {len(tube_placements)}, within domain of {rays} angular rays.'
        )
    for i in range(len(tube_placements)):
        if tube_placements[i] < 0 or tube_placements[i] > rays:
            raise IndexError(f'Angle {tube_placements[i]} is out of bounds, your range should be [0, {rays - 1}]')

    d_radius = r / rings
    d_theta = ((2 * math.pi) / rays)
    d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / (2 * d)

    phi_center = 1 / (math.pi * (d_radius * d_radius))

    mass_retained = 0
    # Mean first passage time
    MFPT = 0
    net_current_out = 0
    d_list = List()

    # *** Mixed configuration block 5/28/25

    if rect_config:
        if d_tube < 0:
            d_tube = sup.solve_d_rect(1, rings, rays, sup.j_max_bef_overlap(rays, tube_placements), 0)

        for m in range(rings):
            j_max = math.ceil((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
            keys = sup.mod_range_flat(tube_placements, j_max, rays, False)
            d = sup.dict_gen(keys, tube_placements)
            d_list.append(d)
    # *** Mixed configuration block 5/28/25

    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0
    i = 0

    while k == 0 or mass_retained > mass_retention_threshold:

        if compute_mfpt:
            net_current_out = 0

        # ***************************************************************************************************************************************************************
        m = 0
        # ***********************
        while m < rings:

            # The advective angle index 'aIdx'
            aIdx = 0
            # The diffusive angle index 'dIdx'
            n = 0

            while n < rays:
                if m == rings - 1:
                    diffusive_layer[1][m][n] = 0
                else:

                    # Mixed configuration block 5/27/25
                    # **********************************************************************************************************************************************
                    if rect_config and n in d_list[m]:

                        j_max = math.ceil((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)

                        diffusive_layer[1][m][n] = num.u_density_rect(diffusive_layer, 0, m, n, d_radius, d_theta,
                                                                      d_time, phi_center, rings, advective_layer,
                                                                      int(d_list[m][n]), a, b, j_max)

                    else:
                        diffusive_layer[1][m][n] = num.u_density(diffusive_layer, 0, m, n, d_radius, d_theta,
                                                                 d_time,
                                                                 phi_center, rings, advective_layer,
                                                                 aIdx,
                                                                 a, b,
                                                                 tube_placements)
                    if n == tube_placements[aIdx]:
                        if rect_config:
                            j_max = math.ceil((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
                            advective_layer[1][m][n] = num.u_tube_rect(advective_layer, diffusive_layer, 0, m, n, a, b,
                                                                       v, d_time, d_radius, d_theta, j_max)
                        else:
                            advective_layer[1][m][n] = num.u_tube(advective_layer, diffusive_layer, 0, m, n, a, b,
                                                                  v,
                                                                  d_time, d_radius, d_theta)
                        if aIdx < len(tube_placements) - 1:
                            aIdx += 1

                if compute_mfpt:
                    if m == rings - 2:
                        net_current_out += num.j_r_r(diffusive_layer, 0, m, n, d_radius, 0) * rings * d_radius * d_theta
                n += 1
            m += 1
        # ************************************************

        if compute_mfpt:
            MFPT += net_current_out * k * d_time * d_time

        '''
        Plotting theta versus diffusive at velocity peak values:
        choose several rings within the domain (at positions M*1/4, M*1/2, M*3/4), and then collect diffusive across every angle across that ring.
        (At varying mass amounts within the domain) [0.1 + epsilon, 0.225, 0.45, 0.675]
        '''

        if approach == 1:
            # if 0.675 < mass_retained < 0.68:
            if 0.985 < mass_retained < 0.99:
                # Implemented for the 2/18/25 task no. 2  128x128 heatmap computation
                domain_snapshot_container[0] = diffusive_layer[0]
                domain_center_container[0] = phi_center
                sim_time_container[0] = k * d_time
                if compute_mfpt:
                    mfpt_container[0] = MFPT
            elif 0.45 < mass_retained < 0.46:
                domain_snapshot_container[1] = diffusive_layer[0]
                domain_center_container[1] = phi_center
                sim_time_container[1] = k * d_time
                if compute_mfpt:
                    mfpt_container[1] = MFPT
            elif 0.225 < mass_retained < 0.26:
                domain_snapshot_container[2] = diffusive_layer[0]
                domain_center_container[2] = phi_center
                sim_time_container[2] = k * d_time
                if compute_mfpt:
                    mfpt_container[2] = MFPT
            elif 0.015 < mass_retained < 0.02:
                domain_snapshot_container[3] = diffusive_layer[0]
                domain_center_container[3] = phi_center
                sim_time_container[3] = k * d_time
                if compute_mfpt:
                    mfpt_container[3] = MFPT
                return
        elif approach == 2:
            if i < len(time_point_container):
                curr_stamp = int(np.floor(time_point_container[i] / d_time))
                if curr_stamp == k:
                    domain_center_container[i] = phi_center
                    domain_snapshot_container[i] = diffusive_layer[0]
                    mfpt_container[i] = MFPT
                    i += 1
            else:
                return

            # determine if k * d_time is in (time_point - epsilon, time_point + epsilon)
            # if i < len(time_point_container) and (time_point_container[i] * 0.95) < k * d_time < (time_point_container[i] * 1.05):
            #     domain_center_container[i] = phi_center
            #     domain_snapshot_container[i] = diffusive_layer[0]
            #     if compute_mfpt:
            #         mfpt_container[i] = MFPT
            #     i = i + 1
            # else:
            #     return

            # if i < len(time_point_container):
            #     time_point = time_point_container[i]
            #     epsilon = time_point * 0.05
            # else:
            #     return
            #
            # if time_point - epsilon < k * d_time < time_point + epsilon:
            #     domain_center_container[i] = phi_center
            #     domain_snapshot_container[i] = diffusive_layer[0]
            #     if compute_mfpt:
            #         mfpt_container[i] = MFPT
            #     i = i + 1

        else:
            raise ValueError(
                f'{approach} is not a valid argument, use either collection approach "1" or "2" (must be an int)')

        if k > 0 and k % int(mass_checkpoint) == 0:
            print("Velocity (V)= ", v, "Time step: ", k, "Simulation time: ", k * d_time, "Current mass: ",
                  mass_retained,
                  "a=", a, "b=", b)

        mass_retained = num.calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays,
                                      tube_placements)
        phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer,
                                  tube_placements, v)
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
        k += 1

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# <***************************** Temporarily retired *****************************>
# @njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
# def comp_mass_loss_glb_pk(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer, r=1.0, d=1.0,
#                           mass_retention_threshold=0.01):
#     """
#
#     Prints biophysical metrics including MFPT and the dimensionless time taken to reach the global-maximum of the mass-loss-rate as a
#     function of time, J(t).
#
#     :param rings: (float) # of radial rings in the cellular domain
#     :param rays: (float) # of angular rays in the cellular domain
#     :param a: (float) the switch rate onto the diffusive layer
#     :param b: (float) the switch rate onto the advective layer
#     :param v: (float) particle velocity on microtubules/filaments
#     :param tube_placements: (list(int)) discrete microtubule/filament positions between [0, rays-1]
#
#     :param diffusive_layer: [np.zeros((2, rings, rays), dtype=np.float64)] a 2 * rings * ray container to collect density at the diffusive layer
#     :param advective_layer: [np.zeros((2, rings, rays), dtype=np.float64)] a 2 * rings * ray container to collect density at the advective layer
#
#     :param r: (float) cellular radius, by default r=1.
#     :param d: (float) diffusion constant, by default d=1
#     :param mass_retention_threshold: (float) the amount of mass remaining in the domain until termination
#     :param mixed_config (bool) toggling the mixed configuration
#     :return: void
#     """
#
#     if ENABLE_JIT:
#         print("Running optimized version.")
#
#     if len(tube_placements) > rays:
#         raise IndexError(
#             f'Too many microtubules requested: {len(tube_placements)}, within domain of {rays} angular rays.')
#
#     for i in range(len(tube_placements)):
#         if tube_placements[i] < 0 or tube_placements[i] > rays:
#             raise IndexError(f'Angle {tube_placements[i]} is out of bounds, your range should be [0, {rays - 1}]')
#
#     d_radius = r / rings
#     d_theta = ((2 * math.pi) / rays)
#     d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / (2 * d)
#
#     phi_center = 1 / (math.pi * (d_radius * d_radius))
#
#     mass_retained = 0
#     # Mean first passage time
#     m_f_p_t = 0
#
#     mass_loss_step_i = 0
#     mass_loss_step_i_plus = 0
#
#     diff_special_angles = np.empty(rays, dtype=np.int64)
#
#     # if mixed_config:
#     #     diff_special_angles = sup.mod_range_flat_sorted(tube_placements, 1, rays)
#
#     # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     k = 0
#
#     while k == 0 or mass_retained > mass_retention_threshold:
#
#         net_current_out = 0
#
#         m = 0
#
#         while m < rings:
#             angle_index = 0
#
#             if m == rings - 2:
#                 if k % 2 == 0:
#                     mass_loss_step_i = num.calc_loss_mass_j_r_r(diffusive_layer, 0, d_radius, d_theta, rings, rays)
#                 else:
#                     mass_loss_step_i_plus = num.calc_loss_mass_j_r_r(diffusive_layer, 0, d_radius, d_theta, rings, rays)
#                 if k > 0 and k % 2 != 0:
#                     if mass_loss_step_i > mass_loss_step_i_plus:
#                         print("Mass loss J(t) global peak time (in dimensional units): ", (k - 1) * d_time,
#                               "# time steps: ", k - 1, "MFPT: ", m_f_p_t)
#                         return
#             n = 0
#             while n < rays:
#                 if m == rings - 1:
#                     diffusive_layer[1][m][n] = 0
#                 else:
#                     diffusive_layer[1][m][n] = num.u_density(diffusive_layer, 0, m, n, d_radius, d_theta, d_time,
#                                                              phi_center, rings, advective_layer, angle_index, a,
#                                                              b,
#                                                              tube_placements)
#                     if n == tube_placements[angle_index]:
#                         advective_layer[1][m][n] = num.u_tube(advective_layer, diffusive_layer, 0, m, n, a, b, v,
#                                                               d_time, d_radius, d_theta)
#                         if angle_index < len(tube_placements) - 1:
#                             angle_index = angle_index + 1
#                 if m == rings - 2:
#                     net_current_out += num.j_r_r(diffusive_layer, 0, m, n, d_radius, 0) * rings * d_radius * d_theta
#                 n += 1
#             m += 1
#
#         m_f_p_t += net_current_out * k * d_time * d_time
#         k += 1
#
#         mass_retained = num.calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays,
#                                       tube_placements)
#         phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer,
#                                   tube_placements, v)
#         diffusive_layer[0] = diffusive_layer[1]
#         advective_layer[0] = advective_layer[1]
#
#
