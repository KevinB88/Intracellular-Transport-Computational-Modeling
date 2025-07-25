from project_src_package_2025.data_visualization import ani_evolution as evo
from project_src_package_2025.computational_tools import numerical_tools as num
from project_src_package_2025.computational_tools import supplements as sup
from project_src_package_2025.data_processing import data_process_functions as pro
import numpy as np


def test_batch_method_1_iter(rg_param, ry_param, w_param, v_param, N_LIST, T_LIST, T_param, T_fixed_ring_seg, D=1.0, domain_radius=1.0,
                             save_png=True, show_plt=False):

    PvT_DL_snapshots = np.zeros((len(T_LIST), ry_param), dtype=np.float64)

    K = int((T_param / num.compute_dT(rg_param, ry_param, domain_radius, D))) + 2

    v_param *= -1

    init_cond_center = num.compute_init_cond_cent(rg_param)

    D_LAYER = np.zeros((K, rg_param, ry_param), dtype=np.float64)
    A_LAYER = np.zeros((K, rg_param, ry_param), dtype=np.float64)
    C_list = np.zeros([K], dtype=np.float64)
    C_list[0] = init_cond_center

    evo.collect_stamps_for_animation_test(rg_param, ry_param, w_param, w_param, v_param, N_LIST, D_LAYER, A_LAYER, PvT_DL_snapshots,
                                          T_LIST, C_list, K, d_tube=0, T_fixed_ring_seg=T_fixed_ring_seg)

    pro.process_PvT_DL(PvT_DL_snapshots, v_param, w_param, N_LIST, T_fixed_ring_seg, save_png, show_plt, T_LIST)


