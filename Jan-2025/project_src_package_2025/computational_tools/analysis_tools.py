from . import math, njit, numerical_tools as num, sys_config

ENABLE_JIT = sys_config.ENABLE_NJIT

'''
    Computational tools for conducting further analysis on diffusion and advection properties.
    
    Including:
        #1) A function for computing the time to reach the global max of J(t) (mass loss as a function of time using angular currents) 
            comp_mass_loss_glb_pk()
    
        #2) A function to collect numerical snapshots across the whole diffusive layer at different pinpoints (relative to the approach2) 
            comp_diffusive_snapshots()
            
        #3) The same as #2, except with the addition of returning an array of MFPT values at the different pinpoints as well
            comp_diffusive_snapshots_with_mfpt()
'''


@njit(nopython=ENABLE_JIT)
# Compute for the global peak time of mass as a function of time
def comp_mass_loss_glb_pk(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer, r=1, d=1, mass_retention_threshold=0.01):

    if ENABLE_JIT:
        print("Running optimized version.")

    if len(tube_placements) > rays:
        raise IndexError(f'Too many microtubules requested: {len(tube_placements)}, within domain of {rays} angular rays.')

    for i in range(len(tube_placements)):
        if tube_placements[i] < 0 or tube_placements[i] > rays:
            raise IndexError(f'Angle {tube_placements[i]} is out of bounds, your range should be [0, {rays-1}]')

    d_radius = r / rings
    d_theta = ((2 * math.pi) / rays)
    d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / (2 * d)

    phi_center = 1 / (math.pi * (d_radius * d_radius))

    mass_retained = 0
    # Mean first passage time
    m_f_p_t = 0

    mass_loss_step_i = 0
    mass_loss_step_i_plus = 0

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
                        print("Mass loss J(t) global peak time (in dimensional units): ", (k-1)*d_time, "# time steps: ", k-1, "MFPT: ", m_f_p_t)
                        return
            n = 0
            while n < rays:
                if m == rings - 1:
                    diffusive_layer[1][m][n] = 0
                else:
                    diffusive_layer[1][m][n] = num.u_density(diffusive_layer, 0, m, n, d_radius, d_theta, d_time, phi_center, rings, advective_layer, angle_index, a, b, tube_placements)
                    if n == tube_placements[angle_index]:
                        advective_layer[1][m][n] = num.u_tube(advective_layer, diffusive_layer, 0, m, n, a, b, v, d_time, d_radius, d_theta)
                        if angle_index < len(tube_placements)-1:
                            angle_index = angle_index + 1
                if m == rings - 2:
                    net_current_out += num.j_r_r(diffusive_layer, 0, m, n, d_radius, 0) * rings * d_radius * d_theta
                n += 1
            m += 1

        m_f_p_t += net_current_out * k * d_time * d_time
        k += 1

        mass_retained = num.calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays, tube_placements)
        phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer, tube_placements, v)
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@njit(nopython=ENABLE_JIT)
# Collecting a snapshot of the domain at a specified stamp, which can be used in heat map plots
def comp_diffusive_snapshots(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer,
                             domain_snapshot_container, domain_center_container, approach, r=1, d=1,
                             mass_retention_threshold=0.01, time_point_container=None, compute_mfpt=False):

    if ENABLE_JIT:
        print("Running optimized version.")

    if len(tube_placements) > rays:
        raise IndexError(f'Too many microtubules requested: {len(tube_placements)}, within domain of {rays} angular rays.')

    for i in range(len(tube_placements)):
        if tube_placements[i] < 0 or tube_placements[i] > rays:
            raise IndexError(f'Angle {tube_placements[i]} is out of bounds, your range should be [0, {rays-1}]')

    d_radius = r / rings
    d_theta = ((2 * math.pi) / rays)
    d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / (2 * d)

    phi_center = 1 / (math.pi * (d_radius * d_radius))

    mass_retained = 0
    # Mean first passage time
    m_f_p_t = 0
    net_current_out = 0

    early_flag = True
    # To be used in assessing the mass loss rate peak (computing using radial currents)

# **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > mass_retention_threshold:

        if compute_mfpt:
            net_current_out = 0

        m = 0

        while m < rings:
            angle_index = 0
            n = 0
            while n < rays:
                if m == rings - 1:
                    diffusive_layer[1][m][n] = 0
                else:
                    diffusive_layer[1][m][n] = num.u_density(diffusive_layer, 0, m, n, d_radius, d_theta, d_time, phi_center, rings, advective_layer, angle_index, a, b, tube_placements)
                    if n == tube_placements[angle_index]:
                        # Update the associated tube within the dictionary
                        advective_layer[1][m][n] = num.u_tube(advective_layer, diffusive_layer, 0, m, n, a, b, v, d_time, d_radius, d_theta)
                        if angle_index < len(tube_placements)-1:
                            angle_index = angle_index + 1
                if compute_mfpt and m == rings - 2:
                    net_current_out += num.j_r_r(diffusive_layer, 0, m, n, d_radius, 0) * rings * d_radius * d_theta
                n += 1
            m += 1

        if compute_mfpt:
            m_f_p_t += net_current_out * k * d_time * d_time
        k += 1

        '''
        Plotting theta versus phi at velocity peak values:
        choose several rings within the domain (at positions M*1/4, M*1/2, M*3/4), and then collect phi across every angle across that ring.
        (At varying mass amounts within the domain) [0.1 + epsilon, 0.225, 0.45, 0.675]
        '''

        if approach == 1:
            if time_point_container is None:
                raise ValueError("Provide time point container which should consist of 4 points: 2 bounds for the early bound, and 2 for the late bound.")
            if time_point_container[0] < k * d_time < time_point_container[1] and early_flag:
                domain_snapshot_container[0] = diffusive_layer[0]
                domain_center_container[0] = phi_center
                early_flag = False
            elif time_point_container[2] < k * d_time < time_point_container[3]:
                domain_snapshot_container[1] = diffusive_layer[0]
                domain_center_container[1] = phi_center
                if compute_mfpt:
                    duration = k * d_time
                    return m_f_p_t, duration
                break
        elif approach == 2:
            if 0.675 < mass_retained < 0.68:
                domain_snapshot_container[0] = diffusive_layer[0]
                domain_center_container[0] = phi_center
            elif 0.45 < mass_retained < 0.46:
                domain_snapshot_container[1] = diffusive_layer[0]
                domain_center_container[1] = phi_center
            elif 0.225 < mass_retained < 0.26:
                domain_snapshot_container[2] = diffusive_layer[0]
                domain_center_container[2] = phi_center
            elif 0.015 < mass_retained < 0.02:
                domain_snapshot_container[3] = diffusive_layer[0]
                domain_center_container[3] = phi_center
                if compute_mfpt:
                    duration = k * d_time
                    return m_f_p_t, duration
                break
        else:
            raise ValueError(f'{approach} is not a valid argument, use either approach2 "1" or "2" (must be an int)')

        mass_retained = num.calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays, tube_placements)
        phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer, tube_placements, v)
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def comp_until_mass_depletion(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer, r=1, d=1, mass_retention_threshold=0.01):
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

    # **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > mass_retention_threshold:

        m = 0

        while m < rings:
            angle_index = 0

            n = 0
            while n < rays:
                if m == rings - 1:
                    diffusive_layer[1][m][n] = 0
                else:
                    diffusive_layer[1][m][n] = num.u_density(diffusive_layer, 0, m, n, d_radius, d_theta, d_time,
                                                             phi_center, rings, advective_layer, angle_index, a,
                                                             b, tube_placements)
                    if n == tube_placements[angle_index]:
                        advective_layer[1][m][n] = num.u_tube(advective_layer, diffusive_layer, 0, m, n, a, b, v,
                                                              d_time, d_radius, d_theta)
                        if angle_index < len(tube_placements) - 1:
                            angle_index = angle_index + 1
                n += 1
            m += 1
        k += 1

        mass_retained = num.calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays,
                                      tube_placements)
        phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer,
                                  tube_placements, v)
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
    return k * d_time
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@njit(nopython=ENABLE_JIT)
# Collecting a snapshot of density across angles (labeled as discrete positions from 0 to N) on a ring (position specified via params)
def comp_diffusive_angle_snapshots(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer,
                                   phi_v_theta_snapshot_container, approach, m_segment=0.5, r=1, d=1, mass_retention_threshold=0.01, time_point_container=None):

    if ENABLE_JIT:
        print("Running optimized version.")

    if len(tube_placements) > rays:
        raise IndexError(f'Too many microtubules requested: {len(tube_placements)}, within domain of {rays} angular rays.')

    for i in range(len(tube_placements)):
        if tube_placements[i] < 0 or tube_placements[i] > rays:
            raise IndexError(f'Angle {tube_placements[i]} is out of bounds, your range should be [0, {rays-1}]')

    d_radius = r / rings
    d_theta = ((2 * math.pi) / rays)
    d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / (2 * d)

    phi_center = 1 / (math.pi * (d_radius * d_radius))

    mass_retained = 0
    early_flag = True
    # initialization of values in approach 3
    i = 0

# **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > mass_retention_threshold:

        m = 0

        while m < rings:
            angle_index = 0
            n = 0
            while n < rays:
                if m == rings - 1:
                    diffusive_layer[1][m][n] = 0
                else:
                    diffusive_layer[1][m][n] = num.u_density(diffusive_layer, 0, m, n, d_radius, d_theta, d_time, phi_center, rings, advective_layer, angle_index, a, b, tube_placements)
                    if n == tube_placements[angle_index]:
                        advective_layer[1][m][n] = num.u_tube(advective_layer, diffusive_layer, 0, m, n, a, b, v, d_time, d_radius, d_theta)
                        if angle_index < len(tube_placements)-1:
                            angle_index = angle_index + 1
                n += 1
            m += 1
        k += 1

        if approach == 1:
            # approach 1 collects density profiles within an open interval, where every two points in the time-point container (up to 4) is either a lower or upper bound.
            if time_point_container is None:
                raise ValueError("Provide time point container which should consist of 4 points: 2 bounds for the early bound, and 2 for the late bound.")
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
            raise ValueError(f'{approach} is not a valid argument, use either approach "1", "2", or "3" (must be an int)')

        mass_retained = num.calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays,
                                      tube_placements)
        phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer,
                                  tube_placements, v)
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]

    # collect for every other ring for an even number of rings, after the mass depletion threshold has been reached
    if approach == 4:
        for i in range(rings/2):
            phi_v_theta_snapshot_container[i] = diffusive_layer[0][i*2]
    return mass_retained

