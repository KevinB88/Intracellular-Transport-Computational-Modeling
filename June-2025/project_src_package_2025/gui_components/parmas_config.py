
PARAMETER_SCHEMAS = {
    "Solve MFPT": {
        "required": [
            ("rg_param", ""),
            ("ry_param", ""),
            ("N_LIST", ""),
            ("v_param", ""),
            ("w_param", ""),
            ("T_param", "")
        ],
        "default": [
            ("domain_radius", 1.0),
            ("D", 1.0),
            ("mass_checkpoint", int(1e6)),
            ("d_tube", 0)
        ]
    },
    "Time Until Mass Depletion": {
        "required": [
            ("rg_param", ""),
            ("ry_param", ""),
            ("N_LIST", ""),
            ("v_param", ""),
            ("w_param", "")
        ],
        "default": [
            ("domain_radius", 1.0),
            ("D", 1.0),
            ("d_tube", 0),
            ("mass_threshold", 0.01)
        ]
    },
    "Phi Angular Dependence": {
        "required": [
            ("rg_param", ""),
            ("ry_param", ""),
            ("v_param", ""),
            ("w_param", ""),
            ("T_param", ""),
            ("N_LIST", ""),
            ("checkpoint_collect_container", ""),
        ],
        "default": [
            ("approach", 2),
            ("T_fixed_ring_seg", 0.5),
            ("d_tube", 0),
            ("domain_radius", 1.0),
            ("D", 1.0),
            ("mass_retention_threshold", 0.01),
            ("mass_checkpoint", int(1e6)),
            ("save_png", True),
            ("show_plt", False)
        ]
    },
    "Density Radial Dependence": {
        "required": [
            ("rg_param", ""),
            ("ry_param", ""),
            ("N_LIST", ""),
            ("v_param", ""),
            ("w_param", ""),
            ("T_param", ""),
            ("checkpoint_collect_container", ""),
        ],
        "default": [
            ("R_fixed_angle", -1),
            ("approach", 2),
            ("domain_radius", 1.0),
            ("D", 1.0),
            ("d_tube", 0),
            ("mass_retention_threshold", 0.01),
            ("mass_checkpoint", int(1e6)),
            ("save_png", True),
            ("show_plt", False)
        ]
    },
    "Mass Analysis": {
        "required": [
            ("rg_param", ""),
            ("ry_param", ""),
            ("v_param", ""),
            ("w_param", ""),
            ("T_param", ""),
            ("N_LIST", ""),
        ],
        "default": [
            ("MA_collection_factor", int(5)),
            ("domain_radius", 1.0),
            ("D", 1.0),
            ("mass_checkpoint", int(1e6)),
            ("d_tube", 0),
            ("MA_collection_factor_limit", int(1e3)),
            ("save_png", True),
            ("show_plt", False)
        ]
    },

    "Full Analysis": {
        "required": [
            ("rg_param", ""),
            ("ry_param", ""),
            ("w_param", ""),
            ("v_param", ""),
            ("T_param", ""),
            ("N_LIST", "")
        ],
        "default": [
            ("d_tube", 0.0),
            ("Timestamp_List", None),
            ("MA_collection_factor", int(5)),
            ("MA_collection_factor_limit", int(1e3)),
            ("D", 1.0),
            ("domain_radius", 1.0),
            ("mass_checkpoint", int(1e6)),
            ("T_fixed_ring_seg", 0.5),
            ("R_fixed_angle", int(-1)),
            ("save_png", True),
            ("save_csv", True),
            ("show_plt", False),
            ("heat_plot_border", False),
            ("heatplot_colorscheme", 'viridis'),
            ("display_extraction", True)
        ]
    }
}

