from __future__ import annotations

from .constants import MONTH_HOURS


def to_hourly_profile(values: list[float], annual_target_mwh: float | None = None, fallback_peak_kw: float | None = None) -> list[float]:
    if values:
        numeric = [float(v) for v in values]
        if len(numeric) == 24:
            profile = numeric
        elif len(numeric) > 24:
            chunk = max(1, len(numeric) // 24)
            profile = [sum(numeric[i : i + chunk]) / len(numeric[i : i + chunk]) for i in range(0, len(numeric), chunk)][:24]
        else:
            profile = numeric + [numeric[-1]] * (24 - len(numeric))
    else:
        peak = float(fallback_peak_kw or 1000.0)
        profile = [peak * 0.45] * 24
        for hour in range(8, 18):
            profile[hour] = peak * 0.82
        for hour in range(18, 22):
            profile[hour] = peak
    if annual_target_mwh and sum(profile) > 0:
        scale = annual_target_mwh * 1000 / 365 / sum(profile)
        profile = [p * scale for p in profile]
    return profile


def scale_hourly_profile(profile: list[float], annual_target_mwh: float | None = None, peak_kw: float | None = None) -> list[float]:
    if not profile:
        return [0.0] * 24
    values = [float(v) for v in profile[:24]]
    if len(values) < 24:
        values += [values[-1]] * (24 - len(values))
    if annual_target_mwh and sum(values) > 0:
        scale = annual_target_mwh * 1000 / 365 / sum(values)
        values = [v * scale for v in values]
    elif peak_kw is not None and max(values) > 0:
        scale = peak_kw / max(values)
        values = [v * scale for v in values]
    return values


def expand_daily_profile_to_year(
    daily_profile_kw: list[float],
    monthly_factors: list[float] | None = None,
    annual_target_mwh: float | None = None,
    weekend_daily_profile_kw: list[float] | None = None,
) -> list[float]:
    weekday = _normalize_24h(daily_profile_kw)
    weekend = _normalize_24h(weekend_daily_profile_kw) if weekend_daily_profile_kw else weekday
    factors = _normalize_monthly_factors(monthly_factors)
    year: list[float] = []
    total_days = sum(h // 24 for h in MONTH_HOURS)
    for day in range(total_days):
        month_idx = _day_to_month(day, _month_day_bounds())
        day_profile = weekend if day % 7 in {5, 6} else weekday
        month_factor = factors[month_idx]
        year.extend([v * month_factor for v in day_profile])
    if annual_target_mwh and sum(year) > 0:
        scale = annual_target_mwh * 1000 / sum(year)
        year = [v * scale for v in year]
    return year


def expand_weekly_profile_to_year(
    weekly_profile_kw: list[float],
    annual_target_mwh: float | None = None,
    monthly_factors: list[float] | None = None,
) -> list[float]:
    week = [float(v) for v in weekly_profile_kw[:168]]
    if len(week) < 168:
        week += [week[-1] if week else 0.0] * (168 - len(week))
    factors = _normalize_monthly_factors(monthly_factors)
    year: list[float] = []
    total_days = sum(h // 24 for h in MONTH_HOURS)
    for day in range(total_days):
        month_idx = _day_to_month(day, _month_day_bounds())
        start = (day % 7) * 24
        day_profile = week[start : start + 24]
        year.extend([v * factors[month_idx] for v in day_profile])
    if annual_target_mwh and sum(year) > 0:
        scale = annual_target_mwh * 1000 / sum(year)
        year = [v * scale for v in year]
    return year


def expand_seasonal_profiles_to_year(
    seasonal_profiles: dict[str, list[float]],
    default_daily: list[float],
    annual_target_mwh: float | None = None,
    monthly_factors: list[float] | None = None,
    weekend_daily: list[float] | None = None,
) -> list[float]:
    season_month_map = {
        "winter": {12, 1, 2},
        "spring": {3, 4, 5},
        "summer": {6, 7, 8},
        "autumn": {9, 10, 11},
    }
    season_daily = {k: _normalize_24h(v) for k, v in seasonal_profiles.items() if v}
    default_weekday = _normalize_24h(default_daily)
    default_weekend = _normalize_24h(weekend_daily) if weekend_daily else default_weekday
    factors = _normalize_monthly_factors(monthly_factors)
    year: list[float] = []
    total_days = sum(h // 24 for h in MONTH_HOURS)
    bounds = _month_day_bounds()
    for day in range(total_days):
        month = _day_to_month(day, bounds) + 1
        season = next((name for name, months in season_month_map.items() if month in months), None)
        day_profile = season_daily.get(season, default_weekday)
        if day % 7 in {5, 6}:
            weekend_profile = season_daily.get(f"{season}_weekend", default_weekend)
            day_profile = weekend_profile
        year.extend([v * factors[month - 1] for v in day_profile])
    if annual_target_mwh and sum(year) > 0:
        scale = annual_target_mwh * 1000 / sum(year)
        year = [v * scale for v in year]
    return year


def _normalize_24h(profile: list[float] | None) -> list[float]:
    if not profile:
        return [0.0] * 24
    values = [float(v) for v in profile[:24]]
    if len(values) < 24:
        values += [values[-1] if values else 0.0] * (24 - len(values))
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


def _normalize_monthly_factors(monthly_factors: list[float] | None) -> list[float]:
    if not monthly_factors:
        return [1.0] * 12
    numeric = [float(v) for v in monthly_factors[:12]]
    if len(numeric) < 12:
        numeric += [numeric[-1]] * (12 - len(numeric))
    avg = sum(numeric) / len(numeric) if numeric else 1.0
    return [v / avg if avg else 1.0 for v in numeric]
