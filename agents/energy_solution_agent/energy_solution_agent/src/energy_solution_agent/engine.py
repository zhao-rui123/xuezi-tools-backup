from __future__ import annotations

from typing import Any

from .annual_series import build_annual_series
from .candidates import generate_candidate_solutions
from .completeness import evaluate_data_completeness
from .data_quality import assess_data_quality
from .industry_templates import get_industry_template
from .live_rules import apply_live_rule_patch, fetch_live_rule_patch
from .data_ingest import ingest_external_series
from .normalize import normalize_input
from .profiles import get_province_profile
from .province_overrides import apply_province_overrides
from .province_adapter import build_market_context
from .resource_models import estimate_pv_generation, estimate_wind_generation
from .reporting import build_report
from .router import route_scenario
from .schema import new_output
from .sensitivity import run_sensitivity
from .settlement import ancillary_and_dr_revenue, annual_demand_charge, annual_energy_charge, build_hourly_price_series
from .solvers import (
    assemble_design_notes,
    estimate_carbon,
    estimate_storage,
    simulate_thermal_equipment_annual,
    simulate_storage_dispatch_annual,
    settlement_and_finance,
    simulate_storage_dispatch,
    synthesize_charging_profile,
    synthesize_thermal_profile,
)
from .timeseries import to_hourly_profile


def analyze_project(payload: dict[str, Any], enable_live_rules: bool = False) -> tuple[dict[str, Any], dict[str, Any], str]:
    data = apply_province_overrides(ingest_external_series(normalize_input(payload)))
    data_quality = assess_data_quality(data)
    completeness_grade, missing_fields = evaluate_data_completeness(data)
    scenario, secondary, reason = route_scenario(data)
    profile = get_province_profile(data.get("project_info", {}).get("province"))
    live_patch = fetch_live_rule_patch(profile) if enable_live_rules else None
    data["market_data"] = apply_live_rule_patch(data.get("market_data", {}), (live_patch or {}).get("structured_patch"))
    market_context = build_market_context(profile, data.get("market_data", {}), live_patch=live_patch)

    charging_profile, charging_summary = synthesize_charging_profile(data)
    thermal_profile, thermal_summary = synthesize_thermal_profile(data)
    load_profile = to_hourly_profile(
        [float(v) for v in (data.get("load_data", {}).get("load_series_kw") or [])],
        annual_target_mwh=float(data.get("load_data", {}).get("annual_consumption_mwh") or 0.0) or None,
        fallback_peak_kw=float(data.get("load_data", {}).get("peak_load_kw") or 1000),
    )
    load_series = build_annual_series(
        raw_series=[float(v) for v in (data.get("load_data", {}).get("load_series_kw") or [])],
        fallback_daily=load_profile,
        annual_target_mwh=float(data.get("load_data", {}).get("annual_consumption_mwh") or 0.0) or None,
        monthly_factors=data.get("load_data", {}).get("monthly_load_factors"),
    )
    pv_result = estimate_pv_generation(data)
    wind_result = estimate_wind_generation(data)
    renewables = {**pv_result, **wind_result}
    prelim_prices = build_hourly_price_series(data.get("market_data", {}), len(load_series))
    storage = estimate_storage(
        data,
        charging_peak_kw=float(charging_summary.get("charging_peak_kw") or 0.0),
        thermal_coupling_kw=float(sum(thermal_profile.get("cooling_electric_kw", [])) + sum(thermal_profile.get("heating_electric_kw", []))) / 24 if thermal_profile else 0.0,
    )

    annual_load = float(data.get("load_data", {}).get("annual_consumption_mwh") or 0.0)
    annual_pv = float(renewables.get("annual_pv_generation_mwh") or 0.0)
    annual_wind = float(renewables.get("annual_wind_generation_mwh") or 0.0)
    annual_charging = float(charging_summary.get("annual_charging_energy_mwh") or 0.0)
    annual_cooling = float(thermal_summary.get("annual_cooling_energy_mwh") or 0.0) if thermal_summary.get("annual_cooling_energy_mwh") is not None else 0.0
    annual_heating = float(thermal_summary.get("annual_heating_energy_mwh") or 0.0) if thermal_summary.get("annual_heating_energy_mwh") is not None else 0.0
    thermal_daily = [
        a + b for a, b in zip(thermal_profile.get("cooling_electric_kw", [0.0] * 24), thermal_profile.get("heating_electric_kw", [0.0] * 24))
    ]
    charging_series = build_annual_series(
        raw_series=[float(v) for v in (data.get("charging_data", {}).get("arrival_profile") or [])],
        fallback_daily=charging_profile,
        annual_target_mwh=float(charging_summary.get("annual_charging_energy_mwh") or 0.0) or None,
        monthly_factors=data.get("charging_data", {}).get("monthly_energy_factors"),
    )
    cooling_series = build_annual_series(
        raw_series=[float(v) for v in (data.get("load_data", {}).get("cooling_load_series_kw") or [])],
        fallback_daily=thermal_profile.get("cooling_kw", [0.0] * 24),
        annual_target_mwh=float(annual_cooling or 0.0) or None,
        monthly_factors=data.get("thermal_system", {}).get("cooling_monthly_factors"),
    )
    heating_series = build_annual_series(
        raw_series=[float(v) for v in (data.get("load_data", {}).get("heating_load_series_kw") or [])],
        fallback_daily=thermal_profile.get("heating_kw", [0.0] * 24),
        annual_target_mwh=float(annual_heating or 0.0) or None,
        monthly_factors=data.get("thermal_system", {}).get("heating_monthly_factors"),
    )
    thermal_annual = simulate_thermal_equipment_annual(
        cooling_series_kw=cooling_series,
        heating_series_kw=heating_series,
        thermal_equipment=data.get("equipment", {}).get("thermal", {}),
    )
    thermal_electric_profile = thermal_daily
    thermal_series = thermal_annual["thermal_electric_series_kw"]
    # ── 自动选择储能策略 ──────────────────────────────────────
    user_strategy = data.get("project_info", {}).get("storage_strategy_mode") or ""
    if user_strategy and user_strategy != "auto":
        storage_strategy = user_strategy
    else:
        market_mode = str(data.get("market_data", {}).get("market_mode") or "").lower()
        has_tou = bool(data.get("market_data", {}).get("tou_tariff"))
        has_market_price = bool(data.get("market_data", {}).get("market_price_series"))
        pv_mwp = float(renewables.get("pv_mwp") or 0)
        wind_mw = float(renewables.get("wind_mw") or 0)
        annual_load = float(data.get("load_data", {}).get("annual_consumption_mwh") or 0)
        renewable_ratio = (pv_mwp * 1200 + wind_mw * 2200) / annual_load if annual_load > 0 else 0

        if "microgrid" in scenario or market_mode == "offgrid_internal":
            storage_strategy = "microgrid"
        elif has_tou or has_market_price or data.get("market_data", {}).get("market_mode") in ("spot", "market_price_series"):
            storage_strategy = "market_responding"
            # 如有现货市场配置，生成现货价格序列
            if data.get("market_data", {}).get("market_mode") == "spot":
                data["market_data"]["market_price_series"] = build_spot_price_series(
                    data["market_data"], 8760
                )
            storage_strategy = "market_responding"
        elif renewable_ratio > 0.3:
            storage_strategy = "renewable_priority"
        else:
            storage_strategy = "peak_shaving"
    # ── 候选储能真实 dispatch + 财务择优（大师级优化）─────────────
    candidate_powers = [float(v) for v in (data.get("equipment", {}).get("storage", {}).get("power_candidate_kw") or [])]
    candidate_energies = [float(v) for v in (data.get("equipment", {}).get("storage", {}).get("energy_candidate_kwh") or [])]
    optimization_target = str(data.get("financial", {}).get("optimization_target") or "irr").lower()
    if candidate_powers and candidate_energies and len(candidate_powers) == len(candidate_energies):
        best_metric = float("-inf")
        best_storage = storage
        cop_cooling = float(data.get("equipment", {}).get("thermal", {}).get("cooling_cop") or 3.5)
        cop_heating = float(data.get("equipment", {}).get("thermal", {}).get("heating_cop") or 3.0)
        export_ratio = float(data.get("network_and_design", {}).get("max_export_ratio") or 0.65)
        curtail_ratio = float(data.get("network_and_design", {}).get("curtailment_ratio") or 0.20)
        gross_demand = annual_load + annual_charging + (annual_cooling / cop_cooling if annual_cooling else 0.0) + (annual_heating / cop_heating if annual_heating else 0.0)
        for p_kw, e_kwh in zip(candidate_powers, candidate_energies):
            cand_storage = {
                **storage,
                "storage_power_mw": round(p_kw / 1000, 3),
                "storage_energy_mwh": round(e_kwh / 1000, 3),
            }
            cand_dispatch = simulate_storage_dispatch_annual(
                load_series_kw=load_series,
                pv_series_kw=renewables.get("pv_annual_series_kw", [0.0] * 8760),
                wind_series_kw=renewables.get("wind_annual_series_kw", [0.0] * 8760),
                charging_series_kw=charging_series,
                thermal_series_kw=thermal_series,
                storage_power_mw=cand_storage["storage_power_mw"],
                storage_energy_mwh=cand_storage["storage_energy_mwh"],
                strategy_mode=storage_strategy,
                price_series=prelim_prices,
                storage_config=data.get("equipment", {}).get("storage", {}),
            )
            cand_grid_purchase = cand_dispatch["annual_grid_purchase_mwh"]
            cand_export = max(0.0, annual_pv + annual_wind - gross_demand * export_ratio)
            cand_curtail = max(0.0, cand_export * curtail_ratio)
            cand_coverage = (gross_demand - cand_grid_purchase) / gross_demand if gross_demand > 0 else None
            cand_simulation = {
                **renewables,
                **cand_storage,
                **charging_summary,
                **thermal_summary,
                "annual_storage_charge_mwh": round(cand_dispatch["daily_storage_charge_mwh"] * 365, 2),
                "annual_storage_discharge_mwh": round(cand_dispatch["daily_storage_discharge_mwh"] * 365, 2),
                "annual_grid_purchase_mwh": round(cand_grid_purchase, 2),
                "annual_export_mwh": round(cand_export, 2),
                "annual_curtailment_mwh": round(cand_curtail, 2),
                "coverage_ratio": round(cand_coverage, 4) if cand_coverage is not None else None,
                "storage_equivalent_full_cycles_per_year": float(cand_dispatch.get("storage_equivalent_full_cycles_per_year") or 0.0),
            }
            cand_carbon = estimate_carbon(data, cand_simulation)
            cand_finance = settlement_and_finance(data, cand_simulation, cand_carbon)
            metric = cand_finance.get("npv") if optimization_target == "npv" else cand_finance.get("irr")
            metric_val = float(metric) if metric is not None else float("-inf")
            if metric_val > best_metric:
                best_metric = metric_val
                best_storage = cand_storage
        storage = best_storage
    dispatch = simulate_storage_dispatch(
        load_profile_kw=load_profile,
        pv_profile_kw=renewables.get("pv_hourly_profile_kw", [0.0] * 24),
        wind_profile_kw=renewables.get("wind_hourly_profile_kw", [0.0] * 24),
        charging_profile_kw=charging_profile,
        thermal_electric_kw=thermal_electric_profile,
        storage_power_mw=storage.get("storage_power_mw"),
        storage_energy_mwh=storage.get("storage_energy_mwh"),
    )
    annual_dispatch = simulate_storage_dispatch_annual(
        load_series_kw=load_series,
        pv_series_kw=renewables.get("pv_annual_series_kw", [0.0] * 8760),
        wind_series_kw=renewables.get("wind_annual_series_kw", [0.0] * 8760),
        charging_series_kw=charging_series,
        thermal_series_kw=thermal_series,
        storage_power_mw=storage.get("storage_power_mw"),
        storage_energy_mwh=storage.get("storage_energy_mwh"),
        strategy_mode=storage_strategy,
        price_series=prelim_prices,
        storage_config=data.get("equipment", {}).get("storage", {}),
    )

    # ── 储能循环次数约束（≥300次/年，有上限保护）─────────────
    # microgrid 策略跳过：循环由过剩电量决定，不是储能大小
    if storage_strategy != "microgrid":
        min_annual_cycles = 300.0
        actual_annual_cycles = float(annual_dispatch.get("storage_equivalent_full_cycles_per_year") or 0.0)
        max_power_mw = 100.0
        max_energy_mwh = 500.0
        max_iter = 3
        iter_count = 0
        while actual_annual_cycles < min_annual_cycles and iter_count < max_iter:
            cur_power = float(storage.get("storage_power_mw") or 0.0)
            cur_energy = float(storage.get("storage_energy_mwh") or 0.0)
            if cur_power <= 0 or cur_energy <= 0 or cur_power >= max_power_mw or cur_energy >= max_energy_mwh:
                break
            iter_count += 1
            new_power = min(round(cur_power * 1.4, 3), max_power_mw)
            new_energy = min(round(cur_energy * 1.4, 3), max_energy_mwh)
            storage = {**storage, "storage_power_mw": new_power, "storage_energy_mwh": new_energy}
            annual_dispatch = simulate_storage_dispatch_annual(
                load_series_kw=load_series,
                pv_series_kw=renewables.get("pv_annual_series_kw", [0.0] * 8760),
                wind_series_kw=renewables.get("wind_annual_series_kw", [0.0] * 8760),
                charging_series_kw=charging_series,
                thermal_series_kw=thermal_series,
                storage_power_mw=new_power,
                storage_energy_mwh=new_energy,
                strategy_mode=storage_strategy,
                price_series=prelim_prices,
                storage_config=data.get("equipment", {}).get("storage", {}),
            )
            actual_annual_cycles = float(annual_dispatch.get("storage_equivalent_full_cycles_per_year") or 0.0)

    cop_cooling = float(data.get("equipment", {}).get("thermal", {}).get("cooling_cop") or 3.5)
    cop_heating = float(data.get("equipment", {}).get("thermal", {}).get("heating_cop") or 3.0)
    export_ratio = float(data.get("network_and_design", {}).get("max_export_ratio") or 0.65)
    curtail_ratio = float(data.get("network_and_design", {}).get("curtailment_ratio") or 0.20)
    gross_demand = annual_load + annual_charging + (annual_cooling / cop_cooling if annual_cooling else 0.0) + (annual_heating / cop_heating if annual_heating else 0.0)
    annual_grid_purchase = annual_dispatch["annual_grid_purchase_mwh"]
    annual_export = max(0.0, annual_pv + annual_wind - gross_demand * export_ratio)
    annual_curtailment = max(0.0, annual_export * curtail_ratio)
    coverage_ratio = (gross_demand - annual_grid_purchase) / gross_demand if gross_demand > 0 else None

    simulation = {
        **renewables,
        **storage,
        **charging_summary,
        **thermal_summary,
        "annual_storage_charge_mwh": round(annual_dispatch["daily_storage_charge_mwh"] * 365, 2),
        "annual_storage_discharge_mwh": round(annual_dispatch["daily_storage_discharge_mwh"] * 365, 2),
        "annual_grid_purchase_mwh": round(annual_grid_purchase, 2),
        "annual_export_mwh": round(annual_export, 2),
        "annual_curtailment_mwh": round(annual_curtailment, 2),
        "renewable_self_consumption_ratio": round((annual_pv + annual_wind - annual_export - annual_curtailment) / max(annual_pv + annual_wind, 0.001), 4) if (annual_pv + annual_wind) > 0 else None,
        "coverage_ratio": round(coverage_ratio, 4) if coverage_ratio is not None else None,
    }
    industry_template = get_industry_template(data.get("carbon_data", {}).get("industry_type"))
    carbon = estimate_carbon(data, simulation)
    finance = settlement_and_finance(data, simulation, carbon)
    storage_power_mw = float(storage.get("storage_power_mw") or 0.0)
    peak_reduction_kw = float(annual_dispatch.get("peak_reduction_kw") or 0.0)
    extra_revenue = ancillary_and_dr_revenue(storage_power_mw, peak_reduction_kw, data.get("market_data", {}))
    finance.update(extra_revenue)
    finance["annual_savings_or_revenue"] = round(
        float(finance["annual_savings_or_revenue"]) + finance["annual_ancillary_service_revenue"] + finance["annual_demand_response_revenue"],
        2,
    )
    finance["annual_energy_charge_cost"] = round(annual_energy_charge(annual_dispatch["post_storage_grid_series_kw"], prelim_prices), 2)
    finance["annual_demand_charge_cost"] = round(annual_demand_charge(annual_dispatch["post_storage_grid_series_kw"], data.get("market_data", {})), 2)
    design = assemble_design_notes(data, profile, scenario, float(charging_summary.get("charging_peak_kw") or 0.0))

    output = new_output()
    project = data.get("project_info", {})
    output["project_summary"].update(
        {
            "project_name": project.get("project_name") or "",
            "scenario_type": scenario,
            "province": project.get("province") or "",
        }
    )
    output["applicability"].update(
        {
            "pv_recommended": bool(renewables.get("pv_mwp")),
            "wind_recommended": bool(renewables.get("wind_mw")),
            "storage_recommended": bool(storage.get("storage_power_mw")),
            "microgrid_recommended": scenario == "microgrid",
            "charging_recommended": bool(charging_summary.get("annual_charging_energy_mwh")),
            "thermal_system_recommended": bool(thermal_summary.get("annual_cooling_energy_mwh") or thermal_summary.get("annual_heating_energy_mwh")),
            "zero_carbon_factory_recommended": scenario == "zero_carbon_factory",
        }
    )
    output["recommended_solution"].update(
        {
            "pv_mwp": renewables.get("pv_mwp"),
            "wind_mw": renewables.get("wind_mw"),
            "storage_power_mw": storage.get("storage_power_mw"),
            "storage_energy_mwh": storage.get("storage_energy_mwh"),
            "charging_capacity_mw": round(float(charging_summary.get("charging_peak_kw") or 0.0) / 1000, 3) if charging_summary.get("charging_peak_kw") else None,
            "cooling_capacity_rt": thermal_summary.get("cooling_capacity_rt"),
            "heating_capacity_mwth": thermal_summary.get("heating_capacity_mwth"),
            "carbon_reduction_path_summary": _carbon_path_summary(data),
            "grid_connection_summary": _grid_summary(data, profile),
            "dispatch_strategy_summary": _dispatch_summary(scenario),
            "market_strategy_summary": _market_summary(data, profile),
        }
    )
    output["alternative_solutions"] = generate_candidate_solutions(data, output["recommended_solution"])
    output["simulation_results"].update(simulation)
    output["resource_results"].update(
        {
            "pv_resource_accuracy": renewables.get("pv_resource_accuracy"),
            "pv_resource_basis": renewables.get("pv_resource_basis"),
            "pv_p50_generation_mwh": renewables.get("pv_p50_generation_mwh"),
            "pv_p90_generation_mwh": renewables.get("pv_p90_generation_mwh"),
            "pv_tilt_factor": renewables.get("pv_tilt_factor"),
            "pv_azimuth_factor": renewables.get("pv_azimuth_factor"),
            "pv_temperature_factor": renewables.get("pv_temperature_factor"),
            "pv_pr_effective": renewables.get("pv_pr_effective"),
            "wind_resource_accuracy": renewables.get("wind_resource_accuracy"),
            "wind_resource_basis": renewables.get("wind_resource_basis"),
            "wind_p50_generation_mwh": renewables.get("wind_p50_generation_mwh"),
            "wind_p90_generation_mwh": renewables.get("wind_p90_generation_mwh"),
            "wind_power_curve_used": renewables.get("wind_power_curve_used"),
            "wind_mean_speed_mps": renewables.get("wind_mean_speed_mps"),
        }
    )
    output["dispatch_results"].update(
        {
            "baseline_peak_grid_kw": round(annual_dispatch["baseline_peak_grid_kw"], 2),
            "post_storage_peak_grid_kw": round(annual_dispatch["post_storage_peak_grid_kw"], 2),
            "estimated_peak_reduction_kw": round(annual_dispatch["peak_reduction_kw"], 2),
            "daily_storage_cycles": round(annual_dispatch["daily_storage_cycles"], 3),
            "charging_peak_kw": round(float(charging_summary.get("charging_peak_kw") or 0.0), 2) if charging_summary.get("charging_peak_kw") else None,
            "thermal_electric_peak_kw": round(max(thermal_electric_profile), 2) if thermal_electric_profile else None,
            "storage_strategy_mode": storage_strategy,
            "charging_queue_index": charging_summary.get("charging_queue_index"),
            "storage_annual_throughput_mwh": round(float(annual_dispatch.get("storage_annual_throughput_mwh") or 0.0), 2),
            "storage_equivalent_full_cycles_per_year": round(float(annual_dispatch.get("storage_equivalent_full_cycles_per_year") or 0.0), 3),
            "storage_life_years_estimate": round(float(annual_dispatch.get("storage_life_years_estimate") or 0.0), 2) if annual_dispatch.get("storage_life_years_estimate") else None,
            "storage_charge_from_renewables_ratio": round(float(annual_dispatch.get("storage_charge_from_renewables_ratio") or 0.0), 4) if annual_dispatch.get("storage_charge_from_renewables_ratio") is not None else None,
            "storage_effective_round_trip_efficiency": round(float(annual_dispatch.get("storage_effective_round_trip_efficiency") or 0.0), 4) if annual_dispatch.get("storage_effective_round_trip_efficiency") is not None else None,
            "storage_reserved_soc_ratio": annual_dispatch.get("storage_reserved_soc_ratio"),
            "storage_backup_soc_ratio": annual_dispatch.get("storage_backup_soc_ratio"),
            "storage_degradation_per_year": annual_dispatch.get("storage_degradation_per_year"),
            "storage_end_of_life_capacity_ratio": annual_dispatch.get("storage_end_of_life_capacity_ratio"),
            "monthly_storage_revenue_breakdown": annual_dispatch.get("monthly_storage_revenue_breakdown") or [],
            "charging_diversity_factor": charging_summary.get("charging_diversity_factor"),
            "thermal_annual_boiler_fuel_equivalent_mwh": thermal_annual.get("annual_boiler_fuel_equivalent_mwh"),
            "thermal_cooling_peak_kwth": thermal_summary.get("cooling_peak_kwth"),
            "thermal_heating_peak_kwth": thermal_summary.get("heating_peak_kwth"),
            "charging_segment_summary": charging_summary.get("charging_segment_summary") or [],
        }
    )
    output["market_and_settlement"].update(
        {
            "market_mode": data.get("market_data", {}).get("market_mode") or "",
            "price_mechanism_summary": finance["price_mechanism_summary"],
            "revenue_breakdown": finance["revenue_breakdown"],
            "deviation_risk_summary": _deviation_risk(data, profile),
            "demand_charge_impact": _demand_charge_impact(data),
            "province_profile_status": market_context["province_profile_status"],
            "market_rule_notes": market_context["market_rule_notes"],
            "profile_grid_region": market_context["profile_grid_region"],
            "live_rule_refresh_enabled": market_context["live_rule_refresh_enabled"],
            "live_rule_refresh_status": market_context["live_rule_refresh_status"],
            "live_rule_last_checked_at": market_context["live_rule_last_checked_at"],
            "live_rule_sources": market_context["live_rule_sources"],
            "live_rule_effective_patch": (live_patch or {}).get("structured_patch", {}),
        }
    )
    # ── 基线对比（无项目时年能源成本） ──────────────────────────
    market_mode = str(data.get("market_data", {}).get("market_mode") or "").lower()
    fuel_cost = float(data.get("market_data", {}).get("fuel_cost_per_kwh") or 0.0)
    if market_mode == "offgrid_internal" and fuel_cost > 0:
        baseline_annual_cost = annual_load * fuel_cost * 1000
    else:
        baseline_annual_cost = annual_load * 0.72 * 1000  # 默认平均电价0.72元
    finance["baseline_annual_energy_cost"] = round(baseline_annual_cost, 2)
    output["design_and_interconnection"].update(design)
    output["financial_results"].update(
        {
            "capex_total": finance["capex_total"],
            "baseline_annual_energy_cost": finance["baseline_annual_energy_cost"],
            "opex_annual": finance["opex_annual"],
            "annual_savings_or_revenue": finance["annual_savings_or_revenue"],
            "irr": finance["irr"],
            "payback_years": finance["payback_years"],
            "npv": finance["npv"],
            "abatement_cost_per_tco2e": finance["abatement_cost_per_tco2e"],
            "annual_energy_charge_cost": finance["annual_energy_charge_cost"],
            "annual_demand_charge_cost": finance["annual_demand_charge_cost"],
            "annual_ancillary_service_revenue": finance["annual_ancillary_service_revenue"],
            "annual_demand_response_revenue": finance["annual_demand_response_revenue"],
            "storage_replacement_year": finance["storage_replacement_year"],
            "storage_replacement_cost": finance["storage_replacement_cost"],
            "opex_escalation_rate": finance["opex_escalation_rate"],
            "lcoe": finance.get("lcoe"),
            "lcos": finance.get("lcos"),
            "pv_lcoe": finance.get("pv_lcoe"),
            "wind_lcoe": finance.get("wind_lcoe"),
            "storage_lcos": finance.get("storage_lcos"),
            "equity_irr": finance.get("equity_irr"),
            "equity_npv": finance.get("equity_npv"),
            "dscr_min": finance.get("dscr_min"),
            "dyn_payback_years": finance.get("dyn_payback_years"),
            "roi": finance.get("roi"),
            "roe": finance.get("roe"),
            "breakeven_price_factor": finance.get("breakeven_price_factor"),
            "gec_revenue_annual": finance.get("gec_revenue_annual"),
            "ccer_total_value": finance.get("ccer_total_value"),
            "residual_salvage_value": finance.get("residual_salvage_value"),
        }
    )
    output["carbon_results"].update(carbon)
    if industry_template:
        output["carbon_results"]["industry_template"] = industry_template
    output["sensitivity_results"] = run_sensitivity(output)
    output["data_quality_results"] = data_quality
    output["assumptions"] = _assumptions(data, scenario)
    output["data_gaps"] = missing_fields + _scenario_specific_gaps(data, scenario, profile, renewables)
    # ── 储能循环效率预警 ──────────────────────────────────────
    storage_cycles = float(annual_dispatch.get("storage_equivalent_full_cycles_per_year") or 0.0)
    cycle_warnings = []
    if float(storage.get("storage_power_mw") or 0) > 0 and storage_cycles < 200:
        cycle_warnings.append(f"储能年循环仅{storage_cycles:.0f}次，低于200次经济下限，建议重新评估储能配置。")
    elif float(storage.get("storage_power_mw") or 0) > 0 and storage_cycles < 365:
        cycle_warnings.append(f"储能年循环{storage_cycles:.0f}次，低于每日1次理想值，建议关注实际利用率。")
    output["risks"] = _risks(data, scenario, completeness_grade, profile, renewables) + data_quality["warnings"] + cycle_warnings
    output["confidence"] = _confidence(completeness_grade, missing_fields, profile, renewables)

    diagnostics = {
        "data_completeness_grade": completeness_grade,
        "missing_fields": missing_fields,
        "scenario": scenario,
        "secondary_scenarios": secondary,
        "routing_reason": reason,
        "profile": profile,
        "charging_profile": charging_profile,
        "thermal_profile": thermal_profile,
        "load_profile": load_profile,
        "dispatch": dispatch,
        "annual_dispatch": annual_dispatch,
        "thermal_annual": thermal_annual,
        "industry_template": industry_template,
        "resource_accuracy": {
            "pv": renewables.get("pv_resource_accuracy"),
            "wind": renewables.get("wind_resource_accuracy"),
        },
        "market_context": market_context,
        "data_quality": data_quality,
    }
    report = build_report(output, diagnostics)
    return output, diagnostics, report


def _grid_summary(data: dict[str, Any], profile: dict[str, Any] | None) -> str:
    grid = data.get("project_info", {}).get("grid_connection_mode") or "grid_tied"
    point = data.get("network_and_design", {}).get("point_of_connection") or "待补并网点"
    if profile:
        return f"建议按 {grid} 模式接入，接入点为 {point}，并结合 {profile['province_name']} 省级 profile 复核接入和市场边界。"
    return f"建议按 {grid} 模式接入，接入点为 {point}，并结合当地最新细则复核。"


def _dispatch_summary(scenario: str) -> str:
    mapping = {
        "charging_station": "按充电负荷高峰+储能削峰+午间光伏优先的光储充协同策略运行。",
        "thermal_system": "按冷热典型日负荷、COP 和季节性差异进行冷热电协同运行。",
        "zero_carbon_factory": "按节能优先、电气化替代、绿电覆盖和源荷储优化协同推进。",
    }
    return mapping.get(scenario, "按峰谷价差、需量控制和新能源自发自用协同优化运行。")


def _market_summary(data: dict[str, Any], profile: dict[str, Any] | None) -> str:
    market_mode = data.get("market_data", {}).get("market_mode") or "unspecified"
    if profile:
        return f"按 {market_mode} 机制建模，并参考 {profile.get('verification_status')} 省级 profile 处理市场差异。"
    return f"按 {market_mode} 机制建模，省级差异待补充。"


def _carbon_path_summary(data: dict[str, Any]) -> str:
    if data.get("carbon_data"):
        return "优先按能效提升、电气化替代、绿电覆盖、冷热协同和数字化能碳管理分阶段推进。"
    return ""


def _deviation_risk(data: dict[str, Any], profile: dict[str, Any] | None) -> str:
    if data.get("market_data", {}).get("market_price_series"):
        return "已启用市场化价格序列，需关注偏差考核与执行约束。"
    if profile and profile.get("spot_market_status"):
        return "所在省份存在市场化或现货相关规则，应区分固定分时与动态价格情景。"
    return "当前按静态或基础电价机制测算，偏差风险未深度展开。"


def _demand_charge_impact(data: dict[str, Any]) -> str:
    if data.get("market_data", {}).get("demand_charge_rule"):
        return "项目含需量或容量收费机制，储能和有序控制对收益影响明显。"
    return "当前未明确需量收费规则。"


def _assumptions(data: dict[str, Any], scenario: str) -> list[str]:
    assumptions = [
        "无第三方核证时，结论为预可研/前置分析口径。",
        "省级 profile 未覆盖的细则需人工补充复核。",
    ]
    if scenario == "zero_carbon_factory":
        assumptions.append("零碳工厂结论以范围一/二边界和环境属性归属复核为前提。")
    return assumptions


def _scenario_specific_gaps(data: dict[str, Any], scenario: str, profile: dict[str, Any] | None, renewables: dict[str, Any]) -> list[str]:
    gaps: list[str] = []
    if scenario == "charging_station" and not data.get("charging_data", {}).get("arrival_profile"):
        gaps.append("charging_data.arrival_profile")
    if scenario in {"thermal_system", "zero_carbon_factory"} and not data.get("load_data", {}).get("cooling_load_series_kw") and not data.get("load_data", {}).get("heating_load_series_kw"):
        gaps.append("load_data.cooling_load_series_kw / heating_load_series_kw")
    if scenario == "zero_carbon_factory" and not data.get("carbon_data", {}).get("baseline_emissions_tco2e"):
        gaps.append("carbon_data.baseline_emissions_tco2e")
    if renewables.get("pv_mwp") and renewables.get("pv_resource_accuracy") == "low":
        gaps.append("resource_data.solar.hourly_generation_profile_kw / monthly_irradiation_kwh_per_m2")
    if renewables.get("wind_mw") and renewables.get("wind_resource_accuracy") == "low":
        gaps.append("resource_data.wind.hourly_generation_profile_kw / monthly_capacity_factor / annual_avg_speed_mps")
    if not profile:
        gaps.append("province profile not found")
    return gaps


def _risks(data: dict[str, Any], scenario: str, completeness_grade: str, profile: dict[str, Any] | None, renewables: dict[str, Any]) -> list[str]:
    risks = []
    if completeness_grade in {"C", "D"}:
        risks.append("数据完整度较低，结果仅适合原则性预判或方案筛选。")
    if profile and profile.get("verification_status") != "verified":
        risks.append(f"{profile.get('province_name')} 省级 profile 尚非 fully verified，需复核最新细则。")
    if scenario == "charging_station":
        risks.append("充电站收益对同时率、到达分布和容量电费高度敏感。")
    if scenario in {"thermal_system", "zero_carbon_factory"}:
        risks.append("冷热负荷若缺少逐时数据，设备容量和运行收益可能偏离实际。")
    if scenario == "zero_carbon_factory":
        risks.append("零碳声明需额外满足碳核算边界、环境属性归属和第三方评价要求。")
    if renewables.get("pv_mwp") and renewables.get("pv_resource_accuracy") != "high":
        risks.append(f"光伏发电量当前基于 {renewables.get('pv_resource_basis')} 估算，资源精度仍可提升。")
    if renewables.get("wind_mw") and renewables.get("wind_resource_accuracy") != "high":
        risks.append(f"风电发电量当前基于 {renewables.get('wind_resource_basis')} 估算，正式方案前应补充更高质量资源数据。")
    return risks


def _confidence(
    completeness_grade: str,
    missing_fields: list[str],
    profile: dict[str, Any] | None,
    renewables: dict[str, Any],
) -> dict[str, str]:
    resource_high = all(
        level in (None, "high", "medium")
        for level in (renewables.get("pv_resource_accuracy"), renewables.get("wind_resource_accuracy"))
    )
    if completeness_grade == "A" and profile and profile.get("verification_status") == "verified" and resource_high:
        level = "high"
    elif completeness_grade in {"A", "B"}:
        level = "medium"
    else:
        level = "low"
    reason = f"数据完整度 {completeness_grade}"
    if missing_fields:
        reason += f"，缺失字段 {len(missing_fields)} 项"
    if profile:
        reason += f"，省级 profile 状态 {profile.get('verification_status')}"
    else:
        reason += "，未命中省级 profile"
    if renewables.get("pv_resource_accuracy"):
        reason += f"，PV资源精度 {renewables.get('pv_resource_accuracy')}"
    if renewables.get("wind_mw") is not None:
        reason += f"，风资源精度 {renewables.get('wind_resource_accuracy')}"
    return {"level": level, "reason": reason}
