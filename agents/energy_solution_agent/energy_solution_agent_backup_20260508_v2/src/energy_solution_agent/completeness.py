from __future__ import annotations

from typing import Any


def evaluate_data_completeness(data: dict[str, Any]) -> tuple[str, list[str]]:
    missing: list[str] = []

    project = data.get("project_info") or {}
    load_data = data.get("load_data") or {}
    market = data.get("market_data") or {}
    financial = data.get("financial") or {}
    resource = data.get("resource_data") or {}
    equipment = data.get("equipment") or {}
    carbon = data.get("carbon_data") or {}

    if not project.get("scenario_type"):
        missing.append("project_info.scenario_type")
    if not project.get("province"):
        missing.append("project_info.province")
    if not load_data.get("load_series_kw") and not load_data.get("peak_load_kw"):
        missing.append("load_data.load_series_kw or load_data.peak_load_kw")
    if not load_data.get("annual_consumption_mwh"):
        missing.append("load_data.annual_consumption_mwh")
    if not market.get("market_mode") and not market.get("tou_tariff") and not market.get("market_price_series"):
        missing.append("market_data.market_mode or market_data.tou_tariff")
    if not (data.get("network_and_design") or {}).get("point_of_connection"):
        missing.append("network_and_design.point_of_connection")
    if not financial.get("capex") and not financial.get("project_years"):
        missing.append("financial.capex or financial.project_years")

    # Scenario-specific checks
    scenario = str(project.get("scenario_type") or "").lower()
    if scenario in {"user_side_storage", "pv_storage", "microgrid", "source_grid_load_storage"}:
        if not equipment.get("storage"):
            missing.append("equipment.storage")
    if carbon.get("industry_type") or carbon.get("carbon_claim_target"):
        if not carbon.get("baseline_emissions_tco2e"):
            missing.append("carbon_data.baseline_emissions_tco2e")
    if resource.get("solar"):
        if not resource["solar"].get("available_area_m2") and not resource["solar"].get("hourly_generation_profile_kw") and not resource["solar"].get("hourly_irradiance_kwh_per_m2"):
            missing.append("resource_data.solar.available_area_m2 or generation/irradiance profile")
    if resource.get("wind"):
        if not resource["wind"].get("annual_avg_speed_mps") and not resource["wind"].get("hourly_generation_profile_kw"):
            missing.append("resource_data.wind.annual_avg_speed_mps or generation profile")

    if len(missing) == 0:
        grade = "A"
    elif len(missing) <= 2:
        grade = "B"
    elif len(missing) <= 4:
        grade = "C"
    else:
        grade = "D"
    return grade, missing
