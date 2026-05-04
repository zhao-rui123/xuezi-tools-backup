from __future__ import annotations

from typing import Any

from .constants import DEFAULT_PV_FULL_LOAD_HOURS, DEFAULT_WIND_CAPACITY_FACTOR
from .device_models import PV_MODULE_MODELS, WIND_TURBINE_MODELS
from .timeseries import expand_daily_profile_to_year, scale_hourly_profile


def estimate_pv_generation(data: dict[str, Any]) -> dict[str, Any]:
    solar = data.get("resource_data", {}).get("solar", {})
    annual_load = float(data.get("load_data", {}).get("annual_consumption_mwh") or 0.0)
    available_area = float(solar.get("available_area_m2") or 0.0)
    module_model = PV_MODULE_MODELS.get(str(solar.get("module_model") or "").lower(), {})
    pr = _effective_pr({**module_model, **solar})
    tilt_factor = _tilt_factor(float(solar.get("tilt_deg") or 25.0), float(solar.get("site_latitude_deg") or 30.0))
    azimuth_factor = _azimuth_factor(float(solar.get("azimuth_deg") or 180.0))
    temp_coeff = float(solar.get("temp_coefficient_pct_per_c") or module_model.get("temp_coefficient_pct_per_c") or -0.35)
    ref_temp = float(solar.get("reference_temp_c") or module_model.get("reference_temp_c") or 25.0)
    temperature_factor = _temperature_factor(
        [float(v) for v in (solar.get("temperature_profile_c") or [])],
        temp_coeff,
        ref_temp,
    )

    hourly_profile = [float(v) for v in (solar.get("hourly_generation_profile_kw") or [])]
    hourly_irr = [float(v) for v in (solar.get("hourly_irradiance_kwh_per_m2") or [])]
    monthly_irr = [float(v) for v in (solar.get("monthly_irradiation_kwh_per_m2") or [])]
    annual_irr = float(solar.get("annual_irradiation_kwh_per_m2") or 0.0)
    source = solar.get("resource_source") or solar.get("provider") or None

    # 优先用 equipment.pv.candidate_mwp（最大那个），否则用 available_area 估算
    candidate_mwp_list = data.get("equipment", {}).get("pv", {}).get("candidate_mwp") or []
    if candidate_mwp_list:
        pv_mwp = float(candidate_mwp_list[-1])  # 取最后一个（最大候选）
    elif available_area:
        area_per_mwp = float(solar.get("area_per_mwp") or module_model.get("area_per_mwp") or 6500)
        pv_mwp = round(available_area / area_per_mwp, 2)
    else:
        pv_mwp = 2.0 if annual_load else 0.0
    annual_series = None
    if hourly_profile:
        accuracy = "high"
        if len(hourly_profile) >= 8760:
            exact_series = [float(v) for v in hourly_profile[:8760]]
            annual_generation = sum(exact_series) / 1000
            basis = "hourly_generation_profile_kw_8760"
            scaled_profile = scale_hourly_profile(exact_series[:24], annual_generation)
            annual_series = exact_series
            monthly_shape = [1.0] * 12
        else:
            daily_kwh = sum(hourly_profile)
            annual_generation = daily_kwh * 365 / 1000
            basis = "hourly_generation_profile_kw"
            scaled_profile = scale_hourly_profile(hourly_profile, annual_generation)
            monthly_shape = [1.0] * 12
    elif hourly_irr:
        derating = float(solar.get("derating_factor") or module_model.get("derating_factor") or 0.9)
        temp_series = [float(v) for v in (solar.get("temperature_series_c") or [])]
        noct = float(solar.get("noct_c") or module_model.get("noct_c") or 45.0)
        if len(hourly_irr) >= 8760:
            exact_series = []
            for i, irr in enumerate(hourly_irr[:8760]):
                amb = temp_series[i] if i < len(temp_series) else ref_temp
                module_temp = amb + (noct - 20.0) / 0.8 * max(float(irr), 0.0)
                temp_loss = max(0.7, 1.0 + (module_temp - ref_temp) * (temp_coeff / 100.0))
                exact_series.append(pv_mwp * float(irr) * pr * derating * tilt_factor * azimuth_factor * temp_loss)
            annual_generation = sum(exact_series) / 1000
            basis = "hourly_irradiance_kwh_per_m2_8760"
            scaled_profile = scale_hourly_profile(exact_series[:24], annual_generation)
            annual_series = exact_series
            monthly_shape = [1.0] * 12
            accuracy = "high"
        else:
            annual_generation = pv_mwp * sum(hourly_irr) * pr * derating * tilt_factor * azimuth_factor * temp_factor_hourly * 365 / 1000
            basis = "hourly_irradiance_kwh_per_m2"
            scaled_profile = scale_hourly_profile(hourly_irr, annual_generation)
            monthly_shape = [1.0] * 12
            accuracy = "medium"
    elif monthly_irr:
        derating = float(solar.get("derating_factor") or module_model.get("derating_factor") or 0.9)
        annual_generation = pv_mwp * sum(monthly_irr) * pr * derating * tilt_factor * azimuth_factor * temperature_factor
        accuracy = "medium"
        basis = "monthly_irradiation_kwh_per_m2"
        scaled_profile = scale_hourly_profile(_default_pv_shape(), annual_generation)
        monthly_shape = monthly_irr
    elif annual_irr:
        derating = float(solar.get("derating_factor") or module_model.get("derating_factor") or 0.9)
        annual_generation = pv_mwp * annual_irr * pr * derating * tilt_factor * azimuth_factor * temperature_factor
        accuracy = "medium"
        basis = "annual_irradiation_kwh_per_m2"
        scaled_profile = scale_hourly_profile(_default_pv_shape(), annual_generation)
        monthly_shape = [0.72, 0.80, 0.92, 1.02, 1.10, 1.14, 1.18, 1.12, 1.00, 0.90, 0.78, 0.70]
    else:
        annual_generation = pv_mwp * DEFAULT_PV_FULL_LOAD_HOURS * pr * tilt_factor * azimuth_factor * temperature_factor
        accuracy = "low"
        basis = "default_full_load_hours"
        scaled_profile = scale_hourly_profile(_default_pv_shape(), annual_generation)
        monthly_shape = [0.72, 0.80, 0.92, 1.02, 1.10, 1.14, 1.18, 1.12, 1.00, 0.90, 0.78, 0.70]
    p50_factor, p90_factor = _resource_scenario_factors(solar, default_p90=0.92)
    p50_generation = annual_generation * p50_factor
    p90_generation = annual_generation * p90_factor
    if annual_series is None:
        annual_series = expand_daily_profile_to_year(
            scale_hourly_profile(scaled_profile, p50_generation),
            monthly_factors=monthly_shape,
            annual_target_mwh=p50_generation,
        )
    elif p50_factor != 1.0 and sum(annual_series) > 0:
        scale = p50_generation * 1000 / sum(annual_series)
        annual_series = [v * scale for v in annual_series]

    return {
        "pv_mwp": pv_mwp if pv_mwp > 0 else None,
        "annual_pv_generation_mwh": round(p50_generation, 2) if pv_mwp > 0 else None,
        "pv_resource_accuracy": accuracy,
        "pv_resource_basis": basis,
        "pv_hourly_profile_kw": scale_hourly_profile(scaled_profile, p50_generation) if pv_mwp > 0 else [0.0] * 24,
        "pv_annual_series_kw": annual_series if pv_mwp > 0 else [0.0] * 8760,
        "pv_p50_generation_mwh": round(p50_generation, 2) if pv_mwp > 0 else None,
        "pv_p90_generation_mwh": round(p90_generation, 2) if pv_mwp > 0 else None,
        "pv_tilt_factor": round(tilt_factor, 4),
        "pv_azimuth_factor": round(azimuth_factor, 4),
        "pv_temperature_factor": round(temperature_factor, 4),
        "pv_pr_effective": round(pr, 4),
        "pv_resource_source": source,
    }


def estimate_wind_generation(data: dict[str, Any]) -> dict[str, Any]:
    wind = data.get("resource_data", {}).get("wind", {})
    annual_load = float(data.get("load_data", {}).get("annual_consumption_mwh") or 0.0)

    hourly_profile = [float(v) for v in (wind.get("hourly_generation_profile_kw") or [])]
    wind_speed_profile = [float(v) for v in (wind.get("wind_speed_series_mps") or [])]
    monthly_cf = [float(v) for v in (wind.get("monthly_capacity_factor") or [])]
    avg_speed = float(wind.get("annual_avg_speed_mps") or 0.0)
    cf_assumption = float(wind.get("capacity_factor_assumption") or DEFAULT_WIND_CAPACITY_FACTOR)
    power_curve = wind.get("power_curve") or []
    source = wind.get("resource_source") or wind.get("provider") or None

    annual_series = None
    if hourly_profile:
        peak_kw = max(hourly_profile) if hourly_profile else 0.0
        wind_mw = round(peak_kw / 1000, 2) if peak_kw else 0.0
        accuracy = "high"
        if len(hourly_profile) >= 8760:
            exact_series = [float(v) for v in hourly_profile[:8760]]
            annual_generation = sum(exact_series) / 1000
            basis = "hourly_generation_profile_kw_8760"
            scaled_profile = scale_hourly_profile(exact_series[:24], annual_generation)
            annual_series = exact_series
            monthly_shape = [1.0] * 12
        else:
            annual_generation = sum(hourly_profile) * 365 / 1000
            basis = "hourly_generation_profile_kw"
            scaled_profile = scale_hourly_profile(hourly_profile, annual_generation)
            monthly_shape = [1.0] * 12
        power_curve_used = False
        mean_speed = None
    elif wind_speed_profile and power_curve:
        power_output = _power_from_curve(wind_speed_profile, power_curve)
        peak_kw = max(power_output) if power_output else 0.0
        wind_mw = round(peak_kw / 1000, 2) if peak_kw else 0.0
        accuracy = "high"
        if len(power_output) >= 8760:
            exact_series = [float(v) for v in power_output[:8760]]
            annual_generation = sum(exact_series) / 1000
            basis = "wind_speed_series_mps_8760 + power_curve"
            scaled_profile = scale_hourly_profile(exact_series[:24], annual_generation)
            annual_series = exact_series
        else:
            annual_generation = sum(power_output) * 365 / 1000
            basis = "wind_speed_series_mps + power_curve"
            scaled_profile = scale_hourly_profile(power_output, annual_generation)
        power_curve_used = True
        mean_speed = round(sum(wind_speed_profile) / len(wind_speed_profile), 3) if wind_speed_profile else None
        monthly_shape = [1.08, 1.06, 1.02, 0.98, 0.95, 0.92, 0.90, 0.92, 0.96, 1.00, 1.06, 1.15]
    elif wind_speed_profile:
        # 若只有风速时序、无功率曲线，则使用默认风机模型 + 高度换算 + 立方功率近似
        turbine_model = WIND_TURBINE_MODELS.get(str(wind.get("turbine_model") or "").lower(), {})
        hub_h = float(wind.get("hub_height_m") or turbine_model.get("hub_height_m") or 100.0)
        ref_h = float(wind.get("reference_height_m") or turbine_model.get("reference_height_m") or 10.0)
        shear = float(wind.get("shear_exponent") or turbine_model.get("shear_exponent") or 0.14)
        cut_in = float(wind.get("cut_in_mps") or turbine_model.get("cut_in_mps") or 3.0)
        rated = float(wind.get("rated_mps") or turbine_model.get("rated_mps") or 12.0)
        cut_out = float(wind.get("cut_out_mps") or turbine_model.get("cut_out_mps") or 25.0)
        speed_profile = [float(v) * (hub_h / max(ref_h, 1.0)) ** shear for v in wind_speed_profile[:8760]]
        hourly_fraction = [_default_wind_power_fraction(v, cut_in, rated, cut_out) for v in speed_profile]
        derived_cf = sum(hourly_fraction) / len(hourly_fraction) if hourly_fraction else max(_wind_cf_from_speed(avg_speed), 0.12)
        user_wind = float(wind.get("wind_mw") or 0.0)
        wind_mw = round(user_wind if user_wind > 0 else (annual_load * 0.15 / (8760 * max(derived_cf, 0.12)) if annual_load else 0.0), 2)
        annual_generation = wind_mw * 8760 * derived_cf
        accuracy = "high" if len(speed_profile) >= 8760 else "medium"
        basis = "wind_speed_series_mps_8760 + synthetic_power_curve" if len(speed_profile) >= 8760 else "wind_speed_series_mps + synthetic_power_curve"
        scaled_profile = scale_hourly_profile([f * wind_mw * 1000 for f in hourly_fraction[:24]], annual_generation)
        annual_series = [f * wind_mw * 1000 for f in hourly_fraction[:8760]] if len(hourly_fraction) >= 8760 else None
        power_curve_used = False
        mean_speed = round(sum(speed_profile) / len(speed_profile), 3) if speed_profile else None
        monthly_shape = [1.08, 1.06, 1.02, 0.98, 0.95, 0.92, 0.90, 0.92, 0.96, 1.00, 1.06, 1.15]
    elif monthly_cf:
        avg_cf = sum(monthly_cf) / len(monthly_cf)
        wind_mw = round(max(0.0, annual_load * 0.15 / (8760 * max(avg_cf, 0.12))), 2) if annual_load else 0.0
        annual_generation = wind_mw * 8760 * avg_cf
        accuracy = "medium"
        basis = "monthly_capacity_factor"
        scaled_profile = scale_hourly_profile(_default_wind_shape(), annual_generation)
        power_curve_used = False
        mean_speed = None
        monthly_shape = monthly_cf
    elif avg_speed:
        derived_cf = _wind_cf_from_speed(avg_speed)
        wind_mw = round(max(0.0, annual_load * 0.15 / (8760 * max(derived_cf, 0.12))), 2) if annual_load else 0.0
        annual_generation = wind_mw * 8760 * derived_cf
        accuracy = "medium"
        basis = "annual_avg_speed_mps"
        scaled_profile = scale_hourly_profile(_default_wind_shape(), annual_generation)
        power_curve_used = False
        mean_speed = avg_speed
        monthly_shape = [1.08, 1.06, 1.02, 0.98, 0.95, 0.92, 0.90, 0.92, 0.96, 1.00, 1.06, 1.15]
    elif "capacity_factor_assumption" in wind and wind.get("capacity_factor_assumption") is not None:
        wind_mw = round(max(0.0, annual_load * 0.15 / (8760 * max(cf_assumption, 0.12))), 2) if annual_load else 0.0
        annual_generation = wind_mw * 8760 * cf_assumption
        accuracy = "low"
        basis = "capacity_factor_assumption/default"
        scaled_profile = scale_hourly_profile(_default_wind_shape(), annual_generation)
        power_curve_used = False
        mean_speed = None
        monthly_shape = [1.08, 1.06, 1.02, 0.98, 0.95, 0.92, 0.90, 0.92, 0.96, 1.00, 1.06, 1.15]
    else:
        wind_mw = 0.0
        annual_generation = 0.0
        accuracy = "low"
        basis = "no_wind_resource"
        scaled_profile = [0.0] * 24
        power_curve_used = False
        mean_speed = None
        monthly_shape = [1.0] * 12
    p50_factor, p90_factor = _resource_scenario_factors(wind, default_p90=0.88)
    # ── 用户指定风电容量覆盖 ──────────────────────────────────
    user_wind_mw = float(wind.get("wind_mw") or 0)
    if user_wind_mw > 0 and wind_mw > 0 and abs(wind_mw - user_wind_mw) > 0.5:
        scale = user_wind_mw / wind_mw
        wind_mw = round(user_wind_mw, 3)
        annual_generation *= scale
        scaled_profile = [v * scale for v in scaled_profile]
        p50_generation = annual_generation * p50_factor
        p90_generation = annual_generation * p90_factor
        accuracy = accuracy if accuracy != "low" else "medium"
        basis = basis + " (user-override)"
    else:
        p50_generation = annual_generation * p50_factor
        p90_generation = annual_generation * p90_factor
    if annual_series is None:
        annual_series = expand_daily_profile_to_year(
            scale_hourly_profile(scaled_profile, p50_generation),
            monthly_factors=monthly_shape,
            annual_target_mwh=p50_generation,
        )
    elif p50_factor != 1.0 and sum(annual_series) > 0:
        scale = p50_generation * 1000 / sum(annual_series)
        annual_series = [v * scale for v in annual_series]

    return {
        "wind_mw": wind_mw if wind_mw > 0 else None,
        "annual_wind_generation_mwh": round(p50_generation, 2) if wind_mw > 0 else None,
        "wind_resource_accuracy": accuracy,
        "wind_resource_basis": basis,
        "wind_hourly_profile_kw": scale_hourly_profile(scaled_profile, p50_generation) if wind_mw > 0 else [0.0] * 24,
        "wind_annual_series_kw": annual_series if wind_mw > 0 else [0.0] * 8760,
        "wind_p50_generation_mwh": round(p50_generation, 2) if wind_mw > 0 else None,
        "wind_p90_generation_mwh": round(p90_generation, 2) if wind_mw > 0 else None,
        "wind_power_curve_used": power_curve_used,
        "wind_mean_speed_mps": mean_speed,
        "wind_resource_source": source,
    }


def _wind_cf_from_speed(avg_speed: float) -> float:
    if avg_speed < 5.0:
        return 0.16
    if avg_speed < 6.0:
        return 0.22
    if avg_speed < 7.0:
        return 0.28
    if avg_speed < 8.0:
        return 0.34
    return 0.40


def _default_pv_shape() -> list[float]:
    return [0, 0, 0, 0, 0, 0.02, 0.10, 0.22, 0.45, 0.68, 0.84, 0.95, 1.0, 0.97, 0.86, 0.70, 0.48, 0.25, 0.08, 0.01, 0, 0, 0, 0]


def _default_wind_shape() -> list[float]:
    return [0.62, 0.60, 0.58, 0.56, 0.55, 0.54, 0.53, 0.50, 0.48, 0.46, 0.45, 0.47, 0.50, 0.53, 0.56, 0.60, 0.64, 0.67, 0.70, 0.72, 0.71, 0.69, 0.66, 0.64]


def _resource_scenario_factors(resource: dict[str, Any], default_p90: float) -> tuple[float, float]:
    p50_factor = float(resource.get("p50_factor") or 1.0)
    p90_factor = float(resource.get("p90_factor") or default_p90)
    return p50_factor, min(p50_factor, p90_factor)


def _effective_pr(solar: dict[str, Any]) -> float:
    if solar.get("pr_breakdown"):
        breakdown = solar["pr_breakdown"]
        components = [
            float(breakdown.get("soiling", 0.98)),
            float(breakdown.get("mismatch", 0.99)),
            float(breakdown.get("dc_wiring", 0.99)),
            float(breakdown.get("inverter", 0.97)),
            float(breakdown.get("availability", 0.99)),
        ]
        pr = 1.0
        for item in components:
            pr *= item
        return max(0.5, min(0.95, pr))
    return float(solar.get("performance_ratio") or 0.82)


def _tilt_factor(tilt_deg: float, latitude_deg: float) -> float:
    delta = abs(tilt_deg - latitude_deg)
    return max(0.86, 1.0 - delta * 0.003)


def _azimuth_factor(azimuth_deg: float) -> float:
    delta = abs(azimuth_deg - 180.0)
    return max(0.82, 1.0 - delta / 180 * 0.12)


def _temperature_factor(temperature_profile_c: list[float], temp_coeff_pct_per_c: float, reference_temp_c: float) -> float:
    if not temperature_profile_c:
        return 1.0
    avg_temp = sum(temperature_profile_c) / len(temperature_profile_c)
    delta = avg_temp - reference_temp_c
    return max(0.88, min(1.02, 1.0 + delta * (temp_coeff_pct_per_c / 100.0)))


def _default_wind_power_fraction(speed_mps: float, cut_in: float = 3.0, rated: float = 12.0, cut_out: float = 25.0) -> float:
    # 简化风机功率曲线
    if speed_mps < cut_in:
        return 0.0
    if speed_mps >= cut_out:
        return 0.0
    if speed_mps >= rated:
        return 1.0
    return ((speed_mps - cut_in) / max(rated - cut_in, 0.1)) ** 3


def _power_from_curve(wind_speeds: list[float], power_curve: list[dict[str, float]]) -> list[float]: 
    if not power_curve:
        return [0.0] * len(wind_speeds)
    curve = sorted(
        [(float(p["speed_mps"]), float(p["power_kw"])) for p in power_curve if "speed_mps" in p and "power_kw" in p],
        key=lambda item: item[0],
    )
    if not curve:
        return [0.0] * len(wind_speeds)
    result: list[float] = []
    for speed in wind_speeds:
        if speed <= curve[0][0]:
            result.append(curve[0][1])
            continue
        if speed >= curve[-1][0]:
            result.append(curve[-1][1])
            continue
        for idx in range(1, len(curve)):
            left_speed, left_power = curve[idx - 1]
            right_speed, right_power = curve[idx]
            if left_speed <= speed <= right_speed:
                span = right_speed - left_speed
                ratio = 0.0 if span == 0 else (speed - left_speed) / span
                result.append(left_power + ratio * (right_power - left_power))
                break
    return result
