from launch_functions import launch

# an example setup of an MFPT computation
if __name__ == "__main__":
    # Rings
    rg_param = 32
    # Rays
    ry_param = 32
    # Microtubule configurations
    N_param = [0, 8, 16, 24]
    # Velocity
    v_param = -10
    # Switch rate, such that a=b=W
    w_param = 10 ** 4

    mfpt, duration = launch.solve_mfpt(rg_param, ry_param, N_param, v_param, w_param, True)

    '''
    'T' denotes simulation time in dimensionless units, in this case, 
    it represents the duration to compute MFPT under given conditions
    '''
    print(f'MFPT: {mfpt}    T: {duration}')
