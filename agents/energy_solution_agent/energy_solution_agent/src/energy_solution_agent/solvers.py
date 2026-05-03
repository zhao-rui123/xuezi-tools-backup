from __future__ import annotations

import math
from typing import Any

from .constants import DEFAULT_GAS_EMISSION_FACTOR, DEFAULT_GRID_EMISSION_FACTOR, DEFAULT_HEAT_PUMP_COP, DEFAULT_THERMAL_COP
from .utils import clamp, safe_div


def _sum_series(values: list[float]) -> float:
    return float(sum(v for v in values if isinstance(v, (int, float))))


def synthesize_charging_profile(data: dict[str, Any]) -> tuple[list[float], dict[str, Any]]:
    charging = data.get("charging_data", {})
    segments = charging.get("vehicle_segments") or []
    power_levels = charging.get("charger_power_kw") or []
    counts = charging.get("num_chargers") or []
    simultaneity = charging.get("simultaneity_factor") or 0.45
    daily_energy = charging.get("daily_energy_kwh") or 0.0

    if charging.get("arrival_profile"):
        profile = [float(v) for v in charging["arrival_profile"]]
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


def simulate_storage_dispatch(
    load_profile_kw: list[float],
    pv_profile_kw: list[float],
    wind_profile_kw: list[float],
    charging_profile_kw: list[float],
    thermal_electric_kw: list[float],
    storage_power_mw: float | None,
    storage_energy_mwh: float | None,
    valley_hours: set[int] | None = None,
) -> dict[str, Any]:
    if not storage_power_mw or not storage_energy_mwh:
        baseline = _baseline_grid_profile(load_profile_kw, charging_profile_kw, thermal_electric_kw, pv_profile_kw, wind_profile_kw)
        return {
            "baseline_grid_profile_kw": baseline,
            "post_storage_grid_profile_kw": baseline[:],
            "daily_storage_charge_mwh": 0.0,
            "daily_storage_discharge_mwh": 0.0,
            "daily_storage_cycles": 0.0,
            "peak_reduction_kw": 0.0,
            "baseline_peak_grid_kw": max(baseline) if baseline else 0.0,
            "post_storage_peak_grid_kw": max(baseline) if baseline else 0.0,
        }

    valley = valley_hours or {0, 1, 2, 3, 4, 5, 12, 13}
    power_kw = storage_power_mw * 1000
    energy_kwh = storage_energy_mwh * 1000
    soc_kwh = energy_kwh * 0.5
    soc_min = energy_kwh * 0.1
    soc_max = energy_kwh * 0.9
    baseline = _baseline_grid_profile(load_profile_kw, charging_profile_kw, thermal_electric_kw, pv_profile_kw, wind_profile_kw)
    positive_baseline = [v for v in baseline if v > 0]
    target_peak = sorted(positive_baseline)[int(len(positive_baseline) * 0.75)] if positive_baseline else 0.0
    valley_threshold = min(target_peak * 0.55, (sum(positive_baseline) / len(positive_baseline)) if positive_baseline else target_peak)
    grid = []
    charged = 0.0
    discharged = 0.0
    for hour, base in enumerate(baseline):
        net = base
        if hour in valley and net > 0 and soc_kwh < soc_max and net < valley_threshold:
            headroom = max(0.0, valley_threshold - net)
            charge_kw = min(power_kw, soc_max - soc_kwh, headroom)
            soc_kwh += charge_kw
            net += charge_kw
            charged += charge_kw
        elif hour not in valley and net > target_peak and soc_kwh > soc_min:
            discharge_kw = min(power_kw, soc_kwh - soc_min, max(0.0, net - target_peak))
            soc_kwh -= discharge_kw
            net -= discharge_kw
            discharged += discharge_kw
        grid.append(max(0.0, net))
    cycles = discharged / energy_kwh if energy_kwh > 0 else 0.0
    return {
        "baseline_grid_profile_kw": baseline,
        "post_storage_grid_profile_kw": grid,
        "daily_storage_charge_mwh": charged / 1000,
        "daily_storage_discharge_mwh": discharged / 1000,
        "daily_storage_cycles": cycles,
        "peak_reduction_kw": max(baseline) - max(grid) if baseline and grid else 0.0,
        "baseline_peak_grid_kw": max(baseline) if baseline else 0.0,
        "post_storage_peak_grid_kw": max(grid) if grid else 0.0,
    }


def simulate_storage_dispatch_annual(
    load_series_kw: list[float],
    pv_series_kw: list[float],
    wind_series_kw: list[float],
    charging_series_kw: list[float],
    thermal_series_kw: list[float],
    storage_power_mw: float | None,
    storage_energy_mwh: float | None,
    strategy_mode: str = "balanced",
    price_series: list[float] | None = None,
    storage_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    storage_config = storage_config or {}
    if not storage_power_mw or not storage_energy_mwh:
        baseline = _baseline_grid_profile(load_series_kw, charging_series_kw, thermal_series_kw, pv_series_kw, wind_series_kw)
        annual_purchase = sum(baseline) / 1000
        return {
            "baseline_grid_series_kw": baseline,
            "post_storage_grid_series_kw": baseline[:],
            "annual_grid_purchase_mwh": annual_purchase,
            "daily_storage_charge_mwh": 0.0,
            "daily_storage_discharge_mwh": 0.0,
            "daily_storage_cycles": 0.0,
            "peak_reduction_kw": 0.0,
            "baseline_peak_grid_kw": max(baseline) if baseline else 0.0,
            "post_storage_peak_grid_kw": max(baseline) if baseline else 0.0,
            "storage_effective_round_trip_efficiency": None,
            "storage_reserved_soc_ratio": None,
            "storage_backup_soc_ratio": None,
            "storage_degradation_per_year": None,
            "storage_end_of_life_capacity_ratio": None,
            "monthly_storage_revenue_breakdown": [],
        }
    power_kw = storage_power_mw * 1000
    energy_kwh = storage_energy_mwh * 1000
    pcs_eff = float(storage_config.get("pcs_efficiency") or 0.98)
    transformer_eff = float(storage_config.get("transformer_efficiency") or 0.99)
    battery_charge_eff = float(storage_config.get("battery_charge_efficiency") or 0.96)
    battery_discharge_eff = float(storage_config.get("battery_discharge_efficiency") or 0.96)
    effective_rte = pcs_eff * transformer_eff * battery_charge_eff * battery_discharge_eff
    soc = energy_kwh * float(storage_config.get("initial_soc") or 0.5)
    reserve_soc = float(storage_config.get("soc_reserve_ratio") or 0.1)
    backup_soc = float(storage_config.get("backup_soc_ratio") or 0.0)
    soc_min = energy_kwh * max(reserve_soc, backup_soc)
    soc_max = energy_kwh * float(storage_config.get("soc_max") or 0.9)
    baseline = _baseline_grid_profile(load_series_kw, charging_series_kw, thermal_series_kw, pv_series_kw, wind_series_kw)
    positive = [v for v in baseline if v > 0]
    if strategy_mode == "market_responding":
        percentile = 0.88
    elif strategy_mode == "peak_shaving":
        percentile = 0.78
    elif strategy_mode == "arbitrage":
        percentile = 0.9
    elif strategy_mode == "renewable_priority":
        percentile = 0.84
    elif strategy_mode == "microgrid":
        percentile = 0.0  # microgrid 用 net > 0 判断，不依赖百分位阈值
    else:
        percentile = 0.82
    target_peak = sorted(positive)[int(len(positive) * percentile)] if positive else 0.0 if strategy_mode != "microgrid" else 0.0
    valley_threshold = min(target_peak * (0.62 if strategy_mode == "arbitrage" else 0.55), (sum(positive) / len(positive)) if positive else target_peak)
    # 确保 valley_threshold 不低于最小净负荷+20%，否则电池永远无法充电
    if positive:
        min_positive = positive[0] if len(positive) > 0 else 0.0
        floor_threshold = min_positive * 1.2 + 50.0  # 比最小净负荷高20%+50kW
        valley_threshold = max(valley_threshold, floor_threshold)
    grid = []
    charged = 0.0
    discharged = 0.0
    renewable_charged = 0.0
    price_series = price_series or [0.72] * len(baseline)
    month_hours = [31 * 24, 28 * 24, 31 * 24, 30 * 24, 31 * 24, 30 * 24, 31 * 24, 31 * 24, 30 * 24, 31 * 24, 30 * 24, 31 * 24]
    monthly_charge = [0.0] * 12
    monthly_discharge = [0.0] * 12
    monthly_margin = [0.0] * 12
    month_idx = 0
    next_month_cutoff = month_hours[0]
    for idx, base in enumerate(baseline):
        if idx >= next_month_cutoff and month_idx < 11:
            month_idx += 1
            next_month_cutoff += month_hours[month_idx]
        hour = idx % 24
        net = base
        price = price_series[idx] if idx < len(price_series) else 0.72
        day_slice = price_series[(idx // 24) * 24 : ((idx // 24) + 1) * 24] or [0.72]
        sorted_day_prices = sorted(day_slice)
        cheap_threshold = sorted_day_prices[max(0, int(len(sorted_day_prices) * 0.25) - 1)]
        expensive_threshold = sorted_day_prices[min(len(sorted_day_prices) - 1, int(len(sorted_day_prices) * 0.75))]
        if strategy_mode == "renewable_priority":
            renewable_surplus = max(0.0, ((pv_series_kw[idx] if idx < len(pv_series_kw) else 0.0) + (wind_series_kw[idx] if idx < len(wind_series_kw) else 0.0)) - ((load_series_kw[idx] if idx < len(load_series_kw) else 0.0) + (charging_series_kw[idx] if idx < len(charging_series_kw) else 0.0) + (thermal_series_kw[idx] if idx < len(thermal_series_kw) else 0.0)))
        else:
            renewable_surplus = max(0.0, ((pv_series_kw[idx] if idx < len(pv_series_kw) else 0.0) + (wind_series_kw[idx] if idx < len(wind_series_kw) else 0.0)) - ((load_series_kw[idx] if idx < len(load_series_kw) else 0.0) + (charging_series_kw[idx] if idx < len(charging_series_kw) else 0.0) + (thermal_series_kw[idx] if idx < len(thermal_series_kw) else 0.0)))
        # ── 微电网能量平衡策略 ──────────────────────────────────────
        # 逻辑：
        #   风光发电 > 负荷  →  充电（存余量）
        #   负荷 > 风光发电  →  放电（补缺口）
        # 两者互斥，不同时发生
        if strategy_mode == "microgrid":
            pv_kw = pv_series_kw[idx] if idx < len(pv_series_kw) else 0.0
            wind_kw = wind_series_kw[idx] if idx < len(wind_series_kw) else 0.0
            gen_kw = pv_kw + wind_kw
            load_kw = load_series_kw[idx] if idx < len(load_series_kw) else 0.0
            charging_kw = charging_series_kw[idx] if idx < len(charging_series_kw) else 0.0
            thermal_kw = thermal_series_kw[idx] if idx < len(thermal_series_kw) else 0.0
            total_load_kw = load_kw + charging_kw + thermal_kw
            surplus_kw = gen_kw - total_load_kw  # >0 = 过剩，<0 = 缺口

            if surplus_kw > 0 and soc < soc_max:
                # 风光过剩 → 充电
                charge_kw = min(power_kw, max(0.0, soc_max - soc), surplus_kw / battery_charge_eff)
                soc += charge_kw * battery_charge_eff
                charged += charge_kw
                monthly_charge[month_idx] += charge_kw / 1000
                renewable_charged += min(charge_kw * battery_charge_eff, surplus_kw)
                grid.append(0.0)  # 过剩电力全部被储能消纳，电网无需供电
            elif surplus_kw < 0 and soc > soc_min:
                # 负荷缺口 → 放电
                deficit_kw = abs(surplus_kw)
                discharge_kw = min(power_kw, max(0.0, soc - soc_min) * battery_discharge_eff, deficit_kw)
                soc -= discharge_kw / max(battery_discharge_eff, 0.01)
                discharged += discharge_kw
                monthly_discharge[month_idx] += discharge_kw / 1000
                monthly_margin[month_idx] += (discharge_kw / 1000) * price
                grid.append(0.0)  # 储能填补缺口，电网无需供电
            else:
                # 刚好平衡或电池无能为力
                grid.append(max(0.0, -surplus_kw))
            continue  # 进入下一小时
        should_charge = (hour in {0, 1, 2, 3, 4, 5, 12, 13} and net < valley_threshold) or renewable_surplus > 0
        if strategy_mode == "market_responding":
            should_charge = should_charge or price <= cheap_threshold
        if should_charge and soc < soc_max:
            headroom = max(0.0, valley_threshold - net)
            charge_limit = max(headroom, renewable_surplus, power_kw * (0.65 if strategy_mode == "market_responding" else 1.0))
            charge_kw = min(power_kw, soc_max - soc, charge_limit)
            soc += charge_kw * battery_charge_eff
            net += charge_kw
            charged += charge_kw
            monthly_charge[month_idx] += charge_kw / 1000
            renewable_charged += min(charge_kw, renewable_surplus)
        should_discharge = net > target_peak
        if strategy_mode == "market_responding":
            should_discharge = should_discharge or price >= expensive_threshold
        if should_discharge and soc > soc_min:
            target_cut = max(0.0, net - target_peak)
            if strategy_mode == "market_responding" and price >= expensive_threshold:
                target_cut = max(target_cut, power_kw * 0.55)
            available_kw = (soc - soc_min) * battery_discharge_eff
            discharge_kw = min(power_kw, available_kw, target_cut)
            soc -= discharge_kw / max(battery_discharge_eff, 0.01)
            net -= discharge_kw * pcs_eff * transformer_eff
            discharged += discharge_kw
            monthly_discharge[month_idx] += discharge_kw / 1000
            monthly_margin[month_idx] += (discharge_kw / 1000) * price
        grid.append(max(0.0, net))
    annual_purchase = sum(grid) / 1000
    daily_cycles = (discharged / energy_kwh) / 365 if energy_kwh > 0 else 0.0
    throughput_mwh = (charged + discharged) / 1000
    annual_fec = discharged / energy_kwh if energy_kwh > 0 else 0.0
    cycle_life = float(storage_config.get("cycle_life") or 6000.0)
    storage_life_years = (cycle_life / annual_fec) if annual_fec > 0 else None
    charge_from_renewables_ratio = (renewable_charged / charged) if charged > 0 else None
    annual_degradation = float(storage_config.get("annual_degradation_rate") or 0.025)
    end_of_life_ratio = max(0.0, 1.0 - annual_degradation * min(storage_life_years or 0.0, 20.0)) if storage_life_years else None
    monthly_breakdown = [
        {
            "month": idx + 1,
            "charge_mwh": round(monthly_charge[idx], 3),
            "discharge_mwh": round(monthly_discharge[idx], 3),
            "gross_margin": round(monthly_margin[idx], 2),
        }
        for idx in range(12)
    ]
    return {
        "baseline_grid_series_kw": baseline,
        "post_storage_grid_series_kw": grid,
        "annual_grid_purchase_mwh": annual_purchase,
        "daily_storage_charge_mwh": charged / 1000 / 365,
        "daily_storage_discharge_mwh": discharged / 1000 / 365,
        "daily_storage_cycles": daily_cycles,
        "peak_reduction_kw": max(baseline) - max(grid) if baseline and grid else 0.0,
        "baseline_peak_grid_kw": max(baseline) if baseline else 0.0,
        "post_storage_peak_grid_kw": max(grid) if grid else 0.0,
        "storage_annual_throughput_mwh": throughput_mwh,
        "storage_equivalent_full_cycles_per_year": annual_fec,
        "storage_life_years_estimate": storage_life_years,
        "storage_charge_from_renewables_ratio": charge_from_renewables_ratio,
        "storage_effective_round_trip_efficiency": effective_rte,
        "storage_reserved_soc_ratio": reserve_soc,
        "storage_backup_soc_ratio": backup_soc,
        "storage_degradation_per_year": annual_degradation,
        "storage_end_of_life_capacity_ratio": end_of_life_ratio,
        "monthly_storage_revenue_breakdown": monthly_breakdown,
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


def _baseline_grid_profile(
    load_profile_kw: list[float],
    charging_profile_kw: list[float],
    thermal_electric_kw: list[float],
    pv_profile_kw: list[float],
    wind_profile_kw: list[float],
) -> list[float]:
    grid = []
    length = max(
        len(load_profile_kw),
        len(charging_profile_kw),
        len(thermal_electric_kw),
        len(pv_profile_kw),
        len(wind_profile_kw),
    )
    for hour in range(length):
        load = load_profile_kw[hour] if hour < len(load_profile_kw) else 0.0
        charging = charging_profile_kw[hour] if hour < len(charging_profile_kw) else 0.0
        thermal = thermal_electric_kw[hour] if hour < len(thermal_electric_kw) else 0.0
        pv = pv_profile_kw[hour] if hour < len(pv_profile_kw) else 0.0
        wind = wind_profile_kw[hour] if hour < len(wind_profile_kw) else 0.0
        grid.append(max(0.0, load + charging + thermal - pv - wind))
    return grid


def estimate_storage(data: dict[str, Any], charging_peak_kw: float = 0.0, thermal_coupling_kw: float = 0.0) -> dict[str, Any]:
    load = data.get("load_data", {})
    market = data.get("market_data", {})
    equipment = data.get("equipment", {}).get("storage", {})
    peak_load_kw = float(load.get("peak_load_kw") or 0.0)
    candidate_powers = [float(v) for v in equipment.get("power_candidate_kw") or []]
    candidate_energies = [float(v) for v in equipment.get("energy_candidate_kwh") or []]

    if candidate_powers:
        power_kw = candidate_powers[-1]  # 用最大的那个（直接取最后一个，而非硬算）
    else:
        base = peak_load_kw * 0.22 + charging_peak_kw * 0.35 + thermal_coupling_kw * 0.2
        if market.get("demand_charge_rule"):
            base *= 1.15
        power_kw = max(500.0, round(base, 0))
    if candidate_energies:
        energy_kwh = candidate_energies[-1]  # 用最大的那个
    else:
        energy_kwh = power_kw * 2.0

    rte = float(equipment.get("round_trip_efficiency") or 0.88)
    annual_discharge = power_kw * 0.55 * 365 / 1000
    annual_charge = annual_discharge / max(rte, 0.01)
    return {
        "storage_power_mw": round(power_kw / 1000, 3),
        "storage_energy_mwh": round(energy_kwh / 1000, 3),
        "annual_storage_charge_mwh": round(annual_charge, 2),
        "annual_storage_discharge_mwh": round(annual_discharge, 2),
    }


def settlement_and_finance(data: dict[str, Any], simulation: dict[str, Any], carbon: dict[str, Any]) -> dict[str, Any]:
    financial = data.get("financial", {})
    market = data.get("market_data", {})
    degradation = financial.get("degradation") or {}
    market_mode = str(market.get("market_mode") or "").lower()
    is_offgrid = market_mode == "offgrid_internal"
    is_ppa = market_mode == "ppa"
    # 从市场数据中提取平均电价和套利价差
    price_series_raw = [float(v) for v in (market.get("market_price_series") or [])]
    tou = market.get("tou_tariff") or []
    if price_series_raw:
        sorted_prices = sorted(price_series_raw)
        valley_price = sorted_prices[max(0, int(len(sorted_prices) * 0.25) - 1)]
        peak_price = sorted_prices[min(len(sorted_prices) - 1, int(len(sorted_prices) * 0.75))]
        avg_price = sum(price_series_raw) / len(price_series_raw)
        avg_spread = max(0.1, peak_price - valley_price)
    elif tou:
        prices = [float(item.get("price", 0.0)) for item in tou if item.get("price") is not None]
        avg_price = sum(prices) / len(prices) if prices else 0.72
        avg_spread = max(0.1, avg_price - 0.35)
    else:
        avg_price = 0.72
        avg_spread = 0.37

    charge_saving = 0.0
    pv_saving = 0.0
    wind_saving = 0.0
    annual_load = float(data.get("load_data", {}).get("annual_consumption_mwh") or 0.0)
    annual_grid_purchase = float(simulation.get("annual_grid_purchase_mwh") or 0.0)
    annual_pv = float(simulation.get("annual_pv_generation_mwh") or 0.0)
    annual_wind = float(simulation.get("annual_wind_generation_mwh") or 0.0)
    total_gen = annual_pv + annual_wind
    delivered_mwh = max(0.0, annual_load - annual_grid_purchase)

    if is_ppa:
        # PPA 模式：收益 = 实际供电量 × 购电协议电价
        ppa_price = float(market.get("ppa_price_per_kwh") or 0.0)
        total_savings = delivered_mwh * ppa_price * 1000  # MWh * RMB/kWh * 1000 = RMB
        if total_gen > 0:
            pv_saving = total_savings * (annual_pv / total_gen)
            wind_saving = total_savings * (annual_wind / total_gen)
        charge_saving = 0.0
    elif is_offgrid:
        # offgrid：收益 = 柴油替代节省量（燃料成本 × 被替代电量）
        fuel_cost = float(market.get("fuel_cost_per_kwh") or 0.0)
        total_savings = delivered_mwh * fuel_cost * 1000
        if total_gen > 0:
            pv_saving = total_savings * (annual_pv / total_gen)
            wind_saving = total_savings * (annual_wind / total_gen)
        charge_saving = 0.0
    else:
        charge_saving = float(simulation.get("annual_storage_discharge_mwh") or 0.0) * avg_spread * 1000
        pv_saving = float(simulation.get("annual_pv_generation_mwh") or 0.0) * avg_price * 0.78 * 1000
        wind_saving = float(simulation.get("annual_wind_generation_mwh") or 0.0) * avg_price * 0.72 * 1000
    charging_margin = float(simulation.get("annual_charging_energy_mwh") or 0.0) * 120
    thermal_saving = (float(simulation.get("annual_cooling_energy_mwh") or 0.0) + float(simulation.get("annual_heating_energy_mwh") or 0.0)) * 70
    carbon_value = float(carbon.get("annual_reduction_tco2e") or 0.0) * float(financial.get("carbon_price_assumption") or 0.0)
    annual_revenue = charge_saving + pv_saving + wind_saving + charging_margin + thermal_saving + carbon_value

    capex = financial.get("capex", {})
    storage_capex = (simulation.get("storage_energy_mwh") or 0.0) * 1000 * float(capex.get("storage_system_cost_per_kwh") or 850)
    pv_capex = (simulation.get("pv_mwp") or 0.0) * 1_000_000 * float(capex.get("pv_cost_per_w") or 3.2)
    wind_capex = (simulation.get("wind_mw") or 0.0) * 1_000_000 * float(capex.get("wind_cost_per_w") or 6.5)
    thermal_capex = float(capex.get("thermal_system_total") or 0.0)
    charging_capex = float(capex.get("charging_system_total") or 0.0)
    capex_total = storage_capex + pv_capex + wind_capex + thermal_capex + charging_capex
    opex_ratio = float((financial.get("opex") or {}).get("annual_om_ratio") or 0.015)
    opex_escalation_rate = float((financial.get("opex") or {}).get("annual_opex_escalation_rate") or 0.02)
    opex_annual = capex_total * opex_ratio
    storage_degradation = float(degradation.get("storage_capacity_fade_per_year") or 0.025)
    pv_degradation = float(degradation.get("pv_degradation_per_year") or 0.005)
    wind_degradation = float(degradation.get("wind_degradation_per_year") or 0.003)
    years = int(financial.get("project_years") or 15)
    discount_rate = float(financial.get("discount_rate") or 0.08)
    cycle_life = float((data.get("equipment", {}).get("storage", {}) or {}).get("cycle_life") or 6000.0)
    annual_fec = float(simulation.get("storage_equivalent_full_cycles_per_year") or 0.0)
    storage_life_years = (cycle_life / annual_fec) if annual_fec > 0 else None
    replacement_year = None
    replacement_cost = 0.0
    if storage_life_years and storage_life_years < years:
        replacement_year = max(1, min(years, int(round(storage_life_years))))
        replacement_cost = storage_capex * float((financial.get("capex") or {}).get("storage_replacement_cost_ratio") or 0.55)

    cashflows = [-capex_total]
    running_cum = -capex_total
    payback = None
    for year in range(1, years + 1):
        storage_factor = max(0.0, 1.0 - storage_degradation * (year - 1))
        pv_factor = max(0.0, 1.0 - pv_degradation * (year - 1))
        wind_factor = max(0.0, 1.0 - wind_degradation * (year - 1))
        year_revenue = (
            charge_saving * storage_factor
            + pv_saving * pv_factor
            + wind_saving * wind_factor
            + charging_margin
            + thermal_saving
            + carbon_value
        )
        year_opex = opex_annual * ((1 + opex_escalation_rate) ** (year - 1))
        year_capex = replacement_cost if replacement_year and year == replacement_year else 0.0
        year_cashflow = year_revenue - year_opex - year_capex
        cashflows.append(year_cashflow)
        running_cum += year_cashflow
        if payback is None and running_cum >= 0:
            payback = float(year)

    # ── 中国税法调整 ───────────────────────────────────────────────
    tax_cfg = financial.get("tax", {})
    # 海外项目自动跳过中国税法
    province = str(data.get("project_info", {}).get("province") or "").lower()
    is_overseas = province in ("overseas", "海外")
    apply_tax = tax_cfg.get("enabled", not is_overseas)
    if apply_tax:
        vat_rate = float(tax_cfg.get("vat_rate", 0.13))
        cit_rate = float(tax_cfg.get("cit_rate", 0.25))
        surcharge_rate = float(tax_cfg.get("surcharge_rate", 0.12))
        dep_pv = int(tax_cfg.get("dep_years_pv", 20))
        dep_wind = int(tax_cfg.get("dep_years_wind", 20))
        dep_storage = int(tax_cfg.get("dep_years_storage", 12))
        residual = float(tax_cfg.get("residual_ratio", 0.05))
        cit_free = int(tax_cfg.get("cit_exemption_years", 3))
        cit_half = int(tax_cfg.get("cit_halved_years", 3))
        invest_mode = str(tax_cfg.get("investment_mode", "self")).lower()
        share_ratio = float(tax_cfg.get("revenue_share_ratio", 1.0))

        # 折旧计算（直线法）
        annual_dep = 0.0
        for asset, cost, dep_y in [
            ("pv", pv_capex, dep_pv),
            ("wind", wind_capex, dep_wind),
            ("storage", storage_capex, dep_storage),
        ]:
            if cost > 0 and dep_y > 0:
                annual_dep += cost * (1 - residual) / dep_y

        # 进项增值税（一次性在首年抵扣）
        input_vat = capex_total * vat_rate
        tax_credit = input_vat  # 留抵税额

        after_tax = [cashflows[0]]  # Year 0 CAPEX unchanged
        running_cum_at = cashflows[0]
        payback_at = None

        for year in range(1, years + 1):
            rev = cashflows[year] + opex_annual * ((1 + opex_escalation_rate) ** (year - 1))
            y_opex = opex_annual * ((1 + opex_escalation_rate) ** (year - 1))

            # 销项增值税
            output_vat = rev * vat_rate if rev > 0 else 0.0
            # 运维进项（仅运维成本的小部分有增值税）
            maint_input_vat = y_opex * vat_rate * 0.3
            net_vat = max(0.0, output_vat - maint_input_vat)
            # 消抵扣留抵
            if tax_credit > 0:
                deduction = min(tax_credit, net_vat)
                net_vat -= deduction
                tax_credit -= deduction

            # 城建税+教育费
            surcharge = net_vat * surcharge_rate

            # 折旧抵税
            dep_deduction = annual_dep

            # 应税所得
            taxable = max(0.0, rev - y_opex - dep_deduction)
            # 三免三减半
            if year <= cit_free:
                cit = 0.0
            elif year <= cit_free + cit_half:
                cit = taxable * cit_rate * 0.5
            else:
                cit = taxable * cit_rate

            # 投资模式调整
            if invest_mode == "third_party":
                rev = rev * share_ratio
                cit = cit * share_ratio
                # 第三方投资模式下，进项税也在投资方账上

            year_at = rev - y_opex - surcharge - cit - (cashflows[year] - rev + y_opex)
            after_tax.append(year_at)
            running_cum_at += year_at
            if payback_at is None and running_cum_at >= 0:
                payback_at = float(year)

        # 用税后现金流重算 IRR 和 NPV
        irr = _calc_irr(after_tax)
        npv = 0.0
        for yr, cf in enumerate(after_tax):
            npv += cf / ((1 + discount_rate) ** yr)
        payback = payback_at
        cashflows = after_tax

    net_annual = cashflows[1] if len(cashflows) > 1 else 0.0
    irr = _calc_irr(cashflows) if not apply_tax else irr
    npv = 0.0
    for year, cashflow in enumerate(cashflows):
        npv += cashflow / ((1 + discount_rate) ** year)
    abatement_cost = None
    if carbon.get("annual_reduction_tco2e"):
        lifetime_reduction = carbon["annual_reduction_tco2e"] * years
        if lifetime_reduction > 0:
            lifetime_cost = capex_total + replacement_cost + sum(opex_annual * ((1 + opex_escalation_rate) ** (year - 1)) for year in range(1, years + 1))
            lifetime_revenue = sum(cashflows[1:]) + replacement_cost + sum(opex_annual * ((1 + opex_escalation_rate) ** (year - 1)) for year in range(1, years + 1))
            abatement_cost = max(0.0, (lifetime_cost - lifetime_revenue) / lifetime_reduction)

    # LCOE/LCOS
    _gen = float(simulation.get("annual_pv_generation_mwh") or 0.0) + float(simulation.get("annual_wind_generation_mwh") or 0.0)
    _dis = float(simulation.get("annual_storage_discharge_mwh") or 0.0)
    _lcoe_val = None
    _lcos_val = None
    if _gen > 0 and years > 0:
        _lg = sum(_gen * max(0.0, 1.0 - pv_degradation * (y-1)) for y in range(1, years+1))
        _lc = capex_total + replacement_cost + sum(opex_annual * ((1+opex_escalation_rate)**(y-1)) for y in range(1, years+1))
        _lcoe_val = _lc / (_lg * 1000) if _lg > 0 else None
    if _dis > 0 and years > 0:
        _ld = sum(_dis * max(0.0, 1.0 - storage_degradation * (y-1)) for y in range(1, years+1))
        _ss = storage_capex / capex_total if capex_total > 0 else 0.0
        _slc = storage_capex + replacement_cost + sum(opex_annual * _ss * ((1+opex_escalation_rate)**(y-1)) for y in range(1, years+1))
        _lcos_val = _slc / (_ld * 1000) if _ld > 0 else None

    # ── 补充财务指标 ────────────────────────────────────────────────
    # 动态回收期（折现现金流累计回正年份）
    cum_disc = -capex_total
    dyn_payback = None
    for y in range(1, years + 1):
        cf = cashflows[y] if y < len(cashflows) else 0.0
        cum_disc += cf / ((1 + discount_rate) ** y)
        if dyn_payback is None and cum_disc >= 0:
            dyn_payback = float(y)

    # ROI / ROE
    avg_annual_profit = sum(cashflows[1:]) / years if years > 0 else 0
    roi = avg_annual_profit / capex_total if capex_total > 0 else None
    equity_total = capex_total * (1 - float(financial.get("debt_ratio", 0.7)))
    roe = avg_annual_profit / equity_total if equity_total > 0 else None

    # 盈亏平衡电价（令 NPV=0 的电价倍率）
    if irr and irr > 0:
        be_price_factor = (1 + discount_rate) ** years / ((1 + irr) ** years) if irr > 0 else None
    else:
        be_price_factor = None

    # ── 融资结构分析（银行贷款 or 融资租赁）────────────────────────
    fin_mode = str(financial.get("financing_mode", "loan")).lower()
    debt_ratio = float(financial.get("debt_ratio", 0.7))
    loan_rate = float(financial.get("loan_rate", 0.045))
    loan_term = int(financial.get("loan_term", min(10, years)))
    total_loan = capex_total * debt_ratio
    equity_invest = capex_total * (1 - debt_ratio)
    annual_principal = total_loan / loan_term if loan_term > 0 else 0.0

    equity_cashflows = [-equity_invest]
    outstanding = total_loan
    dscr_values = []
    for y in range(1, years + 1):
        cf = cashflows[y] if y < len(cashflows) else 0.0
        if fin_mode == "lease":
            # 融资租赁：年租金属性固定，利息部分可抵税
            lease_pmt = total_loan * loan_rate * (1 + loan_rate)**loan_term / ((1+loan_rate)**loan_term - 1) if loan_term > 0 else 0.0
            interest = outstanding * loan_rate
            principal_portion = lease_pmt - interest
            debt_service = lease_pmt
            outstanding -= principal_portion
        else:
            interest = outstanding * loan_rate
            principal = min(annual_principal, outstanding)
            debt_service = interest + principal
            outstanding -= principal
        # 利息抵税
        tax_shield = interest * cit_rate * 0.25 if apply_tax else 0.0
        equity_cf = cf - debt_service + tax_shield
        equity_cashflows.append(equity_cf)
        if debt_service > 0:
            dscr_values.append(cf / debt_service)

    # 残值回收（项目结束时）
    residual_value = capex_total * float(financial.get("residual_value_ratio", 0.05))
    if residual_value > 0:
        equity_cashflows[-1] += residual_value
    debt_ratio = float(financial.get("debt_ratio", 0.7))
    loan_rate = float(financial.get("loan_rate", 0.045))
    loan_term = int(financial.get("loan_term", min(10, years)))
    total_loan = capex_total * debt_ratio
    equity_invest = capex_total * (1 - debt_ratio)
    annual_principal = total_loan / loan_term if loan_term > 0 else 0.0
    equity_cashflows = [-equity_invest]
    outstanding = total_loan
    dscr_values = []
    for y in range(1, years + 1):
        cf = cashflows[y] if y < len(cashflows) else 0.0
        interest = outstanding * loan_rate
        principal = min(annual_principal, outstanding)
        debt_service = interest + principal
        tax_shield = interest * cit_rate * 0.25 if apply_tax else 0.0
        equity_cf = cf - debt_service + tax_shield
        equity_cashflows.append(equity_cf)
        outstanding -= principal
        if debt_service > 0:
            dscr_values.append(cf / debt_service)
    equity_irr = _calc_irr(equity_cashflows)
    equity_npv_val = sum(cf / ((1 + discount_rate) ** y) for y, cf in enumerate(equity_cashflows))
    dscr_min = min(dscr_values) if dscr_values else None

    return {
        "price_mechanism_summary": _describe_price_mode(market),
        "revenue_breakdown": _revenue_breakdown(charge_saving, pv_saving, wind_saving, charging_margin, thermal_saving, carbon_value),
        "annual_savings_or_revenue": round(annual_revenue, 2),
        "capex_total": round(capex_total, 2),
        "opex_annual": round(opex_annual, 2),
        "payback_years": round(payback, 2) if payback else None,
        "irr": round(irr, 4) if irr is not None else None,
        "npv": round(npv, 2),
        "abatement_cost_per_tco2e": round(abatement_cost, 2) if abatement_cost is not None else None,
        "storage_replacement_year": replacement_year,
        "storage_replacement_cost": round(replacement_cost, 2) if replacement_cost else None,
        "opex_escalation_rate": opex_escalation_rate,
        "equity_irr": round(equity_irr, 4) if equity_irr is not None else None,
        "equity_npv": round(equity_npv_val, 2),
        "dscr_min": round(dscr_min, 3) if dscr_min is not None else None,
        "dyn_payback_years": round(dyn_payback, 2) if dyn_payback is not None else None,
        "roi": round(roi, 4) if roi is not None else None,
        "roe": round(roe, 4) if roe is not None else None,
        "breakeven_price_factor": round(be_price_factor, 4) if be_price_factor is not None else None,
        "lcoe": round(_lcoe_val, 4) if _lcoe_val is not None else None,
        "lcos": round(_lcos_val, 4) if _lcos_val is not None else None,
    }


def _calc_irr(cashflows: list[float], max_iter: int = 100, tolerance: float = 1e-7) -> float | None:
    """牛顿法求 IRR"""
    if not cashflows or cashflows[0] >= 0 or sum(float(v) for v in cashflows[1:]) <= 0:
        return None
    rate = 0.15  # 初始猜测
    for _ in range(max_iter):
        npv = 0.0
        dnpv = 0.0  # NPV 对 rate 的一阶导数
        for t, cf in enumerate(cashflows):
            denom = (1.0 + rate) ** t
            npv += cf / denom
            dnpv += -t * cf / (denom * (1.0 + rate))
        if abs(npv) < tolerance:
            return round(max(0.0, rate), 4)
        if abs(dnpv) < 1e-12:
            break
        rate -= npv / dnpv
        if rate < -0.99:
            return None
    return round(max(0.0, rate), 4) if abs(npv) < 0.01 else None


def _describe_price_mode(market: dict[str, Any]) -> str:
    mode = market.get("market_mode") or ""
    if mode:
        return mode
    if market.get("market_price_series"):
        return "market_price_series"
    if market.get("tou_tariff"):
        return "tou_tariff"
    return "unspecified"


def _revenue_breakdown(charge: float, pv: float, wind: float, charging: float, thermal: float, carbon: float) -> list[str]:
    items = []
    if charge > 0:
        items.append("储能节费/削峰收益")
    if pv > 0:
        items.append("光伏自发自用收益")
    if wind > 0:
        items.append("风电替代收益")
    if charging > 0:
        items.append("充电服务毛收益")
    if thermal > 0:
        items.append("冷热系统节费收益")
    if carbon > 0:
        items.append("碳减排价值")
    if pv > 0 and wind > 0 and charge == 0:
        # offgrid 模式下 pv 和 wind 的收益标签已改，这里不动显示
        pass
    return items


def estimate_carbon(data: dict[str, Any], simulation: dict[str, Any]) -> dict[str, Any]:
    carbon = data.get("carbon_data", {})
    baseline = carbon.get("baseline_emissions_tco2e")
    annual_grid_purchase = float(simulation.get("annual_grid_purchase_mwh") or 0.0)
    annual_pv = float(simulation.get("annual_pv_generation_mwh") or 0.0)
    annual_wind = float(simulation.get("annual_wind_generation_mwh") or 0.0)
    annual_heating = float(simulation.get("annual_heating_energy_mwh") or 0.0)
    green_power_ratio = safe_div(annual_pv + annual_wind, annual_grid_purchase + annual_pv + annual_wind) or 0.0

    if baseline is None:
        baseline = annual_grid_purchase * DEFAULT_GRID_EMISSION_FACTOR + annual_heating * DEFAULT_GAS_EMISSION_FACTOR * 0.18
    baseline = float(baseline)
    scope1_reduction = annual_heating * 0.06
    scope2_reduction = (annual_pv + annual_wind + float(simulation.get("annual_storage_discharge_mwh") or 0.0) * 0.15) * DEFAULT_GRID_EMISSION_FACTOR
    scope3_reduction = 0.0
    post_project = max(0.0, baseline - scope1_reduction - scope2_reduction - scope3_reduction)
    annual_reduction = baseline - post_project

    return {
        "baseline_emissions_tco2e": round(baseline, 2),
        "post_project_emissions_tco2e": round(post_project, 2),
        "annual_reduction_tco2e": round(annual_reduction, 2),
        "scope1_reduction_tco2e": round(scope1_reduction, 2),
        "scope2_reduction_tco2e": round(scope2_reduction, 2),
        "scope3_reduction_tco2e": round(scope3_reduction, 2),
        "green_power_coverage_ratio": round(clamp(green_power_ratio, 0.0, 1.0), 4),
        "claim_boundary_summary": (
            carbon.get("carbon_claim_target")
            or "需按范围一/二边界、环境属性归属和外部核证要求进一步确认零碳声明边界"
        ),
        "carbon_path_breakdown": _carbon_path_breakdown(scope1_reduction, scope2_reduction),
    }


def _carbon_path_breakdown(scope1_reduction: float, scope2_reduction: float) -> list[dict[str, Any]]:
    total = scope1_reduction + scope2_reduction
    if total <= 0:
        return []
    return [
        {"path": "工艺/热源替代与能效提升", "reduction_tco2e": round(scope1_reduction, 2), "share": round(scope1_reduction / total, 4)},
        {"path": "绿电/光伏/储能替代购电排放", "reduction_tco2e": round(scope2_reduction, 2), "share": round(scope2_reduction / total, 4)},
    ]


def assemble_design_notes(data: dict[str, Any], profile: dict[str, Any] | None, scenario: str, charging_peak_kw: float) -> dict[str, Any]:
    project = data.get("project_info", {})
    network = data.get("network_and_design", {})
    notes = [
        f"建议按 {project.get('grid_connection_mode') or '项目实际接入方式'} 复核接入边界。",
        "需复核变压器余量、保护配合、计量边界和防逆流要求。",
    ]
    if charging_peak_kw > 0:
        notes.append("充电场站场景需专项复核容量电费风险和有序充电策略。")
    if scenario == "zero_carbon_factory":
        notes.append("零碳工厂场景需同步复核工艺用能、冷热系统和碳核算边界。")
    if profile:
        notes.append(f"已命中省级 profile：{profile.get('province_name')} / {profile.get('verification_status')}")
    return {
        "recommended_voltage_level_kv": project.get("voltage_level_kv"),
        "recommended_connection_mode": project.get("grid_connection_mode") or "",
        "primary_system_notes": notes,
        "secondary_system_notes": [
            "需明确 EMS/PCS/BMS 或冷热控制系统与站控层接口。",
            "如参与市场或聚合控制，需明确通信与调度边界。",
        ],
        "required_studies": [
            "接入容量校核",
            "典型日或逐时负荷仿真",
        ],
        "required_approvals": [
            "内部立项/技术审查",
            "接入方案复核",
        ],
    }
