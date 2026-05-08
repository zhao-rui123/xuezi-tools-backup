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
        "source_grid_load_storage": "user_side_storage",
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


def classify_business_scenario(data: dict[str, Any], primary_scenario: str) -> tuple[str, str]:
    if primary_scenario == "microgrid":
        return _classify_microgrid_business_scenario(data)
    if primary_scenario != "user_side_storage":
        return primary_scenario, primary_scenario

    market = data.get("market_data", {}) or {}
    mode = str(market.get("market_mode") or "").strip().lower()
    if _has_user_side_renewable_sources(data):
        return "source_grid_load_storage", "源网荷储工商业场景"
    if market.get("market_price_series") or any(token in mode for token in ("spot", "trading", "market_price")):
        return "power_trading_commercial_storage", "电力交易工商业储能场景"
    if market.get("tou_tariff") or "tou" in mode:
        return "tou_commercial_storage", "分时电价工商业储能场景"
    return "general_commercial_storage", "通用工商业储能场景"


def _classify_microgrid_business_scenario(data: dict[str, Any]) -> tuple[str, str]:
    project = data.get("project_info", {}) or {}
    load_data = data.get("load_data", {}) or {}
    backup = (data.get("equipment", {}) or {}).get("conventional_backup", {}) or {}
    target_priority = str(project.get("target_priority") or "").strip().lower()
    _ratio = project.get("renewable_penetration_target_ratio")
    if _ratio is None:
        _ratio = project.get("target_renewable_coverage_ratio")
    renewable_target_ratio = float(_ratio) if _ratio is not None else 0.0
    _cl = load_data.get("critical_load_kw")
    critical_load_kw = float(_cl) if _cl is not None else 0.0
    _bh = load_data.get("backup_hours_required")
    backup_hours_required = float(_bh) if _bh is not None else 0.0
    if target_priority == "reliability_first" or (backup.get("enabled") and critical_load_kw > 0 and backup_hours_required > 0):
        return "reliability_offgrid_microgrid", "保供型离网微电网场景"
    if target_priority in {"green_power_first", "high_renewable", "high_renewable_penetration"} or renewable_target_ratio >= 0.7:
        return "high_renewable_offgrid_microgrid", "高绿电渗透率离网微电网场景"
    if target_priority in {"economic_first", "cost_first"}:
        return "economic_offgrid_microgrid", "经济型离网微电网场景"
    return "general_microgrid", "通用微电网场景"


def route_source_grid_load_storage_operation_mode(data: dict[str, Any]) -> tuple[str, str]:
    if not _has_user_side_renewable_sources(data):
        return "", ""

    explicit = str(
        (data.get("project_info", {}) or {}).get("operation_mode")
        or (data.get("market_data", {}) or {}).get("operation_mode")
        or ""
    ).strip().lower()
    explicit_map = {
        "renewable_self_consumption": "renewable_self_consumption",
        "renewable_peak_shaving": "renewable_peak_shaving",
        "renewable_tou_arbitrage": "renewable_tou_arbitrage",
        "renewable_market_cooptimization": "renewable_market_cooptimization",
        "renewable_export_oriented": "renewable_export_oriented",
    }
    if explicit in explicit_map:
        return explicit_map[explicit], "explicit operation_mode"

    market = data.get("market_data", {}) or {}
    market_mode = str(market.get("market_mode") or "").strip().lower()
    target_priority = str((data.get("project_info", {}) or {}).get("target_priority") or "").strip().lower()

    if market.get("allow_export_to_grid"):
        return "renewable_export_oriented", "allow_export_to_grid enabled"
    if market.get("spot_price_daily_profiles") or market.get("market_price_series") or any(
        token in market_mode for token in ("spot", "trading", "market_price")
    ):
        return "renewable_market_cooptimization", "market price series or spot profiles detected"
    if market.get("tou_tariff") or "tou" in market_mode:
        return "renewable_tou_arbitrage", "tou tariff detected"
    if target_priority in {"peak_shaving", "demand_saving", "capacity_saving"}:
        return "renewable_peak_shaving", "target_priority requests peak shaving"
    return "renewable_self_consumption", "default renewable self-consumption routing"


def _has_user_side_renewable_sources(data: dict[str, Any]) -> bool:
    resource = data.get("resource_data", {}) or {}
    solar = resource.get("solar", {}) or {}
    wind = resource.get("wind", {}) or {}
    solar_keys = (
        "available_area_m2",
        "installed_capacity_mwp",
        "installed_capacity_mw",
        "hourly_generation_profile_kw",
        "hourly_generation_profile_kw_path",
        "hourly_irradiance_kwh_per_m2",
        "hourly_irradiance_kwh_per_m2_path",
        "daily_irradiance_kwh_per_m2",
        "monthly_irradiation_kwh_per_m2",
        "annual_irradiation_kwh_per_m2",
        "specific_yield_kwh_per_kwp_year",
    )
    wind_keys = (
        "installed_capacity_mw",
        "hourly_generation_profile_kw",
        "hourly_generation_profile_kw_path",
        "wind_speed_series_mps",
        "wind_speed_series_mps_path",
        "hourly_wind_speed_series_mps",
        "daily_wind_speed_series_mps",
        "monthly_capacity_factor",
        "annual_avg_speed_mps",
        "power_curve",
        "expected_full_load_hours",
    )
    return any(solar.get(key) for key in solar_keys) or any(wind.get(key) for key in wind_keys)
