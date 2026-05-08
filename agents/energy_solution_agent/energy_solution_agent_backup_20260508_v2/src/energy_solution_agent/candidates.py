from __future__ import annotations

from typing import Any


def generate_candidate_solutions(data: dict[str, Any], base: dict[str, Any]) -> list[dict[str, Any]]:
    scenario = data.get("project_info", {}).get("scenario_type") or ""
    storage_power = float(base.get("storage_power_mw") or 0.0)
    storage_energy = float(base.get("storage_energy_mwh") or 0.0)
    pv_mwp = float(base.get("pv_mwp") or 0.0)
    wind_mw = float(base.get("wind_mw") or 0.0)

    # Configurable sensitivity factors (user override via financial.sensitivity_factors)
    factors_cfg = (data.get("financial", {}) or {}).get("sensitivity_factors") or {}
    conservative = float(factors_cfg.get("conservative") or 0.75)
    aggressive = float(factors_cfg.get("aggressive") or 1.25)

    variants: list[tuple[str, float]] = [
        ("保守方案", conservative),
        ("基准方案", 1.0),
        ("激进方案", aggressive),
    ]
    solutions: list[dict[str, Any]] = []
    for name, factor in variants:
        sp = round(storage_power * factor, 3) if storage_power is not None else None
        se = round(storage_energy * factor, 3) if storage_energy is not None else None
        if pv_mwp is not None and pv_mwp > 0:
            effective_factor = min(factor, 1.15) if scenario == "charging_station" else factor
            pv_val = round(pv_mwp * effective_factor, 3)
        else:
            pv_val = None
        wm = round(wind_mw * factor, 3) if wind_mw is not None else None
        item = {
            "name": name,
            "storage_power_mw": sp,
            "storage_energy_mwh": se,
            "pv_mwp": pv_val,
            "wind_mw": wm,
        }
        solutions.append(item)
    return solutions
