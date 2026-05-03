from __future__ import annotations

from typing import Any


def route_scenario(data: dict[str, Any]) -> tuple[str, list[str], str]:
    declared = (data.get("project_info", {}).get("scenario_type") or "").strip().lower()
    charging = data.get("charging_data", {})
    thermal = data.get("thermal_system", {})
    carbon = data.get("carbon_data", {})
    resource = data.get("resource_data", {})

    secondaries: list[str] = []

    if charging.get("station_type") or charging.get("num_chargers"):
        secondaries.append("charging_station")
    if thermal.get("service_type") or data.get("load_data", {}).get("cooling_load_series_kw"):
        secondaries.append("thermal_system")
    if carbon.get("industry_type") or carbon.get("carbon_claim_target"):
        secondaries.append("zero_carbon_factory")
    if resource.get("solar", {}).get("available_area_m2"):
        secondaries.append("pv")
    if resource.get("wind", {}).get("annual_avg_speed_mps"):
        secondaries.append("wind")

    mapping = {
        "user_side_storage": "user_side_storage",
        "industrial_storage": "user_side_storage",
        "pv_storage": "pv_storage",
        "charging_station": "charging_station",
        "thermal_system": "thermal_system",
        "zero_carbon_factory": "zero_carbon_factory",
        "microgrid": "microgrid",
        "wind_pv_storage": "wind_pv_storage",
    }
    if declared in mapping:
        return mapping[declared], secondaries, "declared by input"
    if "zero_carbon_factory" in secondaries:
        return "zero_carbon_factory", secondaries, "derived from carbon_data"
    if "charging_station" in secondaries:
        return "charging_station", secondaries, "derived from charging_data"
    if "thermal_system" in secondaries:
        return "thermal_system", secondaries, "derived from thermal_system"
    if secondaries:
        return "integrated_energy", secondaries, "derived from attached sub-scenarios"
    return "user_side_storage", secondaries, "fallback default"
