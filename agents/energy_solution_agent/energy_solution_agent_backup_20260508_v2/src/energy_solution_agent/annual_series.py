from __future__ import annotations

from typing import Any

from .timeseries import expand_daily_profile_to_year


MONTH_DAY_COUNTS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def build_annual_series(
    raw_series: list[float],
    fallback_daily: list[float],
    annual_target_mwh: float | None = None,
    monthly_factors: list[float] | None = None,
) -> list[float]:
    numeric = [float(v) for v in raw_series if v is not None]
    if len(numeric) == 8760:
        return numeric
    if len(numeric) and len(numeric) % 8760 == 0:
        ratio = len(numeric) // 8760
        return [sum(numeric[i * ratio : (i + 1) * ratio]) / ratio for i in range(8760)]
    normalized = _normalize_subhourly_year_series(numeric)
    if normalized is not None:
        return normalized
    if len(numeric) == 24:
        return expand_daily_profile_to_year(numeric, monthly_factors=monthly_factors, annual_target_mwh=annual_target_mwh)
    if len(numeric) == 48:
        hourly = [(numeric[i] + numeric[i + 1]) / 2 for i in range(0, 48, 2)]
        return expand_daily_profile_to_year(hourly, monthly_factors=monthly_factors, annual_target_mwh=annual_target_mwh)
    if len(numeric) == 96:
        hourly = [sum(numeric[i : i + 4]) / 4 for i in range(0, 96, 4)]
        return expand_daily_profile_to_year(hourly, monthly_factors=monthly_factors, annual_target_mwh=annual_target_mwh)
    return expand_daily_profile_to_year(fallback_daily, monthly_factors=monthly_factors, annual_target_mwh=annual_target_mwh)


def _normalize_subhourly_year_series(values: list[float]) -> list[float] | None:
    if not values or len(values) <= 8760:
        return None
    best_ratio = None
    best_gap = None
    for ratio in (2, 4, 12):
        target = 8760 * ratio
        gap = abs(len(values) - target)
        if best_gap is None or gap < best_gap:
            best_gap = gap
            best_ratio = ratio
    if best_ratio is None:
        return None
    target_len = 8760 * best_ratio
    if best_gap is None or best_gap > target_len * 0.05:
        return None
    padded = values[:target_len]
    if len(padded) < target_len:
        padded += [padded[-1]] * (target_len - len(padded))
    return [sum(padded[i * best_ratio : (i + 1) * best_ratio]) / best_ratio for i in range(8760)]


def preserve_subhourly_year_series(values: list[float]) -> list[float] | None:
    numeric = [float(v) for v in values if v is not None]
    if not numeric or len(numeric) <= 8760:
        return None
    best_ratio = None
    best_gap = None
    for ratio in (2, 4, 12):
        target = 8760 * ratio
        gap = abs(len(numeric) - target)
        if best_gap is None or gap < best_gap:
            best_gap = gap
            best_ratio = ratio
    if best_ratio is None:
        return None
    target_len = 8760 * best_ratio
    if best_gap is None or best_gap > target_len * 0.05:
        return None
    padded = numeric[:target_len]
    if len(padded) < target_len:
        padded += [padded[-1]] * (target_len - len(padded))
    return padded


def extrapolate_sample_period_series(
    raw_series: list[float],
    sample_months: list[int] | None,
    sample_month_map: list[dict[str, Any]] | None = None,
    annual_target_mwh: float | None = None,
) -> list[float] | None:
    numeric = [float(v) for v in raw_series if v is not None]
    if not numeric:
        return None
    if len(numeric) in {24, 48, 96}:
        return None
    steps_per_hour = _infer_steps_per_hour(numeric)
    if steps_per_hour is None:
        return None
    if len(numeric) == 8760 * steps_per_hour:
        return None
    if sample_month_map:
        return _extrapolate_from_explicit_month_map(numeric, sample_month_map, steps_per_hour, annual_target_mwh)
    sample_months = [int(v) for v in (sample_months or []) if 1 <= int(v) <= 12]
    if not sample_months:
        return None
    sample_days = sum(MONTH_DAY_COUNTS[month - 1] for month in sample_months)
    expected_len = sample_days * 24 * steps_per_hour
    if expected_len >= 8760 * steps_per_hour:
        return None
    if abs(len(numeric) - expected_len) > steps_per_hour * 24 * 3:
        return None
    padded = numeric[:expected_len]
    if len(padded) < expected_len:
        padded += [padded[-1]] * (expected_len - len(padded))

    month_chunks: dict[int, list[float]] = {}
    offset = 0
    for month in sample_months:
        days = MONTH_DAY_COUNTS[month - 1]
        count = days * 24 * steps_per_hour
        month_chunks[month] = padded[offset : offset + count]
        offset += count

    month_profiles = {
        month: _extract_daily_pattern(chunk, steps_per_hour)
        for month, chunk in month_chunks.items()
    }
    if not month_profiles:
        return None

    annual_series: list[float] = []
    for month in range(1, 13):
        if month in month_profiles:
            profile = month_profiles[month]
        else:
            # Fall back to nearest available sample month (by absolute difference,
            # wrapping across year boundary e.g. month 1 <-> month 12).
            nearest = min(
                sample_months,
                key=lambda sm: min(abs(month - sm), 12 - abs(month - sm)),
            )
            profile = month_profiles[nearest]
        days = MONTH_DAY_COUNTS[month - 1]
        for _ in range(days):
            annual_series.extend(profile)

    if annual_target_mwh and annual_series:
        current_mwh = sum(annual_series) / steps_per_hour / 1000
        if current_mwh > 0:
            scale = annual_target_mwh / current_mwh
            annual_series = [value * scale for value in annual_series]
    return annual_series


def _extrapolate_from_explicit_month_map(
    numeric: list[float],
    sample_month_map: list[dict[str, Any]],
    steps_per_hour: int,
    annual_target_mwh: float | None,
) -> list[float] | None:
    month_entries = []
    for item in sample_month_map:
        month_raw = item.get("month")
        if month_raw is None:
            continue
        month = int(month_raw)
        if not 1 <= month <= 12:
            continue
        days = int(item.get("days") or MONTH_DAY_COUNTS[month - 1])
        month_entries.append((month, days))
    if not month_entries:
        return None
    expected_len = sum(days for _, days in month_entries) * 24 * steps_per_hour
    if abs(len(numeric) - expected_len) > steps_per_hour * 24 * 3:
        return None
    padded = numeric[:expected_len]
    if len(padded) < expected_len:
        padded += [padded[-1]] * (expected_len - len(padded))

    month_profiles: dict[int, list[float]] = {}
    offset = 0
    for month, days in month_entries:
        count = days * 24 * steps_per_hour
        chunk = padded[offset : offset + count]
        month_profiles[month] = _extract_daily_pattern(chunk, steps_per_hour)
        offset += count
    if not month_profiles:
        return None

    annual_series: list[float] = []
    reference_profile = next(iter(month_profiles.values()))
    for month in range(1, 13):
        profile = month_profiles.get(month, reference_profile)
        days = MONTH_DAY_COUNTS[month - 1]
        for _ in range(days):
            annual_series.extend(profile)

    if annual_target_mwh and annual_series:
        current_mwh = sum(annual_series) / steps_per_hour / 1000
        if current_mwh > 0:
            scale = annual_target_mwh / current_mwh
            annual_series = [value * scale for value in annual_series]
    return annual_series


def _infer_steps_per_hour(values: list[float]) -> int | None:
    for steps_per_hour in (4, 2, 1):
        step_count = 24 * steps_per_hour
        if len(values) % step_count == 0:
            return steps_per_hour
    return None


def _extract_daily_pattern(values: list[float], steps_per_hour: int) -> list[float]:
    """Compress a multi-day chunk into a single 24-hour daily pattern by averaging sub-hourly steps."""
    if steps_per_hour == 1:
        return values[:24]
    hours = []
    for hour in range(24):
        start = hour * steps_per_hour
        end = start + steps_per_hour
        slice_values = values[start:end]
        hours.extend(slice_values)
    return hours
