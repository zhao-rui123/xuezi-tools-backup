from __future__ import annotations

import math
from typing import Any

from .utils import _default_arbitrage_usable_depth, _owner_share_ratio
from .cycles import _materialize_rule_based_cycles, _materialize_rule_based_month_templates, infer_cycles_from_monthly_tou_history

def simulate_rule_based_arbitrage(
    data: dict[str, Any],
    storage: dict[str, Any],
) -> dict[str, Any] | None:
    market = data.get("market_data", {}) or {}
    plan = market.get("arbitrage_plan") or {}
    if str(plan.get("mode") or "").lower() != "rule_based":
        return None
    cycles = _materialize_rule_based_cycles(market, plan, storage)
    monthly_templates = _materialize_rule_based_month_templates(market, plan, storage)
    if not cycles and not monthly_templates:
        return None

    storage_cfg = data.get("equipment", {}).get("storage", {}) or {}
    energy_kwh = float((storage.get("storage_energy_mwh") or 0.0) * 1000)
    cycle_life = float(storage_cfg.get("cycle_life") or 6000.0)
    annual_degradation = float(storage_cfg.get("annual_degradation_rate") or 0.025)
    prices = {str(item.get("period")): float(item.get("price", 0.0)) for item in (market.get("tou_tariff") or [])}
    if not prices:
        return None

    charge_eff = float(storage_cfg.get("battery_charge_efficiency") or 0.96)
    discharge_eff = float(storage_cfg.get("battery_discharge_efficiency") or 0.96)
    pcs_eff = float(storage_cfg.get("pcs_efficiency") or 0.98)
    transformer_eff = float(storage_cfg.get("transformer_efficiency") or 0.99)
    charge_path_eff = charge_eff * pcs_eff * transformer_eff
    discharge_path_eff = discharge_eff * pcs_eff * transformer_eff
    effective_rte = charge_eff * discharge_eff * pcs_eff * transformer_eff
    usable_depth = _default_arbitrage_usable_depth(storage_cfg)
    revenue_share_ratio = _owner_share_ratio(plan)

    annual_charge_kwh = 0.0
    annual_discharge_kwh = 0.0
    annual_margin = 0.0
    annual_charge_cost = 0.0
    annual_discharge_value = 0.0
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    monthly_charge = [0.0] * 12
    monthly_discharge = [0.0] * 12
    monthly_margin = [0.0] * 12

    if monthly_templates:
        for month_idx, template in enumerate(monthly_templates):
            month_cycles = template.get("cycles") or []
            active_days = float(template.get("active_days") or 0.0)
            if active_days <= 0 or not month_cycles:
                continue
            month_charge_kwh = 0.0
            month_discharge_kwh = 0.0
            month_margin = 0.0
            month_charge_cost = 0.0
            month_discharge_value = 0.0

            for cycle in month_cycles:
                charge_period = str(cycle.get("charge_period") or "valley")
                discharge_period = str(cycle.get("discharge_period") or "peak")
                charge_price = float(cycle.get("charge_price") if cycle.get("charge_price") is not None else prices.get(charge_period, 0.0))
                discharge_price = float(cycle.get("discharge_price") if cycle.get("discharge_price") is not None else prices.get(discharge_period, 0.0))
                discharge_energy_kwh = float(cycle.get("discharge_energy_kwh") or 0.0)
                charge_energy_kwh = float(cycle.get("charge_energy_kwh") or 0.0)

                if discharge_energy_kwh <= 0 and energy_kwh > 0:
                    discharge_energy_kwh = energy_kwh * usable_depth * discharge_path_eff
                if charge_energy_kwh <= 0 and discharge_energy_kwh > 0 and effective_rte > 0:
                    charge_energy_kwh = discharge_energy_kwh / effective_rte
                if charge_energy_kwh <= 0 or discharge_energy_kwh <= 0:
                    continue

                cycle_margin = discharge_energy_kwh * discharge_price - charge_energy_kwh * charge_price
                month_charge_kwh += charge_energy_kwh * active_days
                month_discharge_kwh += discharge_energy_kwh * active_days
                month_charge_cost += charge_energy_kwh * charge_price * active_days
                month_discharge_value += discharge_energy_kwh * discharge_price * active_days
                month_margin += cycle_margin * active_days

            annual_charge_kwh += month_charge_kwh
            annual_discharge_kwh += month_discharge_kwh
            annual_charge_cost += month_charge_cost
            annual_discharge_value += month_discharge_value
            annual_margin += month_margin
            monthly_charge[month_idx] = month_charge_kwh / 1000
            monthly_discharge[month_idx] = month_discharge_kwh / 1000
            monthly_margin[month_idx] = month_margin
    else:
        total_days = sum(month_days)
        for cycle in cycles:
            days = float(cycle.get("days_per_year") or cycle.get("days") or 0.0)
            if days <= 0:
                continue
            charge_period = str(cycle.get("charge_period") or "valley")
            discharge_period = str(cycle.get("discharge_period") or "peak")
            charge_price = float(cycle.get("charge_price") if cycle.get("charge_price") is not None else prices.get(charge_period, 0.0))
            discharge_price = float(cycle.get("discharge_price") if cycle.get("discharge_price") is not None else prices.get(discharge_period, 0.0))
            discharge_energy_kwh = float(cycle.get("discharge_energy_kwh") or 0.0)
            charge_energy_kwh = float(cycle.get("charge_energy_kwh") or 0.0)

            if discharge_energy_kwh <= 0 and energy_kwh > 0:
                discharge_energy_kwh = energy_kwh * usable_depth * discharge_path_eff
            if charge_energy_kwh <= 0 and discharge_energy_kwh > 0 and effective_rte > 0:
                charge_energy_kwh = discharge_energy_kwh / effective_rte
            if charge_energy_kwh <= 0 or discharge_energy_kwh <= 0:
                continue

            cycle_margin = discharge_energy_kwh * discharge_price - charge_energy_kwh * charge_price
            annual_charge_kwh += charge_energy_kwh * days
            annual_discharge_kwh += discharge_energy_kwh * days
            annual_charge_cost += charge_energy_kwh * charge_price * days
            annual_discharge_value += discharge_energy_kwh * discharge_price * days
            annual_margin += cycle_margin * days

            for month_idx, month_day in enumerate(month_days):
                month_share = month_day / total_days
                monthly_charge[month_idx] += charge_energy_kwh * days * month_share / 1000
                monthly_discharge[month_idx] += discharge_energy_kwh * days * month_share / 1000
                monthly_margin[month_idx] += cycle_margin * days * month_share

    annual_margin *= revenue_share_ratio
    annual_charge_mwh = annual_charge_kwh / 1000
    annual_discharge_mwh = annual_discharge_kwh / 1000
    annual_fec = annual_discharge_kwh / energy_kwh if energy_kwh > 0 else 0.0
    storage_life_years = (cycle_life / annual_fec) if annual_fec > 0 else None
    end_of_life_ratio = max(0.0, 1.0 - annual_degradation * min(storage_life_years or 0.0, 20.0)) if storage_life_years else None

    return {
        "annual_charge_mwh": round(annual_charge_mwh, 3),
        "annual_discharge_mwh": round(annual_discharge_mwh, 3),
        "annual_gross_margin": round(annual_margin, 2),
        "annual_charge_cost": round(annual_charge_cost, 2),
        "annual_discharge_value": round(annual_discharge_value, 2),
        "annual_fec": round(annual_fec, 3),
        "daily_cycles": round(annual_fec / 365, 3) if annual_fec else 0.0,
        "storage_life_years_estimate": round(storage_life_years, 2) if storage_life_years else None,
        "storage_end_of_life_capacity_ratio": end_of_life_ratio,
        "monthly_storage_revenue_breakdown": [
            {
                "month": idx + 1,
                "charge_mwh": round(monthly_charge[idx], 3),
                "discharge_mwh": round(monthly_discharge[idx], 3),
                "gross_margin": round(monthly_margin[idx], 2),
            }
            for idx in range(12)
        ],
    }


def simulate_commercial_hybrid_value(
    data: dict[str, Any],
    renewables: dict[str, Any],
    storage: dict[str, Any],
) -> dict[str, Any] | None:
    plan = (data.get("market_data", {}) or {}).get("commercial_hybrid_plan") or {}
    mode = str(plan.get("mode") or "").lower()
    if mode not in {"mode_a", "mode_b"}:
        return None

    storage_cfg = data.get("equipment", {}).get("storage", {}) or {}
    pv_generation_mwh = float(renewables.get("annual_pv_generation_mwh") or 0.0)
    storage_energy_mwh = float(storage.get("storage_energy_mwh") or 0.0)
    storage_power_mw = float(storage.get("storage_power_mw") or 0.0)
    if pv_generation_mwh <= 0 or storage_energy_mwh <= 0 or storage_power_mw <= 0:
        return None

    high_price = float(plan.get("high_price") or 0.0)
    if high_price <= 0:
        return None
    low_price = float(plan.get("low_price") or 0.0)
    self_use_price = float(plan.get("self_use_price") or high_price)
    sell_discount = float(plan.get("sell_discount") or 1.0)
    high_window_hours_per_day = float(plan.get("high_window_hours_per_day") or 2.0)
    operating_days = float(plan.get("operating_days_per_year") or 365.0)
    annual_usable_discharge_mwh = float(plan.get("annual_usable_discharge_mwh") or 0.0)
    annual_charge_mwh = float(plan.get("annual_charge_mwh") or 0.0)
    annual_discharge_mwh = float(plan.get("annual_discharge_mwh") or 0.0)
    demand_control_kw = float(plan.get("demand_control_kw") or 0.0)
    demand_rate_per_kw_month = float(plan.get("demand_rate_per_kw_month") or 0.0)
    demand_capture_ratio = float(plan.get("demand_capture_ratio") or 1.0)
    vpp_price_per_mwh = float(plan.get("vpp_price_per_mwh") or 0.0)
    vpp_duration_hours = float(plan.get("vpp_duration_hours") or 0.0)
    vpp_times_per_year = float(plan.get("vpp_times_per_year") or 0.0)
    vpp_effective_ratio = float(plan.get("vpp_effective_ratio") or 1.0)
    vpp_project_share = float(plan.get("vpp_project_share") or 1.0)
    revenue_share_ratio = _owner_share_ratio(plan)

    charge_eff = float(storage_cfg.get("battery_charge_efficiency") or 0.96)
    discharge_eff = float(storage_cfg.get("battery_discharge_efficiency") or 0.96)
    pcs_eff = float(storage_cfg.get("pcs_efficiency") or 0.98)
    transformer_eff = float(storage_cfg.get("transformer_efficiency") or 0.99)
    effective_rte = charge_eff * discharge_eff * pcs_eff * transformer_eff
    usable_depth = _default_arbitrage_usable_depth(storage_cfg)
    deliverable_power_mw = min(storage_power_mw, storage_energy_mwh * usable_depth * discharge_eff * pcs_eff * transformer_eff / max(high_window_hours_per_day, 1e-9))

    if annual_discharge_mwh <= 0:
        annual_discharge_mwh = min(
            pv_generation_mwh * effective_rte,
            deliverable_power_mw * high_window_hours_per_day * operating_days,
        )
    if annual_charge_mwh <= 0:
        annual_charge_mwh = annual_discharge_mwh / max(effective_rte, 1e-9)
    if annual_usable_discharge_mwh <= 0:
        annual_usable_discharge_mwh = annual_discharge_mwh

    sold_energy_mwh = min(annual_usable_discharge_mwh, annual_discharge_mwh)
    if mode == "mode_a":
        energy_value = sold_energy_mwh * high_price * sell_discount * 1000
    else:
        self_used_mwh = min(pv_generation_mwh, sold_energy_mwh)
        arbitrage_mwh = max(0.0, sold_energy_mwh - self_used_mwh)
        energy_value = self_used_mwh * self_use_price * 1000 + arbitrage_mwh * max(high_price * sell_discount - low_price, 0.0) * 1000

    demand_value = demand_control_kw * demand_rate_per_kw_month * 12 * demand_capture_ratio
    vpp_available_mw = min(deliverable_power_mw, float(plan.get("vpp_available_power_mw") or deliverable_power_mw))
    vpp_value = vpp_available_mw * vpp_duration_hours * vpp_times_per_year * vpp_price_per_mwh * vpp_effective_ratio * vpp_project_share

    annual_margin = (energy_value + demand_value + vpp_value) * revenue_share_ratio
    annual_fec = annual_discharge_mwh / max(storage_energy_mwh, 1e-9)
    cycle_life = float(storage_cfg.get("cycle_life") or 6000.0)
    annual_degradation = float(storage_cfg.get("annual_degradation_rate") or 0.025)
    storage_life_years = (cycle_life / annual_fec) if annual_fec > 0 else None
    end_of_life_ratio = max(0.0, 1.0 - annual_degradation * min(storage_life_years or 0.0, 20.0)) if storage_life_years else None

    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    total_days = sum(month_days)
    monthly_breakdown = []
    for idx, days_in_month in enumerate(month_days):
        share = days_in_month / total_days
        monthly_breakdown.append(
            {
                "month": idx + 1,
                "charge_mwh": round(annual_charge_mwh * share, 3),
                "discharge_mwh": round(annual_discharge_mwh * share, 3),
                "gross_margin": round(annual_margin * share, 2),
            }
        )

    return {
        "mode": mode,
        "annual_energy_value": round(energy_value, 2),
        "annual_demand_value": round(demand_value, 2),
        "annual_vpp_value": round(vpp_value, 2),
        "annual_gross_margin": round(annual_margin, 2),
        "annual_charge_mwh": round(annual_charge_mwh, 3),
        "annual_discharge_mwh": round(annual_discharge_mwh, 3),
        "annual_fec": round(annual_fec, 3),
        "daily_cycles": round(annual_fec / 365, 3) if annual_fec else 0.0,
        "deliverable_power_mw": round(deliverable_power_mw, 3),
        "storage_life_years_estimate": round(storage_life_years, 2) if storage_life_years else None,
        "storage_end_of_life_capacity_ratio": end_of_life_ratio,
        "monthly_storage_revenue_breakdown": monthly_breakdown,
    }


def simulate_annual_cycle_value(
    data: dict[str, Any],
    storage: dict[str, Any],
) -> dict[str, Any] | None:
    market = data.get("market_data", {}) or {}
    plan = market.get("arbitrage_plan") or {}
    if str(plan.get("mode") or "").lower() != "annual_cycle_value":
        return None

    storage_cfg = data.get("equipment", {}).get("storage", {}) or {}
    energy_kwh = float((storage.get("storage_energy_mwh") or 0.0) * 1000)
    if energy_kwh <= 0:
        return None

    prices = {str(item.get("period")): float(item.get("price", 0.0)) for item in (market.get("tou_tariff") or [])}
    if not prices:
        return None

    charge_eff = float(storage_cfg.get("battery_charge_efficiency") or storage_cfg.get("charge_efficiency") or 0.96)
    discharge_eff = float(storage_cfg.get("battery_discharge_efficiency") or storage_cfg.get("discharge_efficiency") or 0.96)
    pcs_eff = float(storage_cfg.get("pcs_efficiency") or 0.98)
    transformer_eff = float(storage_cfg.get("transformer_efficiency") or 0.99)
    effective_rte = charge_eff * discharge_eff * pcs_eff * transformer_eff
    cycle_life = float(storage_cfg.get("cycle_life") or 6000.0)
    annual_degradation = float(storage_cfg.get("annual_degradation_rate") or 0.025)
    revenue_share_ratio = _owner_share_ratio(plan)

    annual_margin = 0.0
    annual_charge_kwh = 0.0
    annual_discharge_kwh = 0.0
    monthly_charge = [0.0] * 12
    monthly_discharge = [0.0] * 12
    monthly_margin = [0.0] * 12
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    total_days = sum(month_days)

    cycles = plan.get("cycles") or []
    if not cycles and plan.get("auto_infer_cycles"):
        cycles = infer_cycles_from_monthly_tou_history(data, storage)
    if not cycles:
        return None
    for cycle in cycles:
        charge_period = str(cycle.get("charge_period") or "valley")
        discharge_period = str(cycle.get("discharge_period") or "peak")
        charge_price = float(cycle.get("charge_price") if cycle.get("charge_price") is not None else prices.get(charge_period, 0.0))
        discharge_price = float(cycle.get("discharge_price") if cycle.get("discharge_price") is not None else prices.get(discharge_period, 0.0))
        discharge_energy_kwh = float(cycle.get("discharge_energy_kwh") or 0.0)
        charge_energy_kwh = float(cycle.get("charge_energy_kwh") or 0.0)
        cycle_count = float(cycle.get("days_per_year") or cycle.get("count_per_year") or cycle.get("cycles_per_year") or 0.0)
        if cycle_count <= 0:
            continue
        if discharge_energy_kwh <= 0:
            discharge_energy_kwh = energy_kwh * _default_arbitrage_usable_depth(storage_cfg) * discharge_eff * pcs_eff * transformer_eff
        if charge_energy_kwh <= 0:
            charge_energy_kwh = discharge_energy_kwh / max(effective_rte, 1e-9)
        cycle_margin = discharge_energy_kwh * discharge_price - charge_energy_kwh * charge_price
        annual_margin += cycle_margin * cycle_count
        annual_charge_kwh += charge_energy_kwh * cycle_count
        annual_discharge_kwh += discharge_energy_kwh * cycle_count
        for idx, days in enumerate(month_days):
            share = days / total_days
            monthly_charge[idx] += charge_energy_kwh * cycle_count * share / 1000
            monthly_discharge[idx] += discharge_energy_kwh * cycle_count * share / 1000
            monthly_margin[idx] += cycle_margin * cycle_count * share

    annual_margin *= revenue_share_ratio
    annual_charge_mwh = annual_charge_kwh / 1000
    annual_discharge_mwh = annual_discharge_kwh / 1000
    annual_fec = annual_discharge_kwh / energy_kwh if energy_kwh > 0 else 0.0
    storage_life_years = (cycle_life / annual_fec) if annual_fec > 0 else None
    end_of_life_ratio = max(0.0, 1.0 - annual_degradation * min(storage_life_years or 0.0, 20.0)) if storage_life_years else None

    return {
        "mode": "annual_cycle_value",
        "annual_gross_margin": round(annual_margin, 2),
        "annual_charge_mwh": round(annual_charge_mwh, 3),
        "annual_discharge_mwh": round(annual_discharge_mwh, 3),
        "annual_fec": round(annual_fec, 3),
        "daily_cycles": round(annual_fec / 365, 3) if annual_fec else 0.0,
        "storage_life_years_estimate": round(storage_life_years, 2) if storage_life_years else None,
        "storage_end_of_life_capacity_ratio": end_of_life_ratio,
        "monthly_storage_revenue_breakdown": [
            {
                "month": idx + 1,
                "charge_mwh": round(monthly_charge[idx], 3),
                "discharge_mwh": round(monthly_discharge[idx], 3),
                "gross_margin": round(monthly_margin[idx], 2),
            }
            for idx in range(12)
        ],
    }


def simulate_spot_intraday_arbitrage(
    data: dict[str, Any],
    storage: dict[str, Any],
) -> dict[str, Any] | None:
    market = data.get("market_data", {}) or {}
    plan = _normalized_spot_intraday_plan(market)
    if str(plan.get("mode") or "").lower() != "spot_intraday":
        return None

    daily_profiles = market.get("spot_price_daily_profiles") or _build_daily_spot_profiles_from_series(market.get("market_price_series") or [])
    if not daily_profiles:
        return None

    min_charge_hours = int(plan["min_charge_hours"])
    min_discharge_hours = int(plan["min_discharge_hours"])
    min_spread_yuan_per_mwh = float(plan["min_spread_yuan_per_mwh"])

    storage_cfg = data.get("equipment", {}).get("storage", {}) or {}
    energy_mwh = float(storage.get("storage_energy_mwh") or 0.0)
    power_mw = float(storage.get("storage_power_mw") or 0.0)
    charge_eff = float(storage_cfg.get("battery_charge_efficiency") or 0.96)
    discharge_eff = float(storage_cfg.get("battery_discharge_efficiency") or 0.96)
    pcs_eff = float(storage_cfg.get("pcs_efficiency") or 0.98)
    transformer_eff = float(storage_cfg.get("transformer_efficiency") or 0.99)
    charge_path_eff = charge_eff * pcs_eff * transformer_eff
    effective_rte = charge_eff * discharge_eff * pcs_eff * transformer_eff
    discharge_path_eff = discharge_eff * pcs_eff * transformer_eff
    usable_depth = _default_arbitrage_usable_depth(storage_cfg)
    revenue_share_ratio = _owner_share_ratio(plan)
    cycle_life = float(storage_cfg.get("cycle_life") or 6000.0)
    annual_degradation = float(storage_cfg.get("annual_degradation_rate") or 0.025)
    cap_deliverable_mwh = energy_mwh * usable_depth * discharge_path_eff
    max_charge_hours = max(
        min_charge_hours,
        int(
            plan.get("max_charge_hours")
            or math.ceil((cap_deliverable_mwh / max(effective_rte, 1e-9)) / max(power_mw, 1e-9))
            or min_charge_hours
        ),
    )
    max_discharge_hours = max(
        min_discharge_hours,
        int(
            plan.get("max_discharge_hours")
            or math.ceil(cap_deliverable_mwh / max(power_mw, 1e-9))
            or min_discharge_hours
        ),
    )

    total_cycles = 0
    total_spread_value = 0.0
    total_gross_margin = 0.0
    total_charge_mwh = 0.0
    total_discharge_mwh = 0.0
    daily_schedule: list[dict[str, Any]] = []
    monthly_charge = [0.0] * 12
    monthly_discharge = [0.0] * 12
    monthly_margin = [0.0] * 12
    continuous_horizon = bool(plan["continuous_horizon"])
    if continuous_horizon:
        cycles = _select_best_spot_cycles_continuous(
            daily_profiles=daily_profiles,
            unit_hint=str(plan.get("price_unit") or market.get("spot_price_unit") or market.get("market_price_unit") or ""),
            min_charge_hours=min_charge_hours,
            max_charge_hours=max_charge_hours,
            min_discharge_hours=min_discharge_hours,
            max_discharge_hours=max_discharge_hours,
            min_spread_yuan_per_mwh=min_spread_yuan_per_mwh,
            power_mw=power_mw,
            energy_mwh=energy_mwh,
            usable_depth=usable_depth,
            discharge_path_eff=discharge_path_eff,
            effective_rte=effective_rte,
        )
        grouped = _group_spot_cycles_by_charge_date(cycles)
        for day in grouped:
            day_margin = sum(float(cycle["gross_margin"]) for cycle in day["cycles"])
            total_cycles += len(day["cycles"])
            total_spread_value += sum(float(cycle["spread_yuan_per_mwh"]) for cycle in day["cycles"])
            total_gross_margin += day_margin
            total_charge_mwh += sum(float(cycle["charge_energy_mwh"]) for cycle in day["cycles"])
            total_discharge_mwh += sum(float(cycle["discharge_energy_mwh"]) for cycle in day["cycles"])
            month_idx = _month_index_from_date(day.get("date"))
            if month_idx is not None:
                monthly_charge[month_idx] += sum(float(cycle["charge_energy_mwh"]) for cycle in day["cycles"])
                monthly_discharge[month_idx] += sum(float(cycle["discharge_energy_mwh"]) for cycle in day["cycles"])
                monthly_margin[month_idx] += day_margin * revenue_share_ratio
            daily_schedule.append(
                {
                    "date": day.get("date") or "",
                    "cycle_count": len(day["cycles"]),
                    "gross_margin": round(day_margin * revenue_share_ratio, 2),
                    "cycles": day["cycles"],
                }
            )
        covered_dates = [str(profile.get("date") or "") for profile in daily_profiles]
        existing = {item["date"] for item in daily_schedule}
        for date in covered_dates:
            if date not in existing:
                daily_schedule.append({"date": date, "cycle_count": 0, "gross_margin": 0.0, "cycles": []})
        daily_schedule.sort(key=lambda item: item["date"])
    else:
        for profile in daily_profiles:
            realtime_prices = _normalize_price_series_to_yuan_per_mwh(
                [float(v) for v in (profile.get("realtime_prices") or [])[:24]],
                unit_hint=str(plan.get("price_unit") or market.get("spot_price_unit") or market.get("market_price_unit") or ""),
            )
            if len(realtime_prices) < 24:
                continue
            cycles = _select_best_daily_spot_cycles(
                realtime_prices,
                min_charge_hours=min_charge_hours,
                min_discharge_hours=min_discharge_hours,
                min_spread_yuan_per_mwh=min_spread_yuan_per_mwh,
                power_mw=power_mw,
                energy_mwh=energy_mwh,
                usable_depth=usable_depth,
                charge_path_eff=charge_path_eff,
                discharge_path_eff=discharge_path_eff,
                effective_rte=effective_rte,
            )
            day_margin = 0.0
            day_spread_value = 0.0
            for cycle in cycles:
                day_spread_value += float(cycle["spread_yuan_per_mwh"])
                day_margin += float(cycle["gross_margin"])
            total_cycles += len(cycles)
            total_spread_value += day_spread_value
            total_gross_margin += day_margin
            total_charge_mwh += sum(float(cycle["charge_energy_mwh"]) for cycle in cycles)
            total_discharge_mwh += sum(float(cycle["discharge_energy_mwh"]) for cycle in cycles)

            month_idx = _month_index_from_date(profile.get("date"))
            if month_idx is not None:
                monthly_charge[month_idx] += sum(float(cycle["charge_energy_mwh"]) for cycle in cycles)
                monthly_discharge[month_idx] += sum(float(cycle["discharge_energy_mwh"]) for cycle in cycles)
                monthly_margin[month_idx] += day_margin * revenue_share_ratio

            daily_schedule.append(
                {
                    "date": profile.get("date") or "",
                    "cycle_count": len(cycles),
                    "gross_margin": round(day_margin * revenue_share_ratio, 2),
                    "cycles": cycles,
                }
            )

    if not daily_schedule:
        return None

    days_covered = len(daily_schedule)
    total_gross_margin *= revenue_share_ratio
    annual_fec = total_discharge_mwh / energy_mwh if energy_mwh > 0 else 0.0
    storage_life_years = (cycle_life / annual_fec) if annual_fec > 0 else None
    end_of_life_ratio = max(0.0, 1.0 - annual_degradation * min(storage_life_years or 0.0, 20.0)) if storage_life_years else None
    average_cycles = total_cycles / days_covered if days_covered > 0 else 0.0

    return {
        "mode": "spot_intraday",
        "days_covered": days_covered,
        "total_cycles": total_cycles,
        "annual_gross_margin": round(total_gross_margin, 2),
        "annual_charge_mwh": round(total_charge_mwh, 3),
        "annual_discharge_mwh": round(total_discharge_mwh, 3),
        "annual_fec": round(annual_fec, 3),
        "daily_cycles": round(average_cycles, 3),
        "average_spread_yuan_per_mwh": round(total_spread_value / total_cycles, 2) if total_cycles > 0 else None,
        "storage_life_years_estimate": round(storage_life_years, 2) if storage_life_years else None,
        "storage_end_of_life_capacity_ratio": end_of_life_ratio,
        "cycle_summary": f"{days_covered} 天内共识别 {total_cycles} 次满足阈值的日内实时套利循环",
        "daily_spot_arbitrage_schedule": daily_schedule,
        "monthly_storage_revenue_breakdown": [
            {
                "month": idx + 1,
                "charge_mwh": round(monthly_charge[idx], 3),
                "discharge_mwh": round(monthly_discharge[idx], 3),
                "gross_margin": round(monthly_margin[idx], 2),
            }
            for idx in range(12)
        ],
    }


def _normalized_spot_intraday_plan(market: dict[str, Any]) -> dict[str, Any]:
    plan = dict(market.get("arbitrage_plan") or {})
    if str(plan.get("mode") or "").lower() != "spot_intraday":
        return plan

    min_charge_hours = max(2, int(plan.get("min_charge_hours") or 2))
    min_discharge_hours = max(2, int(plan.get("min_discharge_hours") or 2))
    max_charge_hours = max(min_charge_hours, int(plan.get("max_charge_hours") or 6))
    max_discharge_hours = max(min_discharge_hours, int(plan.get("max_discharge_hours") or 6))
    plan["continuous_horizon"] = bool(plan.get("continuous_horizon", False))
    plan["min_charge_hours"] = min_charge_hours
    plan["min_discharge_hours"] = min_discharge_hours
    plan["max_charge_hours"] = max_charge_hours
    plan["max_discharge_hours"] = max_discharge_hours
    plan["min_spread_yuan_per_mwh"] = float(plan.get("min_spread_yuan_per_mwh") or 250.0)
    return plan


def _build_daily_spot_profiles_from_series(series: list[float]) -> list[dict[str, Any]]:
    values = [float(v) for v in series if v is not None]
    if len(values) < 24 or len(values) % 24 != 0:
        return []
    profiles: list[dict[str, Any]] = []
    for idx in range(0, len(values), 24):
        profiles.append(
            {
                "date": f"day_{idx // 24 + 1}",
                "realtime_prices": values[idx : idx + 24],
                "day_ahead_prices": [],
            }
        )
    return profiles


def _select_best_daily_spot_cycles(
    realtime_prices: list[float],
    min_charge_hours: int,
    min_discharge_hours: int,
    min_spread_yuan_per_mwh: float,
    power_mw: float,
    energy_mwh: float,
    usable_depth: float,
    charge_path_eff: float,
    discharge_path_eff: float,
    effective_rte: float,
    max_charge_hours: int | None = None,
    max_discharge_hours: int | None = None,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    horizon = len(realtime_prices)
    charge_hour_cap = max_charge_hours or horizon
    discharge_hour_cap = max_discharge_hours or horizon
    for charge_start in range(0, horizon - min_charge_hours + 1):
        for charge_end in range(charge_start + min_charge_hours, min(horizon - min_discharge_hours + 1, charge_start + charge_hour_cap + 1)):
            charge_hours = charge_end - charge_start
            charge_slice = realtime_prices[charge_start:charge_end]
            charge_avg = sum(charge_slice) / len(charge_slice)
            for discharge_start in range(charge_end, horizon - min_discharge_hours + 1):
                for discharge_end in range(discharge_start + min_discharge_hours, min(horizon, discharge_start + discharge_hour_cap) + 1):
                    discharge_hours = discharge_end - discharge_start
                    discharge_slice = realtime_prices[discharge_start:discharge_end]
                    discharge_avg = sum(discharge_slice) / len(discharge_slice)
                    spread = discharge_avg - charge_avg
                    if spread < min_spread_yuan_per_mwh:
                        continue

                    deliverable_discharge_mwh = min(
                        power_mw * discharge_hours,
                        power_mw * charge_hours * effective_rte,
                        energy_mwh * usable_depth * discharge_path_eff,
                    )
                    if deliverable_discharge_mwh <= 0:
                        continue
                    grid_charge_mwh = deliverable_discharge_mwh / max(effective_rte, 1e-9)
                    max_grid_charge_mwh = power_mw * charge_hours
                    if grid_charge_mwh > max_grid_charge_mwh + 1e-9:
                        continue

                    gross_margin = deliverable_discharge_mwh * discharge_avg - grid_charge_mwh * charge_avg
                    if gross_margin <= 0:
                        continue

                    candidates.append(
                        {
                            "charge_start": charge_start,
                            "charge_end": charge_end,
                            "discharge_start": discharge_start,
                            "discharge_end": discharge_end,
                            "charge_hours": charge_hours,
                            "discharge_hours": discharge_hours,
                            "charge_avg_price": round(charge_avg, 6),
                            "discharge_avg_price": round(discharge_avg, 6),
                            "spread_yuan_per_mwh": round(spread, 2),
                            "charge_energy_mwh": round(grid_charge_mwh, 6),
                            "discharge_energy_mwh": round(deliverable_discharge_mwh, 6),
                            "gross_margin": round(gross_margin, 2),
                        }
                    )
    if not candidates:
        return []

    candidates.sort(key=lambda item: (item["discharge_end"], item["charge_start"], item["discharge_start"]))
    predecessors: list[int] = []
    for idx, cycle in enumerate(candidates):
        predecessor = -1
        for back in range(idx - 1, -1, -1):
            if candidates[back]["discharge_end"] <= cycle["charge_start"]:
                predecessor = back
                break
        predecessors.append(predecessor)

    best_scores: list[tuple[int, float]] = []
    best_paths: list[list[int]] = []
    for idx, cycle in enumerate(candidates):
        include_score = (1, float(cycle["gross_margin"]))
        include_path = [idx]
        predecessor = predecessors[idx]
        if predecessor >= 0:
            prev_score = best_scores[predecessor]
            include_score = (prev_score[0] + 1, prev_score[1] + float(cycle["gross_margin"]))
            include_path = best_paths[predecessor] + [idx]
        exclude_score = best_scores[idx - 1] if idx > 0 else (0, 0.0)
        exclude_path = best_paths[idx - 1] if idx > 0 else []
        if include_score[0] > exclude_score[0] or (include_score[0] == exclude_score[0] and include_score[1] > exclude_score[1]):
            best_scores.append(include_score)
            best_paths.append(include_path)
        else:
            best_scores.append(exclude_score)
            best_paths.append(exclude_path)

    selected = [candidates[idx] for idx in best_paths[-1]]
    return [
        {
            **cycle,
            "charge_window": _format_hour_window(cycle["charge_start"], cycle["charge_end"]),
            "discharge_window": _format_hour_window(cycle["discharge_start"], cycle["discharge_end"]),
        }
        for cycle in selected
    ]


def _normalize_price_series_to_yuan_per_mwh(values: list[float], unit_hint: str = "") -> list[float]:
    # When unit_hint is provided, trust it. Otherwise use heuristic:
    # values <= 20 likely in yuan/kWh (multiply by 1000 to get yuan/MWh).
    hint = unit_hint.strip().lower()
    if hint in {"yuan_per_kwh", "cny_per_kwh", "kwh"}:
        return [float(value) * 1000.0 for value in values]
    if hint in {"yuan_per_mwh", "cny_per_mwh", "mwh"}:
        return [float(value) for value in values]
    finite = [float(value) for value in values if value is not None]
    if finite and max(finite) <= 20.0:
        return [float(value) * 1000.0 for value in values]
    return [float(value) for value in values]


def _select_best_spot_cycles_continuous(
    daily_profiles: list[dict[str, Any]],
    unit_hint: str,
    min_charge_hours: int,
    max_charge_hours: int,
    min_discharge_hours: int,
    max_discharge_hours: int,
    min_spread_yuan_per_mwh: float,
    power_mw: float,
    energy_mwh: float,
    usable_depth: float,
    discharge_path_eff: float,
    effective_rte: float,
) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    prices: list[float] = []
    for profile in daily_profiles:
        normalized = _normalize_price_series_to_yuan_per_mwh(
            [float(v) for v in (profile.get("realtime_prices") or [])[:24]],
            unit_hint=unit_hint,
        )
        if len(normalized) < 24:
            continue
        date = str(profile.get("date") or "")
        for hour, price in enumerate(normalized):
            flattened.append({"date": date, "hour": hour})
            prices.append(price)
    n = len(prices)
    if n < min_charge_hours + min_discharge_hours:
        return []

    cap_deliverable_mwh = energy_mwh * usable_depth * discharge_path_eff
    prefix = [0.0]
    for price in prices:
        prefix.append(prefix[-1] + float(price))

    dp_count = [0] * (n + 1)
    dp_margin = [0.0] * (n + 1)
    choice: list[dict[str, Any] | None] = [None] * (n + 1)

    for t in range(n - 1, -1, -1):
        best_count = dp_count[t + 1]
        best_margin = dp_margin[t + 1]
        best_choice = {"type": "skip", "next": t + 1}
        for charge_hours in range(min_charge_hours, max_charge_hours + 1):
            charge_end = t + charge_hours
            if charge_end + min_discharge_hours > n:
                break
            charge_avg = (prefix[charge_end] - prefix[t]) / charge_hours
            for discharge_hours in range(min_discharge_hours, max_discharge_hours + 1):
                max_discharge_start = n - discharge_hours
                deliverable_discharge_mwh = min(
                    power_mw * discharge_hours,
                    power_mw * charge_hours * effective_rte,
                    cap_deliverable_mwh,
                )
                if deliverable_discharge_mwh <= 0:
                    continue
                grid_charge_mwh = deliverable_discharge_mwh / max(effective_rte, 1e-9)
                if grid_charge_mwh > power_mw * charge_hours + 1e-9:
                    continue
                for discharge_start in range(charge_end, max_discharge_start + 1):
                    discharge_end = discharge_start + discharge_hours
                    discharge_avg = (prefix[discharge_end] - prefix[discharge_start]) / discharge_hours
                    spread = discharge_avg - charge_avg
                    if spread <= min_spread_yuan_per_mwh:
                        continue
                    gross_margin = deliverable_discharge_mwh * discharge_avg - grid_charge_mwh * charge_avg
                    if gross_margin <= 0:
                        continue
                    candidate_count = 1 + dp_count[discharge_end]
                    candidate_margin = gross_margin + dp_margin[discharge_end]
                    if candidate_count > best_count or (candidate_count == best_count and candidate_margin > best_margin):
                        best_count = candidate_count
                        best_margin = candidate_margin
                        best_choice = {
                            "type": "cycle",
                            "next": discharge_end,
                            "cycle": {
                                "charge_start_index": t,
                                "charge_end_index": charge_end,
                                "discharge_start_index": discharge_start,
                                "discharge_end_index": discharge_end,
                                "charge_hours": charge_hours,
                                "discharge_hours": discharge_hours,
                                "charge_avg_price": round(charge_avg, 6),
                                "discharge_avg_price": round(discharge_avg, 6),
                                "spread_yuan_per_mwh": round(spread, 2),
                                "charge_energy_mwh": round(grid_charge_mwh, 6),
                                "discharge_energy_mwh": round(deliverable_discharge_mwh, 6),
                                "gross_margin": round(gross_margin, 2),
                            },
                        }
        dp_count[t] = best_count
        dp_margin[t] = best_margin
        choice[t] = best_choice

    selected: list[dict[str, Any]] = []
    cursor = 0
    while cursor < n and choice[cursor]:
        current = choice[cursor]
        if current and current.get("type") == "cycle":
            cycle = dict(current["cycle"])
            charge_start = int(cycle["charge_start_index"])
            charge_end = int(cycle["charge_end_index"])
            discharge_start = int(cycle["discharge_start_index"])
            discharge_end = int(cycle["discharge_end_index"])
            cycle["charge_date"] = flattened[charge_start]["date"]
            cycle["discharge_date"] = flattened[discharge_start]["date"]
            cycle["charge_window"] = _format_hour_window(int(flattened[charge_start]["hour"]), int(flattened[charge_end - 1]["hour"]) + 1)
            cycle["discharge_window"] = _format_hour_window(int(flattened[discharge_start]["hour"]), int(flattened[discharge_end - 1]["hour"]) + 1)
            selected.append(cycle)
            cursor = int(current["next"])
        else:
            cursor = int(current["next"]) if current else cursor + 1
    return selected


def _group_spot_cycles_by_charge_date(cycles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for cycle in cycles:
        grouped.setdefault(str(cycle.get("charge_date") or ""), []).append(cycle)
    return [{"date": date, "cycles": grouped[date]} for date in sorted(grouped)]


def _format_hour_window(start: int, end: int) -> str:
    return f"{start:02d}:00-{end:02d}:00"


def _month_index_from_date(value: Any) -> int | None:
    text = str(value or "").strip()
    if len(text) >= 7 and text[4] == "-":
        try:
            month = int(text[5:7])
        except ValueError:
            return None
        if 1 <= month <= 12:
            return month - 1
    return None


def _month_from_profile_or_index(profile: dict[str, Any], profile_idx: int) -> int:
    month_idx = _month_index_from_date(profile.get("date"))
    if month_idx is not None:
        return month_idx + 1
    return max(1, min(12, profile_idx // 31 + 1))


