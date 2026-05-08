from __future__ import annotations

from typing import Any

from .sizing import _renewable_charge_threshold_price_for_step
from .finance import _append_market_daily_cycle_schedule, _build_market_cooptimization_daily_plan

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

    valley = valley_hours or {0, 1, 2, 3, 4, 5, 23}  # Default night valley hours for Chinese TOU schedules.
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
            charge_kw = min(power_kw, (soc_max - soc_kwh) / 1.0, headroom)
            soc_kwh += charge_kw
            net += charge_kw
            charged += charge_kw
        elif hour not in valley and net > target_peak and soc_kwh > soc_min:
            discharge_kw = min(power_kw, (soc_kwh - soc_min) / 1.0, max(0.0, net - target_peak))
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


# NOTE: simulate_storage_dispatch_annual is ~380 lines, covering dispatch simulation, strategy decision,
# output aggregation, and finance reconciliation. Section markers below identify logical phases.
# Future refactoring: extract dispatch strategy functions and simplify the result builder.
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
    market: dict[str, Any] | None = None,
    operation_mode: str = "",
) -> dict[str, Any]:
    storage_config = storage_config or {}
    market = market or {}
    interval_hours = (8760.0 / len(load_series_kw)) if load_series_kw else 1.0
    if not storage_power_mw or not storage_energy_mwh:
        baseline = _baseline_grid_profile(load_series_kw, charging_series_kw, thermal_series_kw, pv_series_kw, wind_series_kw)
        annual_purchase = sum(baseline) * interval_hours / 1000
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
    else:
        percentile = 0.82
    target_peak = sorted(positive)[int(len(positive) * percentile)] if positive else 0.0
    valley_threshold = min(target_peak * (0.62 if strategy_mode == "arbitrage" else 0.55), (sum(positive) / len(positive)) if positive else target_peak)
    grid = []
    charged = 0.0
    discharged = 0.0
    renewable_charged = 0.0
    renewable_to_storage = 0.0
    renewable_to_load = 0.0
    grid_to_load = 0.0
    grid_to_storage = 0.0
    renewable_exported = 0.0
    storage_exported = 0.0
    curtailed_renewable = 0.0
    price_series = price_series or [0.72] * len(baseline)
    month_hours = [31 * 24, 28 * 24, 31 * 24, 30 * 24, 31 * 24, 30 * 24, 31 * 24, 31 * 24, 30 * 24, 31 * 24, 30 * 24, 31 * 24]
    month_steps = [max(1, int(round(hours / max(interval_hours, 1e-9)))) for hours in month_hours]
    monthly_charge = [0.0] * 12
    monthly_discharge = [0.0] * 12
    monthly_margin = [0.0] * 12
    max_daily_cycles = float(storage_config.get("max_daily_cycles") or (2.0 if strategy_mode == "market_responding" else 0.0))
    max_annual_cycles = float(storage_config.get("max_annual_cycles") or 0.0)
    explicit_charge_hours = {int(v) for v in (market.get("storage_charge_hours") or []) if isinstance(v, (int, float))}
    explicit_discharge_hours = {int(v) for v in (market.get("storage_discharge_hours") or []) if isinstance(v, (int, float))}
    steps_per_day = max(1, int(round(24 / max(interval_hours, 1e-9))))
    month_idx = 0
    next_month_cutoff = month_steps[0]
    daily_charged = 0.0
    daily_discharged = 0.0
    allow_export = bool(market.get("allow_export_to_grid"))
    coopt_daily_plan: dict[str, Any] | None = None
    coopt_day_started_discharge = False
    market_daily_cycle_schedule: list[dict[str, Any]] = []
    current_day_charge_energy_kwh = [0.0] * steps_per_day
    current_day_discharge_energy_kwh = [0.0] * steps_per_day
    current_day_renewable_charge_kwh = [0.0] * steps_per_day
    current_day_grid_charge_kwh = [0.0] * steps_per_day
    current_day_charge_prices = [0.0] * steps_per_day
    current_day_discharge_prices = [0.0] * steps_per_day
    for idx, base in enumerate(baseline):
        if idx >= next_month_cutoff and month_idx < 11:
            month_idx += 1
            next_month_cutoff += month_steps[month_idx]
        hour = int((idx % steps_per_day) * interval_hours) % 24
        if idx % steps_per_day == 0:
            if idx > 0 and operation_mode in {"renewable_market_cooptimization", "renewable_export_oriented"}:
                _append_market_daily_cycle_schedule(
                    market_daily_cycle_schedule,
                    day_index=(idx // steps_per_day),
                    interval_hours=interval_hours,
                    charge_energy_kwh=current_day_charge_energy_kwh,
                    discharge_energy_kwh=current_day_discharge_energy_kwh,
                    renewable_charge_kwh=current_day_renewable_charge_kwh,
                    grid_charge_kwh=current_day_grid_charge_kwh,
                    charge_prices=current_day_charge_prices,
                    discharge_prices=current_day_discharge_prices,
                )
            daily_charged = 0.0
            daily_discharged = 0.0
            coopt_day_started_discharge = False
            coopt_daily_plan = None
            current_day_charge_energy_kwh = [0.0] * steps_per_day
            current_day_discharge_energy_kwh = [0.0] * steps_per_day
            current_day_renewable_charge_kwh = [0.0] * steps_per_day
            current_day_grid_charge_kwh = [0.0] * steps_per_day
            current_day_charge_prices = [0.0] * steps_per_day
            current_day_discharge_prices = [0.0] * steps_per_day
        price = price_series[idx] if idx < len(price_series) else 0.72
        day_start = (idx // steps_per_day) * steps_per_day
        day_slice = price_series[day_start : day_start + steps_per_day] or [0.72]
        sorted_day_prices = sorted(day_slice)
        cheap_threshold = sorted_day_prices[max(0, int(len(sorted_day_prices) * 0.25) - 1)]
        expensive_threshold = sorted_day_prices[min(len(sorted_day_prices) - 1, int(len(sorted_day_prices) * 0.75))]
        renewable_kw = (pv_series_kw[idx] if idx < len(pv_series_kw) else 0.0) + (wind_series_kw[idx] if idx < len(wind_series_kw) else 0.0)
        load_kw = (
            (load_series_kw[idx] if idx < len(load_series_kw) else 0.0)
            + (charging_series_kw[idx] if idx < len(charging_series_kw) else 0.0)
            + (thermal_series_kw[idx] if idx < len(thermal_series_kw) else 0.0)
        )
        renewable_surplus = max(0.0, renewable_kw - load_kw)
        if operation_mode in {"renewable_market_cooptimization", "renewable_export_oriented"}:
            if coopt_daily_plan is None:
                coopt_daily_plan = _build_market_cooptimization_daily_plan(
                    day_prices=day_slice,
                    interval_hours=interval_hours,
                    power_mw=power_kw / 1000.0,
                    energy_mwh=energy_kwh / 1000.0,
                    threshold_price=float(
                        market.get("renewable_charge_threshold_price_per_kwh")
                        or market.get("solar_lcoe_per_kwh")
                        or market.get("wind_lcoe_per_kwh")
                        or 0.35
                    ),
                    spread_margin=float(
                        market.get("cooptimization_min_sell_spread_per_kwh")
                        or market.get("min_sell_spread_per_kwh")
                        or 0.15
                    ),
                    min_charge_hours=max(2, int((market.get("arbitrage_plan") or {}).get("min_charge_hours") or 2)),
                    min_discharge_hours=max(2, int((market.get("arbitrage_plan") or {}).get("min_discharge_hours") or 2)),
                    max_charge_hours=max(2, int((market.get("arbitrage_plan") or {}).get("max_charge_hours") or 6)),
                    max_discharge_hours=max(2, int((market.get("arbitrage_plan") or {}).get("max_discharge_hours") or 6)),
                    effective_rte=effective_rte,
                    usable_depth=max(0.0, soc_max / max(energy_kwh, 1e-9) - soc_min / max(energy_kwh, 1e-9)),
                    discharge_path_eff=battery_discharge_eff * pcs_eff * transformer_eff,
                )
            charge_threshold = _renewable_charge_threshold_price_for_step(
                market=market,
                pv_kw=float(pv_series_kw[idx] if idx < len(pv_series_kw) else 0.0),
                wind_kw=float(wind_series_kw[idx] if idx < len(wind_series_kw) else 0.0),
            )
            spread_margin = float(
                market.get("cooptimization_min_sell_spread_per_kwh")
                or market.get("min_sell_spread_per_kwh")
                or 0.15
            )
            plan_step = min(idx % steps_per_day, len(coopt_daily_plan["charge_steps"]) - 1) if coopt_daily_plan["charge_steps"] else 0
            prioritize_renewable_to_storage = renewable_kw > 0 and (
                (plan_step < len(coopt_daily_plan["charge_steps"]) and coopt_daily_plan["charge_steps"][plan_step])
                or (price <= charge_threshold and coopt_daily_plan.get("future_peak_price", price) - price >= spread_margin)
            )
            step_hours = interval_hours
            charge_room_kw = max(0.0, min(power_kw, (soc_max - soc) / max(step_hours * battery_charge_eff, 1e-9)))
            renewable_to_storage_kw = min(renewable_kw, charge_room_kw) if prioritize_renewable_to_storage else 0.0
            remaining_renewable_kw = max(0.0, renewable_kw - renewable_to_storage_kw)
            renewable_to_load_kw = min(load_kw, remaining_renewable_kw)
            net = max(0.0, load_kw - renewable_to_load_kw)
            if renewable_to_storage_kw > 0:
                soc += renewable_to_storage_kw * step_hours * battery_charge_eff
                charged += renewable_to_storage_kw * step_hours
                daily_charged += renewable_to_storage_kw * step_hours
                monthly_charge[month_idx] += renewable_to_storage_kw * step_hours / 1000
                renewable_charged += renewable_to_storage_kw * step_hours
                renewable_to_storage += renewable_to_storage_kw * step_hours
                current_day_charge_energy_kwh[plan_step] += renewable_to_storage_kw * step_hours
                current_day_renewable_charge_kwh[plan_step] += renewable_to_storage_kw * step_hours
                current_day_charge_prices[plan_step] = price
            renewable_to_load += renewable_to_load_kw * step_hours
            grid_to_load += net * step_hours
            remaining_renewable_kw = max(0.0, remaining_renewable_kw - renewable_to_load_kw)
            additional_charge_room_kw = max(0.0, min(power_kw, (soc_max - soc) / max(step_hours * battery_charge_eff, 1e-9)))
            additional_renewable_to_storage_kw = min(remaining_renewable_kw, additional_charge_room_kw)
            if additional_renewable_to_storage_kw > 0:
                soc += additional_renewable_to_storage_kw * step_hours * battery_charge_eff
                charged += additional_renewable_to_storage_kw * step_hours
                daily_charged += additional_renewable_to_storage_kw * step_hours
                monthly_charge[month_idx] += additional_renewable_to_storage_kw * step_hours / 1000
                renewable_charged += additional_renewable_to_storage_kw * step_hours
                renewable_to_storage += additional_renewable_to_storage_kw * step_hours
                current_day_charge_energy_kwh[plan_step] += additional_renewable_to_storage_kw * step_hours
                current_day_renewable_charge_kwh[plan_step] += additional_renewable_to_storage_kw * step_hours
                current_day_charge_prices[plan_step] = price
                remaining_renewable_kw = max(0.0, remaining_renewable_kw - additional_renewable_to_storage_kw)
            exported_renewable_kw = remaining_renewable_kw if allow_export else 0.0
            renewable_exported += exported_renewable_kw * step_hours
            curtailed_renewable += max(0.0, remaining_renewable_kw - exported_renewable_kw) * step_hours
            should_charge = price < 0 and soc < soc_max
            if explicit_charge_hours:
                should_charge = should_charge or hour in explicit_charge_hours
            if should_charge:
                remaining_daily_charge = max(0.0, energy_kwh * max_daily_cycles - daily_charged) if max_daily_cycles > 0 else power_kw * step_hours
                grid_charge_kw = min(
                    power_kw,
                    max(0.0, (soc_max - soc) / max(step_hours * battery_charge_eff, 1e-9)),
                    remaining_daily_charge / max(step_hours, 1e-9),
                )
                if grid_charge_kw > 0:
                    soc += grid_charge_kw * step_hours * battery_charge_eff
                    charged += grid_charge_kw * step_hours
                    daily_charged += grid_charge_kw * step_hours
                    monthly_charge[month_idx] += grid_charge_kw * step_hours / 1000
                    grid_to_storage += grid_charge_kw * step_hours
                    net += grid_charge_kw
                    current_day_charge_energy_kwh[plan_step] += grid_charge_kw * step_hours
                    current_day_grid_charge_kwh[plan_step] += grid_charge_kw * step_hours
                    current_day_charge_prices[plan_step] = price
            should_discharge = (
                (
                    (plan_step < len(coopt_daily_plan["discharge_steps"]) and coopt_daily_plan["discharge_steps"][plan_step])
                    or price >= expensive_threshold
                    or (coopt_day_started_discharge and price > charge_threshold)
                    or net > target_peak
                )
                and soc > soc_min
            )
            if explicit_discharge_hours:
                should_discharge = should_discharge or hour in explicit_discharge_hours
            if should_discharge:
                target_cut = max(0.0, net)
                available_kw = (soc - soc_min) * battery_discharge_eff / max(step_hours, 1e-9)
                if max_daily_cycles > 0:
                    remaining_daily_discharge = max(0.0, energy_kwh * max_daily_cycles - daily_discharged)
                    available_kw = min(available_kw, remaining_daily_discharge / max(step_hours, 1e-9))
                if max_annual_cycles > 0:
                    remaining_annual_discharge = max(0.0, energy_kwh * max_annual_cycles - discharged)
                    available_kw = min(available_kw, remaining_annual_discharge / max(step_hours, 1e-9))
                discharge_kw = min(power_kw, available_kw, target_cut)
                if discharge_kw > 0:
                    soc -= discharge_kw * step_hours / max(battery_discharge_eff, 0.01)
                    net = max(0.0, net - discharge_kw * pcs_eff * transformer_eff)
                    discharged += discharge_kw * step_hours
                    daily_discharged += discharge_kw * step_hours
                    coopt_day_started_discharge = True
                    monthly_discharge[month_idx] += discharge_kw * step_hours / 1000
                    monthly_margin[month_idx] += discharge_kw * step_hours * price
                    current_day_discharge_energy_kwh[plan_step] += discharge_kw * step_hours
                    current_day_discharge_prices[plan_step] = price
            grid.append(max(0.0, net))
            continue
        net = base
        should_charge = (hour in {0, 1, 2, 3, 4, 5, 12, 13} and net < valley_threshold) or renewable_surplus > 0
        if strategy_mode == "market_responding":
            should_charge = should_charge or price <= cheap_threshold
        if explicit_charge_hours:
            should_charge = should_charge or hour in explicit_charge_hours
        if should_charge and soc < soc_max:
            headroom = max(0.0, valley_threshold - net)
            if strategy_mode == "market_responding":
                arbitrage_headroom = max(0.0, target_peak - net)
                charge_limit = max(headroom, renewable_surplus, arbitrage_headroom)
            else:
                charge_limit = max(headroom, renewable_surplus, power_kw)
            if max_daily_cycles > 0:
                remaining_daily_charge = max(0.0, energy_kwh * max_daily_cycles - daily_charged)
                charge_limit = min(charge_limit, remaining_daily_charge / interval_hours)
            charge_kw = min(power_kw, (soc_max - soc) / max(interval_hours * battery_charge_eff, 1e-9), charge_limit)
            soc += charge_kw * interval_hours * battery_charge_eff
            net += charge_kw
            charged += charge_kw * interval_hours
            daily_charged += charge_kw * interval_hours
            monthly_charge[month_idx] += charge_kw * interval_hours / 1000
            renewable_charged += min(charge_kw, renewable_surplus) * interval_hours
        should_discharge = net > target_peak
        if strategy_mode == "market_responding":
            should_discharge = should_discharge or price >= expensive_threshold
        if explicit_discharge_hours:
            should_discharge = should_discharge or hour in explicit_discharge_hours
        if should_discharge and soc > soc_min:
            target_cut = max(0.0, net - target_peak)
            if strategy_mode == "market_responding" and price >= expensive_threshold:
                target_cut = max(target_cut, power_kw * 0.55)
            available_kw = (soc - soc_min) * battery_discharge_eff / interval_hours
            if max_daily_cycles > 0:
                remaining_daily_discharge = max(0.0, energy_kwh * max_daily_cycles - daily_discharged)
                available_kw = min(available_kw, remaining_daily_discharge / interval_hours)
            if max_annual_cycles > 0:
                remaining_annual_discharge = max(0.0, energy_kwh * max_annual_cycles - discharged)
                available_kw = min(available_kw, remaining_annual_discharge / interval_hours)
            discharge_kw = min(power_kw, available_kw, target_cut)
            soc -= discharge_kw * interval_hours / max(battery_discharge_eff, 0.01)
            net -= discharge_kw * pcs_eff * transformer_eff
            discharged += discharge_kw * interval_hours
            daily_discharged += discharge_kw * interval_hours
            monthly_discharge[month_idx] += discharge_kw * interval_hours / 1000
            monthly_margin[month_idx] += discharge_kw * interval_hours * price
        grid.append(max(0.0, net))
    if operation_mode in {"renewable_market_cooptimization", "renewable_export_oriented"}:
        _append_market_daily_cycle_schedule(
            market_daily_cycle_schedule,
            day_index=max(0, len(grid) // steps_per_day),
            interval_hours=interval_hours,
            charge_energy_kwh=current_day_charge_energy_kwh,
            discharge_energy_kwh=current_day_discharge_energy_kwh,
            renewable_charge_kwh=current_day_renewable_charge_kwh,
            grid_charge_kwh=current_day_grid_charge_kwh,
            charge_prices=current_day_charge_prices,
            discharge_prices=current_day_discharge_prices,
        )
    annual_purchase = sum(grid) * interval_hours / 1000
    days = max(1.0, len(grid) * interval_hours / 24.0)
    daily_cycles = (discharged / energy_kwh) / days if energy_kwh > 0 else 0.0
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
        "annual_export_mwh": (renewable_exported + storage_exported) / 1000,
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
        "renewable_to_storage_mwh": renewable_to_storage / 1000,
        "renewable_to_load_mwh": renewable_to_load / 1000,
        "grid_to_load_mwh": grid_to_load / 1000,
        "grid_to_storage_mwh": grid_to_storage / 1000,
        "renewable_export_mwh": renewable_exported / 1000,
        "storage_export_mwh": storage_exported / 1000,
        "curtailed_renewable_mwh": curtailed_renewable / 1000,
        "storage_effective_round_trip_efficiency": effective_rte,
        "storage_reserved_soc_ratio": reserve_soc,
        "storage_backup_soc_ratio": backup_soc,
        "storage_degradation_per_year": annual_degradation,
        "storage_end_of_life_capacity_ratio": end_of_life_ratio,
        "daily_cycle_schedule": market_daily_cycle_schedule,
        "monthly_storage_revenue_breakdown": monthly_breakdown,
        "storage_market_value": sum(monthly_margin),
    }


def _baseline_grid_profile(
    load_profile_kw: list[float],
    charging_profile_kw: list[float],
    thermal_electric_kw: list[float],
    pv_profile_kw: list[float],
    wind_profile_kw: list[float],
) -> list[float]:
    grid = []
    horizon = max(
        len(load_profile_kw),
        len(charging_profile_kw),
        len(thermal_electric_kw),
        len(pv_profile_kw),
        len(wind_profile_kw),
    )
    for hour in range(horizon):
        load = (load_profile_kw[hour] if hour < len(load_profile_kw) else 0.0)
        charging = (charging_profile_kw[hour] if hour < len(charging_profile_kw) else 0.0)
        thermal = (thermal_electric_kw[hour] if hour < len(thermal_electric_kw) else 0.0)
        pv = (pv_profile_kw[hour] if hour < len(pv_profile_kw) else 0.0)
        wind = (wind_profile_kw[hour] if hour < len(wind_profile_kw) else 0.0)
        grid.append(max(0.0, load + charging + thermal - pv - wind))
    return grid


