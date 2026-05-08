from __future__ import annotations

from typing import Any


def route_scenario(data: dict[str, Any]) -> tuple[str, list[str], str]:
    """场景路由：用户显式声明 > 自动推断 > 默认兜底
    
    返回：(主场景, 副场景列表, 推断依据)
    """
    declared = (data.get("project_info", {}).get("scenario_type") or "").strip().lower()
    charging = data.get("charging_data", {})
    thermal = data.get("thermal_system", {})
    carbon = data.get("carbon_data", {})
    resource = data.get("resource_data", {})
    market = data.get("market_data", {})
    load = data.get("load_data", {})

    secondary_candidates: list[str] = []

    if charging.get("station_type") or charging.get("num_chargers") or charging.get("arrival_profile"):
        secondary_candidates.append("charging_station")
    if thermal.get("service_type") or load.get("cooling_load_series_kw") or load.get("heating_load_series_kw"):
        secondary_candidates.append("thermal_system")
    if carbon.get("industry_type") or carbon.get("carbon_claim_target") or carbon.get("baseline_emissions_tco2e"):
        secondary_candidates.append("zero_carbon_factory")
    if resource.get("solar", {}).get("available_area_m2") or resource.get("solar", {}).get("hourly_generation_profile_kw"):
        secondary_candidates.append("pv")
    if resource.get("wind", {}).get("hourly_generation_profile_kw") or resource.get("wind", {}).get("wind_speed_series_mps") or resource.get("wind", {}).get("annual_avg_speed_mps"):
        secondary_candidates.append("wind")

    # ── 显式声明优先 ──
    mapping = {
        "user_side_storage": "user_side_storage",
        "industrial_storage": "user_side_storage",
        "pv_storage": "pv_storage",
        "charging_station": "charging_station",
        "thermal_system": "thermal_system",
        "zero_carbon_factory": "zero_carbon_factory",
        "microgrid": "microgrid",
        "wind_pv_storage": "wind_pv_storage",
        "market_storage": "market_storage",
        "data_center": "data_center",
        "steel_factory": "steel_factory",
    }
    if declared:
        matched = mapping.get(declared)
        if matched:
            return matched, secondary_candidates, "declared by input"
        # 未命中映射的关键词也原样保留
        return declared, secondary_candidates, "declared by input (custom)"

    # ── 自动推断 ──
    market_mode = str(market.get("market_mode") or "").lower()
    has_pv = "pv" in secondary_candidates
    has_wind = "wind" in secondary_candidates
    has_charging = "charging_station" in secondary_candidates
    has_thermal = "thermal_system" in secondary_candidates
    has_carbon = "zero_carbon_factory" in secondary_candidates
    grid_tied = market_mode in ("tou_tariff", "spot", "market_price_series")
    offgrid = market_mode in ("offgrid_internal",)
    has_ppa = market_mode in ("ppa",)
    peak_load = float(load.get("peak_load_kw") or 0.0)
    annual_load = float(load.get("annual_consumption_mwh") or 0.0)
    high_load = annual_load >= 50000

    # 充电站
    if has_charging:
        return "charging_station", secondary_candidates, "auto: charging data detected"
    # 冷热负荷 + 碳 data → zero_carbon_factory
    if has_carbon and (has_thermal or high_load):
        return "zero_carbon_factory", secondary_candidates, "auto: carbon + thermal/load detected"
    # 离网 + 有风光 → microgrid
    if offgrid and (has_pv or has_wind):
        return "microgrid", secondary_candidates, "auto: offgrid + renewables detected"
    # 冷热系统独立
    if has_thermal:
        return "thermal_system", secondary_candidates, "auto: thermal_data detected"
    # 并网 + 有TOU/spot → market_storage
    if grid_tied and peak_load > 0:
        return "market_storage", secondary_candidates, "auto: grid-tied + load detected"
    # PPA
    if has_ppa and high_load:
        return "zero_carbon_factory", secondary_candidates, "auto: PPA + high load"
    # 仅有碳数据 → zero_carbon_factory
    if has_carbon:
        return "zero_carbon_factory", secondary_candidates, "auto: carbon data detected"
    # PV+Wind
    if has_pv and has_wind:
        return "wind_pv_storage", secondary_candidates, "auto: PV + wind detected"
    # 仅有 PV
    if has_pv:
        return "pv_storage", secondary_candidates, "auto: PV detected"
    # 仅有负荷
    if secondary_candidates:
        return "integrated_energy", secondary_candidates, "auto: attached sub-scenarios"
    return "user_side_storage", secondary_candidates, "fallback default"
