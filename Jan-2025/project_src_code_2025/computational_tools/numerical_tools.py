from . import math, njit, sys_config

ENABLE_JIT = sys_config.ENABLE_NJIT


@njit(nopython=ENABLE_JIT)
def u_density(phi, k, m, n, d_radius, d_theta, d_time, central, rings, rho, mt_pos, a, b, tube_placements):

    current_density = phi[k][m][n]

    component_a = ((m+2) * j_r_r(phi, k, m, n, d_radius, rings)) - ((m+1) * j_l_r(phi, k, m, n, d_radius, central))

    component_a *= d_time / ((m+1) * d_radius)

    component_b = (j_r_t(phi, k, m, n, d_radius, d_theta)) - (j_l_t(phi, k, m, n, d_radius, d_theta))
    component_b *= d_time / ((m+1) * d_radius * d_theta)

    if n == tube_placements[mt_pos]:
        component_c = (a * phi[k][m][n]) * d_time - (((b * rho[k][m][n]) * d_time) / ((m+1) * d_radius * d_theta))
    else:
        component_c = 0

    return current_density - component_a - component_b - component_c


@njit(nopython=ENABLE_JIT)
def u_tube(rho, phi, k, m, n, a, b, v, d_time, d_radius, d_theta):

    j_l = v * rho[k][m][n]
    if m == len(phi[k][m]) - 1:
        j_r = 0
    else:
        j_r = v * rho[k][m+1][n]

    return rho[k][m][n] - ((j_r - j_l) / d_radius) * d_time + (a * phi[k][m][n] * (m+1) * d_radius * d_theta) * d_time - b * rho[k][m][n] * d_time


@njit(nopython=ENABLE_JIT)
def u_center(phi, k, d_radius, d_theta, d_time, curr_central, rho, tube_placements, v):

    total_sum = 0
    for n in range(len(phi[k][0])):
        total_sum += j_l_r(phi, k, 0, n, d_radius, curr_central)

    total_sum *= (d_theta * d_time) / (math.pi * d_radius)
    diffusive_sum = curr_central - total_sum

    advective_sum = 0

    for i in range(len(tube_placements)):
        angle = tube_placements[i]
        j_l = rho[k][0][angle] * v
        advective_sum += (abs(j_l) * d_time) / (math.pi * d_radius * d_radius)

    return diffusive_sum + advective_sum


@njit(nopython=ENABLE_JIT)
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


@njit(nopython=ENABLE_JIT)
def calc_loss_mass_j_r_r(phi, k, d_radius, d_theta, rings, rays):
    total_sum = 0
    for n in range(rays):
        total_sum += j_r_r(phi, k, rings-2, n, d_radius, 0)
    total_sum *= rings * d_radius * d_theta

    return total_sum


@njit(nopython=ENABLE_JIT)
def calc_loss_mass_fin_diff(mass_container, d_time):
    array = mass_container[:len(mass_container)-1].copy()
    for k in range(1, len(mass_container)):
        array[k-1] = (mass_container[k-1] - mass_container[k]) / d_time
    return array


@njit(nopython=ENABLE_JIT)
# J Right Radius
def j_r_r(phi, k, m, n, d_radius, rings):
    curr_ring = phi[k][m][n]
    if m == rings - 1:
        next_ring = 0
    else:
        next_ring = phi[k][m+1][n]
    return -1 * ((next_ring - curr_ring) / d_radius)


@njit(nopython=ENABLE_JIT)
# J Left Radius
def j_l_r(phi, k, m, n, d_radius, central):
    curr_ring = phi[k][m][n]
    if m == 0:
        prev_ring = central
    else:
        prev_ring = phi[k][m-1][n]
    return -1 * ((curr_ring - prev_ring) / d_radius)


@njit(nopython=ENABLE_JIT)
# J Right Theta
def j_r_t(phi, k, m, n, d_radius, d_theta):
    b = len(phi[k][m])
    return -1 * (phi[k][m][(n+1) % b] - phi[k][m][n]) / ((m+1) * d_radius * d_theta)


@njit(nopython=ENABLE_JIT)
# J Left Theta
def j_l_t(phi, k, m, n, d_radius, d_theta):
    b = len(phi[k][m])
    return -1 * (phi[k][m][n] - phi[k][m][(n-1) % b]) / ((m+1) * d_radius * d_theta)
