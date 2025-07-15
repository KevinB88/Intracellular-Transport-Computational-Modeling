from . import math, njit, numerical_tools as num, sys_config, supplements as sup, np, struct_init as strc
from numba.typed import List
from numba import int64


ENABLE_JIT = sys_config.ENABLE_NJIT
ENABLE_CACHE = sys_config.ENABLE_NUMBA_CACHING


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def comp_mass_loss_glb_pk(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer, r=1.0, d=1.0,
                          mass_retention_threshold=0.01):
    """

    Prints biophysical metrics including MFPT and the dimensionless time taken to reach the global-maximum of the mass-loss-rate as a
    function of time, J(t).

    :param rings: (float) # of radial rings in the cellular domain
    :param rays: (float) # of angular rays in the cellular domain
    :param a: (float) the switch rate onto the diffusive layer
    :param b: (float) the switch rate onto the advective layer
    :param v: (float) particle velocity on microtubules/filaments
    :param tube_placements: (list(int)) discrete microtubule/filament positions between [0, rays-1]

    :param diffusive_layer: [np.zeros((2, rings, rays), dtype=np.float64)] a 2 * rings * ray container to collect density at the diffusive layer
    :param advective_layer: [np.zeros((2, rings, rays), dtype=np.float64)] a 2 * rings * ray container to collect density at the advective layer

    :param r: (float) cellular radius, by default r=1.
    :param d: (float) diffusion constant, by default d=1
    :param mass_retention_threshold: (float) the amount of mass remaining in the domain until termination
    :param mixed_config (bool) toggling the mixed configuration
    :return: void
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
    # Mean first passage time
    m_f_p_t = 0

    mass_loss_step_i = 0
    mass_loss_step_i_plus = 0

    diff_special_angles = np.empty(rays, dtype=np.int64)

    # if mixed_config:
    #     diff_special_angles = sup.mod_range_flat_sorted(tube_placements, 1, rays)

    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > mass_retention_threshold:

        net_current_out = 0

        m = 0

        while m < rings:
            angle_index = 0

            if m == rings - 2:
                if k % 2 == 0:
                    mass_loss_step_i = num.calc_loss_mass_j_r_r(diffusive_layer, 0, d_radius, d_theta, rings, rays)
                else:
                    mass_loss_step_i_plus = num.calc_loss_mass_j_r_r(diffusive_layer, 0, d_radius, d_theta, rings, rays)
                if k > 0 and k % 2 != 0:
                    if mass_loss_step_i > mass_loss_step_i_plus:
                        print("Mass loss J(t) global peak time (in dimensional units): ", (k - 1) * d_time,
                              "# time steps: ", k - 1, "MFPT: ", m_f_p_t)
                        return
            n = 0
            while n < rays:
                if m == rings - 1:
                    diffusive_layer[1][m][n] = 0
                else:
                    diffusive_layer[1][m][n] = num.u_density(diffusive_layer, 0, m, n, d_radius, d_theta, d_time,
                                                             phi_center, rings, advective_layer, angle_index, a,
                                                             b,
                                                             tube_placements)
                    if n == tube_placements[angle_index]:
                        advective_layer[1][m][n] = num.u_tube(advective_layer, diffusive_layer, 0, m, n, a, b, v,
                                                              d_time, d_radius, d_theta)
                        if angle_index < len(tube_placements) - 1:
                            angle_index = angle_index + 1
                if m == rings - 2:
                    net_current_out += num.j_r_r(diffusive_layer, 0, m, n, d_radius, 0) * rings * d_radius * d_theta
                n += 1
            m += 1

        m_f_p_t += net_current_out * k * d_time * d_time
        k += 1

        mass_retained = num.calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays,
                                      tube_placements)
        phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer,
                                  tube_placements, v)
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
# Collecting a snapshot of the domain at a specified stamp, which can be used in heat map plots
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
                                                                      d_time, phi_center, rings, advective_layer, int(d_list[m][n]), a, b, j_max)

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
        k += 1

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

            # determine if k * d_time is in (time_point - epsilon, time_point + epsilon)
            # if i < len(time_point_container) and (time_point_container[i] * 0.95) < k * d_time < (time_point_container[i] * 1.05):
            #     domain_center_container[i] = phi_center
            #     domain_snapshot_container[i] = diffusive_layer[0]
            #     if compute_mfpt:
            #         mfpt_container[i] = MFPT
            #     i = i + 1
            # else:
            #     return

            if i < len(time_point_container):
                time_point = time_point_container[i]
                epsilon = time_point * 0.05
            else:
                return

            if time_point - epsilon < k * d_time < time_point + epsilon:
                domain_center_container[i] = phi_center
                domain_snapshot_container[i] = diffusive_layer[0]
                if compute_mfpt:
                    mfpt_container[i] = MFPT
                i = i + 1

        else:
            raise ValueError(f'{approach} is not a valid argument, use either collection approach "1" or "2" (must be an int)')

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


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def comp_until_mass_depletion(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer, r=1.0, d=1.0,
                              mass_retention_threshold=0.01, mixed_config=False, d_tube=-1):
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

    # *** Mixed configuration block 5/27/25
    d_list = List()
    # *** Mixed configuration block 5/28/25
    if mixed_config:

        if d_tube <= 0:
            d_tube = sup.solve_d_rect(1, rings, rays, sup.j_max_bef_overlap(rays, tube_placements), 0)

        for m in range(rings):
            j_max = math.floor((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
            # print(j_max)
            if j_max < 0:
                j_max = 0
            keys = sup.mod_range_flat(tube_placements, j_max, rays, False)
            d = sup.dict_gen(keys, tube_placements)
            d_list.append(d)
    # *** Mixed configuration block 5/28/25

    # return

    mass_retained = 0
    # Mean first passage time

    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > mass_retention_threshold:

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
                    if mixed_config and n in d_list[m]:
                        j_max = math.floor((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
                        if j_max < 0:
                            j_max = 0
                        # diffusive_layer[1][m][n] = num.u_density_mixed(diffusive_layer, 0, m, n, d_radius, d_theta,
                        #                                                d_time,
                        #                                                phi_center, rings, advective_layer,
                        #                                                int(d_list[m][n]), a, b)
                        diffusive_layer[1][m][n] = num.u_density_rect(diffusive_layer, 0, m, n, d_radius, d_theta,
                                                                      d_time,
                                                                      phi_center, rings, advective_layer,
                                                                      int(d_list[m][n]), a, b, j_max)
                    else:
                        diffusive_layer[1][m][n] = num.u_density(diffusive_layer, 0, m, n, d_radius, d_theta,
                                                                 d_time,
                                                                 phi_center, rings, advective_layer,
                                                                 aIdx,
                                                                 a, b,
                                                                 tube_placements)

                    if n == tube_placements[aIdx]:
                        if mixed_config:
                            j_max = math.floor((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
                            if j_max < 0:
                                j_max = 0
                            # advective_layer[1][m][n] = num.u_tube_mixed(advective_layer, diffusive_layer, 0, m, n,
                            #                                             a, b,
                            #                                             v,
                            #                                             d_time, d_radius, d_theta, mx_cn_rrange)
                            advective_layer[1][m][n] = num.u_tube_rect(advective_layer, diffusive_layer, 0, m, n,
                                                                       a, b, v, d_time, d_radius, d_theta, j_max)
                        else:
                            advective_layer[1][m][n] = num.u_tube(advective_layer, diffusive_layer, 0, m, n, a, b,
                                                                  v,
                                                                  d_time, d_radius, d_theta)
                        if aIdx < len(tube_placements) - 1:
                            aIdx += 1
                n += 1
            m += 1
        # ***********************
        k += 1
        mass_retained = num.calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays,
                                      tube_placements)
        phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer,
                                  tube_placements, v)
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
    return k * d_time


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
# Collecting a snapshot of density across angles (labeled as discrete positions from 0 to N) on a ring (position specified via params)
def comp_diffusive_angle_snapshots(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer,
                                   phi_v_theta_snapshot_container, approach, m_segment=0.5, r=1.0, d=1.0,
                                   mass_retention_threshold=0.01,
                                   time_point_container=None, mass_checkpoint=10 ** 16, mixed_config=False,
                                   d_tube=-1):
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

    # *** Mixed configuration block 5/27/25
    d_list = List()
    if mixed_config:

        if d_tube <= 0:
            d_tube = sup.solve_d_rect(1, rings, rays, sup.j_max_bef_overlap(rays, tube_placements), 0)

        for m in range(rings):
            j_max = math.floor((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
            # print(j_max)
            if j_max < 0:
                j_max = 0
            keys = sup.mod_range_flat(tube_placements, j_max, rays, False)
            d = sup.dict_gen(keys, tube_placements)
            d_list.append(d)
    # *** Mixed configuration block 5/28/25

    early_flag = False

    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > mass_retention_threshold:

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
                    if mixed_config and n in d_list[m]:

                        j_max = math.floor((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
                        if j_max < 0:
                            j_max = 0

                        diffusive_layer[1][m][n] = num.u_density_rect(diffusive_layer, 0, m, n, d_radius, d_theta, d_time,
                                                                      phi_center, rings, advective_layer, int(d_list[m][n]), a, b, j_max)

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
                    if n == tube_placements[aIdx]:
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
                n += 1
            m += 1
        # ***********************
        k += 1
        if approach == 1:
            # approach 1 collects density profiles within an open interval, where every two points in the time-point container (up to 4) is either a lower or upper bound.
            if time_point_container is None:
                raise ValueError(
                    "Provide time point container which should consist of 4 points: 2 bounds for the early bound, and 2 for the late bound.")
            if time_point_container[0] < k * d_time < time_point_container[1] and early_flag:
                phi_v_theta_snapshot_container[0] = diffusive_layer[0][math.floor(m * m_segment)]
                early_flag = False
            elif time_point_container[2] < k * d_time < time_point_container[3]:
                phi_v_theta_snapshot_container[1] = diffusive_layer[0][math.floor(m * m_segment)]
                break
        elif approach == 2:

            if 0.675 < mass_retained < 0.68:
                phi_v_theta_snapshot_container[0] = diffusive_layer[0][math.floor(m * m_segment)]
            elif 0.45 < mass_retained < 0.46:
                phi_v_theta_snapshot_container[1] = diffusive_layer[0][math.floor(m * m_segment)]
            elif 0.225 < mass_retained < 0.26:
                phi_v_theta_snapshot_container[2] = diffusive_layer[0][math.floor(m * m_segment)]
            elif 0.015 < mass_retained < 0.02:
                phi_v_theta_snapshot_container[3] = diffusive_layer[0][math.floor(m * m_segment)]
                break
        elif approach == 3:
            # approach 3, collects density profiles across angles at specified time points within the time_point_container.
            # please note that this version of the approach may eventually replace approach 1

            if i < len(time_point_container):
                time_point = time_point_container[i]
                epsilon = time_point * 0.05
                # epsilon = time_point * 0.1
            else:
                return

            if time_point - epsilon < k * d_time < time_point + epsilon:
                phi_v_theta_snapshot_container[i] = diffusive_layer[0][math.floor(m * m_segment)]
                i = i + 1
            # labeling this as approach #3, collecting at each individual time point within the container.
            # if the current time point is between an interval (T*k - epsilon, T*k + epsilon) then we collect.
            # epsilon should be 5 - 10 % of the value.
        # else :
        elif approach != 4:
            # temporary condition
            raise ValueError(
                f'{approach} is not a valid argument, use either approach "1", "2", or "3" (must be an int)')

        if k > 0 and k % mass_checkpoint == 0:
            print("Velocity (V)= ", v, "Time step: ", k, "Simulation time: ", k * d_time, "Current mass: ",
                  mass_retained,
                  "a=", a, "b=", b)

        mass_retained = num.calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays,
                                      tube_placements)
        phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer,
                                  tube_placements, v)
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]

    # collect for every other ring for an even number of rings, after the mass depletion threshold has been reached
    if approach == 4:
        for i in range(rings / 2):
            phi_v_theta_snapshot_container[i] = diffusive_layer[0][i * 2]


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def comp_mass_analysis_respect_to_time(rings, rays, a, b, v, T, tube_placements, diffusive_layer, advective_layer,
                                       diff_mass, adv_mass, adv_over_total, adv_over_initial,
                                       total_mass,
                                       collection_width, mass_checkpoint=10 ** 6, r=1.0, d=1.0, mixed_config=False,
                                       d_tube=-1, collect_MFPT=False):
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
    K = math.floor(T / d_time)

    phi_center = 1 / (math.pi * (d_radius * d_radius))

    total_domain_mass = 1
    diffusive_mass = total_domain_mass
    advective_mass = 0

    relative_k = math.floor(K / collection_width)
    k_prime = 0

    d_list = List()

    # *** Mixed configuration block 6/10/25
    if mixed_config:

        if d_tube < 0:
            d_tube = sup.solve_d_rect(1, rings, rays, sup.j_max_bef_overlap(rays, tube_placements), 0)

        for m in range(rings):
            j_max = math.ceil((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
            # print("Ring: ", m, "j_max: ", j_max)
            keys = sup.mod_range_flat(tube_placements, j_max, rays, False)
            dict_ = sup.dict_gen(keys, tube_placements)
            d_list.append(dict_)

        # D = strc.build_rect_config_dict(rings, rays, tube_placements, d_theta, d_radius, d_tube)

    # *** Mixed configuration block 6/10/25

    MFPT = 0
    net_current_out = 0

    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k < K:

        if collect_MFPT:
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
                    # if mixed_config and n in D[m]:
                    if mixed_config and n in d_list[m]:

                        diffusive_layer[1][m][n] = num.u_density_rect(diffusive_layer, 0, m, n, d_radius, d_theta,
                                                                      d_time,
                                                                      phi_center, rings, advective_layer,
                                                                      int(d_list[m][n]), a, b, d_tube)
                        #
                        # diffusive_layer[1][m][n] = num.u_density_rect_v2(diffusive_layer, 0, m, n, d_radius, d_theta,
                        #                                               d_time,
                        #                                               phi_center, rings, advective_layer,
                        #                                               a, b, d_tube, D[m][n])
                    else:
                        diffusive_layer[1][m][n] = num.u_density(diffusive_layer, 0, m, n, d_radius, d_theta,
                                                                 d_time,
                                                                 phi_center, rings, advective_layer,
                                                                 aIdx,
                                                                 a, b,
                                                                 tube_placements)
                    if n == tube_placements[aIdx]:
                        if mixed_config:

                            # j_max = math.ceil((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)

                            advective_layer[1][m][n] = num.u_tube_rect(advective_layer, diffusive_layer, 0, m, n,
                                                                       a, b,
                                                                       v,
                                                                       d_time, d_radius, d_theta, d_tube)

                        else:
                            advective_layer[1][m][n] = num.u_tube(advective_layer, diffusive_layer, 0, m, n, a, b,
                                                                  v,
                                                                  d_time, d_radius, d_theta)
                        if aIdx < len(tube_placements) - 1:
                            aIdx += 1
                if collect_MFPT:
                    if m == rings - 2:
                        net_current_out += num.j_r_r(diffusive_layer, 0, m, n, d_radius, 0) * rings * d_radius * d_theta

                n += 1
            m += 1
        # *****************************************************************************************************************

        if collect_MFPT:
            MFPT += net_current_out * k * d_time * d_time

        if k_prime < relative_k and k % collection_width == 0:
            diff_mass[k_prime] = diffusive_mass
            adv_mass[k_prime] = advective_mass
            total_mass[k_prime] = diffusive_mass + advective_mass
            adv_over_total[k_prime] = advective_mass / total_mass[k_prime]
            adv_over_initial[k_prime] = advective_mass / d

            k_prime += 1

        k += 1
        # Implemented to provide occasional status checks/metrics during MFPT calculation
        if k > 0 and k % mass_checkpoint == 0:
            print("Velocity (V)= ", v, "Time step: ", k, "Simulation time: ", k * d_time, "Current mass: ",
                  diffusive_mass,
                  "a=", a, "b=", b)

        diffusive_mass = num.calc_mass_diff(diffusive_layer, 0, d_radius, d_theta, phi_center, rings, rays)
        advective_mass = num.calc_mass_adv(advective_layer, 0, d_radius, d_theta, rings, tube_placements)
        # total_domain_mass = diffusive_mass + advective_mass

        phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center,
                                  advective_layer, tube_placements, v)

        # transfer updated density info from the next step to the current
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    if collect_MFPT:
        print('MFPT: ', MFPT)


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
# Collecting density across the diffusive and advective layers with respect to radius
# The 'fixed_angle' parameter must be provided as an integer denoting the angle/positioning on the discretized domain
def comp_diffusive_rad_snapshots(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer,
                                 fixed_angle, phi_rad_container, rho_rad_container, time_point_container, r=1.0, d=1.0,
                                 mass_retention_threshold=0.01, mass_checkpoint=10 ** 6, mixed_config=False, d_tube=-1):
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

    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0
    i = 0
    mass_retained = 0

    # *** Mixed configuration block 5/27/25
    d_list = List()

    # *** Mixed configuration block 5/28/25
    if mixed_config:

        if d_tube <= 0:
            d_tube = sup.solve_d_rect(1, rings, rays, sup.j_max_bef_overlap(rays, tube_placements), 0)

        for m in range(rings):
            j_max = math.floor((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
            # print(j_max)
            if j_max < 0:
                j_max = 0
            keys = sup.mod_range_flat(tube_placements, j_max, rays, False)
            d = sup.dict_gen(keys, tube_placements)
            d_list.append(d)
    # *** Mixed configuration block 5/28/25

    while k == 0 or mass_retained > mass_retention_threshold:

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
                    if mixed_config and n in d_list[m]:

                        j_max = math.floor((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
                        if j_max < 0:
                            j_max = 0

                        diffusive_layer[1][m][n] = num.u_density_rect(diffusive_layer, 0, m, n, d_radius, d_theta, d_time,
                                                                      phi_center, rings, advective_layer, int(d_list[m][n]), a, b, j_max)

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
                    if n == tube_placements[aIdx]:
                        if mixed_config:

                            j_max = math.floor((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)
                            if j_max < 0:
                                j_max = 0

                            advective_layer[1][m][n] = num.u_tube_rect(advective_layer, diffusive_layer, 0, m,
                                                                       n, a, b, v, d_time, d_radius, d_theta, rings, j_max)

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

                n += 1
            m += 1
        # ***********************
        k += 1

        if k > 0 and k % mass_checkpoint == 0:
            print("Velocity (V)= ", v, "Time step: ", k, "Simulation time: ", k * d_time, "Current mass: ",
                  mass_retained,
                  "a=", a, "b=", b)

        # ***********************************************************
        if i < len(time_point_container):
            time_point = time_point_container[i]
            epsilon = time_point * 0.05
            # epsilon = time_point * 0.1
        else:
            return

        if time_point - epsilon < k * d_time < time_point + epsilon:

            phi_rad_container[i][0] = phi_center

            for m in range(rings):
                phi_rad_container[i][m + 1] = diffusive_layer[0][m][fixed_angle]
                rho_rad_container[i][m] = advective_layer[0][m][fixed_angle]

            i = i + 1
        # ***********************************************************

        mass_retained = num.calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays,
                                      tube_placements)
        phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer,
                                  tube_placements, v)
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
