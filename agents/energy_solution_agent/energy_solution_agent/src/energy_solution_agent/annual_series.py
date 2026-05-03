from __future__ import annotations

from typing import Any

from .timeseries import expand_daily_profile_to_year


def build_annual_series(
    raw_series: list[float],
    fallback_daily: list[float],
    annual_target_mwh: float | None = None,
    monthly_factors: list[float] | None = None,
) -> list[float]:
    numeric = [float(v) for v in raw_series if v is not None]
    if len(numeric) == 8760:
        return numeric
    if len(numeric) == 24:
        return expand_daily_profile_to_year(numeric, monthly_factors=monthly_factors, annual_target_mwh=annual_target_mwh)
    if len(numeric) == 48:
        hourly = [(numeric[i] + numeric[i + 1]) / 2 for i in range(0, 48, 2)]
        return expand_daily_profile_to_year(hourly, monthly_factors=monthly_factors, annual_target_mwh=annual_target_mwh)
    if len(numeric) == 96:
        hourly = [sum(numeric[i : i + 4]) / 4 for i in range(0, 96, 4)]
        return expand_daily_profile_to_year(hourly, monthly_factors=monthly_factors, annual_target_mwh=annual_target_mwh)
    return expand_daily_profile_to_year(fallback_daily, monthly_factors=monthly_factors, annual_target_mwh=annual_target_mwh)
