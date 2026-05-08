from __future__ import annotations

from typing import Any


def evaluate_data_completeness(data: dict[str, Any]) -> tuple[str, list[str]]:
    missing: list[str] = []

    project = data.get("project_info", {})
    load_data = data.get("load_data", {})
    market = data.get("market_data", {})

    if not project.get("scenario_type"):
        missing.append("project_info.scenario_type")
    if not project.get("province"):
        missing.append("project_info.province")
    if not load_data.get("load_series_kw") and not load_data.get("peak_load_kw"):
        missing.append("load_data.load_series_kw or load_data.peak_load_kw")
    if not market.get("market_mode") and not market.get("tou_tariff"):
        missing.append("market_data.market_mode or market_data.tou_tariff")
    if not data.get("network_and_design", {}).get("point_of_connection"):
        missing.append("network_and_design.point_of_connection")

    if len(missing) == 0:
        grade = "A"
    elif len(missing) <= 2:
        grade = "B"
    elif len(missing) <= 4:
        grade = "C"
    else:
        grade = "D"
    return grade, missing
