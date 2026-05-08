from __future__ import annotations

from typing import Any

from ..settlement import DEFAULT_PERIODS
from .utils import _default_arbitrage_usable_depth

def infer_cycles_from_monthly_tou_history(
    data: dict[str, Any],
    storage: dict[str, Any],
) -> list[dict[str, Any]]:
    market = data.get("market_data", {}) or {}
    history = market.get("monthly_tou_policy_history") or []
    prices = {str(item.get("period")): float(item.get("price", 0.0)) for item in (market.get("tou_tariff") or [])}
    storage_cfg = data.get("equipment", {}).get("storage", {}) or {}
    energy_kwh = float((storage.get("storage_energy_mwh") or 0.0) * 1000)
    if not history or not prices or energy_kwh <= 0:
        return []

    charge_eff = float(storage_cfg.get("battery_charge_efficiency") or storage_cfg.get("charge_efficiency") or 0.96)
    discharge_eff = float(storage_cfg.get("battery_discharge_efficiency") or storage_cfg.get("discharge_efficiency") or 0.96)
    pcs_eff = float(storage_cfg.get("pcs_efficiency") or 0.98)
    transformer_eff = float(storage_cfg.get("transformer_efficiency") or 0.99)
    effective_rte = charge_eff * discharge_eff * pcs_eff * transformer_eff
    discharge_energy_kwh = energy_kwh * _default_arbitrage_usable_depth(storage_cfg) * discharge_eff * pcs_eff * transformer_eff
    charge_energy_kwh = discharge_energy_kwh / max(effective_rte, 1e-9)
    monthly_active_days = float((market.get("arbitrage_plan") or {}).get("monthly_active_days") or 27.5)
    second_cycle_min_spread = float((market.get("arbitrage_plan") or {}).get("second_cycle_min_spread") or 0.25)
    first_cycle_min_spread = float((market.get("arbitrage_plan") or {}).get("first_cycle_min_spread") or 0.15)

    cycles: list[dict[str, Any]] = []
    for item in history:
        month = int(item.get("month"))
        active_days = float(item.get("active_days") or monthly_active_days)
        schedule = item.get("schedule") or {}
        periods = list(str(period) for period in (item.get("periods") or []))
        if not schedule and periods:
            schedule = _build_default_schedule_from_periods(periods)
        inferred = infer_daily_cycles_from_schedule(
            schedule=schedule,
            prices=prices,
            first_cycle_min_spread=first_cycle_min_spread,
            second_cycle_min_spread=second_cycle_min_spread,
            discharge_energy_kwh=discharge_energy_kwh,
            effective_rte=effective_rte,
        )
        for cycle in inferred:
            cycle["month"] = month
            cycle["days_per_year"] = active_days
        cycles.extend(inferred)
    return cycles


def _spread_after_efficiency(prices: dict[str, float], charge_period: str, discharge_period: str, effective_rte: float) -> float:
    charge_price = float(prices.get(charge_period, 0.0))
    discharge_price = float(prices.get(discharge_period, 0.0))
    if effective_rte <= 0:
        return 0.0
    return discharge_price - charge_price / effective_rte


def infer_daily_cycles_from_schedule(
    schedule: dict[str, list[int]],
    prices: dict[str, float],
    first_cycle_min_spread: float,
    second_cycle_min_spread: float,
    discharge_energy_kwh: float,
    effective_rte: float,
) -> list[dict[str, Any]]:
    periods_by_hour = {}
    for period, hours in schedule.items():
        for hour in hours:
            periods_by_hour[int(hour)] = str(period)
    if not periods_by_hour:
        return []

    windows = _extract_price_windows(periods_by_hour, prices)
    if not windows:
        return []
    min_price = min(float(item["price"]) for item in windows)
    discharge_windows = [item for item in windows if float(item["price"]) > min_price]
    candidate_windows = discharge_windows or windows
    selected = sorted(
        sorted(candidate_windows, key=lambda item: item["price"], reverse=True)[:2],
        key=lambda item: item["start_hour"],
    )

    first_window = selected[0]
    first_hour = first_window["start_hour"]
    first_period = first_window["period"]
    first_charge_period = _lowest_period_before_hour(periods_by_hour, prices, first_window["start_hour"])
    cycles: list[dict[str, Any]] = []
    if first_charge_period and _spread_after_efficiency(prices, first_charge_period, first_period, effective_rte) >= first_cycle_min_spread:
        first_discharge_hours = list(range(first_window["start_hour"], first_window["end_hour"]))
        cycles.append(
            {
                "charge_period": first_charge_period,
                "discharge_period": first_period,
                "charge_hours": sorted(set(int(hour) for hour in schedule.get(first_charge_period, [])) - set(first_discharge_hours)),
                "discharge_hours": first_discharge_hours,
                "discharge_energy_kwh": discharge_energy_kwh,
                "charge_energy_kwh": discharge_energy_kwh / max(effective_rte, 1e-9),
            }
        )

    if len(selected) < 2:
        return cycles

    second_window = selected[1]
    second_hour = second_window["start_hour"]
    second_period = second_window["period"]
    second_charge_period = _lowest_period_between_hours(periods_by_hour, prices, first_window["end_hour"], second_window["start_hour"])
    first_discharge_price = float(prices.get(first_period, 0.0))
    second_charge_price = float(prices.get(second_charge_period, 0.0)) if second_charge_period else None
    if (
        cycles
        and
        second_charge_period
        and second_charge_price is not None
        and second_charge_price < first_discharge_price
        and _spread_after_efficiency(prices, second_charge_period, second_period, effective_rte) >= second_cycle_min_spread
    ):
        second_discharge_hours = list(range(second_window["start_hour"], second_window["end_hour"]))
        cycles.append(
            {
                "charge_period": second_charge_period,
                "discharge_period": second_period,
                "charge_hours": sorted(
                    set(int(hour) for hour in schedule.get(second_charge_period, []))
                    - set(cycles[0].get("discharge_hours") or [])
                    - set(second_discharge_hours)
                ),
                "discharge_hours": second_discharge_hours,
                "discharge_energy_kwh": discharge_energy_kwh,
                "charge_energy_kwh": discharge_energy_kwh / max(effective_rte, 1e-9),
            }
        )
    return cycles


def _extract_price_windows(periods_by_hour: dict[int, str], prices: dict[str, float]) -> list[dict[str, Any]]:
    windows: list[dict[str, Any]] = []
    hours = sorted(periods_by_hour)
    if not hours:
        return windows
    start = hours[0]
    prev = hours[0]
    period = periods_by_hour[start]
    for hour in hours[1:]:
        current_period = periods_by_hour[hour]
        if hour == prev + 1 and current_period == period:
            prev = hour
            continue
        windows.append(
            {
                "period": period,
                "start_hour": start,
                "end_hour": prev + 1,
                "price": float(prices.get(period, 0.0)),
            }
        )
        start = hour
        prev = hour
        period = current_period
    windows.append(
        {
            "period": period,
            "start_hour": start,
            "end_hour": prev + 1,
            "price": float(prices.get(period, 0.0)),
        }
    )
    return windows


def _lowest_period_before_hour(periods_by_hour: dict[int, str], prices: dict[str, float], cutoff_hour: int) -> str | None:
    candidates = [period for hour, period in periods_by_hour.items() if hour < cutoff_hour]
    if not candidates:
        return None
    return min(candidates, key=lambda period: float(prices.get(period, 0.0)))


def _lowest_period_between_hours(periods_by_hour: dict[int, str], prices: dict[str, float], start_hour: int, end_hour: int) -> str | None:
    candidates = [period for hour, period in periods_by_hour.items() if start_hour < hour < end_hour]
    if not candidates:
        return None
    return min(candidates, key=lambda period: float(prices.get(period, 0.0)))


def _build_default_schedule_from_periods(periods: list[str]) -> dict[str, list[int]]:
    base = {
        "valley": list(range(0, 8)) + [23],
        "flat": [8, 9, 12, 13, 21, 22],
        "peak": [10, 11, 14, 15, 16, 17, 18, 19, 20],
        "super_peak": [12, 13, 19, 20],
        "deep_valley": [11, 12, 13],
    }
    return {period: base.get(period, []) for period in periods}


def _materialize_rule_based_cycles(market: dict[str, Any], plan: dict[str, Any], storage: dict[str, Any]) -> list[dict[str, Any]]:
    cycles = [dict(item) for item in (plan.get("cycles") or [])]
    if not cycles:
        return []
    if not plan.get("auto_days_from_policy"):
        return cycles
    monthly_active_days = float(plan.get("monthly_active_days") or 27.5)
    default_cycle_map = plan.get("default_cycle_day_ratios") or {
        "super_peak": 0.25,
        "peak": 1.3333333333,
        "flat": 0.4166666667,
    }
    policy_history = plan.get("monthly_tou_policy_history") or market.get("monthly_tou_policy_history") or []
    if policy_history:
        generated_days = _infer_cycle_days_from_policy_history(
            policy_history,
            monthly_active_days=monthly_active_days,
            cycle_day_ratios=default_cycle_map,
        )
    else:
        generated_days = _infer_cycle_days_from_policy(
            market,
            monthly_active_days=monthly_active_days,
            cycle_day_ratios=default_cycle_map,
        )
    for cycle in cycles:
        discharge_period = str(cycle.get("discharge_period") or "")
        if discharge_period in generated_days:
            cycle["days_per_year"] = generated_days[discharge_period]
    return cycles


def _materialize_rule_based_month_templates(
    market: dict[str, Any],
    plan: dict[str, Any],
    storage: dict[str, Any],
) -> list[dict[str, Any]]:
    explicit_templates = plan.get("monthly_cycle_templates") or []
    if explicit_templates:
        templates = [{"month": idx + 1, "active_days": 0.0, "cycles": []} for idx in range(12)]
        for item in explicit_templates:
            month = int(item.get("month"))
            if 1 <= month <= 12:
                templates[month - 1] = {
                    "month": month,
                    "active_days": float(item.get("active_days") or 0.0),
                    "cycles": [dict(cycle) for cycle in (item.get("cycles") or [])],
                }
        return templates

    monthly_history = plan.get("monthly_tou_policy_history") or market.get("monthly_tou_policy_history") or []
    if not monthly_history:
        return []

    cycles = _materialize_rule_based_cycles(market, plan, storage)
    if not cycles:
        return []

    monthly_active_days = float(plan.get("monthly_active_days") or 27.5)
    cycle_days_by_period = {}
    for cycle in cycles:
        period = str(cycle.get("discharge_period") or "")
        cycle_days_by_period[period] = float(cycle.get("days_per_year") or cycle.get("days") or 0.0)

    templates = []
    for month in range(1, 13):
        active_periods = None
        for item in monthly_history:
            if int(item.get("month")) == month:
                active_periods = set(str(period) for period in (item.get("periods") or []))
                break
        month_cycles = []
        for cycle in cycles:
            discharge_period = str(cycle.get("discharge_period") or "")
            if active_periods and discharge_period not in active_periods:
                continue
            month_cycles.append(dict(cycle))
        active_days = monthly_active_days if month_cycles else 0.0
        templates.append({"month": month, "active_days": active_days, "cycles": month_cycles})
    return templates


def _infer_cycle_days_from_policy(
    market: dict[str, Any],
    monthly_active_days: float,
    cycle_day_ratios: dict[str, float],
) -> dict[str, float]:
    seasonal_schedules = market.get("tou_schedule_seasonal") or {}
    season_month_map = market.get("season_month_map") or {
        "winter": [12, 1, 2],
        "spring": [3, 4, 5],
        "summer": [6, 7, 8],
        "autumn": [9, 10, 11],
    }
    explicit = {}
    for period, ratio in cycle_day_ratios.items():
        if ratio <= 0:
            continue
        explicit[period] = 0.0
    for month in range(1, 13):
        active_days = monthly_active_days
        month_periods = set(DEFAULT_PERIODS.keys())
        for season, months in season_month_map.items():
            if month in months and seasonal_schedules.get(season):
                month_periods = set(str(key) for key in seasonal_schedules[season].keys())
                break
        for period, ratio in cycle_day_ratios.items():
            if period in month_periods:
                explicit[period] += active_days * ratio
    return {key: round(value, 3) for key, value in explicit.items()}


def _infer_cycle_days_from_policy_history(
    policy_history: list[dict[str, Any]],
    monthly_active_days: float,
    cycle_day_ratios: dict[str, float],
) -> dict[str, float]:
    explicit = {period: 0.0 for period, ratio in cycle_day_ratios.items() if ratio > 0}
    for item in policy_history:
        periods = set(str(period) for period in (item.get("periods") or []))
        active_days = float(item.get("active_days") or monthly_active_days)
        for period, ratio in cycle_day_ratios.items():
            if period in periods:
                explicit[period] += active_days * ratio
    return {key: round(value, 3) for key, value in explicit.items()}


