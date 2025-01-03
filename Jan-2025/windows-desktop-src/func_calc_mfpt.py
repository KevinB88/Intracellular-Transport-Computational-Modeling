import math
import time as clk
import aux_print as pr
import numpy as np


# !This version generalizes microtubule calculation across the domain!

# Update contents at the diffusive layer (Particle density computation across the domain), returns a floating point number
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


# Update contents at advective layer (Particle density computation along a microtubule), returns a floating point number
def u_tube(rho, phi, k, m, n, a, b, v, d_time, d_radius, d_theta):
    j_l = v * rho[k][m][n]
    if m == len(phi[k][m]) - 1:
        j_r = 0
    else:
        j_r = v * rho[k][m+1][n]

    return rho[k][m][n] - ((j_r - j_l) / d_radius) * d_time + (a * phi[k][m][n] * (m+1) * d_radius * d_theta) * d_time - b * rho[k][m][n] * d_time


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


# calculate mass loss using the J_R_R scheme, returns a floating point number
def calc_loss_mass_j_r_r(phi, k, d_radius, d_theta, rings, rays):
    total_sum = 0
    for n in range(rays):
        total_sum += j_r_r(phi, k, rings-2, n, d_radius, 0)
    total_sum *= rings * d_radius * d_theta

    return total_sum


# calculate mass loss using the derivative scheme, returns a floating point number
def calc_loss_mass_derivative(mass_container, d_time):
    array = np.zeros([len(mass_container) - 1])
    for k in range(1, len(mass_container)):
        array[k-1] = (mass_container[k-1] - mass_container[k]) / d_time
    return array


# J Right Radius
def j_r_r(phi, k, m, n, d_radius, rings):
    curr_ring = phi[k][m][n]
    if m == rings - 1:
        next_ring = 0
    else:
        next_ring = phi[k][m+1][n]
    return -1 * ((next_ring - curr_ring) / d_radius)


# J Left Radius
def j_l_r(phi, k, m, n, d_radius, central):
    curr_ring = phi[k][m][n]
    if m == 0:
        prev_ring = central
    else:
        prev_ring = phi[k][m-1][n]
    return -1 * ((curr_ring - prev_ring) / d_radius)


# J Right Theta
def j_r_t(phi, k, m, n, d_radius, d_theta):
    b = len(phi[k][m])
    return -1 * (phi[k][m][(n+1) % b] - phi[k][m][n]) / ((m+1) * d_radius * d_theta)


# J Left Theta
def j_l_t(phi, k, m, n, d_radius, d_theta):
    b = len(phi[k][m])
    return -1 * (phi[k][m][n] - phi[k][m][(n-1) % b]) / ((m+1) * d_radius * d_theta)


'''
rings   = Radial curves 
rays    = Angular rays
r       = Domain radius
d       = Diffusion coefficient
t       = Run time
q       = Passing a boolean value to determine if the user would like to print initial quantities
p       = Progression frequency for print operations
a       = 
b       = 
v       = velocity (default value assigned to velocity in this rendition is -1)
angle   = The particular angle for which the microtubule is being calculated for 
(In later versions, the angle parameter has been altered to a container-data-structure filled with various angles for which microtubules are placed upon)

Additional note: when a = b, we label this as 'w'. (Not within this function explicitly however)
'''


# ext_fact = extension-factor
# ext_automate : a boolean parameter which automatically extends the sim-time by a factor of ext_fact
def solve(rings, rays, r, d, t, q, p, a, b, v, tube_placements, ext_automate, ext_fact):

    if len(tube_placements) > rays:
        raise IndexError(f'Too many microtubules requested: {len(tube_placements)}, within domain of {rays} angular rays.')

    for i in range(len(tube_placements)):
        if tube_placements[i] < 0 or tube_placements[i] > rays:
            raise IndexError(f'Angle {tube_placements[i]} is out of bounds, your range should be [0, {rays-1}]')

    start = clk.time()
    d_radius = r / rings
    d_theta = ((2 * math.pi) / rays)
    d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / (2 * d)

    time_steps = math.ceil(t / d_time)

    print(13047187 * d_time)
    phi_center = 1 / (math.pi * (d_radius * d_radius))

    if q:
        print(f'Time Steps : {time_steps}')
        print(f'Approximated run time: {pr.convert_time((time_steps * rings * rays * 4 * 10 ** -6))}')

    mass_loss_tab = np.zeros([2])
    diffusive_layer = np.zeros([2, rings, rays])
    advective_layer = np.zeros([2, rings, rays])
    # Mean first passage time
    m_f_p_t = 0

# **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k < time_steps:

        net_current_out = 0

        if q and p >= 1:
            if k % p == 0:
                pr.pr_progress(k, time_steps)
        m = 0

        while m < rings:
            angle_index = 0
            if m == rings - 2:
                if k % 2 == 0:
                    mass_loss_tab[0] = calc_loss_mass_j_r_r(diffusive_layer, 0, d_radius, d_theta, rings, rays)
                else:
                    mass_loss_tab[1] = calc_loss_mass_j_r_r(diffusive_layer, 0, d_radius, d_theta, rings, rays)
                # print(f'past: {mass_loss_tab[0]}, current: {mass_loss_tab[1]}')
                # # clk.sleep(0.002)
                # print(f'Time Step: {k}')
                if k > 0 and k % 2 != 0 and ext_automate:
                    if mass_loss_tab[0] > mass_loss_tab[1]:
                        glb_peak_time = (k-1) * d_time
                        end = clk.time()
                        # Including a space within the print operation
                        print()
                        print(f'glb peak time attained: {glb_peak_time}')
                        print(f'Time taken to reach global max: {end - start :.4f}')
                        ext_automate = False
                        glb_peak_time *= ext_fact
                        time_steps = math.ceil(glb_peak_time / d_time)
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
        phi_center = u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer,
                              tube_placements, v)

        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    return m_f_p_t


'''
    There will two approaches:
    
    A hybrid between the 2-T method and the mass-retention method
    
    The mass retention method ensuring that all the data is stored as well. 
'''


# Calculating MFPT by using the mass-retained method
def solve_mass_retained_2T(rings, rays, r, d, a, b, v, tube_placements):

    if len(tube_placements) > rays:
        raise IndexError(f'Too many microtubules requested: {len(tube_placements)}, within domain of {rays} angular rays.')

    for i in range(len(tube_placements)):
        if tube_placements[i] < 0 or tube_placements[i] > rays:
            raise IndexError(f'Angle {tube_placements[i]} is out of bounds, your range should be [0, {rays-1}]')

    start = clk.time()
    d_radius = r / rings
    d_theta = ((2 * math.pi) / rays)
    d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / (2 * d)

    print('Meta data:')
    print(f'd-radius: {d_radius}')
    print(f'd-theta: {d_theta}')
    print(f'd-time: {d_time}')

    phi_center = 1 / (math.pi * (d_radius * d_radius))

    # if q:
    #     print(f'Approximated run time: {pr.convert_time((time_steps * rings * rays * 4 * 10 ** -6))}')

    # The extension method

    mass_retained = 0
    diffusive_layer = np.zeros([2, rings, rays])
    advective_layer = np.zeros([2, rings, rays])

    # Mean first passage time
    m_f_p_t = 0

# **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > 0.01:

        net_current_out = 0

        # if q and p >= 1:
        #     if k % p == 0:
        #         pr.pr_progress(k, time_steps)
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
        # print(f'Time step (k): {k}, Mass: {mass_retained}')
        k += 1

        mass_retained = calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays, tube_placements)
        phi_center = u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer, tube_placements, v)
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    end = clk.time()
    print(f'Number of time-steps needed to complete: {k}')
    print(f'Time elapsed: {end - start:.4f} seconds.')
    return m_f_p_t


def solve_mass_retained_2T_profile_check_test(rings, rays, r, d, a, b, v, tube_placements, step_check, mass_container):

    if len(tube_placements) > rays:
        raise IndexError(f'Too many microtubules requested: {len(tube_placements)}, within domain of {rays} angular rays.')

    for i in range(len(tube_placements)):
        if tube_placements[i] < 0 or tube_placements[i] > rays:
            raise IndexError(f'Angle {tube_placements[i]} is out of bounds, your range should be [0, {rays-1}]')

    start = clk.time()
    d_radius = r / rings
    d_theta = ((2 * math.pi) / rays)
    d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / (2 * d)

    print('Meta data:')
    print(f'd-radius: {d_radius}')
    print(f'd-theta: {d_theta}')
    print(f'd-time: {d_time}')

    phi_center = 1 / (math.pi * (d_radius * d_radius))

    # if q:
    #     print(f'Approximated run time: {pr.convert_time((time_steps * rings * rays * 4 * 10 ** -6))}')

    # The extension method

    mass_retained = 0
    diffusive_layer = np.zeros([2, rings, rays])
    advective_layer = np.zeros([2, rings, rays])

    density_profile = np.zeros([1, rings, rays])

    # Mean first passage time
    m_f_p_t = 0

# **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > 0.01:

        net_current_out = 0

        # if q and p >= 1:
        #     if k % p == 0:
        #         pr.pr_progress(k, time_steps)
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
        # print(f'Time step (k): {k}, Mass: {mass_retained}')
        k += 1

        mass_container[k] = mass_retained
        mass_retained = calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays, tube_placements)
        phi_center = u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer, tube_placements, v)

        if k == step_check:
            density_profile = diffusive_layer[0]

        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    end = clk.time()
    print(f'Number of time-steps needed to complete: {k}')
    print(f'Time elapsed: {end - start:.4f} seconds.')
    return m_f_p_t, density_profile, mass_container


def solve_mass_retained_history(rings, rays, r, d, t, q, p, a, b, v, tube_placements, ext_automate, ext_fact):

    if len(tube_placements) > rays:
        raise IndexError(f'Too many microtubules requested: {len(tube_placements)}, within domain of {rays} angular rays.')

    for i in range(len(tube_placements)):
        if tube_placements[i] < 0 or tube_placements[i] > rays:
            raise IndexError(f'Angle {tube_placements[i]} is out of bounds, your range should be [0, {rays-1}]')

    start = clk.time()
    d_radius = r / rings
    d_theta = ((2 * math.pi) / rays)
    d_time = (0.1 * min(d_radius * d_radius, d_theta * d_theta * d_radius * d_radius)) / (2 * d)

    phi_center = 1 / (math.pi * (d_radius * d_radius))

    # if q:
    #     print(f'Approximated run time: {pr.convert_time((time_steps * rings * rays * 4 * 10 ** -6))}')

    # The extension method

    mass_retained = 0
    diffusive_layer = np.zeros([1000, rings, rays])
    advective_layer = np.zeros([1000, rings, rays])
    # Mean first passage time
    m_f_p_t = 0

# **** - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    k = 0

    while k == 0 or mass_retained > 0.01:

        net_current_out = 0

        # if q and p >= 1:
        #     if k % p == 0:
        #         pr.pr_progress(k, time_steps)
        m = 0

        while m < rings:
            angle_index = 0
            n = 0
            while n < rays:
                if m == rings - 1:
                    diffusive_layer[k+1][m][n] = 0
                else:
                    diffusive_layer[k+1][m][n] = u_density(diffusive_layer, k, m, n, d_radius, d_theta, d_time, phi_center, rings, advective_layer, angle_index, a, b, tube_placements)
                    if n == tube_placements[angle_index]:
                        # Update the associated tube within the dictionary
                        advective_layer[k+1][m][n] = u_tube(advective_layer, diffusive_layer, k, m, n, a, b, v, d_time, d_radius, d_theta)
                        if angle_index < len(tube_placements)-1:
                            angle_index = angle_index + 1
                if m == rings - 2:
                    net_current_out += j_r_r(diffusive_layer, k, m, n, d_radius, 0) * rings * d_radius * d_theta
                n += 1
            m += 1

        m_f_p_t += net_current_out * k * d_time * d_time
        k += 1
        if k > 0 and k % 1000 == 0:
            diffusive_layer = np.concatenate((diffusive_layer, np.zeros([1000])), 0)
            advective_layer = np.concatenate((advective_layer, np.zeros([1000])), 0)

        mass_retained = calc_mass(diffusive_layer, advective_layer, k, d_radius, d_theta, phi_center, rings, rays, tube_placements)
        phi_center = u_center(diffusive_layer, k, d_radius, d_theta, d_time, phi_center, advective_layer, tube_placements, v)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    end = clk.time()
    print(f'Number of time-steps needed to complete: {k}')
    print(f'Time elapsed: {end - start:.4f} seconds.')
    return m_f_p_t

