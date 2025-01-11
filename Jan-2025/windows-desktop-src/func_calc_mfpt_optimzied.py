from numba import njit
import numpy as np
import math


# Compiled functions under the JIT numba decorators do not support dynamically behaving containers, so they must be pre-compiled
def initialize_layers(rings, rays):
    diffusive_layer = np.zeros((2, rings, rays), dtype=np.float64)
    advective_layer = np.zeros((2, rings, rays), dtype=np.float64)
    return diffusive_layer, advective_layer


@njit
def u_density(phi, k, m, n, d_radius, d_theta, d_time, central, rings, rho, dict_index, a, b, tube_placements):

    current_density = phi[k][m][n]

    component_a = ((m+2) * j_r_r(phi, k, m, n, d_radius, rings)) - ((m+1) * j_l_r(phi, k, m, n, d_radius, central))

    component_a *= d_time / ((m+1) * d_radius)

    component_b = (j_r_t(phi, k, m, n, d_radius, d_theta)) - (j_l_t(phi, k, m, n, d_radius, d_theta))
    component_b *= d_time / ((m+1) * d_radius * d_theta)

    if n == tube_placements[dict_index]:  # if the current angle 'n' equates to the angle for which the microtubule is positioned at
        component_c = (a * phi[k][m][n]) * d_time - (((b * rho[k][m][n]) * d_time) / ((m+1) * d_radius * d_theta))
        # print(f'k={k}, m={m}, n={n}, dict_index={dict_index}')
        #
        # print(f'Dict index{dict_index}, Comp c: {component_c}, removed at angle {n}')
        # if m == 0:
        #     print(f' Component C at segment: {m} and at angle {n} : {component_c}')
    else:
        component_c = 0

    return current_density - component_a - component_b - component_c


@njit
# Update contents at advective layer (Particle density computation along a microtubule), returns a floating point number
def u_tube(rho, phi, k, m, n, a, b, v, d_time, d_radius, d_theta):
    j_l = v * rho[k][m][n]
    if m == len(phi[k][m]) - 1:
        j_r = 0
    else:
        j_r = v * rho[k][m+1][n]

    return rho[k][m][n] - ((j_r - j_l) / d_radius) * d_time + (a * phi[k][m][n] * (m+1) * d_radius * d_theta) * d_time - b * rho[k][m][n] * d_time


@njit
# Update the central patch, returns a floating point value
def u_center(phi, k, d_radius, d_theta, d_time, curr_central, rho, tube_placements, v):
    total_sum = 0
    for n in range(len(phi[k][0])):
        total_sum += j_l_r(phi, k, 0, n, d_radius, curr_central)

    total_sum *= (d_theta * d_time) / (math.pi * d_radius)
    diffusive_sum = curr_central - total_sum

    advective_sum = 0

    # Necessary for acquiring the associated angle at a microtubule via index from the list of keys from the dictionary

    for i in range(len(tube_placements)):
        angle = tube_placements[i]
        j_l = rho[k][0][angle] * v
        advective_sum += (abs(j_l) * d_time) / (math.pi * d_radius * d_radius)

    return diffusive_sum + advective_sum
    # return diffusive_sum


@njit
# calculate for total mass across domain, returns a floating point number
def calc_mass(phi, rho, k, d_radius, d_theta, curr_central, rings, rays, tube_placements):
    mass = 0
    for m in range(rings):
        for n in range(rays):
            mass += phi[k][m][n] * (m+1)
    mass *= (d_radius * d_radius) * d_theta

    microtubule_mass = 0

    for i in range(len(tube_placements)):
        angle = tube_placements[i]
        for m in range(rings):
            microtubule_mass += rho[k][m][angle] * d_radius

    return (curr_central * math.pi * d_radius * d_radius) + mass + microtubule_mass
    # return (curr_central * math.pi * d_radius * d_radius) + mass


@njit
# calculate mass loss using the J_R_R scheme
def calc_loss_mass_j_r_r(phi, k, d_radius, d_theta, rings, rays):
    total_sum = 0
    for n in range(rays):
        total_sum += j_r_r(phi, k, rings-2, n, d_radius, 0)
    total_sum *= rings * d_radius * d_theta

    return total_sum


@njit
# calculate mass loss using the derivative scheme, returns a floating point number
def calc_loss_mass_derivative(mass_container, d_time):
    array = np.zeros([len(mass_container) - 1])
    for k in range(1, len(mass_container)):
        array[k-1] = (mass_container[k-1] - mass_container[k]) / d_time
    return array


@njit
# J Right Radius
def j_r_r(phi, k, m, n, d_radius, rings):
    curr_ring = phi[k][m][n]
    if m == rings - 1:
        next_ring = 0
    else:
        next_ring = phi[k][m+1][n]
    return -1 * ((next_ring - curr_ring) / d_radius)


@njit
# J Left Radius
def j_l_r(phi, k, m, n, d_radius, central):
    curr_ring = phi[k][m][n]
    if m == 0:
        prev_ring = central
    else:
        prev_ring = phi[k][m-1][n]
    return -1 * ((curr_ring - prev_ring) / d_radius)


@njit
# J Right Theta
def j_r_t(phi, k, m, n, d_radius, d_theta):
    b = len(phi[k][m])
    return -1 * (phi[k][m][(n+1) % b] - phi[k][m][n]) / ((m+1) * d_radius * d_theta)


@njit
# J Left Theta
def j_l_t(phi, k, m, n, d_radius, d_theta):
    b = len(phi[k][m])
    return -1 * (phi[k][m][n] - phi[k][m][(n-1) % b]) / ((m+1) * d_radius * d_theta)


@njit
# Calculating MFPT by using the mass-retained method
def solve_mass_retained_2T(rings, rays, r, d, a, b, v, tube_placements, diffusive_layer, advective_layer, mass_loss_container=None, mass_loss_info_interval=None):

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

# **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > 0.01:

        net_current_out = 0

        m = 0

        while m < rings:
            angle_index = 0
            n = 0
            while n < rays:
                if m == rings - 1:
                    diffusive_layer[1][m][n] = 0
                else:
                    diffusive_layer[1][m][n] = u_density(diffusive_layer, 0, m, n, d_radius, d_theta, d_time, phi_center, rings, advective_layer, angle_index, a, b, tube_placements)
                    if n == tube_placements[angle_index]:
                        # Update the associated tube within the dictionary
                        advective_layer[1][m][n] = u_tube(advective_layer, diffusive_layer, 0, m, n, a, b, v, d_time, d_radius, d_theta)
                        if angle_index < len(tube_placements)-1:
                            angle_index = angle_index + 1
                if m == rings - 2:
                    net_current_out += j_r_r(diffusive_layer, 0, m, n, d_radius, 0) * rings * d_radius * d_theta
                    if mass_loss_container is not None and mass_loss_info_interval is not None:
                        if mass_loss_info_interval % k == 0:
                            mass_loss_container[k] = net_current_out
                    # net_current_out *= rings * d_radius * d_theta
                n += 1
            m += 1

        m_f_p_t += net_current_out * k * d_time * d_time
        k += 1
        if k > 0 and k % 10 ** 7 == 0:
            mass_percent = int(mass_retained * 10000)
            print(f"V={v}   Time step: {k}  Current mass retained: {mass_percent}   Switch on/off rate: {a}")

        mass_retained = calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays, tube_placements)
        phi_center = u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer, tube_placements, v)
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    duration = k * d_time
    return m_f_p_t, duration


@njit(nopython=True)
# Collecting phi across Theta on several rings at 4 different segments of mass retention
def solve_mass_retained_2T_theta_phi(rings, rays, r, d, a, b, v, tube_placements, diffusive_layer, advective_layer, phi_v_theta_container, m_segment, output_peak=False):

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
    glb_pk_mass_retention_flag = False
    flag = True
    early_flag = True
    # To be used in assessing the mass loss rate peak (computing using radial currents)

# **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > 0.01:

        net_current_out = 0

        m = 0

        while m < rings:
            angle_index = 0

            if output_peak:
                if m == rings - 2:
                    if k % 2 == 0:
                        mass_loss_step_i = calc_loss_mass_j_r_r(diffusive_layer, 0, d_radius, d_theta, rings, rays)
                    else:
                        mass_loss_step_i_plus = calc_loss_mass_j_r_r(diffusive_layer, 0, d_radius, d_theta, rings, rays)
                    if k > 0 and k % 2 != 0 and flag:
                        if mass_loss_step_i > mass_loss_step_i_plus:
                            print(f'{k-1} steps to achieve global mass loss peak. (multiply this value by d_time in order to convert to simulation time/dimensionless units')
                            print(f'Global peak simulation time (in dimensionless units): {(k-1) * d_time}')
                            glb_pk_mass_retention_flag = True
                            flag = False
            n = 0
            while n < rays:
                if m == rings - 1:
                    diffusive_layer[1][m][n] = 0
                else:
                    diffusive_layer[1][m][n] = u_density(diffusive_layer, 0, m, n, d_radius, d_theta, d_time, phi_center, rings, advective_layer, angle_index, a, b, tube_placements)
                    if n == tube_placements[angle_index]:
                        # Update the associated tube within the dictionary
                        advective_layer[1][m][n] = u_tube(advective_layer, diffusive_layer, 0, m, n, a, b, v, d_time, d_radius, d_theta)
                        if angle_index < len(tube_placements)-1:
                            angle_index = angle_index + 1
                if m == rings - 2:
                    net_current_out += j_r_r(diffusive_layer, 0, m, n, d_radius, 0) * rings * d_radius * d_theta
                n += 1
            m += 1

        m_f_p_t += net_current_out * k * d_time * d_time
        k += 1

        '''
        Plotting theta versus phi at velocity peak values:
        choose several rings within the domain (at positions M*1/4, M*1/2, M*3/4), and then collect phi across every angle across that ring.
        (At varying mass amounts within the domain) [0.1 + epsilon, 0.225, 0.45, 0.675]
        '''

        # if 0.045 < k * d_time < 0.05 and early_flag:
        #     phi_v_theta_container[0] = diffusive_layer[0][math.floor(m * m_segment)]
        #     early_flag = False
        # elif 0.45 < k * d_time < 0.5:
        #     phi_v_theta_container[1] = diffusive_layer[0][math.floor(m * m_segment)]
        #     break

        if 0.675 < mass_retained < 0.68:
            phi_v_theta_container[0] = diffusive_layer[0][math.floor(m * m_segment)]
        elif 0.45 < mass_retained < 0.46:
            phi_v_theta_container[1] = diffusive_layer[0][math.floor(m * m_segment)]
        elif 0.225 < mass_retained < 0.26:
            phi_v_theta_container[2] = diffusive_layer[0][math.floor(m * m_segment)]
        elif 0.015 < mass_retained < 0.02:
            phi_v_theta_container[3] = diffusive_layer[0][math.floor(m * m_segment)]

            # edit the following section so that floats are able to be viewed during run time
        # if k > 0 and k % 10 ** 6 == 0:
            # mass_percent = int(mass_retained * 10000)
            # print(f"V={v}   Time step: {k}  Current mass retained: {mass_retained}   Switch on/off rate: {a}")
        elif glb_pk_mass_retention_flag:
            print("Mass retained at the global peak time.")
            print(f"V={v}   Time step: {k}  Current mass retained: {mass_retained}   Switch on/off rate: {a}")
            glb_pk_mass_retention_flag = False

        mass_retained = calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays, tube_placements)
        phi_center = u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer, tube_placements, v)
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    duration = k * d_time

    return m_f_p_t, duration


@njit(nopython=True)
# Collecting a snapshot of the domain at a specified stamp, which can be used in heat map plots
def solve_mass_retained_2T_domain_snapshot(rings, rays, r, d, a, b, v, tube_placements, diffusive_layer, advective_layer, domain_snapshot_container, domain_center_container, approach, time_point_container=None, output_peak=False):

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
    early_flag = True
    # To be used in assessing the mass loss rate peak (computing using radial currents)

# **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > 0.01:

        net_current_out = 0

        m = 0

        while m < rings:
            angle_index = 0

            if output_peak:
                if m == rings - 2:
                    if k % 2 == 0:
                        mass_loss_step_i = calc_loss_mass_j_r_r(diffusive_layer, 0, d_radius, d_theta, rings, rays)
                    else:
                        mass_loss_step_i_plus = calc_loss_mass_j_r_r(diffusive_layer, 0, d_radius, d_theta, rings, rays)
                    if k > 0 and k % 2 != 0:
                        if mass_loss_step_i > mass_loss_step_i_plus:
                            print(f'{k-1} steps to achieve global mass loss peak. (multiply this value by d_time in order to convert to simulation time/dimensionless units')
                            print(f'Global peak simulation time (in dimensionless units): {(k-1) * d_time}')
                            duration = k * d_time
                            return m_f_p_t, duration
            n = 0
            while n < rays:
                if m == rings - 1:
                    diffusive_layer[1][m][n] = 0
                else:
                    diffusive_layer[1][m][n] = u_density(diffusive_layer, 0, m, n, d_radius, d_theta, d_time, phi_center, rings, advective_layer, angle_index, a, b, tube_placements)
                    if n == tube_placements[angle_index]:
                        # Update the associated tube within the dictionary
                        advective_layer[1][m][n] = u_tube(advective_layer, diffusive_layer, 0, m, n, a, b, v, d_time, d_radius, d_theta)
                        if angle_index < len(tube_placements)-1:
                            angle_index = angle_index + 1
                if m == rings - 2:
                    net_current_out += j_r_r(diffusive_layer, 0, m, n, d_radius, 0) * rings * d_radius * d_theta
                n += 1
            m += 1

        m_f_p_t += net_current_out * k * d_time * d_time
        k += 1

        '''
        Plotting theta versus phi at velocity peak values:
        choose several rings within the domain (at positions M*1/4, M*1/2, M*3/4), and then collect phi across every angle across that ring.
        (At varying mass amounts within the domain) [0.1 + epsilon, 0.225, 0.45, 0.675]
        '''

        if approach == "1":
            if time_point_container is None:
                raise ValueError("Provide time point container which should consist of 4 points: 2 bounds for the early bound, and 2 for the late bound.")
            if time_point_container[0] < k * d_time < time_point_container[1] and early_flag:
                domain_snapshot_container[0] = diffusive_layer[0]
                domain_center_container[0] = phi_center
                early_flag = False
            elif time_point_container[2] < k * d_time < time_point_container[3]:
                domain_snapshot_container[1] = diffusive_layer[0]
                domain_center_container[1] = phi_center
                break
        elif approach == "2":
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
                break
        else:
            raise ValueError(f'{approach} is not a valid argument, use either approach "1" or "2" (must be a string)')

            # edit the following section so that floats are able to be viewed during run time
        # if k > 0 and k % 10 ** 6 == 0:
            # mass_percent = int(mass_retained * 10000)
            # print(f"V={v}   Time step: {k}  Current mass retained: {mass_retained}   Switch on/off rate: {a}")

        mass_retained = calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays, tube_placements)
        phi_center = u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer, tube_placements, v)
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    duration = k * d_time

    return m_f_p_t, duration

@njit
def solve_mass_retained_2T_profile_test(rings, rays, r, d, a, b, v, tube_placements, diffusive_layer, advective_layer, density_profile, step_check, mass_container):

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

# **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > 0.01:

        net_current_out = 0

        m = 0

        while m < rings:
            angle_index = 0

            n = 0
            while n < rays:
                if m == rings - 1:
                    diffusive_layer[1][m][n] = 0
                else:
                    diffusive_layer[1][m][n] = u_density(diffusive_layer, 0, m, n, d_radius, d_theta, d_time, phi_center, rings, advective_layer, angle_index, a, b, tube_placements)
                    if n == tube_placements[angle_index]:
                        # Update the associated tube within the dictionary
                        advective_layer[1][m][n] = u_tube(advective_layer, diffusive_layer, 0, m, n, a, b, v, d_time, d_radius, d_theta)
                        if angle_index < len(tube_placements)-1:
                            angle_index = angle_index + 1
                if m == rings - 2:
                    net_current_out += j_r_r(diffusive_layer, 0, m, n, d_radius, 0) * rings * d_radius * d_theta
                n += 1
            m += 1

        m_f_p_t += net_current_out * k * d_time * d_time
        k += 1
        if k > 0 and k % 10 ** 4:
            print(f"Current retained mass: {mass_retained}")

        mass_container[k] = mass_retained
        mass_retained = calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays, tube_placements)
        phi_center = u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer, tube_placements, v)

        if k == step_check:
            density_profile = diffusive_layer[0]
            # store the values within the array to a csv file
            # and then plot the density as function versus radius.

        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    print(f'Number of steps taken to execute: {k}')
    return m_f_p_t, density_profile, mass_container
