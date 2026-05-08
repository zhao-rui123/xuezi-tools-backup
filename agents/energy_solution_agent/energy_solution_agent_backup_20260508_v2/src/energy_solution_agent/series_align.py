from __future__ import annotations


def align_annual_series_to_length(series: list[float], target_len: int) -> list[float]:
    if target_len <= 0:
        return []
    values = [float(v) for v in (series or [])]
    if not values:
        return [0.0] * target_len
    if len(values) == target_len:
        return values
    if target_len % len(values) == 0:
        ratio = target_len // len(values)
        expanded: list[float] = []
        for value in values:
            expanded.extend([value] * ratio)
        return expanded
    if len(values) % target_len == 0:
        ratio = len(values) // target_len
        return [sum(values[i * ratio : (i + 1) * ratio]) / ratio for i in range(target_len)]
    if len(values) > target_len:
        # Use tail-end truncation to preserve the most recent data points,
        # which are most representative of current conditions.
        return values[-target_len:]
    # Last-value repeat: when series is shorter than target, pad by repeating
    # the final observation. This is intentional and appropriate for the domain
    # where conditions persist until a new measurement arrives.
    return values + [values[-1]] * (target_len - len(values))
