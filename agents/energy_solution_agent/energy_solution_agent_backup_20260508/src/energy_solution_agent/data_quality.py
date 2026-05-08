from __future__ import annotations

from typing import Any


VALID_SERIES_LENGTHS = {24, 48, 96, 8760}


def assess_data_quality(data: dict[str, Any]) -> dict[str, Any]:
    checks = []
    warnings: list[str] = []
    score = 100

    checks.extend(
        [
            _check_series("load_data.load_series_kw", data.get("load_data", {}).get("load_series_kw")),
            _check_series("load_data.cooling_load_series_kw", data.get("load_data", {}).get("cooling_load_series_kw")),
            _check_series("load_data.heating_load_series_kw", data.get("load_data", {}).get("heating_load_series_kw")),
            _check_series("resource_data.solar.hourly_generation_profile_kw", data.get("resource_data", {}).get("solar", {}).get("hourly_generation_profile_kw")),
            _check_series("resource_data.wind.hourly_generation_profile_kw", data.get("resource_data", {}).get("wind", {}).get("hourly_generation_profile_kw")),
            _check_series("resource_data.wind.wind_speed_series_mps", data.get("resource_data", {}).get("wind", {}).get("wind_speed_series_mps")),
            _check_series("charging_data.arrival_profile", data.get("charging_data", {}).get("arrival_profile")),
        ]
    )

    for item in checks:
        if item["status"] == "warning":
            warnings.append(item["message"])
            score -= 7
        if item["status"] == "fail":
            warnings.append(item["message"])
            score -= 15

    if data.get("project_info", {}).get("scenario_type") == "zero_carbon_factory" and not data.get("carbon_data", {}).get("baseline_emissions_tco2e"):
        warnings.append("零碳工厂场景缺少碳排基线数据。")
        score -= 12

    if data.get("market_data", {}).get("market_mode") == "market_price_series" and not data.get("market_data", {}).get("market_price_series"):
        warnings.append("声明了市场价格模式，但缺少价格序列。")
        score -= 20

    if score >= 90:
        level = "high"
    elif score >= 75:
        level = "medium"
    else:
        level = "low"

    return {
        "score": max(0, score),
        "level": level,
        "checks": checks,
        "warnings": warnings,
    }


def _check_series(name: str, values: Any) -> dict[str, Any]:
    if not values:
        return {"name": name, "status": "missing", "message": f"{name} 缺失或为空。"}
    if not isinstance(values, list):
        return {"name": name, "status": "fail", "message": f"{name} 不是数组。"}
    length = len(values)
    if length not in VALID_SERIES_LENGTHS:
        return {"name": name, "status": "warning", "message": f"{name} 长度为 {length}，不是常见的 24/48/96/8760。"}
    numeric = [v for v in values if isinstance(v, (int, float))]
    if len(numeric) != len(values):
        return {"name": name, "status": "fail", "message": f"{name} 存在非数值项。"}
    if max(numeric) == min(numeric):
        return {"name": name, "status": "warning", "message": f"{name} 全部相同，时序质量偏低。"}
    return {"name": name, "status": "ok", "message": f"{name} 长度 {length}。"}
