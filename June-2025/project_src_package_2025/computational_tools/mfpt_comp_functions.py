from . import njit, math, numerical_tools as num, sys_config, supplements as sup, np
# import time
from project_src_package_2025.computational_tools import struct_init

from numba.typed import Dict, List
from numba import int64

ENABLE_JIT = sys_config.ENABLE_NJIT
ENABLE_CACHE = sys_config.ENABLE_NUMBA_CACHING

# (****) (****)
@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def comp_mfpt_by_mass_loss(rg_param, ry_param, switch_param_a, switch_param_b, v_param,
                           N_LIST, D_LAYER, A_LAYER, mass_checkpoint=10**6,
                           domain_radius=1.0, D=1.0, mass_retention_threshold=0.01, d_tube=0.0):

    if ENABLE_JIT:
        print("Running optimized version.")

    dRad = num.compute_dRad(rg_param, domain_radius)
    dThe = num.compute_dThe(ry_param)
    dT = num.compute_dT(rg_param, ry_param, domain_radius, D)
    central_patch = num.compute_init_cond_cent(rg_param, domain_radius)
    d_list = struct_init.build_d_tube_mapping_no_overlap(rg_param, ry_param, N_LIST, d_tube, domain_radius)
    v_param *= -1
    k = 0
    mass_retained = 0
    MFPT = 0

    while k == 0 or mass_retained > mass_retention_threshold:

        net_current_out = num.comp_DL_AL_kp1_2step(ry_param, ry_param, d_list, D_LAYER, central_patch, A_LAYER,
                                                   N_LIST, dRad, dThe, dT, switch_param_a, switch_param_b, v_param, d_tube)

        MFPT += net_current_out * k * dT ** 2
        # Implemented to provide occasional status checks/metrics during MFPT calculation
        if k > 0 and k % mass_checkpoint == 0:
            print("Velocity (V)= ", v_param, "Time step: ", k, "Simulation time: ", k * dT, "Current mass: ",
                  mass_retained,
                  "a=", switch_param_a, "b=", switch_param_b)

        # This block will need to be modified for performance related optimizations (the computation of mass(k) is independent from computing MFPT)
        mass_retained = num.calc_mass(D_LAYER, A_LAYER, 0, dRad, dThe, central_patch,
                                      rg_param, ry_param, N_LIST)
        central_patch = num.u_center(D_LAYER, 0, dRad, dThe, dT, central_patch, A_LAYER, N_LIST, v_param)

        D_LAYER[0] = D_LAYER[1]
        A_LAYER[0] = A_LAYER[1]
        k += 1

    sim_time_duration = dT * k

    return MFPT, sim_time_duration

# (****) (****)
@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def comp_mfpt_by_time(rg_param, ry_param, switch_param_a, switch_param_b, v_param, N_LIST, D_LAYER, A_LAYER,
                      T_param, mass_checkpoint=10 ** 6, domain_radius=1.0, D=1.0, d_tube=0):
    if ENABLE_JIT:
        print("Running optimized version.")

    dRad = num.compute_dRad(rg_param, domain_radius)
    dThe = num.compute_dThe(ry_param)
    dT = num.compute_dT(rg_param, ry_param, domain_radius, D)
    K = num.compute_K(rg_param, ry_param, T_param, domain_radius, D)
    central_patch = num.compute_init_cond_cent(rg_param, domain_radius)
    v_param *= -1

    d_list = struct_init.build_d_tube_mapping_no_overlap(rg_param, ry_param, N_LIST, d_tube, domain_radius)

    MFPT = 0
    mass_retained = 0

    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k < K:

        net_current_out = 0

        net_current_out += num.comp_DL_AL_kp1_2step(ry_param, rg_param, d_list, D_LAYER, central_patch, A_LAYER, N_LIST, dRad, dThe, dT, switch_param_a, switch_param_b, v_param, d_tube)

        MFPT += net_current_out * k * dT ** 2
        # Implemented to provide occasional status checks/metrics during MFPT calculation
        if k > 0 and k % mass_checkpoint == 0:
            print("Velocity (V)= ", v_param, "Time step: ", k, "Simulation time: ", k * dT, "Current mass: ",
                  mass_retained,
                  "a=", switch_param_a, "b=", switch_param_b)

        mass_retained = num.calc_mass(D_LAYER, A_LAYER, 0, dRad, dThe, central_patch,
                                      rg_param, ry_param, N_LIST)
        central_patch = num.u_center(D_LAYER, 0, dRad, dThe, dT, central_patch,
                                     A_LAYER, N_LIST, v_param)

        D_LAYER[0] = D_LAYER[1]
        A_LAYER[0] = A_LAYER[1]
        # transfer updated density info from the next step to the current
        # num.update_layer_inplace(diffusive_layer[0], diffusive_layer[1], rays, rings)
        # num.update_layer_inplace(advective_layer[0], advective_layer[1], rays, rings)
        k += 1
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    return MFPT


# (****) (****)
@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def comp_mfpt_by_time_points_mass_dep(rg_param, ry_param, switch_param_a, switch_param_b, v_param,
                                      N_LIST, D_LAYER, A_LAYER, checkpoint_collect_container, MFPT_snapshots,
                                      mass_retention_threshold=0.01, mass_checkpoint=10**6, domain_radius=1.0, D=1.0, d_tube=0.0):
    if ENABLE_JIT:
        print("Running optimized version.")

    dRad = num.compute_dRad(rg_param, domain_radius)
    dThe = num.compute_dThe(ry_param)
    dT = num.compute_dT(rg_param, ry_param, domain_radius, D)
    central_patch = num.compute_init_cond_cent(rg_param, domain_radius)
    v_param *= -1

    d_list = struct_init.build_d_tube_mapping_no_overlap(rg_param, ry_param, N_LIST, d_tube, domain_radius)

    MFPT = 0
    mass_retained = 0

    checkpoint_iter = 0

    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > mass_retention_threshold:

        net_current_out = 0

        net_current_out += num.comp_DL_AL_kp1_2step(ry_param, rg_param, d_list, D_LAYER, central_patch, A_LAYER, N_LIST,
                                                    dRad, dThe, dT, switch_param_a, switch_param_b, v_param, d_tube)
        if k > 0 and k % mass_checkpoint == 0:
            print("Velocity (V)= ", v_param, "Time step: ", k, "Simulation time: ", k * dT, "Current mass: ",
                  mass_retained,
                  "a=", switch_param_a, "b=", switch_param_b)

        MFPT += net_current_out * k * dT ** 2

        if checkpoint_iter < len(checkpoint_collect_container):
            curr_mass_stamp = checkpoint_collect_container[checkpoint_iter]
            if curr_mass_stamp * 0.99 < mass_retained < curr_mass_stamp * 1.01:
                MFPT_snapshots[checkpoint_iter] = MFPT
                checkpoint_iter += 1
        else:
            return

        mass_retained = num.calc_mass(D_LAYER, A_LAYER, 0, dRad, dThe, central_patch, rg_param, ry_param,
                                      N_LIST)
        central_patch = num.u_center(D_LAYER, 0, dRad, dThe, dT, central_patch, A_LAYER, N_LIST, v_param)

        D_LAYER[0] = D_LAYER[1]
        A_LAYER[0] = A_LAYER[1]
        # transfer updated density info from the next step to the current
        # num.update_layer_inplace(diffusive_layer[0], diffusive_layer[1], rays, rings)
        # num.update_layer_inplace(advective_layer[0], advective_layer[1], rays, rings)
        k += 1

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# (****) (****)
@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def comp_mfpt_by_time_points_time_dep(rg_param, ry_param, switch_param_a, switch_param_b, v_param,
                                      N_LIST, D_LAYER, A_LAYER, checkpoint_collect_container, MFPT_snapshots,
                                      T_param, mass_checkpoint=10**6, domain_radius=1.0, D=1.0, d_tube=0.0):
    if ENABLE_JIT:
        print("Running optimized version.")

    dRad = num.compute_dRad(rg_param, domain_radius)
    dThe = num.compute_dThe(ry_param)
    dT = num.compute_dT(rg_param, ry_param, domain_radius, D)
    K = num.compute_K(rg_param, ry_param, T_param, domain_radius, D)
    central_patch = num.compute_init_cond_cent(rg_param, domain_radius)
    v_param *= -1

    d_list = struct_init.build_d_tube_mapping_no_overlap(rg_param, ry_param, N_LIST, d_tube, domain_radius)

    MFPT = 0
    mass_retained = 0

    checkpoint_iter = 0

    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k < K:

        net_current_out = 0

        net_current_out += num.comp_DL_AL_kp1_2step(ry_param, rg_param, d_list, D_LAYER, central_patch, A_LAYER, N_LIST,
                                                    dRad, dThe, dT, switch_param_a, switch_param_b, v_param, d_tube)
        if k > 0 and k % mass_checkpoint == 0:
            print("Velocity (V)= ", v_param, "Time step: ", k, "Simulation time: ", k * dT, "Current mass: ",
                  mass_retained,
                  "a=", switch_param_a, "b=", switch_param_b)

        MFPT += net_current_out * k * dT ** 2

        if checkpoint_iter < len(checkpoint_collect_container):
            curr_stamp = np.floor(checkpoint_collect_container[checkpoint_iter] / dT)
            if k == curr_stamp:
                MFPT_snapshots[checkpoint_iter] = MFPT
                checkpoint_iter += 1
        else:
            return

        mass_retained = num.calc_mass(D_LAYER, A_LAYER, 0, dRad, dThe, central_patch, rg_param, ry_param,
                                      N_LIST)
        central_patch = num.u_center(D_LAYER, 0, dRad, dThe, dT, central_patch, A_LAYER, N_LIST, v_param)

        D_LAYER[0] = D_LAYER[1]
        A_LAYER[0] = A_LAYER[1]
        # transfer updated density info from the next step to the current
        # num.update_layer_inplace(diffusive_layer[0], diffusive_layer[1], rays, rings)
        # num.update_layer_inplace(advective_layer[0], advective_layer[1], rays, rings)
        k += 1

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -




# To be potentially wiped in a future update 8-8-25 10:39 AM @Kevin
# # (****) (****)
# @njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
# def comp_mfpt_by_mass_loss(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer,
#                            mass_checkpoint=10 ** 6, r=1.0, d=1.0, mass_retention_threshold=0.01):
#     """
#     Computation of Mean First Passage Time using a two-time step scheme such that particle density across the diffusive and advective
#     layers are updated iteratively between two time points, the current and the next. MFPT is integrated numerically by summing
#     radial segments of patches across the last ring before the absorbing boundary. The calculation will terminate after the
#     mass_retention_threshold has been reached. (Run until mass_retention_threshold amount of mass remains)
#
#     The center patch is considered separately from both diffusive and advective layers as variable, phi_center.
#
#     The absorbing boundary condition is set at the (m-1)th ring within the domain, where particle density is set to 0 at this position for all
#     angular rays 'n'.
#
#     Refer to project_src_package_2025/computational_tools/visual-discretization-demos for more details on the discretization scheme, absorbing boundary condition,
#     array representation of the diffusive/advective layers, and placement of microtubules/filaments across the domain.
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
#     :param mass_checkpoint: (float) used to print biophysical metrics onto screen after evey mass_checkpoint number of time-steps,
#     by default, mass_checkpoint=10**6
#
#     :param r: (float) cellular radius, by default r=1.
#     :param d: (float) diffusion constant, by default d=1
#     :param mass_retention_threshold: (float) the amount of mass remaining in the domain until termination
#     :return: a tuple, [(float), (float)]. The first being Mean First Passage Time (m_f_p_t), and the second being Simulation Time (duration)
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
#     m_f_p_t = 0
#
#     # main bulk of the numerical solution for calculating MFPT
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
#             n = 0
#             while n < rays:
#                 # absorbing boundary condition
#                 if m == rings - 1:
#                     diffusive_layer[1][m][n] = 0
#                 else:
#                     diffusive_layer[1][m][n] = num.u_density(diffusive_layer, 0, m, n, d_radius, d_theta, d_time,
#                                                              phi_center, rings, advective_layer, angle_index,
#                                                              a, b, tube_placements)
#                     if n == tube_placements[angle_index]:
#                         advective_layer[1][m][n] = num.u_tube(advective_layer, diffusive_layer, 0, m, n, a, b, v,
#                                                               d_time,
#                                                               d_radius, d_theta)
#                         if angle_index < len(tube_placements) - 1:
#                             angle_index = angle_index + 1
#
#                 if m == rings - 2:
#                     # incrementally calculating the amount of mass exiting from the final ring at the current time-step
#                     net_current_out += num.j_r_r(diffusive_layer, 0, m, n, d_radius, 0) * rings * d_radius * d_theta
#                 n += 1
#             m += 1
#
#         m_f_p_t += net_current_out * k * d_time * d_time
#
#         k += 1
#         # Implemented to provide occasional status checks/metrics during MFPT calculation
#         if k > 0 and k % mass_checkpoint == 0:
#             print("Velocity (V)= ", v, "Time step: ", k, "Simulation time: ", k * d_time, "Current mass: ",
#                   mass_retained,
#                   "a=", a, "b=", b)
#
#         mass_retained = num.calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center,
#                                       rings, rays, tube_placements)
#         phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center,
#                                   advective_layer, tube_placements, v)
#
#         # transfer updated density info from the next step to the current
#         diffusive_layer[0] = diffusive_layer[1]
#         advective_layer[0] = advective_layer[1]
#     # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     # calculate the sim-time
#     duration = k * d_time
#
#     return m_f_p_t, duration
