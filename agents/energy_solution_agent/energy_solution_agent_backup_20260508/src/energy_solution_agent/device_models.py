from __future__ import annotations

PV_MODULE_MODELS = {
    "mono_pperc_550w": {
        "area_per_mwp": 7000,
        "derating_factor": 0.92,
        "performance_ratio": 0.84,
        "temp_coefficient_pct_per_c": -0.34,
        "reference_temp_c": 25.0,
        "noct_c": 45.0,
    },
    "desert_utility_pv": {
        "area_per_mwp": 7600,
        "derating_factor": 0.90,
        "performance_ratio": 0.82,
        "temp_coefficient_pct_per_c": -0.35,
        "reference_temp_c": 25.0,
        "noct_c": 46.0,
    },
}

WIND_TURBINE_MODELS = {
    "onshore_3mw_ieciii": {
        "hub_height_m": 100.0,
        "reference_height_m": 10.0,
        "shear_exponent": 0.14,
        "cut_in_mps": 3.0,
        "rated_mps": 12.0,
        "cut_out_mps": 25.0,
    },
    "high_wind_5mw": {
        "hub_height_m": 120.0,
        "reference_height_m": 10.0,
        "shear_exponent": 0.12,
        "cut_in_mps": 3.0,
        "rated_mps": 11.5,
        "cut_out_mps": 25.0,
    },
}
