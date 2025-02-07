from . import njit, math, numerical_tools as num, sys_config
import time

ENABLE_JIT = sys_config.ENABLE_NJIT

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


# computing Mean First Passage Time using the mass loss technique until a given mass retention threshold, 0.01 by default
@njit(nopython=ENABLE_JIT)
def comp_mfpt_by_mass_loss(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer,
                           mass_checkpoint=10**6, r=1, d=1, mass_retention_threshold=0.01):
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
                if m == rings - 1:
                    diffusive_layer[1][m][n] = 0
                else:
                    diffusive_layer[1][m][n] = num.u_density(diffusive_layer, 0, m, n, d_radius, d_theta, d_time,
                                                         phi_center, rings, advective_layer, angle_index, a, b,
                                                         tube_placements)
                    if n == tube_placements[angle_index]:
                        advective_layer[1][m][n] = num.u_tube(advective_layer, diffusive_layer, 0, m, n, a, b, v, d_time,
                                                          d_radius, d_theta)
                        if angle_index < len(tube_placements) - 1:
                            angle_index = angle_index + 1

                if m == rings - 2:
                    net_current_out += num.j_r_r(diffusive_layer, 0, m, n, d_radius, 0) * rings * d_radius * d_theta
                n += 1
            m += 1

        m_f_p_t += net_current_out * k * d_time * d_time
        k += 1
        if k > 0 and k % mass_checkpoint == 0:
            print("Velocity (V)= ", v, "Time step: ", k, "Simulation time: ", k * d_time, "Current mass: ", mass_retained,
                  "a=", a, "b=", b)

        mass_retained = num.calc_mass(diffusive_layer, advective_layer, 0, d_radius, d_theta, phi_center, rings, rays,
                                  tube_placements)
        phi_center = num.u_center(diffusive_layer, 0, d_radius, d_theta, d_time, phi_center, advective_layer,
                              tube_placements, v)
        diffusive_layer[0] = diffusive_layer[1]
        advective_layer[0] = advective_layer[1]
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    duration = k * d_time

    return m_f_p_t, duration