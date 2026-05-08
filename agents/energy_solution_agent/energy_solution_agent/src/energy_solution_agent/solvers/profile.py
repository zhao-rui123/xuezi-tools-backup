from __future__ import annotations

from typing import Any

from ..constants import DEFAULT_HEAT_PUMP_COP, DEFAULT_THERMAL_COP

def synthesize_charging_profile(data: dict[str, Any]) -> tuple[list[float], dict[str, Any]]:
    charging = data.get("charging_data", {})
    segments = charging.get("vehicle_segments") or []
    power_levels = charging.get("charger_power_kw") or []
    counts = charging.get("num_chargers") or []
    simultaneity = charging.get("simultaneity_factor") or 0.45
    daily_energy = charging.get("daily_energy_kwh") or 0.0

    if charging.get("arrival_profile"):
        raw_arrival = [float(v) for v in charging["arrival_profile"]]
        # Detect annual series (>= 8760 points) vs daily profile (< 8760 points).
        # Convert annual series to 24h average by collapsing each hour slot across days.
        if len(raw_arrival) >= 8760:
            profile = [sum(raw_arrival[hour::24]) / max(1, len(raw_arrival[hour::24])) for hour in range(24)]
        else:
            profile = raw_arrival
    elif segments:
        profile = [0.0] * 24
        total_daily = 0.0
        segment_stats: list[dict[str, Any]] = []
        for seg in segments:
            seg_power = float(seg.get("charger_power_kw") or 0.0)
            seg_count = float(seg.get("num_chargers") or 0.0)
            seg_daily = float(seg.get("daily_energy_kwh") or 0.0)
            seg_sim = float(seg.get("simultaneity_factor") or simultaneity)
            peak_hours = seg.get("peak_hours") or ([10, 11, 12] if seg.get("vehicle_type") in {"bus", "fleet"} else [18, 19, 20, 21])
            peak_kw = seg_power * seg_count * seg_sim
            seg_profile = [0.0] * 24
            for hour in peak_hours:
                seg_profile[int(hour)] = peak_kw
            for hour in [7, 8, 13, 17, 22]:
                if seg_profile[hour] == 0:
                    seg_profile[hour] = peak_kw * 0.35
            if seg_daily and sum(seg_profile) > 0:
                scale = seg_daily / sum(seg_profile)
                seg_profile = [v * scale for v in seg_profile]
            total_daily += seg_daily
            profile = [a + b for a, b in zip(profile, seg_profile)]
            segment_stats.append(
                {
                    "vehicle_type": seg.get("vehicle_type") or "unknown",
                    "daily_energy_kwh": seg_daily,
                    "peak_kw": max(seg_profile) if seg_profile else 0.0,
                }
            )
        if total_daily > 0:
            daily_energy = total_daily
    else:
        total_nameplate = sum(p * c for p, c in zip(power_levels, counts))
        peak_kw = total_nameplate * simultaneity
        profile = [0.0] * 24
        peak_hours = range(9, 12) if charging.get("vehicle_type") in {"bus", "fleet"} else range(18, 22)
        for hour in peak_hours:
            profile[hour] = peak_kw
        shoulder = peak_kw * 0.45
        for hour in range(0, 24):
            if profile[hour] == 0.0 and hour in (7, 8, 12, 13, 17, 22):
                profile[hour] = shoulder
        if daily_energy and sum(profile) > 0:
            scale = daily_energy / sum(profile)
            profile = [p * scale for p in profile]
    utilization = (daily_energy / (sum(p * c for p, c in zip(power_levels, counts)) * 24)) if power_levels and counts and daily_energy else None
    queue_risk = "high" if simultaneity and simultaneity > 0.7 else ("medium" if simultaneity and simultaneity > 0.45 else "low")
    queue_index = None
    if power_levels and counts and daily_energy:
        nameplate = sum(p * c for p, c in zip(power_levels, counts))
        if nameplate > 0:
            queue_index = round((max(profile) / nameplate) * (utilization or 0.0) * 2.2, 4)
    diversity_factor = None
    if segments:
        total_segment_peak = sum(item["peak_kw"] for item in segment_stats) or 0.0
        if total_segment_peak > 0:
            diversity_factor = round((max(profile) / total_segment_peak), 4)
    return profile, {
        "annual_charging_energy_mwh": sum(profile) * 365 / 1000,
        "charging_peak_kw": max(profile) if profile else 0.0,
        "charging_utilization_ratio": round(utilization, 4) if utilization is not None else None,
        "charging_queue_risk": queue_risk,
        "charging_queue_index": queue_index,
        "charging_diversity_factor": diversity_factor,
        "charging_segment_summary": segment_stats if segments else [],
    }


def synthesize_thermal_profile(data: dict[str, Any]) -> tuple[dict[str, list[float]], dict[str, Any]]:
    load_data = data.get("load_data", {})
    cooling = [float(v) for v in (load_data.get("cooling_load_series_kw") or [])]
    heating = [float(v) for v in (load_data.get("heating_load_series_kw") or [])]
    thermal = data.get("thermal_system", {})
    if not cooling and thermal.get("service_type"):
        peak = float(load_data.get("peak_load_kw") or 1000) * 0.35
        cooling = [0.0] * 24
        for h in range(9, 18):
            cooling[h] = peak * (0.65 + 0.35 * math.sin((h - 9) / 9 * math.pi))
    if not heating and thermal.get("service_type"):
        peak = float(load_data.get("peak_load_kw") or 1000) * 0.25
        heating = [0.0] * 24
        for h in range(6, 22):
            heating[h] = peak * (0.75 + 0.25 * math.sin((h - 6) / 16 * math.pi))

    eq = data.get("equipment", {}).get("thermal", {})
    chiller_cop = float(eq.get("chiller_cop") or DEFAULT_THERMAL_COP)
    heat_pump_cop = float(eq.get("heat_pump_cop") or DEFAULT_HEAT_PUMP_COP)
    cooling_electric = [v / chiller_cop for v in cooling]
    heating_electric = [v / heat_pump_cop for v in heating]
    seasonal_shape = {
        "summer_peak_factor": round((max(cooling) / (sum(cooling) / len(cooling))), 3) if cooling and sum(cooling) > 0 else None,
        "winter_peak_factor": round((max(heating) / (sum(heating) / len(heating))), 3) if heating and sum(heating) > 0 else None,
    }
    return {
        "cooling_kw": cooling,
        "heating_kw": heating,
        "cooling_electric_kw": cooling_electric,
        "heating_electric_kw": heating_electric,
    }, {
        "annual_cooling_energy_mwh": sum(cooling) * 365 / 1000 if cooling else None,
        "annual_heating_energy_mwh": sum(heating) * 365 / 1000 if heating else None,
        "cooling_capacity_rt": max(cooling) / 3.517 if cooling else None,
        "heating_capacity_mwth": max(heating) / 1000 if heating else None,
        "cooling_peak_kwth": max(cooling) if cooling else None,
        "heating_peak_kwth": max(heating) if heating else None,
        **seasonal_shape,
    }


def simulate_thermal_equipment_annual(
    cooling_series_kw: list[float],
    heating_series_kw: list[float],
    thermal_equipment: dict[str, Any],
) -> dict[str, Any]:
    chiller_cop = float(thermal_equipment.get("chiller_cop") or DEFAULT_THERMAL_COP)
    heat_pump_cop = float(thermal_equipment.get("heat_pump_cop") or DEFAULT_HEAT_PUMP_COP)
    boiler_eff = float(thermal_equipment.get("boiler_efficiency") or 0.92)
    cooling_storage_capacity = float(thermal_equipment.get("cooling_storage_capacity_kwh") or 0.0)
    heating_storage_capacity = float(thermal_equipment.get("heating_storage_capacity_kwh") or 0.0)

    free_cooling_ratio = float(thermal_equipment.get("free_cooling_ratio") or 0.0)
    absorption_chiller_share = float(thermal_equipment.get("absorption_chiller_share") or 0.0)
    cooling_storage_soc = cooling_storage_capacity * 0.5
    heating_storage_soc = heating_storage_capacity * 0.5
    electric_series: list[float] = []
    boiler_heat_series: list[float] = []

    for idx in range(max(len(cooling_series_kw), len(heating_series_kw))):
        hour = idx % 24
        cooling = cooling_series_kw[idx] if idx < len(cooling_series_kw) else 0.0
        heating = heating_series_kw[idx] if idx < len(heating_series_kw) else 0.0
        cooling_priority = thermal_equipment.get("cooling_source_priority") or "electric_first"
        effective_cooling = cooling * (1.0 - free_cooling_ratio)
        electric_kw = effective_cooling / chiller_cop
        if absorption_chiller_share > 0:
            electric_kw *= (1.0 - absorption_chiller_share * 0.35)
        heat_pump_output = heating
        boiler_output = 0.0

        if cooling_storage_capacity > 0 and hour in {0, 1, 2, 3, 4, 5}:
            charge = min(cooling_storage_capacity - cooling_storage_soc, cooling * 0.18)
            cooling_storage_soc += charge
            electric_kw += charge / chiller_cop
        elif cooling_storage_soc > 0 and hour in {13, 14, 15, 16}:
            discharge = min(cooling_storage_soc, cooling * 0.2)
            cooling_storage_soc -= discharge
            electric_kw -= discharge / chiller_cop
        if cooling_priority == "storage_first" and cooling_storage_soc > 0 and hour in {10, 11, 12, 13, 14, 15, 16}:
            discharge = min(cooling_storage_soc, cooling * 0.12)
            cooling_storage_soc -= discharge
            electric_kw -= discharge / chiller_cop

        priority = thermal_equipment.get("heating_source_priority") or "heat_pump_first"
        if heating > 0 and priority == "boiler_first":
            boiler_output = heating * 0.45
            heat_pump_output = heating - boiler_output
        elif heating > 0 and priority == "hybrid":
            boiler_output = heating * 0.25 if hour in {6, 7, 8, 18, 19, 20} else heating * 0.10
            heat_pump_output = heating - boiler_output
        if heating_storage_capacity > 0 and hour in {0, 1, 2, 3, 4, 5}:
            charge = min(heating_storage_capacity - heating_storage_soc, heating * 0.15)
            heating_storage_soc += charge
            heat_pump_output += charge
        elif heating_storage_soc > 0 and hour in {7, 8, 9, 18, 19, 20}:
            discharge = min(heating_storage_soc, heating * 0.18)
            heating_storage_soc -= discharge
            heat_pump_output = max(0.0, heat_pump_output - discharge)

        electric_kw += heat_pump_output / heat_pump_cop
        boiler_heat_series.append(boiler_output / max(boiler_eff, 0.01))
        electric_series.append(max(0.0, electric_kw))

    return {
        "thermal_electric_series_kw": electric_series,
        "boiler_fuel_series_kw": boiler_heat_series,
        "thermal_electric_peak_kw": max(electric_series) if electric_series else 0.0,
        "annual_boiler_fuel_equivalent_mwh": sum(boiler_heat_series) / 1000,
    }


