from __future__ import annotations

from datetime import date
from typing import Any

from .constants import MONTH_HOURS


DEFAULT_PERIODS = {
    "peak": {10, 11, 14, 15, 16, 17, 18, 19, 20},
    "flat": {8, 9, 12, 13, 21, 22},
    "valley": {0, 1, 2, 3, 4, 5, 6, 7, 23},
}


def resolve_price_series_start_weekday(context: dict[str, Any] | None) -> int:
    if not context:
        return 0
    market = context.get("market_data") if isinstance(context.get("market_data"), dict) else context
    project = context.get("project_info") if isinstance(context.get("project_info"), dict) else {}
    resource = context.get("resource_data") if isinstance(context.get("resource_data"), dict) else {}

    for candidate in (
        market.get("price_series_start_weekday"),
        market.get("start_weekday"),
        project.get("price_series_start_weekday"),
        project.get("start_weekday"),
    ):
        try:
            weekday = int(candidate)
        except (TypeError, ValueError):
            continue
        if 0 <= weekday <= 6:
            return weekday

    solar = resource.get("solar") if isinstance(resource.get("solar"), dict) else {}
    for candidate in (
        market.get("price_series_year"),
        market.get("calendar_year"),
        project.get("calendar_year"),
        project.get("analysis_year"),
        project.get("resource_year"),
        project.get("weather_year"),
        resource.get("public_resource_year"),
        solar.get("public_resource_year"),
    ):
        try:
            year = int(candidate)
        except (TypeError, ValueError):
            continue
        if 1900 <= year <= 2100:
            return date(year, 1, 1).weekday()
    return 0


def build_hourly_price_series(market: dict[str, Any], length: int, start_weekday: int = 0) -> list[float]:
    """Build hourly price series with weekday/weekend TOU schedules.

    Args:
        market: Market configuration dict.
        length: Number of hourly steps to generate.
        start_weekday: Day of week for the first entry (0=Monday, 6=Sunday).
                        Defaults to 0 (Monday-start assumption).
    """
    direct: list[float] = []
    for v in (market.get("market_price_series") or []):
        if v is not None:
            try:
                direct.append(float(v))
            except (TypeError, ValueError):
                continue
    if len(direct) == length:
        return direct
    if len(direct) == 24 and length % 24 == 0:
        return direct * (length // 24)

    tou_tariff = market.get("tou_tariff") or []
    if not tou_tariff:
        if str(market.get("market_mode") or "").lower() == "offgrid_internal":
            fuel_cost = float(market.get("fuel_cost_per_kwh") or market.get("diesel_cost_per_kwh") or 0.72)
            return [fuel_cost] * length
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
        weekend = (day + start_weekday) % 7 in {5, 6}
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


def annual_demand_charge(dispatch_series_kw: list[float], market: dict[str, Any], interval_hours: float = 1.0) -> float:
    if not market.get("demand_charge_rule") and not market.get("capacity_charge_rule"):
        return 0.0
    mode = str(market.get("demand_charge_mode") or "max_demand")
    raw_rate = market.get("demand_charge_rate_per_kw_month")
    rate = 28.0 if raw_rate is None else float(raw_rate)
    if not dispatch_series_kw:
        return 0.0
    month_hours = [31 * 24, 28 * 24, 31 * 24, 30 * 24, 31 * 24, 30 * 24, 31 * 24, 31 * 24, 30 * 24, 31 * 24, 30 * 24, 31 * 24]
    # NOTE: If dispatch_series_kw is shorter than 365 days (8760 steps at 1h), month slices
    # after the available data will be empty, silently yielding zero contribution for those months.
    # Consider validating the series covers at least the expected full year before calling this function.
    offset = 0
    total = 0.0
    contract_kw = float(market.get("contract_capacity_kw") or 0.0)
    transformer_kw = float(market.get("transformer_capacity_kva") or 0.0)
    for hours in month_hours:
        steps = max(1, int(round(hours / max(interval_hours, 1e-9))))
        month_slice = dispatch_series_kw[offset : offset + steps]
        offset += steps
        if month_slice:
            month_peak = max(month_slice)
            if mode == "contract_capacity" and contract_kw > 0:
                total += contract_kw * rate
            elif mode == "transformer_capacity" and transformer_kw > 0:
                total += transformer_kw * rate
            else:
                total += month_peak * rate
    return total


def annual_energy_charge(dispatch_series_kw: list[float], prices: list[float], interval_hours: float = 1.0) -> float:
    if not dispatch_series_kw:
        return 0.0
    return sum(max(0.0, kw) * price * interval_hours for kw, price in zip(dispatch_series_kw, prices))


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


def summarize_power_trading_settlement(
    market: dict[str, Any],
    monthly_breakdown: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    hourly_prices = build_hourly_price_series(market, 24)
    if not hourly_prices:
        return {
            "trading_price_spread_per_kwh": None,
            "trading_charge_benchmark_price_per_kwh": None,
            "trading_discharge_benchmark_price_per_kwh": None,
            "trading_volatility_index": None,
            "trading_best_month": "",
            "trading_worst_month": "",
            "trading_execution_summary": "",
            "trading_settlement_summary": "",
        }

    ordered = sorted(float(price) for price in hourly_prices)
    band_size = max(1, len(ordered) // 4)
    charge_band = ordered[:band_size]
    discharge_band = ordered[-band_size:]
    charge_price = sum(charge_band) / len(charge_band)
    discharge_price = sum(discharge_band) / len(discharge_band)
    avg_price = sum(ordered) / len(ordered)
    spread = max(0.0, discharge_price - charge_price)
    volatility = (spread / avg_price) if avg_price > 0 else None

    best_month = ""
    worst_month = ""
    if monthly_breakdown:
        ranked = sorted(
            (
                {
                    "month": str(item.get("month") or ""),
                    "gross_margin": float(item.get("gross_margin") or 0.0),
                }
                for item in monthly_breakdown
            ),
            key=lambda item: item["gross_margin"],
        )
        if ranked:
            worst_month = ranked[0]["month"]
            best_month = ranked[-1]["month"]

    execution_summary = (
        f"按价格序列驱动低价充电、高价放电；基准充电电价约 {charge_price:.3f} 元/kWh，"
        f"基准放电电价约 {discharge_price:.3f} 元/kWh，价差约 {spread:.3f} 元/kWh。"
    )
    settlement_summary = "收益以现货/交易价差套利为主，叠加需求响应与辅助服务时，应单列执行考核和偏差结算边界。"
    if best_month and worst_month:
        settlement_summary += f" 当前月度毛收益表现最优为 {best_month} 月，最弱为 {worst_month} 月。"

    return {
        "trading_price_spread_per_kwh": round(spread, 4),
        "trading_charge_benchmark_price_per_kwh": round(charge_price, 4),
        "trading_discharge_benchmark_price_per_kwh": round(discharge_price, 4),
        "trading_volatility_index": round(volatility, 4) if volatility is not None else None,
        "trading_best_month": best_month,
        "trading_worst_month": worst_month,
        "trading_execution_summary": execution_summary,
        "trading_settlement_summary": settlement_summary,
    }


def extract_valley_hours(market: dict[str, Any] | None) -> set[int]:
    """Extract valley (low-price) hours from TOU tariff or seasonal schedule.

    Falls back to a province-aware default when no TOU data is available.
    """
    if not market:
        return {0, 1, 2, 3, 4, 5, 23}
    tou = market.get("tou_tariff") or []
    valley_periods = {"valley", "deep_valley", "谷", "深谷"}
    valley_hours: set[int] = set()
    for item in tou:
        period = str(item.get("period") or "").lower()
        if period in valley_periods:
            hours = item.get("hours") or []
            if hours:
                valley_hours.update(int(h) for h in hours)
    if valley_hours:
        return valley_hours
    # Check seasonal schedules for a representative month (January = winter)
    seasonal = market.get("tou_schedule_seasonal") or {}
    season_map = market.get("season_month_map") or {
        "winter": [12, 1, 2], "spring": [3, 4, 5],
        "summer": [6, 7, 8], "autumn": [9, 10, 11],
    }
    for season, months in season_map.items():
        if 1 in months:
            schedule = seasonal.get(season) or {}
            for period, hours in schedule.items():
                if str(period).lower() in valley_periods:
                    valley_hours.update(int(h) for h in hours)
            if valley_hours:
                return valley_hours
    # Check default periods
    defaults = market.get("tou_schedule") or DEFAULT_PERIODS
    for period, hours in defaults.items():
        if str(period).lower() in valley_periods:
            valley_hours.update(int(h) for h in hours)
    if valley_hours:
        return valley_hours
    return {0, 1, 2, 3, 4, 5, 23}


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
