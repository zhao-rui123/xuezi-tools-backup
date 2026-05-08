from __future__ import annotations

from typing import Any

def _sum_series(values: list[float]) -> float:
    return sum(v for v in values if isinstance(v, (int, float)))


def _clean_workbook_text(value: Any) -> str:
    return str(value).replace("\xa0", "").strip() if value not in (None, "") else ""


def _owner_share_ratio(plan: dict[str, Any]) -> float:
    if plan.get("owner_share_ratio") is not None:
        return float(plan.get("owner_share_ratio") or 0.0)
    if plan.get("customer_share_ratio") is not None:
        return max(0.0, 1.0 - float(plan.get("customer_share_ratio") or 0.0))
    return float(plan.get("revenue_share_ratio") or 1.0)


def _default_arbitrage_usable_depth(storage_cfg: dict[str, Any]) -> float:
    if storage_cfg.get("arbitrage_usable_depth") is not None:
        return float(storage_cfg.get("arbitrage_usable_depth") or 0.0)
    if storage_cfg.get("first_discharge_depth") is not None:
        return float(storage_cfg.get("first_discharge_depth") or 0.0)
    soc_max = float(storage_cfg.get("soc_max") or 0.9)
    soc_floor = max(float(storage_cfg.get("soc_reserve_ratio") or 0.1), float(storage_cfg.get("backup_soc_ratio") or 0.0))
    return max(0.0, soc_max - soc_floor)


def _infer_steps_per_hour_for_sizing(values: list[float]) -> int | None:
    for steps_per_hour in (4, 2, 1):
        if len(values) == 8760 * steps_per_hour:
            return steps_per_hour
    return None


def _calendar_month_slices(steps_per_hour: int) -> dict[int, tuple[int, int]]:
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    slices: dict[int, tuple[int, int]] = {}
    cursor = 0
    for month, days in enumerate(month_days, start=1):
        count = days * 24 * steps_per_hour
        slices[month] = (cursor, cursor + count)
        cursor += count
    return slices


def _resolve_monthly_billing_baseline_kw(data: dict[str, Any], month_series: list[float], month: int) -> float:
    market = data.get("market_data", {}) or {}
    load = data.get("load_data", {}) or {}
    monthly_baseline = market.get("monthly_billing_baseline_kw") or load.get("monthly_billing_baseline_kw")
    if isinstance(monthly_baseline, list) and len(monthly_baseline) >= month:
        value = monthly_baseline[month - 1]
        if value not in (None, "", 0):
            return float(value)
    contract_capacity_kw = market.get("contract_capacity_kw")
    if contract_capacity_kw not in (None, "", 0) and str(market.get("demand_charge_mode") or "").lower() == "contract_capacity":
        return float(contract_capacity_kw)
    return max(float(v) for v in month_series) if month_series else 0.0


def _integrate_charge_space_kwh(day_series: list[float], baseline_kw: float, hours: list[int], steps_per_hour: int) -> float:
    total = 0.0
    step_hours = 1.0 / steps_per_hour
    for hour in hours:
        start = hour * steps_per_hour
        end = start + steps_per_hour
        for value in day_series[start:end]:
            total += max(0.0, baseline_kw - float(value)) * step_hours
    return total


def _integrate_discharge_space_kwh(day_series: list[float], hours: list[int], steps_per_hour: int) -> float:
    total = 0.0
    step_hours = 1.0 / steps_per_hour
    for hour in hours:
        start = hour * steps_per_hour
        end = start + steps_per_hour
        for value in day_series[start:end]:
            total += max(0.0, float(value)) * step_hours
    return total


def _max_charge_space_kw(day_series: list[float], baseline_kw: float, hours: list[int], steps_per_hour: int) -> float:
    values = []
    for hour in hours:
        start = hour * steps_per_hour
        end = start + steps_per_hour
        values.extend(max(0.0, baseline_kw - float(value)) for value in day_series[start:end])
    return max(values) if values else 0.0


def _max_discharge_space_kw(day_series: list[float], hours: list[int], steps_per_hour: int) -> float:
    values = []
    for hour in hours:
        start = hour * steps_per_hour
        end = start + steps_per_hour
        values.extend(max(0.0, float(value)) for value in day_series[start:end])
    return max(values) if values else 0.0


def _percentile_inc(values: list[float], p: float) -> float:
    ordered = sorted(float(v) for v in values)
    if not ordered:
        return 0.0
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * p
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    weight = rank - low
    return ordered[low] + (ordered[high] - ordered[low]) * weight


