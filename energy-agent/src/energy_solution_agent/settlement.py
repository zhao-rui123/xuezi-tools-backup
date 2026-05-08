from __future__ import annotations

from typing import Any

from .constants import MONTH_HOURS


DEFAULT_PERIODS = {
    "peak": {10, 11, 14, 15, 16, 17, 18, 19, 20},
    "flat": {8, 9, 12, 13, 21, 22},
    "valley": {0, 1, 2, 3, 4, 5, 6, 7, 23},
}


def build_hourly_price_series(market: dict[str, Any], length: int) -> list[float]:
    direct = [float(v) for v in (market.get("market_price_series") or []) if v is not None]
    if len(direct) == length:
        return direct
    if len(direct) == 24 and length % 24 == 0:
        return direct * (length // 24)

    tou_tariff = market.get("tou_tariff") or []
    if not tou_tariff:
        return [0.72] * length
    prices = {str(item.get("period")): float(item.get("price", 0.0)) for item in tou_tariff}
    seasonal_schedules = market.get("tou_schedule_seasonal") or {}
    season_month_map = market.get("season_month_map") or {
        "winter": [12, 1, 2],
        "spring": [3, 4, 5],
        "summer": [6, 7, 8],
        "autumn": [9, 10, 11],
    }
    weekday_schedule = _build_tou_schedule(market, schedule_key="tou_schedule", default_periods=DEFAULT_PERIODS)
    weekend_schedule = _build_tou_schedule(
        market,
        schedule_key="tou_schedule_weekend",
        default_periods=market.get("tou_schedule_weekend_default") or {"flat": set(range(24))},
    )
    month_multipliers = _month_price_multipliers(market)
    province_modifier = _province_market_modifier(market)
    result: list[float] = []
    if length % 24 != 0:
        hourly_day = [prices.get(weekday_schedule[hour], prices.get("flat", 0.72)) for hour in range(24)]
        return [hourly_day[i % 24] for i in range(length)]
    total_days = length // 24
    month_day_bounds = _month_day_bounds()
    for day in range(total_days):
        month_idx = _day_to_month(day, month_day_bounds)
        weekend = day % 7 in {5, 6}
        active_schedule = weekend_schedule if weekend else weekday_schedule
        season_schedule = _seasonal_schedule_for_month(month_idx + 1, seasonal_schedules, season_month_map)
        if season_schedule:
            active_schedule = _build_schedule_from_map(season_schedule, fallback=active_schedule)
        multiplier = month_multipliers[month_idx]
        for hour in range(24):
            result.append(prices.get(active_schedule[hour], prices.get("flat", 0.72)) * multiplier * province_modifier)
    return result


def _build_tou_schedule(market: dict[str, Any], schedule_key: str, default_periods: dict[str, set[int]] | dict[str, list[int]]) -> dict[int, str]:
    custom = market.get(schedule_key) or {}
    if custom:
        schedule: dict[int, str] = {}
        for period, hours in custom.items():
            for hour in hours:
                schedule[int(hour)] = str(period)
        for hour in range(24):
            schedule.setdefault(hour, "flat")
        return schedule
    schedule = {}
    for period, hours in default_periods.items():
        for hour in hours:
            schedule[hour] = period
    return schedule


def _month_price_multipliers(market: dict[str, Any]) -> list[float]:
    raw = market.get("monthly_price_multipliers") or []
    if not raw:
        return [1.0] * 12
    values = [float(v) for v in raw[:12]]
    if len(values) < 12:
        values += [values[-1]] * (12 - len(values))
    return values


def _month_day_bounds() -> list[int]:
    bounds = []
    total = 0
    for hours in MONTH_HOURS:
        total += hours // 24
        bounds.append(total)
    return bounds


def _day_to_month(day: int, bounds: list[int]) -> int:
    for idx, bound in enumerate(bounds):
        if day < bound:
            return idx
    return len(bounds) - 1


def _seasonal_schedule_for_month(month: int, seasonal_schedules: dict[str, Any], season_month_map: dict[str, list[int]]) -> dict[str, list[int]] | None:
    if not seasonal_schedules:
        return None
    for season, months in season_month_map.items():
        if month in months and seasonal_schedules.get(season):
            return seasonal_schedules[season]
    return None


def _build_schedule_from_map(custom: dict[str, Any], fallback: dict[int, str]) -> dict[int, str]:
    schedule = dict(fallback)
    for period, hours in custom.items():
        for hour in hours:
            schedule[int(hour)] = str(period)
    return schedule


def annual_demand_charge(dispatch_series_kw: list[float], market: dict[str, Any]) -> float:
    if not market.get("demand_charge_rule") and not market.get("capacity_charge_rule"):
        return 0.0
    mode = str(market.get("demand_charge_mode") or "max_demand")
    rate = float(market.get("demand_charge_rate_per_kw_month") or 28.0)
    if not dispatch_series_kw:
        return 0.0
    month_hours = [31 * 24, 28 * 24, 31 * 24, 30 * 24, 31 * 24, 30 * 24, 31 * 24, 31 * 24, 30 * 24, 31 * 24, 30 * 24, 31 * 24]
    offset = 0
    total = 0.0
    contract_kw = float(market.get("contract_capacity_kw") or 0.0)
    transformer_kw = float(market.get("transformer_capacity_kva") or 0.0)
    for hours in month_hours:
        month_slice = dispatch_series_kw[offset : offset + hours]
        offset += hours
        if month_slice:
            month_peak = max(month_slice)
            if mode == "contract_capacity" and contract_kw > 0:
                total += contract_kw * rate
            elif mode == "transformer_capacity" and transformer_kw > 0:
                total += transformer_kw * rate
            else:
                total += month_peak * rate
    return total


def annual_energy_charge(dispatch_series_kw: list[float], prices: list[float]) -> float:
    if not dispatch_series_kw:
        return 0.0
    return sum(max(0.0, kw) * price for kw, price in zip(dispatch_series_kw, prices))


def ancillary_and_dr_revenue(
    storage_power_mw: float,
    peak_reduction_kw: float,
    market: dict[str, Any],
) -> dict[str, float]:
    ancillary_mode = str(market.get("ancillary_service_mode") or "capacity")
    ancillary_rate = float(market.get("ancillary_service_rate_per_mw_year") or 0.0)
    ancillary_hours = float(market.get("ancillary_service_called_hours") or 0.0)
    demand_response_rate = float(market.get("demand_response_rate_per_kw_year") or 0.0)
    demand_response_events = float(market.get("demand_response_events_per_year") or 1.0)

    if ancillary_mode == "energy_called":
        ancillary_revenue = storage_power_mw * ancillary_hours * ancillary_rate
    else:
        ancillary_revenue = storage_power_mw * ancillary_rate
    demand_response_revenue = peak_reduction_kw * demand_response_rate * demand_response_events
    return {
        "annual_ancillary_service_revenue": round(ancillary_revenue, 2),
        "annual_demand_response_revenue": round(demand_response_revenue, 2),
    }


def _province_market_modifier(market: dict[str, Any]) -> float:
    province_profile = str(market.get("province_policy_profile") or "").lower()
    mode = str(market.get("market_mode") or "").lower()
    if "spot" in mode or "market_price" in mode:
        if "山东" in province_profile or "shandong" in province_profile:
            return 1.03
        if "广东" in province_profile or "guangdong" in province_profile:
            return 1.02
        if "福建" in province_profile or "fujian" in province_profile:
            return 1.015
    return 1.0
