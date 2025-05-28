@njit(nopython=ENABLE_JIT)
def comp_until_mass_depletion(rings, rays, a, b, v, tube_placements, diffusive_layer, advective_layer, r=1.0, d=1.0,
                              mass_retention_threshold=0.01, mixed_config=False, mx_cn_rrange=1, init_j_max=1):
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
    d_rect = 0
    if mixed_config:
        '''
            if init_j_max is selected outside an invalid range then j_max is decided automatically relative to the configuration of filaments,
            otherwise the user is able to select a j_max within the appropriate range. 
        '''

        j_max = sup.j_max_bef_overlap(rays, tube_placements)

        if init_j_max < 0 or init_j_max > j_max:
            d_rect = sup.solve_d_rect(r, rings, rays, j_max, 0)
            print('Initial j-max: ', j_max)
        else:
            d_rect = sup.solve_d_rect(r, rings, rays, init_j_max, 0)
            print('Initial j-max', init_j_max)

        for m in range(mx_cn_rrange):
            j_max = math.floor(d_rect / ((m + 1) * d_radius * d_theta) - 0.5)
            # print(j_max)
            keys = sup.mod_range_flat(tube_placements, j_max, rays, False)
            # print(keys)
            d = sup.dict_gen(keys, tube_placements)
            d_list.append(d)
    # *** Mixed configuration block 5/27/25

    # print(d_list)

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
                    if mixed_config and m < mx_cn_rrange and n in d_list[m]:
                        j_max = math.floor(d_rect / ((m + 1) * d_radius * d_theta) - 0.5)
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
                            j_max = math.floor(d_rect / ((m + 1) * d_radius * d_theta) - 0.5)
                            # advective_layer[1][m][n] = num.u_tube_mixed(advective_layer, diffusive_layer, 0, m, n,
                            #                                             a, b,
                            #                                             v,
                            #                                             d_time, d_radius, d_theta, mx_cn_rrange)
                            advective_layer[1][m][n] = num.u_tube_rect(advective_layer, diffusive_layer, 0, m, n,
                                                                        a, b,
                                                                        v,
                                                                        d_time, d_radius, d_theta, mx_cn_rrange, j_max)
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
