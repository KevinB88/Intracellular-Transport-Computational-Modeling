from . import njit, math, numerical_tools as num, sys_config, supplements as sup, np
# import time
from project_src_package_2025.computational_tools import struct_init

from numba.typed import Dict, List
from numba import int64

ENABLE_JIT = sys_config.ENABLE_NJIT
ENABLE_CACHE = sys_config.ENABLE_NUMBA_CACHING


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
        # <<<< ------------- Updating DL and AL for the K+1-th step ------------- >>>>
        m = 0

        while m < rg_param:

            # The advective angle index 'aIdx'
            aIdx = 0
            n = 0

            while n < ry_param:
                if m == rg_param - 1:
                    D_LAYER[1][m][n] = 0
                else:
                    if n in d_list[m]:
                        # n denotes a discrete position (an extraction region ray) within an extraction region centered at a microtubule (indices contained in N_LIST)
                        # if the iteration steps on an extraction region ray at ring m, then:
                        # int(d_list[m][n]) is the corresponding microtubule position of the extraction region ray (n) at ring (m)
                        corr_MT_pos = int(d_list[m][n])
                        D_LAYER[1][m][n] = num.u_density_rect(D_LAYER, 0, m, n, dRad, dThe,
                                                              dT,
                                                              central_patch, rg_param, A_LAYER,
                                                              corr_MT_pos, switch_param_a, switch_param_b, d_tube)

                    else:
                        D_LAYER[1][m][n] = num.u_density(D_LAYER, 0, m, n, dRad, dThe,
                                                         dT,
                                                         central_patch, rg_param, A_LAYER,
                                                         aIdx,
                                                         switch_param_a, switch_param_b,
                                                         N_LIST)
                    if n == N_LIST[aIdx]:

                        A_LAYER[1][m][n] = num.u_tube_rect(A_LAYER, D_LAYER, 0, m, n, switch_param_a,
                                                           switch_param_b, v_param, dT, dRad, dThe, d_tube)
                        if aIdx < len(N_LIST) - 1:
                            aIdx += 1

                    if m == rg_param - 2:
                        net_current_out += num.j_r_r(D_LAYER, 0, m, n, dRad, 0) * rg_param * dRad * dThe
                n += 1
            m += 1
        # <<<< ------------- Updating DL and AL for the K+1-th step ------------- >>>>

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
def comp_mfpt_by_time_points(rg_param, ry_param, switch_param_a, switch_param_b, v_param, N_LIST, D_LAYER, A_LAYER,
                             Timestamp_LIST,
                             MFPT_snapshots,
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

    timestamp = 0

    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k < K:

        net_current_out = 0
        m = 0

        # **************************************************************************************************
        while m < rg_param:

            # The advective angle index 'aIdx'
            aIdx = 0
            n = 0

            while n < ry_param:
                if m == rg_param - 1:
                    D_LAYER[1][m][n] = 0
                else:

                    # **********************************************************************************************************************************************
                    if n in d_list[m]:

                        D_LAYER[1][m][n] = num.u_density_rect(D_LAYER, 0, m, n, dRad, dThe,
                                                              dT,
                                                              central_patch, rg_param, A_LAYER,
                                                              int(d_list[m][n]), switch_param_a, switch_param_b, d_tube)

                    else:
                        D_LAYER[1][m][n] = num.u_density(D_LAYER, 0, m, n, dRad, dThe,
                                                         dT,
                                                         central_patch, rg_param, A_LAYER,
                                                         aIdx,
                                                         switch_param_a, switch_param_b,
                                                         N_LIST)
                    if n == N_LIST[aIdx]:

                        A_LAYER[1][m][n] = num.u_tube_rect(A_LAYER, D_LAYER, 0, m, n, switch_param_a,
                                                           switch_param_b, v_param, dT, dRad, dThe, d_tube)
                        if aIdx < len(N_LIST) - 1:
                            aIdx += 1

                    if m == rg_param - 2:
                        net_current_out += num.j_r_r(D_LAYER, 0, m, n, dRad, 0) * rg_param * dRad * dThe
                n += 1
            m += 1
        # *****************************************************************************************************************

        if k > 0 and k % mass_checkpoint == 0:
            print("Velocity (V)= ", v_param, "Time step: ", k, "Simulation time: ", k * dT, "Current mass: ",
                  mass_retained,
                  "a=", switch_param_a, "b=", switch_param_b)

        MFPT += net_current_out * k * dT ** 2

        if timestamp < len(Timestamp_LIST):
            curr_stamp = np.floor(Timestamp_LIST[timestamp] / dT)
            if k == curr_stamp:
                MFPT_snapshots[timestamp] = MFPT
                timestamp += 1
        else:
            return

        mass_retained = num.calc_mass(D_LAYER, A_LAYER, 0, dRad, dThe, central_patch, rg_param, ry_param,
                                      N_LIST)
        phi_center = num.u_center(D_LAYER, 0, dRad, dThe, dT, central_patch, A_LAYER,
                                  N_LIST, v_param)

        D_LAYER[0] = D_LAYER[1]
        A_LAYER[0] = A_LAYER[1]
        # transfer updated density info from the next step to the current
        # num.update_layer_inplace(diffusive_layer[0], diffusive_layer[1], rays, rings)
        # num.update_layer_inplace(advective_layer[0], advective_layer[1], rays, rings)
        k += 1

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def comp_mfpt_by_mass_loss(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer,
                           mass_checkpoint=10 ** 6, r=1.0, d=1.0, mass_retention_threshold=0.01):
    """
    Computation of Mean First Passage Time using a two-time step scheme such that particle density across the diffusive and advective
    layers are updated iteratively between two time points, the current and the next. MFPT is integrated numerically by summing
    radial segments of patches across the last ring before the absorbing boundary. The calculation will terminate after the
    mass_retention_threshold has been reached. (Run until mass_retention_threshold amount of mass remains)

    The center patch is considered separately from both diffusive and advective layers as variable, phi_center.

    The absorbing boundary condition is set at the (m-1)th ring within the domain, where particle density is set to 0 at this position for all
    angular rays 'n'.

    Refer to project_src_package_2025/computational_tools/visual-discretization-demos for more details on the discretization scheme, absorbing boundary condition,
    array representation of the diffusive/advective layers, and placement of microtubules/filaments across the domain.

    :param rings: (float) # of radial rings in the cellular domain
    :param rays: (float) # of angular rays in the cellular domain
    :param a: (float) the switch rate onto the diffusive layer
    :param b: (float) the switch rate onto the advective layer
    :param v: (float) particle velocity on microtubules/filaments
    :param tube_placements: (list(int)) discrete microtubule/filament positions between [0, rays-1]

    :param diffusive_layer: [np.zeros((2, rings, rays), dtype=np.float64)] a 2 * rings * ray container to collect density at the diffusive layer
    :param advective_layer: [np.zeros((2, rings, rays), dtype=np.float64)] a 2 * rings * ray container to collect density at the advective layer

    :param mass_checkpoint: (float) used to print biophysical metrics onto screen after evey mass_checkpoint number of time-steps,
    by default, mass_checkpoint=10**6

    :param r: (float) cellular radius, by default r=1.
    :param d: (float) diffusion constant, by default d=1
    :param mass_retention_threshold: (float) the amount of mass remaining in the domain until termination
    :return: a tuple, [(float), (float)]. The first being Mean First Passage Time (m_f_p_t), and the second being Simulation Time (duration)
    """

    if ENABLE_JIT:
        print("Running optimized version.")

    if len(tube_placements) > rays:
        raise IndexError(
            f'Too many microtubules requested: {len(tube_placements)}, within domain of {rays} angular rays.')

    for i in range(len(tube_placements)):
        if tube_placements[i] < 0 or tube_placements[i] > rays:
            raise IndexError(f'Angle {tube_placements[i]} is out of bounds, your range should be [0, {rays - 1}]')

    d_radius = r / rings
    d_theta = ((2 * math.pi) / rays)
    d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / (2 * d)

    phi_center = 1 / (math.pi * (d_radius * d_radius))

    mass_retained = 0
    m_f_p_t = 0

    # main bulk of the numerical solution for calculating MFPT
    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > mass_retention_threshold:

        net_current_out = 0

        m = 0

        while m < rings:
            angle_index = 0
            n = 0
            while n < rays:
                # absorbing boundary condition
                if m == rings - 1:
                    diffusive_layer[1][m][n] = 0
                else:
                    diffusive_layer[1][m][n] = num.u_density(diffusive_layer, 0, m, n, d_radius, d_theta, d_time,
                                                             phi_center, rings, advective_layer, angle_index,
                                                             a, b, tube_placements)
                    if n == tube_placements[angle_index]:
                        advective_layer[1][m][n] = num.u_tube(advective_layer, diffusive_layer, 0, m, n, a, b, v,
                                                              d_time,
                                                              d_radius, d_theta)
                        if angle_index < len(tube_placements) - 1:
                            angle_index = angle_index + 1

                if m == rings - 2:
                    # incrementally calculating the amount of mass exiting from the final ring at the current time-step
                    net_current_out += num.j_r_r(diffusive_layer, 0, m, n, d_radius, 0) * rings * d_radius * d_theta
                n += 1
            m += 1

        m_f_p_t += net_current_out * k * d_time * d_time

        k += 1
        # Implemented to provide occasional status checks/metrics during MFPT calculation
        if k > 0 and k % mass_checkpoint == 0:
            print("Velocity (V)= ", v, "Time step: ", k, "Simulation time: ", k * d_time, "Current mass: ",
                  mass_retained,
                  "a=", a, "b=", b)

        mass_retained = num.calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center,
                                      rings, rays, tube_placements)
        phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center,
                                  advective_layer, tube_placements, v)

        # transfer updated density info from the next step to the current
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # calculate the sim-time
    duration = k * d_time

    return m_f_p_t, duration


# using the rectangular modification for DL update

@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def comp_mfpt_by_mass_loss_rect(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer,
                                mass_checkpoint=10 ** 6, r=1.0, d=1.0, mass_retention_threshold=0.01,
                                mixed_config=False, d_tube=-1):
    """
    Computation of Mean First Passage Time using a two-time step scheme such that particle density across the diffusive and advective
    layers are updated iteratively between two time points, the current and the next. MFPT is integrated numerically by summing
    radial segments of patches across the last ring before the absorbing boundary. The calculation will terminate after the
    mass_retention_threshold has been reached. (Run until mass_retention_threshold amount of mass remains)

    The center patch is considered separately from both diffusive and advective layers as variable, phi_center.

    The absorbing boundary condition is set at the (m-1)th ring within the domain, where particle density is set to 0 at this position for all
    angular rays 'n'.

    Refer to project_src_package_2025/computational_tools/visual-discretization-demos for more details on the discretization scheme, absorbing boundary condition,
    array representation of the diffusive/advective layers, and placement of microtubules/filaments across the domain.

    :param rings: (float) # of radial rings in the cellular domain
    :param rays: (float) # of angular rays in the cellular domain
    :param a: (float) the switch rate onto the diffusive layer
    :param b: (float) the switch rate onto the advective layer
    :param v: (float) particle velocity on microtubules/filaments
    :param tube_placements: (list(int)) discrete microtubule/filament positions between [0, rays-1]

    :param diffusive_layer: [np.zeros((2, rings, rays), dtype=np.float64)] a 2 * rings * ray container to collect density at the diffusive layer
    :param advective_layer: [np.zeros((2, rings, rays), dtype=np.float64)] a 2 * rings * ray container to collect density at the advective layer

    :param mass_checkpoint: (float) used to print biophysical metrics onto screen after evey mass_checkpoint number of time-steps,
    by default, mass_checkpoint=10**6

    :param r: (float) cellular radius, by default r=1.
    :param d: (float) diffusion constant, by default d=1
    :param mass_retention_threshold: (float) the amount of mass remaining in the domain until termination
    :param mixed_config (bool)
    :param d_tube (float)
    :return: a tuple, [(float), (float)]. The first being Mean First Passage Time (m_f_p_t), and the second being Simulation Time (duration)
    """

    if ENABLE_JIT:
        print("Running optimized version.")

    if len(tube_placements) > rays:
        raise IndexError(
            f'Too many microtubules requested: {len(tube_placements)}, within domain of {rays} angular rays.')

    for i in range(len(tube_placements)):
        if tube_placements[i] < 0 or tube_placements[i] > rays:
            raise IndexError(f'Angle {tube_placements[i]} is out of bounds, your range should be [0, {rays - 1}]')

    d_radius = r / rings
    d_theta = ((2 * math.pi) / rays)
    d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / (2 * d)

    phi_center = 1 / (math.pi * (d_radius * d_radius))

    mass_retained = 0
    m_f_p_t = 0

    d_list = List()

    # *** Mixed configuration block 5/28/25
    if mixed_config:

        for m in range(rings):
            j_max = math.ceil((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)

            keys = sup.mod_range_flat(tube_placements, j_max, rays, False)
            d = sup.dict_gen(keys, tube_placements)
            d_list.append(d)
    # *** Mixed configuration block 5/28/25

    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > mass_retention_threshold:

        net_current_out = 0
        m = 0

        # **************************************************************************************************
        while m < rings:

            # The advective angle index 'aIdx'
            aIdx = 0
            n = 0

            while n < rays:
                if m == rings - 1:
                    diffusive_layer[1][m][n] = 0
                else:

                    # Mixed configuration block 5/28/25
                    # **********************************************************************************************************************************************
                    if mixed_config and n in d_list[m]:

                        j_max = math.ceil((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)

                        diffusive_layer[1][m][n] = num.u_density_rect(diffusive_layer, 0, m, n, d_radius, d_theta,
                                                                      d_time,
                                                                      phi_center, rings, advective_layer,
                                                                      int(d_list[m][n]), a, b, j_max)

                        # diffusive_layer[1][m][n] = num.u_density_mixed(diffusive_layer, 0, m, n, d_radius, d_theta,
                        #                                                d_time,
                        #                                                phi_center, rings, advective_layer,
                        #                                                int(d_list[m][n]), a, b)

                    else:
                        diffusive_layer[1][m][n] = num.u_density(diffusive_layer, 0, m, n, d_radius, d_theta,
                                                                 d_time,
                                                                 phi_center, rings, advective_layer,
                                                                 aIdx,
                                                                 a, b,
                                                                 tube_placements)
                    if n == tube_placements[aIdx]:  # potentially replace this line with a dictionary
                        if mixed_config:
                            j_max = math.floor((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
                            if j_max < 0:
                                j_max = 0

                            advective_layer[1][m][n] = num.u_tube_rect(advective_layer, diffusive_layer, 0, m, n,
                                                                       a, b,
                                                                       v,
                                                                       d_time, d_radius, d_theta, rings, j_max)

                            # advective_layer[1][m][n] = num.u_tube_mixed(advective_layer, diffusive_layer, 0, m, n,
                            #                                             a, b,
                            #                                             v,
                            #                                             d_time, d_radius, d_theta, mx_cn_rrange)
                        else:
                            advective_layer[1][m][n] = num.u_tube(advective_layer, diffusive_layer, 0, m, n, a, b,
                                                                  v,
                                                                  d_time, d_radius, d_theta)
                        if aIdx < len(tube_placements) - 1:
                            aIdx += 1

                    if m == rings - 2:
                        # incrementally calculating the amount of mass exiting from the final ring at the current time-step
                        net_current_out += num.j_r_r(diffusive_layer, 0, m, n, d_radius, 0) * rings * d_radius * d_theta
                n += 1
            m += 1
        # *****************************************************************************************************************

        m_f_p_t += net_current_out * k * d_time * d_time

        k += 1
        # Implemented to provide occasional status checks/metrics during MFPT calculation
        if k > 0 and k % mass_checkpoint == 0:
            print("Velocity (V)= ", v, "Time step: ", k, "Simulation time: ", k * d_time, "Current mass: ",
                  mass_retained,
                  "a=", a, "b=", b)

        mass_retained = num.calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center,
                                      rings, rays, tube_placements)
        phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center,
                                  advective_layer, tube_placements, v)

        # transfer updated density info from the next step to the current
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # calculate the sim-time
    duration = k * d_time

    return m_f_p_t, duration


'''
    Kevin Bedoya
    1/13/25 : 12:21 AM

    Additional features to implement, implement an "execution ID" to each numerical computation executed,
    which will print the exec_ID after some interval of time to track the specific computation that was 
    initialized. Before computing the solution(s), print out a text file containing the expected tasks
    to be completed including their parameters, estimated runtimes, how much memory they will possibly use,
    and which cores they are currently running on. 

    It would also help to include a UI to indicate progress for a specific task.

    Potential implementation, but requires clarification before action. Should there be a safety feature to 
    prevent numerical instability for a small enough domain size for a specific number of microtubules?
    Such as in cases where the domain size is 8x8 and for N=4? Is this type of safeguard necessary to implement?

'''
