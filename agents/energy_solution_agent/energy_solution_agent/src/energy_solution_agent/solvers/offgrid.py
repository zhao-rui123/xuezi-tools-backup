from __future__ import annotations

from typing import Any

from .dispatch import simulate_storage_dispatch_annual
from .carbon import estimate_carbon
from .finance import settlement_and_finance

def optimize_offgrid_pv_storage(
    data: dict[str, Any],
    pv_result: dict[str, Any],
    wind_result: dict[str, Any],
    load_series_kw: list[float],
    charging_series_kw: list[float],
    thermal_series_kw: list[float],
    price_series: list[float],
) -> dict[str, Any] | None:
    market = data.get("market_data", {})
    backup = data.get("equipment", {}).get("conventional_backup", {})
    if str(market.get("market_mode") or "").lower() != "offgrid_internal":
        return None
    if not backup.get("enabled"):
        return None
    fuel_cost = float(market.get("fuel_cost_per_kwh") or backup.get("fuel_cost_per_kwh") or 0.0)
    if fuel_cost <= 0:
        return None

    pv_base_mwp = float(pv_result.get("pv_mwp") or 0.0)
    pv_base_generation = float(pv_result.get("annual_pv_generation_mwh") or 0.0)
    if pv_base_mwp <= 0 or pv_base_generation <= 0:
        return None

    storage_cfg = data.get("equipment", {}).get("storage", {})
    annual_load_mwh = float(data.get("load_data", {}).get("annual_consumption_mwh") or 0.0)
    settings = _offgrid_optimization_settings(data)
    pv_candidates = _offgrid_pv_candidates(data, pv_result, annual_load_mwh, settings)
    wind_candidates = _offgrid_wind_candidates(data, wind_result, annual_load_mwh, settings)
    storage_pairs = _offgrid_storage_candidates(data, settings)
    if not pv_candidates or not wind_candidates or not storage_pairs:
        return None

    best: dict[str, Any] | None = None

    for wind_mw in wind_candidates:
        scaled_wind = _scale_wind_result(wind_result, wind_mw)
        wind_series_kw = scaled_wind.get("wind_annual_series_kw", [0.0] * len(load_series_kw))
        for pv_mwp in pv_candidates:
            scaled_pv = _scale_pv_result(pv_result, pv_mwp)
            pv_series_kw = scaled_pv.get("pv_annual_series_kw", [0.0] * len(load_series_kw))
            for storage_power_mw, storage_energy_mwh in storage_pairs:
                dispatch = simulate_storage_dispatch_annual(
                    load_series_kw=load_series_kw,
                    pv_series_kw=pv_series_kw,
                    wind_series_kw=wind_series_kw,
                    charging_series_kw=charging_series_kw,
                    thermal_series_kw=thermal_series_kw,
                    storage_power_mw=storage_power_mw,
                    storage_energy_mwh=storage_energy_mwh,
                    strategy_mode=data.get("project_info", {}).get("storage_strategy_mode") or "renewable_priority",
                    price_series=price_series,
                    storage_config=storage_cfg,
                )
                simulation = {
                    **scaled_pv,
                    **scaled_wind,
                    "storage_power_mw": storage_power_mw,
                    "storage_energy_mwh": storage_energy_mwh,
                    "annual_storage_charge_mwh": round(float(dispatch.get("daily_storage_charge_mwh") or 0.0) * 365, 2),
                    "annual_storage_discharge_mwh": round(float(dispatch.get("daily_storage_discharge_mwh") or 0.0) * 365, 2),
                    "annual_grid_purchase_mwh": round(float(dispatch.get("annual_grid_purchase_mwh") or 0.0), 2),
                    "annual_export_mwh": 0.0,
                    "annual_curtailment_mwh": 0.0,
                    "annual_charging_energy_mwh": 0.0,
                    "annual_cooling_energy_mwh": None,
                    "annual_heating_energy_mwh": None,
                    "coverage_ratio": round(1.0 - float(dispatch.get("annual_grid_purchase_mwh") or 0.0) / annual_load_mwh, 4) if annual_load_mwh else None,
                    "renewable_energy_coverage_ratio": round(
                        (
                            float(scaled_pv.get("annual_pv_generation_mwh") or 0.0)
                            + float(scaled_wind.get("annual_wind_generation_mwh") or 0.0)
                        )
                        / annual_load_mwh,
                        4,
                    )
                    if annual_load_mwh
                    else None,
                    "storage_annual_throughput_mwh": round(float(dispatch.get("storage_annual_throughput_mwh") or 0.0), 2),
                    "storage_equivalent_full_cycles_per_year": round(float(dispatch.get("storage_equivalent_full_cycles_per_year") or 0.0), 3),
                }
                if not _candidate_meets_offgrid_constraints(simulation, storage_power_mw, storage_energy_mwh, settings):
                    continue
                carbon = estimate_carbon(data, simulation)
                finance = settlement_and_finance(data, simulation, carbon)
                score = _offgrid_candidate_score(finance, simulation, dispatch, settings)
                residual_diesel_cost = float(dispatch.get("annual_grid_purchase_mwh") or 0.0) * fuel_cost * 1000
                capex_total = float(finance.get("capex_total") or 0.0)
                candidate = {
                    "score": score,
                    "coverage_ratio": float(simulation.get("coverage_ratio") or 0.0),
                    "residual_diesel_cost": residual_diesel_cost,
                    "capex_total": capex_total,
                    "renewables": {**scaled_pv, **scaled_wind},
                    "storage": {
                        "storage_power_mw": storage_power_mw,
                        "storage_energy_mwh": storage_energy_mwh,
                        "annual_storage_charge_mwh": simulation["annual_storage_charge_mwh"],
                        "annual_storage_discharge_mwh": simulation["annual_storage_discharge_mwh"],
                    },
                }
                if _is_better_offgrid_candidate(candidate, best, settings):
                    best = candidate

    return best


def _offgrid_pv_candidates(
    data: dict[str, Any],
    pv_result: dict[str, Any],
    annual_load_mwh: float,
    settings: dict[str, Any],
) -> list[float]:
    equipment_pv = data.get("equipment", {}).get("pv", {})
    fixed = settings.get("fixed_pv_mwp")
    if fixed is not None:
        return [round(float(fixed), 3)]
    explicit = [float(v) for v in (equipment_pv.get("candidate_mwp") or settings.get("candidate_pv_mwp") or []) if v is not None]
    if explicit:
        return sorted({round(max(0.0, value), 3) for value in explicit})

    base_pv_mwp = float(pv_result.get("pv_mwp") or 0.0)
    annual_generation = float(pv_result.get("annual_pv_generation_mwh") or 0.0)
    yield_per_mwp = annual_generation / base_pv_mwp if base_pv_mwp > 0 else 0.0
    area_per_mwp = float(data.get("resource_data", {}).get("solar", {}).get("area_per_mwp_m2") or 6500)
    area_limit_mwp = float(data.get("resource_data", {}).get("solar", {}).get("available_area_m2") or 0.0) / area_per_mwp if data.get("resource_data", {}).get("solar", {}).get("available_area_m2") else 0.0
    if yield_per_mwp > 0 and annual_load_mwh > 0:
        load_cover_limit = annual_load_mwh / yield_per_mwp
    else:
        load_cover_limit = base_pv_mwp
    upper = max(base_pv_mwp, load_cover_limit)
    if area_limit_mwp > 0:
        upper = min(upper, area_limit_mwp)
    if upper <= 0:
        return []
    fractions = [0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0]
    return sorted({round(upper * fraction, 3) for fraction in fractions})


def _offgrid_wind_candidates(
    data: dict[str, Any],
    wind_result: dict[str, Any],
    annual_load_mwh: float,
    settings: dict[str, Any],
) -> list[float]:
    equipment_wind = data.get("equipment", {}).get("wind", {})
    fixed = settings.get("fixed_wind_mw")
    if fixed is not None:
        return [round(float(fixed), 3)]
    explicit = [float(v) for v in (equipment_wind.get("candidate_mw") or settings.get("candidate_wind_mw") or []) if v is not None]
    if explicit:
        return sorted({round(max(0.0, value), 3) for value in explicit})

    base_wind_mw = float(wind_result.get("wind_mw") or 0.0)
    annual_generation = float(wind_result.get("annual_wind_generation_mwh") or 0.0)
    if base_wind_mw <= 0 or annual_generation <= 0 or annual_load_mwh <= 0:
        return [0.0]
    yield_per_mw = annual_generation / base_wind_mw
    upper = max(base_wind_mw, annual_load_mwh * 0.55 / yield_per_mw)
    fractions = [0.0, 0.5, 0.75, 1.0, 1.25, 1.5]
    return sorted({round(max(0.0, upper * fraction), 3) for fraction in fractions})


def _offgrid_storage_candidates(data: dict[str, Any], settings: dict[str, Any]) -> list[tuple[float | None, float | None]]:
    storage = data.get("equipment", {}).get("storage", {})
    fixed_power = settings.get("fixed_storage_power_mw")
    fixed_energy = settings.get("fixed_storage_energy_mwh")
    if fixed_power is not None or fixed_energy is not None:
        power = None if fixed_power in (None, 0) else round(float(fixed_power), 3)
        energy = None if fixed_energy in (None, 0) else round(float(fixed_energy), 3)
        return [(power, energy)]
    powers_kw = [float(v) for v in (storage.get("power_candidate_kw") or []) if v is not None]
    energies_kwh = [float(v) for v in (storage.get("energy_candidate_kwh") or []) if v is not None]
    if not powers_kw:
        peak_load_kw = float(data.get("load_data", {}).get("peak_load_kw") or 0.0)
        powers_kw = [0.0, round(peak_load_kw * 0.15, 0), round(peak_load_kw * 0.25, 0), round(peak_load_kw * 0.35, 0)]
    if not energies_kwh:
        energies_kwh = [0.0]
        for power_kw in powers_kw:
            if power_kw > 0:
                for hours in (2, 4, 6):
                    energies_kwh.append(power_kw * hours)

    critical_load_kw = float(data.get("load_data", {}).get("critical_load_kw") or 0.0)
    backup_hours_required = float(data.get("load_data", {}).get("backup_hours_required") or 0.0)
    if settings.get("enforce_backup_requirement"):
        required_backup_mwh = critical_load_kw * backup_hours_required / 1000 if critical_load_kw and backup_hours_required else 0.0
    else:
        required_backup_mwh = 0.0
    min_power_mw = float(settings.get("min_storage_power_mw") or 0.0)
    min_energy_mwh = float(settings.get("min_storage_energy_mwh") or 0.0)
    min_duration_hours = float(settings.get("min_storage_duration_hours") or 0.0)
    pairs: list[tuple[float | None, float | None]] = [(None, None)]
    for power_kw in powers_kw:
        for energy_kwh in energies_kwh:
            if power_kw <= 0 or energy_kwh <= 0:
                continue
            duration_hours = energy_kwh / power_kw if power_kw > 0 else 0.0
            if duration_hours < 1.0 or duration_hours > 8.0:
                continue
            energy_mwh = energy_kwh / 1000
            power_mw = power_kw / 1000
            if required_backup_mwh and energy_mwh + 1e-6 < required_backup_mwh:
                continue
            if min_power_mw and power_mw + 1e-6 < min_power_mw:
                continue
            if min_energy_mwh and energy_mwh + 1e-6 < min_energy_mwh:
                continue
            if min_duration_hours and duration_hours + 1e-6 < min_duration_hours:
                continue
            pairs.append((round(power_mw, 3), round(energy_mwh, 3)))
    return list(dict.fromkeys(pairs))


def _scale_pv_result(pv_result: dict[str, Any], target_mwp: float) -> dict[str, Any]:
    base_mwp = float(pv_result.get("pv_mwp") or 0.0)
    if target_mwp <= 0 or base_mwp <= 0:
        return {
            "pv_mwp": None,
            "annual_pv_generation_mwh": None,
            "pv_resource_accuracy": pv_result.get("pv_resource_accuracy"),
            "pv_resource_basis": pv_result.get("pv_resource_basis"),
            "pv_hourly_profile_kw": [0.0] * 24,
            "pv_annual_series_kw": [0.0] * len(pv_result.get("pv_annual_series_kw", [0.0] * 8760)),
            "pv_p50_generation_mwh": None,
            "pv_p90_generation_mwh": None,
            "pv_effective_tilt_deg": pv_result.get("pv_effective_tilt_deg"),
            "pv_recommended_tilt_deg": pv_result.get("pv_recommended_tilt_deg"),
            "pv_tilt_factor": pv_result.get("pv_tilt_factor"),
            "pv_azimuth_factor": pv_result.get("pv_azimuth_factor"),
            "pv_tracking_factor": pv_result.get("pv_tracking_factor"),
            "pv_temperature_factor": pv_result.get("pv_temperature_factor"),
            "pv_pr_effective": pv_result.get("pv_pr_effective"),
        }
    factor = target_mwp / base_mwp
    return {
        "pv_mwp": round(target_mwp, 3),
        "annual_pv_generation_mwh": round(float(pv_result.get("annual_pv_generation_mwh") or 0.0) * factor, 2),
        "pv_resource_accuracy": pv_result.get("pv_resource_accuracy"),
        "pv_resource_basis": pv_result.get("pv_resource_basis"),
        "pv_hourly_profile_kw": [round(float(value) * factor, 6) for value in pv_result.get("pv_hourly_profile_kw", [0.0] * 24)],
        "pv_annual_series_kw": [float(value) * factor for value in pv_result.get("pv_annual_series_kw", [0.0] * 8760)],
        "pv_p50_generation_mwh": round(float(pv_result.get("pv_p50_generation_mwh") or 0.0) * factor, 2),
        "pv_p90_generation_mwh": round(float(pv_result.get("pv_p90_generation_mwh") or 0.0) * factor, 2),
        "pv_effective_tilt_deg": pv_result.get("pv_effective_tilt_deg"),
        "pv_recommended_tilt_deg": pv_result.get("pv_recommended_tilt_deg"),
        "pv_tilt_factor": pv_result.get("pv_tilt_factor"),
        "pv_azimuth_factor": pv_result.get("pv_azimuth_factor"),
        "pv_tracking_factor": pv_result.get("pv_tracking_factor"),
        "pv_temperature_factor": pv_result.get("pv_temperature_factor"),
        "pv_pr_effective": pv_result.get("pv_pr_effective"),
    }


def _scale_wind_result(wind_result: dict[str, Any], target_mw: float) -> dict[str, Any]:
    base_mw = float(wind_result.get("wind_mw") or 0.0)
    if target_mw <= 0 or base_mw <= 0:
        return {
            "wind_mw": None,
            "annual_wind_generation_mwh": None,
            "wind_resource_accuracy": wind_result.get("wind_resource_accuracy"),
            "wind_resource_basis": wind_result.get("wind_resource_basis"),
            "wind_hourly_profile_kw": [0.0] * 24,
            "wind_annual_series_kw": [0.0] * len(wind_result.get("wind_annual_series_kw", [0.0] * 8760)),
            "wind_p50_generation_mwh": None,
            "wind_p90_generation_mwh": None,
            "wind_power_curve_used": wind_result.get("wind_power_curve_used"),
            "wind_mean_speed_mps": wind_result.get("wind_mean_speed_mps"),
        }
    factor = target_mw / base_mw
    return {
        "wind_mw": round(target_mw, 3),
        "annual_wind_generation_mwh": round(float(wind_result.get("annual_wind_generation_mwh") or 0.0) * factor, 2),
        "wind_resource_accuracy": wind_result.get("wind_resource_accuracy"),
        "wind_resource_basis": wind_result.get("wind_resource_basis"),
        "wind_hourly_profile_kw": [round(float(value) * factor, 6) for value in wind_result.get("wind_hourly_profile_kw", [0.0] * 24)],
        "wind_annual_series_kw": [float(value) * factor for value in wind_result.get("wind_annual_series_kw", [0.0] * 8760)],
        "wind_p50_generation_mwh": round(float(wind_result.get("wind_p50_generation_mwh") or 0.0) * factor, 2),
        "wind_p90_generation_mwh": round(float(wind_result.get("wind_p90_generation_mwh") or 0.0) * factor, 2),
        "wind_power_curve_used": wind_result.get("wind_power_curve_used"),
        "wind_mean_speed_mps": wind_result.get("wind_mean_speed_mps"),
    }


def _offgrid_optimization_settings(data: dict[str, Any]) -> dict[str, Any]:
    optimization = (data.get("financial", {}) or {}).get("optimization", {}) or {}
    equipment_pv = data.get("equipment", {}).get("pv", {}) or {}
    equipment_wind = data.get("equipment", {}).get("wind", {}) or {}
    equipment_storage = data.get("equipment", {}).get("storage", {}) or {}
    return {
        "objective": str(optimization.get("objective") or "max_npv"),
        "min_coverage_ratio": float(optimization.get("min_coverage_ratio") or 0.0),
        "min_energy_coverage_ratio": float(optimization.get("min_energy_coverage_ratio") or 0.0),
        "max_grid_purchase_mwh": float(optimization.get("max_grid_purchase_mwh") or 0.0),
        "min_storage_power_mw": float(optimization.get("min_storage_power_mw") or 0.0),
        "min_storage_energy_mwh": float(optimization.get("min_storage_energy_mwh") or 0.0),
        "min_storage_duration_hours": float(optimization.get("min_storage_duration_hours") or 0.0),
        "enforce_backup_requirement": bool(optimization.get("enforce_backup_requirement") or False),
        "fixed_pv_mwp": optimization.get("fixed_pv_mwp", equipment_pv.get("fixed_capacity_mwp")),
        "fixed_wind_mw": optimization.get("fixed_wind_mw", equipment_wind.get("fixed_capacity_mw")),
        "fixed_storage_power_mw": optimization.get("fixed_storage_power_mw", equipment_storage.get("fixed_power_mw")),
        "fixed_storage_energy_mwh": optimization.get("fixed_storage_energy_mwh", equipment_storage.get("fixed_energy_mwh")),
        "candidate_pv_mwp": optimization.get("candidate_pv_mwp"),
        "candidate_wind_mw": optimization.get("candidate_wind_mw"),
    }


def _candidate_meets_offgrid_constraints(
    simulation: dict[str, Any],
    storage_power_mw: float | None,
    storage_energy_mwh: float | None,
    settings: dict[str, Any],
) -> bool:
    coverage_ratio = float(simulation.get("coverage_ratio") or 0.0)
    if coverage_ratio + 1e-6 < float(settings.get("min_coverage_ratio") or 0.0):
        return False
    energy_coverage_ratio = float(simulation.get("renewable_energy_coverage_ratio") or 0.0)
    if energy_coverage_ratio + 1e-6 < float(settings.get("min_energy_coverage_ratio") or 0.0):
        return False
    max_grid_purchase_mwh = float(settings.get("max_grid_purchase_mwh") or 0.0)
    if max_grid_purchase_mwh and float(simulation.get("annual_grid_purchase_mwh") or 0.0) - 1e-6 > max_grid_purchase_mwh:
        return False
    min_storage_power_mw = float(settings.get("min_storage_power_mw") or 0.0)
    min_storage_energy_mwh = float(settings.get("min_storage_energy_mwh") or 0.0)
    min_storage_duration_hours = float(settings.get("min_storage_duration_hours") or 0.0)
    if min_storage_power_mw and float(storage_power_mw or 0.0) + 1e-6 < min_storage_power_mw:
        return False
    if min_storage_energy_mwh and float(storage_energy_mwh or 0.0) + 1e-6 < min_storage_energy_mwh:
        return False
    if min_storage_duration_hours:
        duration = float(storage_energy_mwh or 0.0) / float(storage_power_mw or 1.0) if storage_power_mw else 0.0
        if duration + 1e-6 < min_storage_duration_hours:
            return False
    return True


def _offgrid_candidate_score(
    finance: dict[str, Any],
    simulation: dict[str, Any],
    dispatch: dict[str, Any],
    settings: dict[str, Any],
) -> tuple[float, ...]:
    objective = str(settings.get("objective") or "max_npv").lower()
    npv = float(finance.get("npv") or float("-inf"))
    coverage = float(simulation.get("coverage_ratio") or 0.0)
    residual_grid = float(dispatch.get("annual_grid_purchase_mwh") or 0.0)
    capex_total = float(finance.get("capex_total") or 0.0)
    if objective == "max_coverage":
        return (coverage, npv, -residual_grid, -capex_total)
    if objective == "min_grid_purchase":
        return (-residual_grid, npv, coverage, -capex_total)
    return (npv, coverage, -residual_grid, -capex_total)


def _is_better_offgrid_candidate(candidate: dict[str, Any], best: dict[str, Any] | None, settings: dict[str, Any]) -> bool:
    if best is None:
        return True
    return tuple(candidate["score"]) > tuple(best["score"])


