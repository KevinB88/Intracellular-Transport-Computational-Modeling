
PARAMETER_SCHEMAS = {
    "Solve MFPT": {
        "required": [
            ("rg_param", ""),
            ("ry_param", ""),
            ("N_param", ""),
            ("v_param", ""),
            ("w_param", ""),
            ("T_param", "")
        ],
        "default": [
            ("r", 1.0),
            ("d", 1.0),
            ("mass_checkpoint", int(1e6)),
            ("d_tube", 0),
            ("return_duration", False)
        ]
    },
    "Time Until Mass Depletion": {
        "required": [
            ("rg_param", ""),
            ("ry_param", ""),
            ("N_param", ""),
            ("v_param", ""),
            ("w_param", "")
        ],
        "default": [
            ("mass_threshold", 0.01),
            ("mixed_config", False),
            ("d_tube", 0)
        ]
    },
    "Phi Angular Dependence": {
        "required": [
            ("rg_param", ""),
            ("ry_param", ""),
            ("N_param", ""),
            ("v_param", ""),
            ("w_param", ""),
        ],
        "default": [
            ("approach", 3),
            ("m_segment", 0.5),
            ("r", 1.0),
            ("d", 1.0),
            ("mass_retention_threshold", 0.01),
            ("time_point_container", "[1.0, 2.0, 3.0]"),
            ("mixed_config", False),
            ("d_tube", 0),
            ("save_png", True),
            ("show_plt", False)
        ]
    },
    "Density Radial Dependence": {
        "required": [
            ("rg_param", ""),
            ("ry_param", ""),
            ("N_param", ""),
            ("v_param", ""),
            ("w_param", ""),
            ("fixed_angle", ""),
            ("time_point_container", "")
        ],
        "default": [
            ("r", 1.0),
            ("d", 1.0),
            ("mass_retention_threshold", 0.01),
            ("mass_checkpoint", int(1e6)),
            ("save_png", True),
            ("show_plt", False),
            ("mixed_config", False),
            ("d_tube", 0)
        ]
    },
    "Mass Analysis": {
        "required": [
            ("rg_param", ""),
            ("ry_param", ""),
            ("N_param", ""),
            ("v_param", ""),
            ("w_param", ""),
            ("T_param", ""),
            ("collection_width", "")
        ],
        "default": [
            ("r", 1.0),
            ("d", 1.0),
            ("mass_checkpoint", int(1e6)),
            ("save_png", False),
            ("show_plt", True),
            ("mixed_config", False),
            ("d_tube", 0),
            ("collect_MFPT", False),
            ("collect_plots", True)
        ]
    }
}
