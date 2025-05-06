from . import np, sys_config, njit

ENABLE_JIT = sys_config.ENABLE_NJIT

def initialize_layers(rg_param, ry_param):
    diffusive_layer = np.zeros((2, rg_param, ry_param), dtype=np.float64)
    advective_layer = np.zeros((2, rg_param, ry_param), dtype=np.float64)
    return diffusive_layer, advective_layer


'''
Generates a list of angles to be considered when updating the diffusive layer with respect to
the "mixed-code"
'''
@njit(nopython=ENABLE_JIT)
def mod_range_flat_sorted(centers, radius, N):
    total_len = len(centers) * (2 * radius + 1)
    flat_result = np.empty(total_len, dtype=np.int64)
    idx = 0

    for i in range(len(centers)):
        center = centers[i]
        for offset in range(-radius, radius + 1):
            val = (center + offset) % N
            flat_result[idx] = val
            idx += 1

    return np.sort(flat_result)

@njit(nopython=ENABLE_JIT)
def in_ring(val, center, radius, N):
    """

    Args:
        val: (int) value we're interested in checking
        center: (int) center of the modular ring
        radius: (int) the range/"reach" of our modular ring
        N: (int) the length of the modular ring before cycling

    Returns: (bool) if the value is contained within the modular ring

    """
    for i in range(-radius, radius + 1):
        if (center + i) % N == val % N:
            return True
    return False


# This function/algorithm is currently under construction
def MTOC_offset_bound(bound_arr, rg_param, ry_param, offset_theta, offset_radius, disable_vert=False, disable_horz=False):

    if disable_horz:
        a = 0
    else:
        a = 1
    if disable_vert:
        b = 0
    else:
        b = 1

    offset_vert = ((1 - offset_radius) * np.sin(offset_theta)) * a
    offset_horz = ((1 - offset_radius) * np.cos(offset_theta)) * b

    delta_theta = (2 * np.pi) / ry_param
    delta_radius = 1 / rg_param

    for n in range(ry_param):
        ang_phi = n * delta_theta
        x = offset_horz * np.cos(ang_phi) + offset_vert * np.sin(ang_phi)
        rho = np.sqrt((x ** 2) + (offset_radius ** 2) - (offset_vert ** 2) - (offset_horz ** 2)) + x
        bound_arr[n] = np.ceil(rho * delta_radius)
    return


