from __future__ import annotations

from typing import Any

from .constants import DEFAULT_PV_FULL_LOAD_HOURS, DEFAULT_PV_NOCT_C, DEFAULT_STANDARD_AIR_DENSITY_KG_PER_M3, DEFAULT_WIND_CAPACITY_FACTOR
from .timeseries import expand_daily_profile_to_year, scale_hourly_profile


def estimate_pv_generation(data: dict[str, Any]) -> dict[str, Any]:
    solar = data.get("resource_data", {}).get("solar", {})
    project = data.get("project_info", {})
    annual_load = float(data.get("load_data", {}).get("annual_consumption_mwh") or 0.0)
    available_area = float(solar.get("available_area_m2") or 0.0)
    explicit_pv_mwp = float(solar.get("installed_capacity_mwp") or solar.get("installed_capacity_mw") or 0.0)
    pr = _effective_pr(solar)
    latitude_deg = _solar_site_latitude_deg(solar, project)
    effective_tilt_deg = _effective_pv_tilt_deg(solar, latitude_deg)
    recommended_tilt_deg = _recommended_pv_tilt_deg(latitude_deg)
    tilt_factor = _tilt_factor(effective_tilt_deg, latitude_deg)
    azimuth_factor = _azimuth_factor(float(solar.get("azimuth_deg") or 180.0))
    tracking_factor = _tracking_factor(
        str(solar.get("tracking_mode") or "fixed_tilt"),
        latitude_deg,
    )
    temperature_factor = _temperature_factor(
        [float(v) for v in (solar.get("temperature_profile_c") or solar.get("daily_temperature_c") or solar.get("hourly_temperature_c") or [])],
        float(solar.get("temp_coefficient_pct_per_c") or -0.35),
        float(solar.get("reference_temp_c") or 25.0),
    )
    availability_factor = float(solar.get("availability_factor") or 1.0)
    calibration_factor = float(solar.get("calibration_factor") or 1.0)
    shading_factor = _pv_shading_factor(solar)
    bifacial_factor = _pv_bifacial_factor(solar)

    hourly_profile = [float(v) for v in (solar.get("hourly_generation_profile_kw") or [])]
    hourly_irr = [float(v) for v in (solar.get("hourly_irradiance_kwh_per_m2") or [])]
    daily_irr = [float(v) for v in (solar.get("daily_irradiance_kwh_per_m2") or [])]
    monthly_irr = [float(v) for v in (solar.get("monthly_irradiation_kwh_per_m2") or [])]
    annual_irr = float(solar.get("annual_irradiation_kwh_per_m2") or 0.0)
    specific_yield = float(solar.get("specific_yield_kwh_per_kwp_year") or solar.get("specific_yield_kwh_per_kw_year") or 0.0)

    has_resource_signal = any(
        solar.get(key)
        for key in (
            "available_area_m2",
            "installed_capacity_mwp",
            "installed_capacity_mw",
            "hourly_generation_profile_kw",
            "hourly_irradiance_kwh_per_m2",
            "daily_irradiance_kwh_per_m2",
            "monthly_irradiation_kwh_per_m2",
            "annual_irradiation_kwh_per_m2",
            "specific_yield_kwh_per_kwp_year",
            "specific_yield_kwh_per_kw_year",
        )
    )
    pv_mwp = round(explicit_pv_mwp, 2) if explicit_pv_mwp > 0 else (round(available_area / 6500, 2) if available_area else 0.0)
    if not has_resource_signal and pv_mwp <= 0:
        return {
            "pv_mwp": None,
            "annual_pv_generation_mwh": None,
            "pv_resource_accuracy": None,
            "pv_resource_basis": None,
            "pv_hourly_profile_kw": [0.0] * 24,
            "pv_annual_series_kw": [0.0] * 8760,
            "pv_p50_generation_mwh": None,
            "pv_p90_generation_mwh": None,
            "pv_effective_tilt_deg": round(effective_tilt_deg, 2),
            "pv_recommended_tilt_deg": round(recommended_tilt_deg, 2),
            "pv_tilt_factor": round(tilt_factor, 4),
            "pv_azimuth_factor": round(azimuth_factor, 4),
            "pv_tracking_factor": round(tracking_factor, 4),
            "pv_temperature_factor": round(temperature_factor, 4),
            "pv_pr_effective": round(pr, 4),
        }
    if hourly_profile:
        if len(hourly_profile) >= 8760:
            annual_series = [float(v) for v in hourly_profile[:8760]]
            annual_generation = sum(annual_series) / 1000
            scaled_profile = _profile_from_annual_series(annual_series)
            accuracy = "high"
            basis = "hourly_generation_profile_kw_8760"
        else:
            daily_kwh = sum(hourly_profile)
            annual_generation = daily_kwh * 365 / 1000
            scaled_profile = scale_hourly_profile(hourly_profile, annual_generation)
            annual_series = expand_daily_profile_to_year(scaled_profile, annual_target_mwh=annual_generation)
            accuracy = "high"
            basis = "hourly_generation_profile_kw"
    elif hourly_irr:
        if len(hourly_irr) >= 8760:
            annual_irr_equivalent = sum(hourly_irr[:8760])
            annual_generation = pv_mwp * annual_irr_equivalent * pr * tilt_factor * azimuth_factor * tracking_factor * temperature_factor * availability_factor * calibration_factor * shading_factor * bifacial_factor
            annual_series = _solar_annual_series_from_hourly_irradiance(
                hourly_irr[:8760],
                pv_mwp,
                pr,
                tilt_factor,
                azimuth_factor,
                tracking_factor,
                float(solar.get("temp_coefficient_pct_per_c") or -0.35),
                float(solar.get("reference_temp_c") or 25.0),
                [float(v) for v in (solar.get("hourly_temperature_c") or [])],
                availability_factor,
                calibration_factor,
                shading_factor,
                bifacial_factor,
                solar,
            )
            annual_series = _apply_pv_ac_limits(annual_series, solar, pv_mwp)
            annual_generation = sum(annual_series) / 1000
            scaled_profile = _profile_from_annual_series(annual_series)
            accuracy = "high"
            basis = "hourly_irradiance_kwh_per_m2_8760"
        else:
            annual_generation = pv_mwp * sum(hourly_irr) * 365 * pr * tilt_factor * azimuth_factor * tracking_factor * temperature_factor * availability_factor * calibration_factor * shading_factor * bifacial_factor
            scaled_profile = scale_hourly_profile(hourly_irr, annual_generation)
            annual_series = expand_daily_profile_to_year(scaled_profile, annual_target_mwh=annual_generation)
            annual_series = _apply_pv_ac_limits(annual_series, solar, pv_mwp)
            annual_generation = sum(annual_series) / 1000
            accuracy = "high"
            basis = "hourly_irradiance_kwh_per_m2"
    elif daily_irr:
        annual_generation = pv_mwp * sum(daily_irr) * pr * tilt_factor * azimuth_factor * tracking_factor * temperature_factor * availability_factor * calibration_factor * shading_factor * bifacial_factor
        annual_series = _solar_annual_series_from_daily_irradiance(
            daily_irr,
            pv_mwp,
            pr,
            tilt_factor,
            azimuth_factor,
            tracking_factor,
            float(solar.get("temp_coefficient_pct_per_c") or -0.35),
            float(solar.get("reference_temp_c") or 25.0),
            [float(v) for v in (solar.get("daily_temperature_c") or [])],
            availability_factor,
            calibration_factor,
            shading_factor,
            bifacial_factor,
            solar,
        )
        annual_series = _apply_pv_ac_limits(annual_series, solar, pv_mwp)
        annual_generation = sum(annual_series) / 1000
        scaled_profile = _profile_from_annual_series(annual_series)
        accuracy = "high"
        basis = "daily_irradiance_kwh_per_m2"
    elif specific_yield:
        annual_generation = pv_mwp * specific_yield * availability_factor * calibration_factor * shading_factor * bifacial_factor
        scaled_profile = scale_hourly_profile(_default_pv_shape(), annual_generation)
        annual_series = expand_daily_profile_to_year(
            scaled_profile,
            monthly_factors=monthly_irr if monthly_irr else [0.72, 0.80, 0.92, 1.02, 1.10, 1.14, 1.18, 1.12, 1.00, 0.90, 0.78, 0.70],
            annual_target_mwh=annual_generation,
        )
        annual_series = _apply_pv_ac_limits(annual_series, solar, pv_mwp)
        annual_generation = sum(annual_series) / 1000
        accuracy = "high"
        basis = "specific_yield_kwh_per_kwp_year"
    elif monthly_irr:
        annual_generation = pv_mwp * sum(monthly_irr) * pr * tilt_factor * azimuth_factor * tracking_factor * temperature_factor * availability_factor * calibration_factor * shading_factor * bifacial_factor
        accuracy = "medium"
        basis = "monthly_irradiation_kwh_per_m2"
        scaled_profile = scale_hourly_profile(_default_pv_shape(), annual_generation)
        annual_series = expand_daily_profile_to_year(scaled_profile, monthly_factors=monthly_irr, annual_target_mwh=annual_generation)
        annual_series = _apply_pv_ac_limits(annual_series, solar, pv_mwp)
        annual_generation = sum(annual_series) / 1000
    elif annual_irr:
        annual_generation = pv_mwp * annual_irr * pr * tilt_factor * azimuth_factor * tracking_factor * temperature_factor * availability_factor * calibration_factor * shading_factor * bifacial_factor
        accuracy = "medium"
        basis = "annual_irradiation_kwh_per_m2"
        scaled_profile = scale_hourly_profile(_default_pv_shape(), annual_generation)
        annual_series = expand_daily_profile_to_year(
            scaled_profile,
            monthly_factors=[0.72, 0.80, 0.92, 1.02, 1.10, 1.14, 1.18, 1.12, 1.00, 0.90, 0.78, 0.70],
            annual_target_mwh=annual_generation,
        )
        annual_series = _apply_pv_ac_limits(annual_series, solar, pv_mwp)
        annual_generation = sum(annual_series) / 1000
    else:
        annual_generation = pv_mwp * DEFAULT_PV_FULL_LOAD_HOURS * pr * tilt_factor * azimuth_factor * tracking_factor * temperature_factor * availability_factor * calibration_factor * shading_factor * bifacial_factor
        accuracy = "low"
        basis = "default_full_load_hours"
        scaled_profile = scale_hourly_profile(_default_pv_shape(), annual_generation)
        annual_series = expand_daily_profile_to_year(
            scaled_profile,
            monthly_factors=[0.72, 0.80, 0.92, 1.02, 1.10, 1.14, 1.18, 1.12, 1.00, 0.90, 0.78, 0.70],
            annual_target_mwh=annual_generation,
        )
        annual_series = _apply_pv_ac_limits(annual_series, solar, pv_mwp)
        annual_generation = sum(annual_series) / 1000
    p50_factor, p90_factor = _resource_scenario_factors(solar, default_p90=0.92)
    p50_generation = annual_generation * p50_factor
    p90_generation = annual_generation * p90_factor
    if annual_series:
        annual_series = _scale_series_to_annual_target(annual_series, p50_generation)
        annual_series = _apply_pv_ac_limits(annual_series, solar, pv_mwp)
    else:
        annual_series = expand_daily_profile_to_year(scale_hourly_profile(scaled_profile, p50_generation), annual_target_mwh=p50_generation)
    scaled_profile = _profile_from_annual_series(annual_series)

    return {
        "pv_mwp": pv_mwp if pv_mwp > 0 else None,
        "annual_pv_generation_mwh": round(p50_generation, 2) if pv_mwp > 0 else None,
        "pv_resource_accuracy": accuracy,
        "pv_resource_basis": basis,
        "pv_hourly_profile_kw": scale_hourly_profile(scaled_profile, p50_generation) if pv_mwp > 0 else [0.0] * 24,
        "pv_annual_series_kw": annual_series if pv_mwp > 0 else [0.0] * 8760,
        "pv_p50_generation_mwh": round(p50_generation, 2) if pv_mwp > 0 else None,
        "pv_p90_generation_mwh": round(p90_generation, 2) if pv_mwp > 0 else None,
        "pv_effective_tilt_deg": round(effective_tilt_deg, 2),
        "pv_recommended_tilt_deg": round(recommended_tilt_deg, 2),
        "pv_tilt_factor": round(tilt_factor, 4),
        "pv_azimuth_factor": round(azimuth_factor, 4),
        "pv_tracking_factor": round(tracking_factor, 4),
        "pv_temperature_factor": round(temperature_factor, 4),
        "pv_pr_effective": round(pr, 4),
    }


def estimate_wind_generation(data: dict[str, Any]) -> dict[str, Any]:
    wind = data.get("resource_data", {}).get("wind", {})
    annual_load = float(data.get("load_data", {}).get("annual_consumption_mwh") or 0.0)
    explicit_wind_mw = float(wind.get("installed_capacity_mw") or 0.0)

    hourly_profile = [float(v) for v in (wind.get("hourly_generation_profile_kw") or [])]
    wind_speed_profile = [float(v) for v in (wind.get("wind_speed_series_mps") or wind.get("hourly_wind_speed_series_mps") or [])]
    daily_wind_speed = [float(v) for v in (wind.get("daily_wind_speed_series_mps") or [])]
    monthly_cf = [float(v) for v in (wind.get("monthly_capacity_factor") or [])]
    avg_speed = float(wind.get("annual_avg_speed_mps") or 0.0)
    cf_assumption = float(wind.get("capacity_factor_assumption") or DEFAULT_WIND_CAPACITY_FACTOR)
    power_curve = wind.get("power_curve") or []
    expected_full_load_hours = float(wind.get("expected_full_load_hours") or 0.0)
    specific_yield_per_mw = expected_full_load_hours if expected_full_load_hours > 0 else 0.0
    availability_factor = float(wind.get("availability_factor") or 1.0)
    wake_loss_factor = float(wind.get("wake_loss_factor") or 1.0)
    curtailment_factor = float(wind.get("curtailment_factor") or 1.0)
    calibration_factor = float(wind.get("calibration_factor") or 1.0)
    air_density_factor = _wind_air_density_factor(wind)
    net_factor = availability_factor * wake_loss_factor * curtailment_factor * calibration_factor * air_density_factor

    has_resource_signal = any(
        wind.get(key)
        for key in (
            "installed_capacity_mw",
            "hourly_generation_profile_kw",
            "wind_speed_series_mps",
            "hourly_wind_speed_series_mps",
            "daily_wind_speed_series_mps",
            "monthly_capacity_factor",
            "annual_avg_speed_mps",
            "capacity_factor_assumption",
            "expected_full_load_hours",
        )
    )
    if not has_resource_signal and explicit_wind_mw <= 0:
        return {
            "wind_mw": None,
            "annual_wind_generation_mwh": None,
            "wind_resource_accuracy": None,
            "wind_resource_basis": None,
            "wind_hourly_profile_kw": [0.0] * 24,
            "wind_annual_series_kw": [0.0] * 8760,
            "wind_p50_generation_mwh": None,
            "wind_p90_generation_mwh": None,
            "wind_power_curve_used": False,
            "wind_mean_speed_mps": None,
            "wind_net_factor": 1.0,
        }

    if hourly_profile:
        if len(hourly_profile) >= 8760:
            annual_series = [float(v) for v in hourly_profile[:8760]]
            peak_kw = max(annual_series) if annual_series else 0.0
            wind_mw = round(peak_kw / 1000, 2) if peak_kw else 0.0
            annual_series = _scale_series(annual_series, net_factor)
            annual_generation = sum(annual_series) / 1000
            accuracy = "high"
            basis = "hourly_generation_profile_kw_8760"
            scaled_profile = _profile_from_annual_series(annual_series)
        else:
            peak_kw = max(hourly_profile) if hourly_profile else 0.0
            wind_mw = round(peak_kw / 1000, 2) if peak_kw else 0.0
            annual_generation = sum(hourly_profile) * 365 / 1000 * net_factor
            accuracy = "high"
            basis = "hourly_generation_profile_kw"
            scaled_profile = scale_hourly_profile(hourly_profile, annual_generation)
            annual_series = expand_daily_profile_to_year(scaled_profile, annual_target_mwh=annual_generation)
        power_curve_used = False
        mean_speed = None
    elif wind_speed_profile and power_curve:
        if len(wind_speed_profile) >= 8760:
            hourly_wind = _adjust_wind_speed_to_hub_height(wind_speed_profile[:8760], wind)
            power_output = _power_from_curve(hourly_wind, power_curve)
            annual_series = power_output[:8760]
            peak_kw = max(annual_series) if annual_series else 0.0
            wind_mw = round(float(wind.get("installed_capacity_mw") or peak_kw / 1000 or 0.0), 2) if peak_kw else float(wind.get("installed_capacity_mw") or 0.0)
            if wind_mw and peak_kw and abs(wind_mw * 1000 - peak_kw) > 1e-6:
                annual_series = _scale_series(annual_series, (wind_mw * 1000) / peak_kw)
            annual_series = _scale_series(annual_series, net_factor)
            annual_generation = sum(annual_series) / 1000
            scaled_profile = _profile_from_annual_series(annual_series)
            accuracy = "high"
            basis = "wind_speed_series_mps_8760 + power_curve"
            mean_speed = round(sum(hourly_wind) / len(hourly_wind), 3) if hourly_wind else None
        else:
            power_output = _power_from_curve(_adjust_wind_speed_to_hub_height(wind_speed_profile, wind), power_curve)
            peak_kw = max(power_output) if power_output else 0.0
            wind_mw = round(float(wind.get("installed_capacity_mw") or peak_kw / 1000 or 0.0), 2) if peak_kw else float(wind.get("installed_capacity_mw") or 0.0)
            if wind_mw and peak_kw and abs(wind_mw * 1000 - peak_kw) > 1e-6:
                power_output = _scale_series(power_output, (wind_mw * 1000) / peak_kw)
            annual_generation = sum(power_output) * 365 / 1000 * net_factor
            scaled_profile = scale_hourly_profile(power_output, annual_generation)
            annual_series = expand_daily_profile_to_year(scaled_profile, annual_target_mwh=annual_generation)
            accuracy = "high"
            basis = "wind_speed_series_mps + power_curve"
            mean_speed = round(sum(wind_speed_profile) / len(wind_speed_profile), 3) if wind_speed_profile else None
        power_curve_used = True
    elif daily_wind_speed and power_curve:
        daily_hub_speed = _adjust_wind_speed_to_hub_height(daily_wind_speed, wind)
        annual_series = _wind_annual_series_from_daily_speed(daily_hub_speed, power_curve, float(wind.get("installed_capacity_mw") or 0.0))
        peak_kw = max(annual_series) if annual_series else 0.0
        wind_mw = round(float(wind.get("installed_capacity_mw") or peak_kw / 1000 or 0.0), 2) if peak_kw else float(wind.get("installed_capacity_mw") or 0.0)
        if wind_mw and peak_kw and abs(wind_mw * 1000 - peak_kw) > 1e-6:
            annual_series = _scale_series(annual_series, (wind_mw * 1000) / peak_kw)
        annual_series = _scale_series(annual_series, net_factor)
        annual_generation = sum(annual_series) / 1000
        accuracy = "high"
        basis = "daily_wind_speed_series_mps + power_curve"
        scaled_profile = _profile_from_annual_series(annual_series)
        power_curve_used = True
        mean_speed = round(sum(daily_hub_speed) / len(daily_hub_speed), 3) if daily_hub_speed else None
    elif monthly_cf:
        avg_cf = sum(monthly_cf) / len(monthly_cf)
        wind_mw = round(float(wind.get("installed_capacity_mw") or max(0.0, annual_load * 0.15 / (8760 * max(avg_cf, 0.12))) or 0.0), 2) if annual_load or wind.get("installed_capacity_mw") else 0.0
        annual_generation = wind_mw * 8760 * avg_cf * net_factor
        accuracy = "medium"
        basis = "monthly_capacity_factor"
        scaled_profile = scale_hourly_profile(_default_wind_shape(), annual_generation)
        annual_series = expand_daily_profile_to_year(scaled_profile, monthly_factors=monthly_cf, annual_target_mwh=annual_generation)
        power_curve_used = False
        mean_speed = None
    elif "capacity_factor_assumption" in wind and wind.get("capacity_factor_assumption") is not None:
        wind_mw = round(float(wind.get("installed_capacity_mw") or max(0.0, annual_load * 0.15 / (8760 * max(cf_assumption, 0.12))) or 0.0), 2) if annual_load or wind.get("installed_capacity_mw") else 0.0
        annual_generation = wind_mw * (specific_yield_per_mw if specific_yield_per_mw > 0 else 8760 * cf_assumption) * net_factor
        accuracy = "medium" if specific_yield_per_mw > 0 else "low"
        basis = "expected_full_load_hours" if specific_yield_per_mw > 0 else "capacity_factor_assumption/default"
        scaled_profile = scale_hourly_profile(_default_wind_shape(), annual_generation)
        annual_series = expand_daily_profile_to_year(
            scaled_profile,
            monthly_factors=monthly_cf if monthly_cf else [1.08, 1.06, 1.02, 0.98, 0.95, 0.92, 0.90, 0.92, 0.96, 1.00, 1.06, 1.15],
            annual_target_mwh=annual_generation,
        )
        power_curve_used = False
        mean_speed = None
    elif avg_speed:
        derived_cf = _wind_cf_from_speed(_adjust_single_wind_speed(avg_speed, wind))
        wind_mw = round(float(wind.get("installed_capacity_mw") or max(0.0, annual_load * 0.15 / (8760 * max(derived_cf, 0.12))) or 0.0), 2) if annual_load or wind.get("installed_capacity_mw") else 0.0
        annual_generation = wind_mw * 8760 * derived_cf * net_factor
        accuracy = "medium"
        basis = "annual_avg_speed_mps"
        scaled_profile = scale_hourly_profile(_default_wind_shape(), annual_generation)
        annual_series = expand_daily_profile_to_year(
            scaled_profile,
            monthly_factors=[1.08, 1.06, 1.02, 0.98, 0.95, 0.92, 0.90, 0.92, 0.96, 1.00, 1.06, 1.15],
            annual_target_mwh=annual_generation,
        )
        power_curve_used = False
        mean_speed = avg_speed
    else:
        wind_mw = 0.0
        annual_generation = 0.0
        accuracy = "low"
        basis = "no_wind_resource"
        scaled_profile = [0.0] * 24
        annual_series = [0.0] * 8760
        power_curve_used = False
        mean_speed = None
    p50_factor, p90_factor = _resource_scenario_factors(wind, default_p90=0.88)
    p50_generation = annual_generation * p50_factor
    p90_generation = annual_generation * p90_factor
    annual_series = _scale_series_to_annual_target(annual_series, p50_generation) if annual_series else [0.0] * 8760
    scaled_profile = _profile_from_annual_series(annual_series)

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
        "wind_net_factor": round(net_factor, 4),
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


def _solar_site_latitude_deg(solar: dict[str, Any], project: dict[str, Any]) -> float:
    for value in (
        solar.get("site_latitude_deg"),
        project.get("latitude"),
        project.get("latitude_deg"),
    ):
        try:
            if value not in (None, ""):
                return float(value)
        except (TypeError, ValueError):
            continue
    return 30.0


def _effective_pv_tilt_deg(solar: dict[str, Any], latitude_deg: float) -> float:
    tilt = solar.get("tilt_deg")
    if tilt not in (None, ""):
        return float(tilt)
    return _recommended_pv_tilt_deg(latitude_deg)


def _recommended_pv_tilt_deg(latitude_deg: float) -> float:
    latitude = abs(float(latitude_deg))
    if latitude <= 10:
        return max(5.0, round(latitude * 0.8, 1))
    if latitude <= 25:
        return round(latitude * 0.9, 1)
    if latitude <= 40:
        return round(latitude, 1)
    return min(40.0, round(latitude * 0.95, 1))


def _azimuth_factor(azimuth_deg: float) -> float:
    delta = abs(azimuth_deg - 180.0)
    return max(0.82, 1.0 - delta / 180 * 0.12)


def _temperature_factor(temperature_profile_c: list[float], temp_coeff_pct_per_c: float, reference_temp_c: float) -> float:
    if not temperature_profile_c:
        return 1.0
    avg_temp = sum(temperature_profile_c) / len(temperature_profile_c)
    delta = avg_temp - reference_temp_c
    return max(0.88, min(1.02, 1.0 + delta * (temp_coeff_pct_per_c / 100.0)))


def _pv_shading_factor(solar: dict[str, Any]) -> float:
    if solar.get("shading_factor") not in (None, ""):
        return float(solar.get("shading_factor") or 1.0)
    if solar.get("shading_loss_ratio") not in (None, ""):
        return max(0.0, 1.0 - float(solar.get("shading_loss_ratio") or 0.0))
    return float(solar.get("horizon_shading_factor") or 1.0)


def _pv_bifacial_factor(solar: dict[str, Any]) -> float:
    if solar.get("bifacial_gain_factor") not in (None, ""):
        return float(solar.get("bifacial_gain_factor") or 1.0)
    bifaciality = float(solar.get("bifaciality_factor") or 0.0)
    albedo = float(solar.get("albedo_factor") or solar.get("albedo") or 0.2)
    if bifaciality <= 0:
        return 1.0
    # Typical bifacial gain: 5-15% for ground-mount in China (bifaciality ~0.7, albedo ~0.2).
    # Gain = bifaciality * albedo * ground_view_factor.
    # ground_view_factor ≈ 0.40 (configurable) reflects realistic rear-side irradiance capture.
    view_factor = float(solar.get("bifacial_view_factor") or 0.40)
    return 1.0 + max(0.0, bifaciality * albedo * view_factor)


def _tracking_factor(tracking_mode: str, latitude_deg: float) -> float:
    mode = tracking_mode.lower().strip()
    if mode in {"single_axis", "single_axis_tracking", "1p"}:
        if abs(latitude_deg) < 20:
            return 1.16
        if abs(latitude_deg) < 35:
            return 1.14
        return 1.12
    if mode in {"dual_axis", "dual_axis_tracking", "2p"}:
        return 1.22
    return 1.0


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


def _pv_cell_temperature_c(ambient_c: float, irradiance_kwh_per_m2: float, solar: dict[str, Any]) -> float:
    noct_c = float(solar.get("noct_c") or DEFAULT_PV_NOCT_C)
    irradiance_w_per_m2 = max(0.0, irradiance_kwh_per_m2) * 1000.0
    return ambient_c + (noct_c - 20.0) / 800.0 * irradiance_w_per_m2


def _pv_temperature_derate(cell_temp_c: float, temp_coeff_pct_per_c: float, reference_temp_c: float) -> float:
    return max(0.70, min(1.05, 1.0 + (cell_temp_c - reference_temp_c) * (temp_coeff_pct_per_c / 100.0)))


def _apply_pv_ac_limits(series: list[float], solar: dict[str, Any], pv_mwp: float) -> list[float]:
    if not series or pv_mwp <= 0:
        return series
    inverter_mwac = float(solar.get("inverter_capacity_mwac") or solar.get("installed_capacity_mwac") or 0.0)
    if inverter_mwac <= 0 and solar.get("dc_ac_ratio") not in (None, ""):
        dc_ac_ratio = float(solar.get("dc_ac_ratio") or 1.0)
        inverter_mwac = pv_mwp / max(dc_ac_ratio, 1e-9)
    if inverter_mwac <= 0:
        return series
    ac_limit_kw = inverter_mwac * 1000.0
    inverter_efficiency = float(solar.get("inverter_efficiency") or 0.985)
    transformer_efficiency = float(solar.get("transformer_efficiency") or 0.99)
    ac_limited = []
    for dc_kw in series:
        ac_kw = float(dc_kw) * inverter_efficiency * transformer_efficiency
        ac_limited.append(min(ac_kw, ac_limit_kw))
    return ac_limited


def _wind_air_density_factor(wind: dict[str, Any]) -> float:
    if wind.get("air_density_factor") not in (None, ""):
        return float(wind.get("air_density_factor") or 1.0)
    density = wind.get("air_density_kg_per_m3")
    if density in (None, ""):
        temperature_c = float(wind.get("ambient_temperature_c") or 15.0)
        elevation_m = float(wind.get("site_elevation_m") or 0.0)
        density = DEFAULT_STANDARD_AIR_DENSITY_KG_PER_M3 * (1.0 - 0.00011856 * elevation_m) * (288.15 / (273.15 + temperature_c))
    return max(0.85, min(1.15, float(density) / DEFAULT_STANDARD_AIR_DENSITY_KG_PER_M3))


def _profile_from_annual_series(series: list[float]) -> list[float]:
    if not series:
        return [0.0] * 24
    if len(series) >= 24:
        return [sum(series[hour::24]) / max(1, len(series[hour::24])) for hour in range(24)]
    return scale_hourly_profile(series)


def _scale_series(values: list[float], factor: float) -> list[float]:
    return [float(v) * factor for v in values]


def _scale_series_to_annual_target(series: list[float], annual_target_mwh: float) -> list[float]:
    if not series or annual_target_mwh is None:
        return series
    total_mwh = sum(series) / 1000
    if total_mwh <= 0:
        return series
    return _scale_series(series, annual_target_mwh / total_mwh)


def _solar_annual_series_from_hourly_irradiance(
    hourly_irradiance: list[float],
    pv_mwp: float,
    pr: float,
    tilt_factor: float,
    azimuth_factor: float,
    tracking_factor: float,
    temp_coeff_pct_per_c: float,
    reference_temp_c: float,
    hourly_temperature_c: list[float],
    availability_factor: float,
    calibration_factor: float,
    shading_factor: float,
    bifacial_factor: float,
    solar: dict[str, Any],
) -> list[float]:
    series: list[float] = []
    for idx, irr in enumerate(hourly_irradiance[:8760]):
        temperature = hourly_temperature_c[idx] if idx < len(hourly_temperature_c) else reference_temp_c
        cell_temp = _pv_cell_temperature_c(float(temperature), float(irr), solar)
        temp_factor = _pv_temperature_derate(cell_temp, temp_coeff_pct_per_c, reference_temp_c)
        series.append(
            pv_mwp
            * irr
            * pr
            * tilt_factor
            * azimuth_factor
            * tracking_factor
            * temp_factor
            * availability_factor
            * calibration_factor
            * shading_factor
            * bifacial_factor
            * 1000
        )
    return series


def _solar_annual_series_from_daily_irradiance(
    daily_irradiance: list[float],
    pv_mwp: float,
    pr: float,
    tilt_factor: float,
    azimuth_factor: float,
    tracking_factor: float,
    temp_coeff_pct_per_c: float,
    reference_temp_c: float,
    daily_temperature_c: list[float],
    availability_factor: float,
    calibration_factor: float,
    shading_factor: float,
    bifacial_factor: float,
    solar: dict[str, Any],
) -> list[float]:
    day_shape = _default_pv_shape()
    total_shape = sum(day_shape) or 1.0
    series: list[float] = []
    for idx, irr_day in enumerate(daily_irradiance[:366]):
        temperature = daily_temperature_c[idx] if idx < len(daily_temperature_c) else reference_temp_c
        cell_temp = _pv_cell_temperature_c(float(temperature), float(irr_day) / max(total_shape, 1e-9), solar)
        temp_factor = _pv_temperature_derate(cell_temp, temp_coeff_pct_per_c, reference_temp_c)
        day_energy_kwh = pv_mwp * irr_day * pr * tilt_factor * azimuth_factor * tracking_factor * temp_factor * availability_factor * calibration_factor * shading_factor * bifacial_factor * 1000
        for weight in day_shape:
            series.append(day_energy_kwh * weight / total_shape)
    return _ensure_8760(series)


def _adjust_wind_speed_to_hub_height(speeds: list[float], wind: dict[str, Any]) -> list[float]:
    source_height = float(wind.get("source_height_m") or wind.get("measurement_height_m") or 50.0)
    hub_height = float(wind.get("hub_height_m") or source_height)
    shear_exponent = float(wind.get("shear_exponent") or 0.14)
    if source_height <= 0 or hub_height <= 0 or abs(hub_height - source_height) < 1e-9:
        return [float(v) for v in speeds]
    factor = (hub_height / source_height) ** shear_exponent
    return [float(v) * factor for v in speeds]


def _adjust_single_wind_speed(speed: float, wind: dict[str, Any]) -> float:
    adjusted = _adjust_wind_speed_to_hub_height([speed], wind)
    return adjusted[0] if adjusted else speed


def _wind_annual_series_from_daily_speed(
    daily_speed: list[float],
    power_curve: list[dict[str, float]],
    installed_capacity_mw: float,
) -> list[float]:
    multipliers = _default_wind_shape()
    avg_multiplier = sum(multipliers) / len(multipliers) if multipliers else 1.0
    normalized = [value / avg_multiplier for value in multipliers] if avg_multiplier else multipliers
    base_curve = _power_from_curve([1.0], power_curve)
    rated_kw = max(float(installed_capacity_mw or 0.0) * 1000, max((point.get("power_kw", 0.0) for point in power_curve), default=0.0))
    series: list[float] = []
    for speed in daily_speed[:366]:
        hourly_speed = [max(0.0, speed * factor) for factor in normalized]
        hourly_power = _power_from_curve(hourly_speed, power_curve)
        if installed_capacity_mw > 0 and rated_kw > 0 and max(hourly_power or [0.0]) > 0:
            hourly_power = _scale_series(hourly_power, (installed_capacity_mw * 1000) / rated_kw)
        series.extend(hourly_power)
    return _ensure_8760(series)


def _ensure_8760(series: list[float]) -> list[float]:
    if len(series) >= 8760:
        return series[:8760]
    if not series:
        return [0.0] * 8760
    last = series[-1]
    return series + [last] * (8760 - len(series))
