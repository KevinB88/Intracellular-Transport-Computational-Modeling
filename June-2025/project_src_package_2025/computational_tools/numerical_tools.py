from . import njit, sys_config, np

ENABLE_JIT = sys_config.ENABLE_NJIT
ENABLE_CACHE = sys_config.ENABLE_NUMBA_CACHING


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def compute_dT(rg_param, ry_param, domain_radius=1.0, D=1.0):
    dRad = domain_radius / rg_param
    dThe = (2 * np.pi) / ry_param
    dT = (0.1 * min(dRad ** 2, dThe ** 2 * dRad ** 2)) / (2 * D)
    return dT


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def convert_K_to_T(RG, RY, K):
    dR = 1 / RG
    dT = 2 * np.pi / RY
    dK = (0.1 * (min(dR ** 2, dT ** 2 * dR ** 2))) * 0.5
    return K * dK


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def update_layer_inplace(layer_target, layer_source, N, M):
    for i in range(M):
        for j in range(N):
            layer_target[i][j] = layer_source[i][j]


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def u_density(phi, k, m, n, d_radius, d_theta, d_time, central, rings, rho, mt_pos, a, b, tube_placements):
    """

    Calculate particle density at a position (m,n) on the diffusive layer at a time-point k.
    (Positions are relative to patches across our domain for the diffusive layer)

    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) time-point
    :param m: (int) position of radial ring
    :param n: (int) position of angular ray
    :param d_radius: (float) delta_radius
    :param d_theta: (float) delta_theta
    :param d_time: (float) delta_time
    :param central: (float) particle density at the center
    :param rings: (int) # of radial rings in the domain
    :param rho: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param mt_pos: (int) indexed position from the 'tube_placements' container
    (to specify particle density on the advective layer relative to microtubule/filament)

    :param a: (float) switch rate onto the diffusive layer (switch-on rate)
    :param b: (float) switch rate onto the advective layer (switch-off rate)
    :param tube_placements: (list(int)) discrete microtubule/filament positions between [0, rays-1]
    :return: particle density at a position (m,n) on the diffusive layer
    """

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


# This function will be called when the solver iterates onto the appropriate patch (i.e, the patch within the diffusive-to-advective extraction range)
# microtubules (marked by indices in the tube_placements container) are centered within the diffusive-to-advective range
@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def u_density_mixed(phi, k, m, n, d_radius, d_theta, d_time, central, rings, rho, mt_pos, a, b):
    """

    Calculate particle density at a position (m,n) on the diffusive layer at a time-point k.
    (Positions are relative to patches across our domain for the diffusive layer)

    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) time-point
    :param m: (int) position of radial ring
    :param n: (int) position of angular ray
    :param d_radius: (float) delta_radius
    :param d_theta: (float) delta_theta
    :param d_time: (float) delta_time
    :param central: (float) particle density at the center
    :param rings: (int) # of radial rings in the domain
    :param rho: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param mt_pos: (int) indexed position from the 'tube_placements' container
    (to specify particle density on the advective layer relative to microtubule/filament)

    :param a: (float) switch rate onto the diffusive layer (switch-on rate)
    :param b: (float) switch rate onto the advective layer (switch-off rate)
    :param tube_placements: (list(int)) discrete microtubule/filament positions between [0, rays-1]
    :return: particle density at a position (m,n) on the diffusive layer
    """

    current_density = phi[k][m][n]

    component_a = ((m+2) * j_r_r(phi, k, m, n, d_radius, rings)) - ((m+1) * j_l_r(phi, k, m, n, d_radius, central))

    component_a *= d_time / ((m+1) * d_radius)

    component_b = (j_r_t(phi, k, m, n, d_radius, d_theta)) - (j_l_t(phi, k, m, n, d_radius, d_theta))

    component_b *= d_time / ((m+1) * d_radius * d_theta)

    component_c = a * phi[k][m][n] * d_time - (b * rho[k][m][mt_pos] * d_time) / (3 * (m+1) * d_radius * d_theta)
    # component_c was previously computed as follows:
    # component_c = a * phi[k][m][mt_pos] * d_time - (b * rho[k][m][mt_pos] * d_time) / (3 * (m+1) * d_radius * d_theta)
    # This ^ resulted in the mass conservation error as we noticed before in prior meetings

    return current_density - component_a - component_b - component_c


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def u_density_rect(phi, k, m, n, d_radius, d_theta, d_time, central, rings, rho, mt_pos, a, b, d_tube):
    """

    Calculate particle density at a position (m,n) on the diffusive layer at a time-point k.
    (Positions are relative to patches across our domain for the diffusive layer)

    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) time-point
    :param m: (int) position of radial ring
    :param n: (int) position of angular ray
    :param d_radius: (float) delta_radius
    :param d_theta: (float) delta_theta
    :param d_time: (float) delta_time
    :param central: (float) particle density at the center
    :param rings: (int) # of radial rings in the domain
    :param rho: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param mt_pos: (int) indexed position from the 'tube_placements' container
    (to specify particle density on the advective layer relative to microtubule/filament)

    :param a: (float) switch rate onto the diffusive layer (switch-on rate)
    :param b: (float) switch rate onto the advective layer (switch-off rate)
    :param d_tube (float)
    :return: particle density at a position (m,n) on the diffusive layer
    """

    j_max = np.ceil((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)

    current_density = phi[k][m][n]

    component_a = ((m+2) * j_r_r(phi, k, m, n, d_radius, rings)) - ((m+1) * j_l_r(phi, k, m, n, d_radius, central))

    component_a *= d_time / ((m+1) * d_radius)

    component_b = (j_r_t(phi, k, m, n, d_radius, d_theta)) - (j_l_t(phi, k, m, n, d_radius, d_theta))

    component_b *= d_time / ((m+1) * d_radius * d_theta)

    # at the moment there is no overlap between the regions

    component_c = a * phi[k][m][n] * d_time - (b * rho[k][m][mt_pos] * d_time) / ((1 + 2 * j_max) * (m+1) * d_radius * d_theta)
    # component_c was previously computed as follows:
    # component_c = a * phi[k][m][mt_pos] * d_time - (b * rho[k][m][mt_pos] * d_time) / (3 * (m+1) * d_radius * d_theta)
    # This ^ resulted in the mass conservation error as we noticed before in prior meetings

    return current_density - component_a - component_b - component_c


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def u_density_rect_v2(phi, k, m, n, d_radius, d_theta, d_time, central, rings, rho, a, b, d_tube, dict_list):
    """

    Calculate particle density at a position (m,n) on the diffusive layer at a time-point k.
    (Positions are relative to patches across our domain for the diffusive layer)

    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) time-point
    :param m: (int) position of radial ring
    :param n: (int) position of angular ray
    :param d_radius: (float) delta_radius
    :param d_theta: (float) delta_theta
    :param d_time: (float) delta_time
    :param central: (float) particle density at the center
    :param rings: (int) # of radial rings in the domain
    :param rho: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    (to specify particle density on the advective layer relative to microtubule/filament)

    :param a: (float) switch rate onto the diffusive layer (switch-on rate)
    :param b: (float) switch rate onto the advective layer (switch-off rate)
    :param d_tube (float)
    :param dict_list (List[int])
    :return: particle density at a position (m,n) on the diffusive layer
    """

    j_max = np.ceil((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)

    current_density = phi[k][m][n]

    component_a = ((m+2) * j_r_r(phi, k, m, n, d_radius, rings)) - ((m+1) * j_l_r(phi, k, m, n, d_radius, central))

    component_a *= d_time / ((m+1) * d_radius)

    component_b = (j_r_t(phi, k, m, n, d_radius, d_theta)) - (j_l_t(phi, k, m, n, d_radius, d_theta))

    component_b *= d_time / ((m+1) * d_radius * d_theta)

    rho_sum = 0
    for i in range(dict_list.shape[0]):
        rho_sum += rho[k][m][dict_list[i]]

    component_c = a * phi[k][m][n] * d_time + (b * rho_sum * d_time) / ((1 + 2 * j_max) * (m+1) * d_radius * d_theta)

    return current_density - component_a - component_b - component_c


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def u_tube(rho, phi, k, m, n, a, b, v, d_time, d_radius, d_theta):
    """

    Calculate particle density at a position (m,n) on the advective layer at a time-point k.

    :param rho: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) current time step
    :param m: (int) position of the radial ring
    :param n: (int) position of the angular ray
    :param a: (float) switch-on rate
    :param b: (float) switch-off rate
    :param v: (float) velocity across the advective layer
    :param d_time: (float) delta-time
    :param d_radius: (float) delta-radius
    :param d_theta: (float) delta-theta
    :return: particle density at position (m,n) on the advective layer.
    """

    # N = phi.shape[2]
    N = len(phi[k][m])
    j_l = v * rho[k][m][n]
    if m == N - 1:
        j_r = 0
    else:
        j_r = v * rho[k][m+1][n]

    # The following block has been modified to match the flow of computation with the rectangular configuration under d_tube=0

    component_a = (rho[k][m][n] - ((j_r - j_l) * (1/d_radius)) * d_time)
    component_b = phi[k][m][n]
    component_b *= a * (m+1) * (d_radius * d_theta * d_time)
    component_c = b * rho[k][m][n] * d_time
    #
    return component_a + component_b - component_c

    # return rho[k][m][n] - ((j_r - j_l) / d_radius) * d_time + (a * phi[k][m][n] * (m+1) * d_radius * d_theta) * d_time - b * rho[k][m][n] * d_time


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def u_tube_mixed(rho, phi, k, m, n, a, b, v, d_time, d_radius, d_theta, mx_cn_rrange):
    """

    Calculate particle density at a position (m,n) on the advective layer at a time-point k.

    :param rho: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) current time step
    :param m: (int) position of the radial ring
    :param n: (int) position of the angular ray
    :param a: (float) switch-on rate
    :param b: (float) switch-off rate
    :param v: (float) velocity across the advective layer
    :param d_time: (float) delta-time
    :param d_radius: (float) delta-radius
    :param d_theta: (float) delta-theta
    :param mx_cn_rrange (float)
    :return: particle density at position (m,n) on the advective layer.
    """

    # N = phi.shape[2]
    N = len(phi[k][m])
    j_l = v * rho[k][m][n]
    if m == N - 1:
        j_r = 0
    else:
        j_r = v * rho[k][m+1][n]

    component_a = (rho[k][m][n] - ((j_r - j_l) * (1/d_radius)) * d_time)

    if m < mx_cn_rrange:
        component_b = a * (m+1) * (d_radius * d_theta * d_time) * (phi[k][m][n] + phi[k][m][(n-1) % N] + phi[k][m][(n+1) % N])
    else:
        component_b = a * phi[k][m][n] * (m+1) * d_radius * d_theta * d_time

    component_c = b * rho[k][m][n] * d_time

    return component_a + component_b - component_c


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def u_tube_rect(rho, phi, k, m, n, a, b, v, d_time, d_radius, d_theta, d_tube):
    """

    Calculate particle density at a position (m,n) on the advective layer at a time-point k.

    :param rho: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) current time step
    :param m: (int) position of the radial ring
    :param n: (int) position of the angular ray
    :param a: (float) switch-on rate
    :param b: (float) switch-off rate
    :param v: (float) velocity across the advective layer
    :param d_time: (float) delta-time
    :param d_radius: (float) delta-radius
    :param d_theta: (float) delta-theta
    :param d_tube (int)
    :return: particle density at position (m,n) on the advective layer.
    """

    j_l = v * rho[k][m][n]
    if m == len(phi[k][m]) - 1:
        j_r = 0
    else:
        j_r = v * rho[k][m+1][n]

    component_a = (rho[k][m][n] - ((j_r - j_l) * (1/d_radius)) * d_time)

    N = len(phi[k][m])

    j_max = np.ceil((d_tube / ((m + 1) * d_radius * d_theta)) - 0.5)

    component_b = 0
    for j in range(-j_max, j_max + 1):
        component_b += phi[k][m][(n + j) % N]
    component_b *= a * (m+1) * (d_radius * d_theta * d_time)

    component_c = b * rho[k][m][n] * d_time

    return component_a + component_b - component_c


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def u_center(phi, k, d_radius, d_theta, d_time, curr_central, rho, tube_placements, v):
    """
    Calculates the particle density in the central patch.

    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) time-point
    :param d_radius: (float) delta-radius
    :param d_theta: (float) delta-theta
    :param d_time: (float) delta-time
    :param curr_central: (float) the current particle density at the center
    :param rho: (float) particle density on the
    :param tube_placements: (list(int)) discrete microtubule/filament positions between [0, rays-1]
    :param v: (float) velocity across the advective layer
    :return: particle density for the center patch
    """

    total_sum = 0
    for n in range(len(phi[0][0])):
        total_sum += j_l_r(phi, k, 0, n, d_radius, curr_central)

    total_sum *= (d_theta * d_time) / (np.pi * d_radius)
    diffusive_sum = curr_central - total_sum

    advective_sum = 0

    for i in range(len(tube_placements)):
        angle = tube_placements[i]
        j_l = rho[k][0][angle] * v
        advective_sum += (abs(j_l) * d_time) / (np.pi * d_radius * d_radius)

    return diffusive_sum + advective_sum


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def calc_mass(phi, rho, k, d_radius, d_theta, curr_central, rings, rays, tube_placements):
    """
    Calculates mass across the whole domain.

    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param rho: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) time-point
    :param d_radius: (float) delta-radius
    :param d_theta: (float) delta-theta
    :param curr_central: (float) the current particle density at the center
    :param rings: (int) # of radial rings in the domain
    :param rays: (int) # of angular rays in the domain
    :param tube_placements: (list(int)) discrete microtubule/filament positions between [0, rays-1]
    :return: domain mass
    """
    #
    # diffusive_mass = 0
    # for m in range(rings):
    #     for n in range(rays):
    #         diffusive_mass += phi[k][m][n] * (m+1)
    # diffusive_mass *= (d_radius * d_radius) * d_theta
    #
    # advective_mass = 0
    #
    # for i in range(len(tube_placements)):
    #     angle = tube_placements[i]
    #     for m in range(rings):
    #         advective_mass += rho[k][m][angle] * d_radius

    return calc_mass_diff(phi, k, d_radius, d_theta, curr_central, rings, rays) + calc_mass_adv(rho, k, d_radius, d_theta, rings, tube_placements)

    # return (curr_central * np.pi * d_radius * d_radius) + diffusive_mass + advective_mass


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def calc_mass_diff(phi, k, d_radius, d_theta, curr_central, rings, rays):
    diffusive_mass = 0
    for m in range(rings):
        for n in range(rays):
            diffusive_mass += phi[k][m][n] * (m + 1)
    diffusive_mass *= (d_radius * d_radius) * d_theta
    return (curr_central * np.pi * d_radius * d_radius) + diffusive_mass


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def calc_mass_adv(rho, k, d_radius, d_theta, rings, tube_placements):
    advective_mass = 0
    for i in range(len(tube_placements)):
        angle = tube_placements[i]
        for m in range(rings):
            advective_mass += rho[k][m][angle] * d_radius

    return advective_mass


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def calc_loss_mass_j_r_r(phi, k, d_radius, d_theta, rings, rays):
    """
    Calculates the amount of mass exiting the last ring of patches in the domain using radial currents.

    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) time-point
    :param d_radius: (float) delta_radius
    :param d_theta: (float) delta_theta
    :param rings: (int) # of radial rings in the domain
    :param rays: (int) # of angular rays in the domain
    :return: total mass exiting the final ring of patches
    """
    total_sum = 0
    for n in range(rays):
        total_sum += j_r_r(phi, k, rings-2, n, d_radius, 0)
    total_sum *= rings * d_radius * d_theta

    return total_sum


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def calc_mass_v_time_derivative(mass_container, d_time):
    """
    Calculates the derivative of mass as a function of time, m'(t), using
    a finite difference method.

    :param mass_container: (1-D float array) Domain mass for k time steps
    :param d_time: (float) delta-time
    :return: a 1-D float array of m'(t)
    """
    array = mass_container[:len(mass_container)-1].copy()
    for k in range(1, len(mass_container)):
        array[k-1] = (mass_container[k-1] - mass_container[k]) / d_time
    return array


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def j_r_r(phi, k, m, n, d_radius, rings):
    """

    Calculates the rightwards radial current

    Refer to project_src_package_2025/computational_tools/visual-discretization-demos for
    more information on the implementation/graphics of radial/angular currents

    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) time-point
    :param m: (int) position of radial ring
    :param n: (int) position of angular ray
    :param d_radius: (float) delta-radius
    :param rings: (int) # of radial rings in the domain
    :return: rightwards radial current
    """
    curr_ring = phi[k][m][n]
    if m == rings - 1:
        next_ring = 0
    else:
        next_ring = phi[k][m+1][n]
    return -1 * ((next_ring - curr_ring) / d_radius)


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def j_l_r(phi, k, m, n, d_radius, central):
    """

    Calculates the leftwards radial current

    Refer to project_src_package_2025/computational_tools/visual-discretization-demos for
    more information on the implementation/graphics of radial/angular currents

    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) time-point
    :param m: (int) position of radial ring
    :param n: (int) position of radial ring
    :param d_radius: (float) delta-radius
    :param central (float) the current particle density at the center
    :return: leftwards radial current
    """
    curr_ring = phi[k][m][n]
    if m == 0:
        prev_ring = central
    else:
        prev_ring = phi[k][m-1][n]
    return -1 * ((curr_ring - prev_ring) / d_radius)


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def j_r_t(phi, k, m, n, d_radius, d_theta):
    """
    Calculates the rightwards angular current

    Refer to project_src_package_2025/computational_tools/visual-discretization-demos for
    more information on the implementation/graphics of radial/angular currents

    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) time-point
    :param m: (int) position of radial ring
    :param n: (int) position of radial ring
    :param d_radius: (float) delta-radius
    :param d_theta: (float) delta-theta
    :return: rightwards angular current
    """
    b = len(phi[k][m])
    return -1 * (phi[k][m][(n+1) % b] - phi[k][m][n]) / ((m+1) * d_radius * d_theta)


@njit(nopython=ENABLE_JIT, cache=ENABLE_CACHE)
def j_l_t(phi, k, m, n, d_radius, d_theta):
    """
       Calculates the leftwards angular current

       Refer to project_src_package_2025/computational_tools/visual-discretization-demos for
       more information on the implementation/graphics of radial/angular currents

       :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
       :param k: (int) time-point
       :param m: (int) position of radial ring
       :param n: (int) position of radial ring
       :param d_radius: (float) delta-radius
       :param d_theta: (float) delta-theta
       :return: leftwards angular current
       """
    b = len(phi[k][m])
    return -1 * (phi[k][m][n] - phi[k][m][(n-1) % b]) / ((m+1) * d_radius * d_theta)


# !! The following functions below are used for the strict-rectangular config. Should be avoided in this version of the codebase [May-2025] !!
# ***********************************************************************************************************************************************
@njit(nopython=ENABLE_JIT)
def u_density_rec(phi, k, m, n, d_radius, d_theta, d_time, central, rings, rho, a, b, tube_placements, N, j_max):
    """

    Calculate particle density at a position (m,n) on the diffusive layer at a time-point k.
    (Positions are relative to patches across our domain for the diffusive layer)

    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) time-point
    :param m: (int) position of radial ring
    :param n: (int) position of angular ray
    :param d_radius: (float) delta_radius
    :param d_theta: (float) delta_theta
    :param d_time: (float) delta_time
    :param central: (float) particle density at the center
    :param rings: (int) # of radial rings in the domain
    :param rho: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param N (int)
    :param j_max (int)
    (to specify particle density on the advective layer relative to microtubule/filament)

    :param a: (float) switch rate onto the diffusive layer (switch-on rate)
    :param b: (float) switch rate onto the advective layer (switch-off rate)
    :param tube_placements: (list(int)) discrete microtubule/filament positions between [0, rays-1]
    :return: particle density at a position (m,n) on the diffusive layer
    """

    current_density = phi[k][m][n]

    component_a = ((m+2) * j_r_r(phi, k, m, n, d_radius, rings)) - ((m+1) * j_l_r(phi, k, m, n, d_radius, central))

    component_a *= d_time / ((m+1) * d_radius)

    component_b = (j_r_t(phi, k, m, n, d_radius, d_theta)) - (j_l_t(phi, k, m, n, d_radius, d_theta))

    component_b *= d_time / ((m+1) * d_radius * d_theta)

    component_c = 0

    # check if there is any microtubule within range of the current rectangular interval

    for t in range(len(tube_placements)):
        mt_pos = tube_placements[t]
        if (n-j_max) % N <= mt_pos <= (n+j_max) % N:
            component_c += ((b * rho[k][m][mt_pos]) * d_time) / ((m+1) * d_radius * d_theta * (1+2*j_max))

    if component_c > 0:
        component_c = (a * phi[k][m][n]) * d_time - component_c

    return current_density - component_a - component_b - component_c


@njit(nopython=ENABLE_JIT)
def u_tube_rec(rho, phi, k, m, n, a, b, v, d_time, d_radius, d_theta, j_max, N):
    """

    Calculate particle density at a position (m,n) on the advective layer at a time-point k.

    :param rho: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param phi: (3-D float array) With 2 time points, m rings (rows), and n rays (columns)
    :param k: (int) current time step
    :param m: (int) position of the radial ring
    :param n: (int) position of the angular ray
    :param a: (float) switch-on rate
    :param b: (float) switch-off rate
    :param v: (float) velocity across the advective layer
    :param d_time: (float) delta-time
    :param d_radius: (float) delta-radius
    :param d_theta: (float) delta-theta
    :return: particle density at position (m,n) on the advective layer.
    """

    j_l = v * rho[k][m][n]
    if m == len(phi[k][m]) - 1:
        j_r = 0
    else:
        j_r = v * rho[k][m+1][n]

    comp_a = rho[k][m][n] - ((j_r - j_l) / d_radius) * d_time
    comp_b = b * rho[k][m][n] * d_time

    sum = 0
    for j in range(-j_max, j_max+1):
        sum += phi[k][m][(n+j_max) % N]

    comp_c = (a * (m+1) * d_radius * d_theta * d_time) * sum

    return comp_a - comp_b + comp_c
