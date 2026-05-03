from __future__ import annotations

from typing import Any


def generate_candidate_solutions(data: dict[str, Any], base: dict[str, Any]) -> list[dict[str, Any]]:
    scenario = data.get("project_info", {}).get("scenario_type") or ""
    storage_power = float(base.get("storage_power_mw") or 0.0)
    storage_energy = float(base.get("storage_energy_mwh") or 0.0)
    pv_mwp = float(base.get("pv_mwp") or 0.0)
    wind_mw = float(base.get("wind_mw") or 0.0)

    variants: list[tuple[str, float]] = [("保守方案", 0.75), ("基准方案", 1.0), ("激进方案", 1.25)]
    solutions: list[dict[str, Any]] = []
    for name, factor in variants:
        item = {
            "name": name,
            "storage_power_mw": round(storage_power * factor, 3) if storage_power else None,
            "storage_energy_mwh": round(storage_energy * factor, 3) if storage_energy else None,
            "pv_mwp": round(pv_mwp * factor, 3) if pv_mwp and scenario != "charging_station" else (round(pv_mwp * min(factor, 1.15), 3) if pv_mwp else None),
            "wind_mw": round(wind_mw * factor, 3) if wind_mw else None,
        }
        solutions.append(item)
    return solutions
