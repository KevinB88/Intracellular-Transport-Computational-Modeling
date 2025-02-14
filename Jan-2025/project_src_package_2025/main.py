from launch_functions import launch
# from data_visualization import animation_functions as ani, plot_functions as plt
from auxiliary_tools import unit_conversion_functions as uni
# from system_configuration import file_paths as fp
# from computational_tools import analysis_tools as ant

import time as clk

if __name__ == "__main__":

    rg_param = 48
    ry_param = 48
    N_param = [0, 4, 8, 12]
    v_param = -100
    w_param = 10 ** 4

    # Task 1

    # find time to reach 1% of mass rate, T
    start = clk.time()
    T = launch.output_time_until_mass_depletion(rg_param, ry_param, N_param, v_param, w_param)
    end = clk.time()
    op_duration_1 = end - start
    print("Duration to reach 1% of mass: (real time)", uni.convert_seconds(op_duration_1))
    start = clk.time()
    # collecting at the following time-points
    time_points = [T*0.01, T*0.1, T*0.2, T*0.3, T*0.4, T*0.5, T*0.6, T*0.7, T*0.8, T*0.9, T]
    # for i in range(11): time_points.append(i/10)
    # configure the computation for phi-theta density profiles at points in time_points.
    launch.collect_phi_v_theta(rg_param, ry_param, N_param, v_param, w_param, 3, time_point_container=time_points, verbose=True, save_png=True)
    end = clk.time()
    op_duration_2 = end - start
    print("Duration to collect phi-theta density profiles at points in time_points: (real time)", uni.convert_seconds(op_duration_2))

    # Task 2

    start = clk.time()
    T2 = launch.output_time_until_mass_depletion(rg_param, ry_param, N_param, v_param, w_param, mass_threshold=0.5002)
    print("<**********> Time until approx. 50% of mass exited: (sim time)", T2)
    end = clk.time()

    op_duration_3 = end - start
    print("Duration until approx. 50% of mass exited: (real time)", uni.convert_seconds(op_duration_3))

    start = clk.time()
    launch.collect_phi_v_theta(rg_param, ry_param, N_param, v_param, w_param, 4, verbose=True, mass_retention_threshold=0.5002,
                               time_point_container=[1])
    end = clk.time()

    op_duration_4 = end - start
    print("Duration to collect phi-theta density profiles across every other ring: (real time)", uni.convert_seconds(op_duration_4))

    start = clk.time()
    T3 = launch.output_time_until_mass_depletion(rg_param, ry_param, N_param, v_param, w_param, mass_threshold=0.99005)
    print("<**********> Time until approx. 1% of mass exited: (sim time)", T3)
    end = clk.time()

    op_duration_5 = end - start
    print("Duration until approx. 1% of mass exited: (real time)", uni.convert_seconds(op_duration_3))

    start = clk.time()
    launch.collect_phi_v_theta(rg_param, ry_param, N_param, v_param, w_param, 4, verbose=True,
                               mass_retention_threshold=0.99005, time_point_container=[1])
    end = clk.time()

    op_duration_6 = end - start
    print("Duration to collect phi-theta density profiles across every other ring: (real time)",
          uni.convert_seconds(op_duration_6))








