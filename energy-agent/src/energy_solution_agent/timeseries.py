from __future__ import annotations

from typing import Any

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
) -> list[float]:
    profile = [float(v) for v in daily_profile_kw[:24]]
    if len(profile) < 24:
        profile += [profile[-1] if profile else 0.0] * (24 - len(profile))
    factors = _normalize_monthly_factors(monthly_factors)
    year: list[float] = []
    for month_idx, hours in enumerate(MONTH_HOURS):
        month_factor = factors[month_idx]
        for hour in range(hours):
            day_hour = hour % 24
            year.append(profile[day_hour] * month_factor)
    if annual_target_mwh and sum(year) > 0:
        scale = annual_target_mwh * 1000 / sum(year)
        year = [v * scale for v in year]
    return year


def _normalize_monthly_factors(monthly_factors: list[float] | None) -> list[float]:
    if not monthly_factors:
        return [1.0] * 12
    numeric = [float(v) for v in monthly_factors[:12]]
    if len(numeric) < 12:
        numeric += [numeric[-1]] * (12 - len(numeric))
    avg = sum(numeric) / len(numeric) if numeric else 1.0
    return [v / avg if avg else 1.0 for v in numeric]
