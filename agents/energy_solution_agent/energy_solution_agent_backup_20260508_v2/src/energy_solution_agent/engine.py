from __future__ import annotations

import itertools
import logging
from typing import Any

logger = logging.getLogger(__name__)

from .annual_series import build_annual_series, extrapolate_sample_period_series, preserve_subhourly_year_series
from .candidates import generate_candidate_solutions
from .completeness import evaluate_data_completeness
from .constants import DEFAULT_HEAT_PUMP_COP, DEFAULT_THERMAL_COP
from .data_quality import assess_data_quality
from .industry_templates import get_industry_template
from .live_rules import apply_live_rule_patch, fetch_live_rule_patch
from .data_ingest import ingest_external_series
from .material_extract import enrich_from_material_workbooks
from .normalize import normalize_input
from .network_http import get_proxy_url
from .profiles import get_province_profile
from .province_overrides import apply_province_overrides
from .province_adapter import build_market_context
from .province_cycle_rules import enrich_from_province_cycle_rules
from .province_tou_schedule import enrich_from_province_tou_schedule_workbook
from .policy_classify import classify_market_policy_mode
from .resource_fetch import enrich_with_auto_resource_data
from .resource_models import estimate_pv_generation, estimate_wind_generation
from .reporting import build_report
from .router import classify_business_scenario, route_scenario, route_source_grid_load_storage_operation_mode
from .schema import new_output
from .series_align import align_annual_series_to_length
from .sensitivity import run_sensitivity
from .settlement import (
    ancillary_and_dr_revenue,
    annual_demand_charge,
    annual_energy_charge,
    build_hourly_price_series,
    extract_valley_hours,
    resolve_price_series_start_weekday,
    summarize_power_trading_settlement,
)
from .solvers import (
    apply_storage_product_selection,
    assemble_design_notes,
    estimate_carbon,
    optimize_offgrid_pv_storage,
    estimate_storage,
    simulate_spot_intraday_arbitrage,
    simulate_annual_cycle_value,
    simulate_commercial_hybrid_value,
    simulate_rule_based_arbitrage,
    simulate_thermal_equipment_annual,
    simulate_storage_dispatch_annual,
    settlement_and_finance,
    simulate_storage_dispatch,
    synthesize_charging_profile,
    synthesize_thermal_profile,
)
from .tou_policy_fetch import enrich_with_monthly_tou_policy_history
from .timeseries import to_hourly_profile


def analyze_project(payload: dict[str, Any], enable_live_rules: bool = False) -> tuple[dict[str, Any], dict[str, Any], str]:
    data = apply_province_overrides(ingest_external_series(normalize_input(payload)))
    data = enrich_from_material_workbooks(data)
    data = enrich_from_province_tou_schedule_workbook(data)
    data = enrich_from_province_cycle_rules(data)
    data, resource_fetch_meta = enrich_with_auto_resource_data(data)
    proxy_url = get_proxy_url(data.get("network"))
    backup_cfg = data.get("equipment", {}).get("conventional_backup", {})
    if backup_cfg.get("fuel_cost_per_kwh") is not None and data.get("market_data", {}).get("fuel_cost_per_kwh") is None:
        data.setdefault("market_data", {})["fuel_cost_per_kwh"] = float(backup_cfg.get("fuel_cost_per_kwh"))
    data_quality = assess_data_quality(data)
    completeness_grade, missing_fields = evaluate_data_completeness(data)
    scenario, secondary, reason = route_scenario(data)
    scenario_detail_code, scenario_detail_label = classify_business_scenario(data, scenario)
    operation_mode, operation_mode_reason = route_source_grid_load_storage_operation_mode(data)
    analysis_mode = _resolve_analysis_mode(data, operation_mode)
    if operation_mode:
        data.setdefault("project_info", {})["operation_mode"] = operation_mode
    if analysis_mode:
        data.setdefault("project_info", {})["analysis_mode"] = analysis_mode
    profile = get_province_profile(data.get("project_info", {}).get("province"))
    data, tou_policy_fetch_meta = enrich_with_monthly_tou_policy_history(data, profile)
    data = classify_market_policy_mode(data, tou_policy_fetch_meta.get("tou_policy_fetch_sources"))
    live_patch = fetch_live_rule_patch(profile, proxy_url=proxy_url) if enable_live_rules else None
    data["market_data"] = apply_live_rule_patch(data.get("market_data", {}), (live_patch or {}).get("structured_patch"))
    market_context = build_market_context(profile, data.get("market_data", {}), live_patch=live_patch)

    charging_profile, charging_summary = synthesize_charging_profile(data)
    thermal_profile, thermal_summary = synthesize_thermal_profile(data)
    raw_load_series = [float(v) for v in (data.get("load_data", {}).get("load_series_kw") or [])]
    load_profile = to_hourly_profile(
        raw_load_series,
        annual_target_mwh=float(data.get("load_data", {}).get("annual_consumption_mwh") or 0.0) or None,
        fallback_peak_kw=float(data.get("load_data", {}).get("peak_load_kw") or 1000),
    )
    load_series = (
        preserve_subhourly_year_series(raw_load_series)
        or extrapolate_sample_period_series(
            raw_load_series,
            sample_months=data.get("load_data", {}).get("sample_months"),
            sample_month_map=data.get("load_data", {}).get("sample_month_map"),
            annual_target_mwh=float(data.get("load_data", {}).get("annual_consumption_mwh") or 0.0) or None,
        )
        or build_annual_series(
        raw_series=raw_load_series,
        fallback_daily=load_profile,
        annual_target_mwh=float(data.get("load_data", {}).get("annual_consumption_mwh") or 0.0) or None,
        monthly_factors=data.get("load_data", {}).get("monthly_load_factors"),
        )
    )
    pv_result = estimate_pv_generation(data)
    wind_result = estimate_wind_generation(data)
    renewables = {**pv_result, **wind_result}
    renewable_lcoe = _derive_renewable_lcoe(data, renewables)
    data.setdefault("market_data", {}).setdefault("solar_lcoe_per_kwh", renewable_lcoe["pv_lcoe_per_kwh"])
    data.setdefault("market_data", {}).setdefault("wind_lcoe_per_kwh", renewable_lcoe["wind_lcoe_per_kwh"])
    target_series_len = len(load_series)
    pv_series_aligned = align_annual_series_to_length(renewables.get("pv_annual_series_kw", [0.0] * 8760), target_series_len)
    wind_series_aligned = align_annual_series_to_length(renewables.get("wind_annual_series_kw", [0.0] * 8760), target_series_len)
    price_series_start_weekday = resolve_price_series_start_weekday(data)
    prelim_prices = build_hourly_price_series(
        data.get("market_data", {}),
        len(load_series),
        start_weekday=price_series_start_weekday,
    )
    annual_load = float(data.get("load_data", {}).get("annual_consumption_mwh") or 0.0)
    annual_cooling = float(thermal_summary.get("annual_cooling_energy_mwh") or 0.0) if thermal_summary.get("annual_cooling_energy_mwh") is not None else 0.0
    annual_heating = float(thermal_summary.get("annual_heating_energy_mwh") or 0.0) if thermal_summary.get("annual_heating_energy_mwh") is not None else 0.0
    thermal_daily = [
        a + b for a, b in itertools.zip_longest(
            thermal_profile.get("cooling_electric_kw", []),
            thermal_profile.get("heating_electric_kw", []),
            fillvalue=0.0,
        )
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
    charging_series = align_annual_series_to_length(charging_series, target_series_len)
    cooling_series = align_annual_series_to_length(cooling_series, target_series_len)
    heating_series = align_annual_series_to_length(heating_series, target_series_len)
    thermal_series = align_annual_series_to_length(thermal_annual["thermal_electric_series_kw"], target_series_len)
    offgrid_optimized = optimize_offgrid_pv_storage(
        data,
        pv_result=pv_result,
        wind_result=wind_result,
        load_series_kw=load_series,
        charging_series_kw=charging_series,
        thermal_series_kw=thermal_series,
        price_series=prelim_prices,
    )
    if offgrid_optimized:
        renewables = offgrid_optimized["renewables"]
        storage = offgrid_optimized["storage"]
        pv_series_aligned = align_annual_series_to_length(renewables.get("pv_annual_series_kw", [0.0] * 8760), target_series_len)
        wind_series_aligned = align_annual_series_to_length(renewables.get("wind_annual_series_kw", [0.0] * 8760), target_series_len)
        sizing_load_series: list[float] = []
        storage_sizing_basis = "offgrid_optimization"
    else:
        sizing_load_series, storage_sizing_basis = _build_storage_sizing_load_series(
            scenario_detail_code=scenario_detail_code,
            operation_mode=operation_mode,
            load_series_kw=load_series,
            pv_series_kw=pv_series_aligned,
            wind_series_kw=wind_series_aligned,
        )
        # For charging station scenarios, merge the charging load into the sizing
        # load curve so that series-based storage sizing sees the full demand profile
        # rather than just the base building load.
        if scenario == "charging_station" and charging_series:
            horizon = min(len(sizing_load_series), len(charging_series))
            sizing_load_series = [
                float(sizing_load_series[idx]) + float(charging_series[idx])
                for idx in range(horizon)
            ]
            storage_sizing_basis = "load_plus_charging"
        storage = estimate_storage(
            data,
            charging_peak_kw=float(charging_summary.get("charging_peak_kw") or 0.0),
            thermal_coupling_kw=float(sum(thermal_profile.get("cooling_electric_kw", [])) + sum(thermal_profile.get("heating_electric_kw", []))) / 24 if thermal_profile else 0.0,
            load_series_kw=sizing_load_series,
            pv_series_kw=pv_series_aligned,
            wind_series_kw=wind_series_aligned,
            operation_mode=operation_mode,
        )
    renewable_interaction = _summarize_renewable_interaction(load_series, pv_series_aligned, wind_series_aligned)
    storage = apply_storage_product_selection(data, storage)
    annual_pv = float(renewables.get("annual_pv_generation_mwh") or 0.0)
    annual_wind = float(renewables.get("annual_wind_generation_mwh") or 0.0)
    annual_charging = float(charging_summary.get("annual_charging_energy_mwh") or 0.0)
    storage_strategy = _resolve_storage_strategy_mode(data, operation_mode)
    dispatch = simulate_storage_dispatch(
        load_profile_kw=load_profile,
        pv_profile_kw=renewables.get("pv_hourly_profile_kw", [0.0] * 24),
        wind_profile_kw=renewables.get("wind_hourly_profile_kw", [0.0] * 24),
        charging_profile_kw=charging_profile,
        thermal_electric_kw=thermal_electric_profile,
        storage_power_mw=storage.get("storage_power_mw"),
        storage_energy_mwh=storage.get("storage_energy_mwh"),
        valley_hours=extract_valley_hours(data.get("market_data", {})),
    )
    annual_dispatch = simulate_storage_dispatch_annual(
        load_series_kw=load_series,
        pv_series_kw=pv_series_aligned,
        wind_series_kw=wind_series_aligned,
        charging_series_kw=charging_series,
        thermal_series_kw=thermal_series,
        storage_power_mw=storage.get("storage_power_mw"),
        storage_energy_mwh=storage.get("storage_energy_mwh"),
        strategy_mode=storage_strategy,
        price_series=prelim_prices,
        storage_config=data.get("equipment", {}).get("storage", {}),
        market=data.get("market_data", {}),
        operation_mode=operation_mode,
    )
    active_storage_value_model = ""
    rule_based_arbitrage = None
    annual_cycle_value = None
    commercial_hybrid_value = None
    spot_intraday_value = None
    if scenario == "user_side_storage":
        _validate_user_side_storage_value_models(data)
        spot_intraday_value = simulate_spot_intraday_arbitrage(data, storage)
        rule_based_arbitrage = simulate_rule_based_arbitrage(data, storage)
        annual_cycle_value = simulate_annual_cycle_value(data, storage)
        commercial_hybrid_value = simulate_commercial_hybrid_value(data, renewables, storage)

    gross_demand = annual_load + annual_charging + (annual_cooling / DEFAULT_THERMAL_COP if annual_cooling else 0.0) + (annual_heating / DEFAULT_HEAT_PUMP_COP if annual_heating else 0.0)
    annual_grid_purchase = annual_dispatch["annual_grid_purchase_mwh"]
    annual_export = float(annual_dispatch.get("annual_export_mwh") or 0.0)
    annual_curtailment = float(annual_dispatch.get("curtailed_renewable_mwh") or 0.0)
    coverage_ratio = (gross_demand - annual_grid_purchase) / gross_demand if gross_demand > 0 else None

    simulation = {
        **renewables,
        **storage,
        **charging_summary,
        **thermal_summary,
        "annual_renewable_direct_use_mwh": renewable_interaction["annual_renewable_direct_use_mwh"],
        "annual_renewable_surplus_mwh": renewable_interaction["annual_renewable_surplus_mwh"],
        "annual_renewable_to_storage_mwh": round(float(annual_dispatch.get("renewable_to_storage_mwh") or 0.0), 2),
        "annual_renewable_to_load_mwh": round(float(annual_dispatch.get("renewable_to_load_mwh") or 0.0), 2),
        "annual_grid_to_load_mwh": round(float(annual_dispatch.get("grid_to_load_mwh") or 0.0), 2),
        "annual_grid_to_storage_mwh": round(float(annual_dispatch.get("grid_to_storage_mwh") or 0.0), 2),
        "annual_storage_charge_mwh": round(float(annual_dispatch.get("storage_annual_throughput_mwh") or 0.0) / 2, 2),
        "annual_storage_discharge_mwh": round(float(annual_dispatch.get("storage_annual_throughput_mwh") or 0.0) / 2, 2),
        "annual_grid_purchase_mwh": round(annual_grid_purchase, 2),
        "annual_export_mwh": round(annual_export, 2),
        "annual_curtailment_mwh": round(annual_curtailment, 2),
        "coverage_ratio": round(coverage_ratio, 4) if coverage_ratio is not None else None,
        "renewable_energy_coverage_ratio": round((annual_pv + annual_wind) / gross_demand, 4) if gross_demand > 0 else None,
    }
    # Cascade: storage dispatch results. Later modes override earlier ones.
    # Only one mode should be active at a time; log warnings if multiple fire.
    _last_charge_source = "dispatch"
    if rule_based_arbitrage:
        simulation["annual_storage_charge_mwh"] = rule_based_arbitrage["annual_charge_mwh"]
        simulation["annual_storage_discharge_mwh"] = rule_based_arbitrage["annual_discharge_mwh"]
        _last_charge_source = "rule_based_arbitrage"
    if spot_intraday_value:
        if _last_charge_source not in ("dispatch", "spot_intraday_value"):
            logger.warning("spot_intraday_value overwrites %s charge/discharge values", _last_charge_source)
        simulation["annual_storage_charge_mwh"] = spot_intraday_value["annual_charge_mwh"]
        simulation["annual_storage_discharge_mwh"] = spot_intraday_value["annual_discharge_mwh"]
        _last_charge_source = "spot_intraday_value"
    if annual_cycle_value:
        if _last_charge_source not in ("dispatch", "annual_cycle_value"):
            logger.warning("annual_cycle_value overwrites %s charge/discharge values", _last_charge_source)
        simulation["annual_storage_charge_mwh"] = annual_cycle_value["annual_charge_mwh"]
        simulation["annual_storage_discharge_mwh"] = annual_cycle_value["annual_discharge_mwh"]
        _last_charge_source = "annual_cycle_value"
    if commercial_hybrid_value:
        if _last_charge_source not in ("dispatch", "commercial_hybrid_value"):
            logger.warning("commercial_hybrid_value overwrites %s charge/discharge values", _last_charge_source)
        simulation["annual_storage_charge_mwh"] = commercial_hybrid_value["annual_charge_mwh"]
        simulation["annual_storage_discharge_mwh"] = commercial_hybrid_value["annual_discharge_mwh"]
        _last_charge_source = "commercial_hybrid_value"
    industry_template = get_industry_template(data.get("carbon_data", {}).get("industry_type"))
    carbon = estimate_carbon(data, simulation)
    prices = build_hourly_price_series(
        data.get("market_data", {}),
        len(annual_dispatch["post_storage_grid_series_kw"]),
        start_weekday=price_series_start_weekday,
    )
    interval_hours = 8760.0 / len(annual_dispatch["post_storage_grid_series_kw"]) if annual_dispatch["post_storage_grid_series_kw"] else 1.0
    baseline_energy_charge_cost = annual_energy_charge(annual_dispatch["baseline_grid_series_kw"], prices, interval_hours=interval_hours)
    post_energy_charge_cost = annual_energy_charge(annual_dispatch["post_storage_grid_series_kw"], prices, interval_hours=interval_hours)
    baseline_demand_charge_cost = annual_demand_charge(annual_dispatch["baseline_grid_series_kw"], data.get("market_data", {}), interval_hours=interval_hours)
    post_demand_charge_cost = annual_demand_charge(annual_dispatch["post_storage_grid_series_kw"], data.get("market_data", {}), interval_hours=interval_hours)
    # Cascade: storage value override. Later arbitrage modes override earlier ones.
    # Only one mode should be active; log warnings if multiple fire.
    storage_value_override = None
    _last_value_source = None
    if scenario == "user_side_storage" and not renewables.get("pv_mwp") and not renewables.get("wind_mw"):
        storage_value_override = max(
            0.0,
            baseline_energy_charge_cost + baseline_demand_charge_cost - post_energy_charge_cost - post_demand_charge_cost,
        )
        _last_value_source = "baseline_delta"
    if rule_based_arbitrage:
        if _last_value_source is not None:
            logger.warning("rule_based_arbitrage overwrites storage_value_override from %s", _last_value_source)
        storage_value_override = rule_based_arbitrage["annual_gross_margin"]
        _last_value_source = "rule_based_arbitrage"
    if spot_intraday_value:
        if _last_value_source is not None and _last_value_source != "spot_intraday_value":
            logger.warning("spot_intraday_value overwrites storage_value_override from %s", _last_value_source)
        storage_value_override = spot_intraday_value["annual_gross_margin"]
        _last_value_source = "spot_intraday_value"
    if annual_cycle_value:
        if _last_value_source is not None and _last_value_source != "annual_cycle_value":
            logger.warning("annual_cycle_value overwrites storage_value_override from %s", _last_value_source)
        storage_value_override = annual_cycle_value["annual_gross_margin"]
        _last_value_source = "annual_cycle_value"
    if commercial_hybrid_value:
        if _last_value_source is not None and _last_value_source != "commercial_hybrid_value":
            logger.warning("commercial_hybrid_value overwrites storage_value_override from %s", _last_value_source)
        storage_value_override = commercial_hybrid_value["annual_gross_margin"]
        _last_value_source = "commercial_hybrid_value"
    if operation_mode == "renewable_market_cooptimization" and annual_dispatch.get("storage_market_value") is not None:
        if _last_value_source is not None:
            logger.warning("market_cooptimization overwrites storage_value_override from %s", _last_value_source)
        storage_value_override = float(annual_dispatch.get("storage_market_value") or 0.0)
        _last_value_source = "market_cooptimization"
    active_storage_value_model = _last_value_source or ""
    storage_power_mw = float(storage.get("storage_power_mw") or 0.0)
    peak_reduction_kw = float(annual_dispatch.get("peak_reduction_kw") or 0.0)
    extra_revenue = ancillary_and_dr_revenue(storage_power_mw, peak_reduction_kw, data.get("market_data", {}))
    extra_annual_revenue = float(extra_revenue["annual_ancillary_service_revenue"]) + float(extra_revenue["annual_demand_response_revenue"])
    finance = settlement_and_finance(
        data,
        simulation,
        carbon,
        storage_value_override=storage_value_override,
        extra_annual_revenue=extra_annual_revenue,
    )
    finance.update(extra_revenue)
    finance["annual_energy_charge_cost"] = _resolve_annual_energy_charge_cost(
        post_energy_charge_cost=post_energy_charge_cost,
        baseline_energy_charge_cost=baseline_energy_charge_cost,
        scenario=scenario,
        rule_based_arbitrage=rule_based_arbitrage,
        spot_intraday_value=spot_intraday_value,
        annual_cycle_value=annual_cycle_value,
        commercial_hybrid_value=commercial_hybrid_value,
    )
    finance["annual_demand_charge_cost"] = round(post_demand_charge_cost, 2)
    trading_settlement = {}
    if data.get("market_data", {}).get("market_price_series") or data.get("market_data", {}).get("market_price_series_path"):
        trading_settlement = summarize_power_trading_settlement(
            data.get("market_data", {}),
            _resolve_output_monthly_breakdown(
                annual_dispatch=annual_dispatch,
                spot_intraday_value=spot_intraday_value,
                rule_based_arbitrage=rule_based_arbitrage,
                annual_cycle_value=annual_cycle_value,
                commercial_hybrid_value=commercial_hybrid_value,
            ),
        )
    design = assemble_design_notes(data, profile, scenario, float(charging_summary.get("charging_peak_kw") or 0.0))

    output = new_output()
    project = data.get("project_info", {})
    output["project_summary"].update(
        {
            "project_name": project.get("project_name") or "",
            "scenario_type": scenario,
            "scenario_detail_code": scenario_detail_code,
            "scenario_detail_label": scenario_detail_label,
            "operation_mode": operation_mode,
            "analysis_mode": analysis_mode,
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
            "zero_carbon_factory_recommended": scenario == "zero_carbon_factory" or bool(data.get("carbon_data")),
        }
    )
    output["recommended_solution"].update(
        {
            "pv_mwp": renewables.get("pv_mwp"),
            "wind_mw": renewables.get("wind_mw"),
            "storage_power_mw": storage.get("storage_power_mw"),
            "storage_energy_mwh": storage.get("storage_energy_mwh"),
            "raw_storage_power_mw": storage.get("raw_storage_power_mw"),
            "raw_storage_energy_mwh": storage.get("raw_storage_energy_mwh"),
            "selected_product_power_mw": storage.get("selected_product_power_mw"),
            "selected_product_energy_mwh": storage.get("selected_product_energy_mwh"),
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
            "pv_effective_tilt_deg": renewables.get("pv_effective_tilt_deg"),
            "pv_recommended_tilt_deg": renewables.get("pv_recommended_tilt_deg"),
            "pv_tilt_factor": renewables.get("pv_tilt_factor"),
            "pv_azimuth_factor": renewables.get("pv_azimuth_factor"),
            "pv_tracking_factor": renewables.get("pv_tracking_factor"),
            "pv_temperature_factor": renewables.get("pv_temperature_factor"),
            "pv_pr_effective": renewables.get("pv_pr_effective"),
            "pv_lcoe_per_kwh": renewable_lcoe["pv_lcoe_per_kwh"],
            "wind_resource_accuracy": renewables.get("wind_resource_accuracy"),
            "wind_resource_basis": renewables.get("wind_resource_basis"),
            "wind_p50_generation_mwh": renewables.get("wind_p50_generation_mwh"),
            "wind_p90_generation_mwh": renewables.get("wind_p90_generation_mwh"),
            "wind_power_curve_used": renewables.get("wind_power_curve_used"),
            "wind_mean_speed_mps": renewables.get("wind_mean_speed_mps"),
            "wind_net_factor": renewables.get("wind_net_factor"),
            "wind_lcoe_per_kwh": renewable_lcoe["wind_lcoe_per_kwh"],
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
            "operation_mode": operation_mode,
            "operation_mode_routing_reason": operation_mode_reason,
            "analysis_mode": analysis_mode,
            "storage_sizing_basis": storage_sizing_basis,
            "sizing_net_load_peak_kw": renewable_interaction["sizing_net_load_peak_kw"],
            "charging_queue_index": charging_summary.get("charging_queue_index"),
            "storage_annual_throughput_mwh": round(float(annual_dispatch.get("storage_annual_throughput_mwh") or 0.0), 2),
            "storage_equivalent_full_cycles_per_year": round(float(annual_dispatch.get("storage_equivalent_full_cycles_per_year") or 0.0), 3),
            "storage_power_utilization_ratio": storage.get("storage_power_utilization_ratio"),
            "storage_energy_utilization_ratio": storage.get("storage_energy_utilization_ratio"),
            "storage_power_oversize_ratio": storage.get("storage_power_oversize_ratio"),
            "storage_energy_oversize_ratio": storage.get("storage_energy_oversize_ratio"),
            "storage_life_years_estimate": round(float(annual_dispatch.get("storage_life_years_estimate") or 0.0), 2) if annual_dispatch.get("storage_life_years_estimate") else None,
            "storage_charge_from_renewables_ratio": round(float(annual_dispatch.get("storage_charge_from_renewables_ratio") or 0.0), 4) if annual_dispatch.get("storage_charge_from_renewables_ratio") is not None else None,
            "storage_effective_round_trip_efficiency": round(float(annual_dispatch.get("storage_effective_round_trip_efficiency") or 0.0), 4) if annual_dispatch.get("storage_effective_round_trip_efficiency") is not None else None,
            "renewable_to_storage_mwh": round(float(annual_dispatch.get("renewable_to_storage_mwh") or 0.0), 2),
            "renewable_to_load_mwh": round(float(annual_dispatch.get("renewable_to_load_mwh") or 0.0), 2),
            "grid_to_load_mwh": round(float(annual_dispatch.get("grid_to_load_mwh") or 0.0), 2),
            "grid_to_storage_mwh": round(float(annual_dispatch.get("grid_to_storage_mwh") or 0.0), 2),
            "curtailed_renewable_mwh": round(float(annual_dispatch.get("curtailed_renewable_mwh") or 0.0), 2),
            "daily_cycle_schedule": annual_dispatch.get("daily_cycle_schedule") or [],
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
    # NOTE: The following dispatch_results override cascade has a highly repetitive pattern
    # (rule_based_arbitrage, spot_intraday_value, annual_cycle_value, commercial_hybrid_value).
    # Each block sets the same 6 keys. Future refactoring could extract a shared helper
    # that accepts a source dict and a key-mapping config.
    if rule_based_arbitrage:
        output["dispatch_results"]["daily_storage_cycles"] = rule_based_arbitrage["daily_cycles"]
        output["dispatch_results"]["storage_annual_throughput_mwh"] = round(
            rule_based_arbitrage["annual_charge_mwh"] + rule_based_arbitrage["annual_discharge_mwh"],
            2,
        )
        output["dispatch_results"]["storage_equivalent_full_cycles_per_year"] = rule_based_arbitrage["annual_fec"]
        output["dispatch_results"]["storage_life_years_estimate"] = rule_based_arbitrage["storage_life_years_estimate"]
        output["dispatch_results"]["storage_end_of_life_capacity_ratio"] = rule_based_arbitrage["storage_end_of_life_capacity_ratio"]
        output["dispatch_results"]["monthly_storage_revenue_breakdown"] = rule_based_arbitrage["monthly_storage_revenue_breakdown"]
    if spot_intraday_value:
        output["dispatch_results"]["daily_storage_cycles"] = spot_intraday_value["daily_cycles"]
        output["dispatch_results"]["storage_annual_throughput_mwh"] = round(
            spot_intraday_value["annual_charge_mwh"] + spot_intraday_value["annual_discharge_mwh"],
            2,
        )
        output["dispatch_results"]["storage_equivalent_full_cycles_per_year"] = spot_intraday_value["annual_fec"]
        output["dispatch_results"]["storage_life_years_estimate"] = spot_intraday_value["storage_life_years_estimate"]
        output["dispatch_results"]["storage_end_of_life_capacity_ratio"] = spot_intraday_value["storage_end_of_life_capacity_ratio"]
        output["dispatch_results"]["monthly_storage_revenue_breakdown"] = spot_intraday_value["monthly_storage_revenue_breakdown"]
        output["dispatch_results"]["daily_cycle_schedule"] = _normalize_spot_daily_cycle_schedule(
            spot_intraday_value["daily_spot_arbitrage_schedule"]
        )
    if annual_cycle_value:
        output["dispatch_results"]["daily_storage_cycles"] = annual_cycle_value["daily_cycles"]
        output["dispatch_results"]["storage_annual_throughput_mwh"] = round(
            annual_cycle_value["annual_charge_mwh"] + annual_cycle_value["annual_discharge_mwh"],
            2,
        )
        output["dispatch_results"]["storage_equivalent_full_cycles_per_year"] = annual_cycle_value["annual_fec"]
        output["dispatch_results"]["storage_life_years_estimate"] = annual_cycle_value["storage_life_years_estimate"]
        output["dispatch_results"]["storage_end_of_life_capacity_ratio"] = annual_cycle_value["storage_end_of_life_capacity_ratio"]
        output["dispatch_results"]["monthly_storage_revenue_breakdown"] = annual_cycle_value["monthly_storage_revenue_breakdown"]
    if commercial_hybrid_value:
        output["dispatch_results"]["daily_storage_cycles"] = commercial_hybrid_value["daily_cycles"]
        output["dispatch_results"]["storage_annual_throughput_mwh"] = round(
            commercial_hybrid_value["annual_charge_mwh"] + commercial_hybrid_value["annual_discharge_mwh"],
            2,
        )
        output["dispatch_results"]["storage_equivalent_full_cycles_per_year"] = commercial_hybrid_value["annual_fec"]
        output["dispatch_results"]["storage_life_years_estimate"] = commercial_hybrid_value["storage_life_years_estimate"]
        output["dispatch_results"]["storage_end_of_life_capacity_ratio"] = commercial_hybrid_value["storage_end_of_life_capacity_ratio"]
        output["dispatch_results"]["monthly_storage_revenue_breakdown"] = commercial_hybrid_value["monthly_storage_revenue_breakdown"]
    output["market_and_settlement"].update(
        {
            "market_mode": data.get("market_data", {}).get("market_mode") or "",
            "market_policy_mode": data.get("market_data", {}).get("market_policy_mode") or "",
            "price_mechanism_summary": finance["price_mechanism_summary"],
            "revenue_breakdown": finance["revenue_breakdown"],
            "active_storage_value_model": active_storage_value_model,
            "cooptimization_execution_summary": _cooptimization_execution_summary(data, output, annual_dispatch),
            "historical_backtest_days": _historical_backtest_days(load_series),
            "historical_backtest_charge_price_avg": _historical_backtest_charge_price_avg(output, prelim_prices),
            "historical_backtest_discharge_price_avg": _historical_backtest_discharge_price_avg(output, prelim_prices),
            "monthly_tou_policy_history": data.get("market_data", {}).get("monthly_tou_policy_history") or [],
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
            "spot_trading_days_covered": spot_intraday_value["days_covered"] if spot_intraday_value else None,
            "spot_trading_total_cycles": spot_intraday_value["total_cycles"] if spot_intraday_value else None,
            "spot_trading_average_spread_yuan_per_mwh": spot_intraday_value["average_spread_yuan_per_mwh"] if spot_intraday_value else None,
            "spot_trading_cycle_summary": spot_intraday_value["cycle_summary"] if spot_intraday_value else "",
            "daily_spot_arbitrage_schedule": spot_intraday_value["daily_spot_arbitrage_schedule"] if spot_intraday_value else [],
            **trading_settlement,
        }
    )
    output["design_and_interconnection"].update(design)
    output["financial_results"].update(
        {
            "capex_total": finance["capex_total"],
            "opex_annual": finance["opex_annual"],
            "annual_savings_or_revenue": finance["annual_savings_or_revenue"],
            "annual_tax_total": finance["annual_tax_total"],
            "annual_income_tax": finance["annual_income_tax"],
            "annual_vat_and_surcharges": finance["annual_vat_and_surcharges"],
            "annual_vat_payable": finance.get("annual_vat_payable"),
            "annual_vat_surcharges_only": finance.get("annual_vat_surcharges_only"),
            "initial_input_vat_credit": finance.get("initial_input_vat_credit"),
            "tax_model": finance["tax_model"],
            "irr": finance["irr"],
            "payback_years": finance["payback_years"],
            "npv": finance["npv"],
            "abatement_cost_per_tco2e": finance["abatement_cost_per_tco2e"],
            "annual_energy_charge_cost": finance["annual_energy_charge_cost"],
            "annual_demand_charge_cost": finance["annual_demand_charge_cost"],
            "annual_ancillary_service_revenue": finance["annual_ancillary_service_revenue"],
            "annual_demand_response_revenue": finance["annual_demand_response_revenue"],
            "annual_export_revenue": finance["annual_export_revenue"],
            "storage_replacement_year": finance["storage_replacement_year"],
            "storage_replacement_cost": finance["storage_replacement_cost"],
            "opex_escalation_rate": finance["opex_escalation_rate"],
        }
    )
    output["carbon_results"].update(carbon)
    if industry_template:
        output["carbon_results"]["industry_template"] = industry_template
    output["sensitivity_results"] = run_sensitivity(output)
    output["data_quality_results"] = data_quality
    output["assumptions"] = _assumptions(data, scenario)
    output["data_gaps"] = missing_fields + _scenario_specific_gaps(data, scenario, profile, renewables)
    output["risks"] = _risks(data, scenario, completeness_grade, profile, renewables) + data_quality["warnings"]
    output["confidence"] = _confidence(completeness_grade, missing_fields, profile, renewables)

    diagnostics = {
        "data_completeness_grade": completeness_grade,
        "missing_fields": missing_fields,
        "scenario": scenario,
        "secondary_scenarios": secondary,
        "routing_reason": reason,
        "operation_mode": operation_mode,
        "operation_mode_routing_reason": operation_mode_reason,
        "analysis_mode": analysis_mode,
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
        "resource_fetch": resource_fetch_meta,
        "tou_policy_fetch": tou_policy_fetch_meta,
        "network_proxy": proxy_url or "",
    }
    report = build_report(output, diagnostics)
    return output, diagnostics, report


def _build_storage_sizing_load_series(
    scenario_detail_code: str,
    operation_mode: str,
    load_series_kw: list[float],
    pv_series_kw: list[float],
    wind_series_kw: list[float],
) -> tuple[list[float], str]:
    if scenario_detail_code != "source_grid_load_storage":
        return [float(v) for v in load_series_kw], "raw_load_curve"
    if operation_mode in {"renewable_market_cooptimization", "renewable_export_oriented"}:
        return [float(v) for v in load_series_kw], "renewable_market_cooptimized_proxy"
    horizon = min(len(load_series_kw), len(pv_series_kw), len(wind_series_kw))
    net_load = [
        max(0.0, float(load_series_kw[idx]) - float(pv_series_kw[idx]) - float(wind_series_kw[idx]))
        for idx in range(horizon)
    ]
    if len(load_series_kw) > horizon:
        net_load.extend(float(v) for v in load_series_kw[horizon:])
    return net_load, "net_load_after_pv_wind"


def _derive_renewable_lcoe(data: dict[str, Any], renewables: dict[str, Any]) -> dict[str, float | None]:
    financial = data.get("financial", {}) or {}
    capex = financial.get("capex", {}) or {}
    degradation = financial.get("degradation") or {}
    pv_lcoe = _technology_lcoe_per_kwh(
        installed_mw=float(renewables.get("pv_mwp") or 0.0),
        annual_generation_mwh=float(renewables.get("pv_p50_generation_mwh") or 0.0),
        capex_per_w=float(capex.get("pv_cost_per_w") or 1.8),
        years=max(1, int(financial.get("renewable_lifetime_years") or 25)),
        annual_degradation=float(degradation.get("pv_degradation_per_year") or 0.005),
    )
    wind_lcoe = _technology_lcoe_per_kwh(
        installed_mw=float(renewables.get("wind_mw") or 0.0),
        annual_generation_mwh=float(renewables.get("wind_p50_generation_mwh") or 0.0),
        capex_per_w=float(capex.get("wind_cost_per_w") or 3.5),
        years=max(1, int(financial.get("renewable_lifetime_years") or 25)),
        annual_degradation=float(degradation.get("wind_degradation_per_year") or 0.003),
    )
    return {
        "pv_lcoe_per_kwh": round(pv_lcoe, 4) if pv_lcoe is not None else None,
        "wind_lcoe_per_kwh": round(wind_lcoe, 4) if wind_lcoe is not None else None,
    }


def _technology_lcoe_per_kwh(
    installed_mw: float,
    annual_generation_mwh: float,
    capex_per_w: float,
    years: int,
    annual_degradation: float,
) -> float | None:
    if installed_mw <= 0 or annual_generation_mwh <= 0 or capex_per_w <= 0 or years <= 0:
        return None
    capex_total = installed_mw * 1_000_000 * capex_per_w
    lifetime_generation_kwh = 0.0
    for year in range(years):
        factor = max(0.0, 1.0 - annual_degradation * year)
        lifetime_generation_kwh += annual_generation_mwh * factor * 1000
    if lifetime_generation_kwh <= 0:
        return None
    return capex_total / lifetime_generation_kwh


def _summarize_renewable_interaction(
    load_series_kw: list[float],
    pv_series_kw: list[float],
    wind_series_kw: list[float],
) -> dict[str, float | None]:
    horizon = min(len(load_series_kw), len(pv_series_kw), len(wind_series_kw))
    if horizon <= 0:
        return {
            "annual_renewable_direct_use_mwh": None,
            "annual_renewable_surplus_mwh": None,
            "sizing_net_load_peak_kw": None,
        }
    interval_hours = 8760.0 / horizon
    direct_use_mwh = 0.0
    surplus_mwh = 0.0
    net_load_peak_kw = 0.0
    for idx in range(horizon):
        load_kw = float(load_series_kw[idx])
        renewable_kw = float(pv_series_kw[idx]) + float(wind_series_kw[idx])
        direct_use_mwh += min(load_kw, renewable_kw) * interval_hours / 1000
        surplus_mwh += max(0.0, renewable_kw - load_kw) * interval_hours / 1000
        net_load_peak_kw = max(net_load_peak_kw, max(0.0, load_kw - renewable_kw))
    return {
        "annual_renewable_direct_use_mwh": round(direct_use_mwh, 2),
        "annual_renewable_surplus_mwh": round(surplus_mwh, 2),
        "sizing_net_load_peak_kw": round(net_load_peak_kw, 2),
    }


def _resolve_storage_strategy_mode(data: dict[str, Any], operation_mode: str) -> str:
    explicit = str((data.get("project_info", {}) or {}).get("storage_strategy_mode") or "").strip()
    if explicit:
        return explicit
    if operation_mode in {"renewable_market_cooptimization", "renewable_export_oriented"}:
        return "market_responding"
    if operation_mode == "renewable_peak_shaving":
        return "peak_shaving"
    if operation_mode in {"renewable_self_consumption", "renewable_tou_arbitrage", "renewable_export_oriented"}:
        return "renewable_priority"
    return "balanced"


def _resolve_analysis_mode(data: dict[str, Any], operation_mode: str) -> str:
    explicit = str((data.get("project_info", {}) or {}).get("analysis_mode") or "").strip()
    if explicit:
        return explicit
    if operation_mode in {"renewable_market_cooptimization", "renewable_export_oriented"}:
        return "historical_backtest"
    return ""


def _cooptimization_execution_summary(data: dict[str, Any], output: dict[str, Any], annual_dispatch: dict[str, Any]) -> str:
    operation_mode = str((output.get("project_summary", {}) or {}).get("operation_mode") or "")
    if operation_mode not in {"renewable_market_cooptimization", "renewable_export_oriented"}:
        return ""
    market = data.get("market_data", {}) or {}
    threshold = float(
        market.get("renewable_charge_threshold_price_per_kwh")
        or market.get("solar_lcoe_per_kwh")
        or market.get("wind_lcoe_per_kwh")
        or 0.35
    )
    spread = float(market.get("cooptimization_min_sell_spread_per_kwh") or market.get("min_sell_spread_per_kwh") or 0.15)
    export_price = market.get("export_price_per_kwh")
    renewable_to_storage = round(float(annual_dispatch.get("renewable_to_storage_mwh") or 0.0), 2)
    grid_to_load = round(float(annual_dispatch.get("grid_to_load_mwh") or 0.0), 2)
    grid_to_storage = round(float(annual_dispatch.get("grid_to_storage_mwh") or 0.0), 2)
    exported = round(float(annual_dispatch.get("annual_export_mwh") or 0.0), 2)
    parts = [
        f"低价阈值 {threshold:.3f} 元/kWh",
        f"最小卖出价差 {spread:.3f} 元/kWh",
        f"绿电转储 {renewable_to_storage} MWh",
        f"电网供负荷 {grid_to_load} MWh",
        f"电网充储 {grid_to_storage} MWh",
    ]
    if exported > 0:
        if export_price not in (None, ""):
            parts.append(f"外送 {exported} MWh @ {float(export_price):.3f} 元/kWh")
        else:
            parts.append(f"外送 {exported} MWh")
    return "；".join(parts)


def _historical_backtest_days(load_series_kw: list[float]) -> int | None:
    if not load_series_kw:
        return None
    for steps_per_hour in (4, 2, 1):
        steps_per_day = 24 * steps_per_hour
        if len(load_series_kw) % steps_per_day == 0:
            return len(load_series_kw) // steps_per_day
    return None


def _historical_backtest_charge_price_avg(output: dict[str, Any], price_series: list[float]) -> float | None:
    if not price_series:
        return None
    operation_mode = str((output.get("project_summary", {}) or {}).get("operation_mode") or "")
    if operation_mode not in {"renewable_market_cooptimization", "renewable_export_oriented"}:
        return None
    ordered = sorted(float(v) for v in price_series)
    band = ordered[: max(1, len(ordered) // 4)]
    return round(sum(band) / len(band), 4) if band else None


def _historical_backtest_discharge_price_avg(output: dict[str, Any], price_series: list[float]) -> float | None:
    if not price_series:
        return None
    operation_mode = str((output.get("project_summary", {}) or {}).get("operation_mode") or "")
    if operation_mode not in {"renewable_market_cooptimization", "renewable_export_oriented"}:
        return None
    ordered = sorted(float(v) for v in price_series)
    band = ordered[-max(1, len(ordered) // 4) :]
    return round(sum(band) / len(band), 4) if band else None


def _normalize_spot_daily_cycle_schedule(daily_schedule: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for day in daily_schedule:
        cycles = []
        for idx, cycle in enumerate(day.get("cycles", []), start=1):
            charge_avg_price = float(cycle.get("charge_avg_price") or 0.0) / 1000.0
            discharge_avg_price = float(cycle.get("discharge_avg_price") or 0.0) / 1000.0
            cycles.append(
                {
                    "cycle_index": idx,
                    "charge_window": cycle.get("charge_window") or "",
                    "discharge_window": cycle.get("discharge_window") or "",
                    "charge_price_avg": round(charge_avg_price, 6),
                    "discharge_price_avg": round(discharge_avg_price, 6),
                    "spread_yuan_per_mwh": cycle.get("spread_yuan_per_mwh"),
                    "effective_spread_yuan_per_mwh": round((float(cycle.get("gross_margin") or 0.0) / max(float(cycle.get("discharge_energy_mwh") or 0.0), 1e-9)), 2)
                    if cycle.get("discharge_energy_mwh")
                    else None,
                    "charge_energy_mwh": cycle.get("charge_energy_mwh"),
                    "discharge_energy_mwh": cycle.get("discharge_energy_mwh"),
                    "gross_margin": cycle.get("gross_margin"),
                    "charge_source": "grid",
                }
            )
        normalized.append(
            {
                "date": day.get("date") or "",
                "cycle_count": len(cycles),
                "gross_margin": day.get("gross_margin") or 0.0,
                "cycles": cycles,
            }
        )
    return normalized


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


def _alternatives(solution: dict[str, Any]) -> list[dict[str, Any]]:
    base_storage = float(solution.get("storage_power_mw") or 0.0)
    base_energy = float(solution.get("storage_energy_mwh") or 0.0)
    options = []
    if base_storage > 0:
        options.append({"name": "保守方案", "storage_power_mw": round(base_storage * 0.7, 3), "storage_energy_mwh": round(base_energy * 0.7, 3)})
        options.append({"name": "激进方案", "storage_power_mw": round(base_storage * 1.25, 3), "storage_energy_mwh": round(base_energy * 1.25, 3)})
    return options


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


def _resolve_output_monthly_breakdown(
    annual_dispatch: dict[str, Any],
    spot_intraday_value: dict[str, Any] | None,
    rule_based_arbitrage: dict[str, Any] | None,
    annual_cycle_value: dict[str, Any] | None,
    commercial_hybrid_value: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if commercial_hybrid_value:
        return commercial_hybrid_value.get("monthly_storage_revenue_breakdown") or []
    if annual_cycle_value:
        return annual_cycle_value.get("monthly_storage_revenue_breakdown") or []
    if spot_intraday_value:
        return spot_intraday_value.get("monthly_storage_revenue_breakdown") or []
    if rule_based_arbitrage:
        return rule_based_arbitrage.get("monthly_storage_revenue_breakdown") or []
    return annual_dispatch.get("monthly_storage_revenue_breakdown") or []


def _resolve_annual_energy_charge_cost(
    post_energy_charge_cost: float,
    baseline_energy_charge_cost: float,
    scenario: str,
    rule_based_arbitrage: dict[str, Any] | None,
    spot_intraday_value: dict[str, Any] | None,
    annual_cycle_value: dict[str, Any] | None,
    commercial_hybrid_value: dict[str, Any] | None,
) -> float:
    cost = round(post_energy_charge_cost, 2)
    last_source = "post_storage"
    if scenario != "user_side_storage":
        return cost
    if rule_based_arbitrage:
        cost = round(max(0.0, baseline_energy_charge_cost - rule_based_arbitrage["annual_gross_margin"]), 2)
        last_source = "rule_based_arbitrage"
    if spot_intraday_value:
        if last_source not in ("post_storage", "spot_intraday_value"):
            logger.warning("spot_intraday_value overwrites energy_charge_cost from %s", last_source)
        cost = round(max(0.0, baseline_energy_charge_cost - spot_intraday_value["annual_gross_margin"]), 2)
        last_source = "spot_intraday_value"
    if annual_cycle_value:
        if last_source not in ("post_storage", "annual_cycle_value"):
            logger.warning("annual_cycle_value overwrites energy_charge_cost from %s", last_source)
        cost = round(max(0.0, baseline_energy_charge_cost - annual_cycle_value["annual_gross_margin"]), 2)
        last_source = "annual_cycle_value"
    if commercial_hybrid_value:
        if last_source not in ("post_storage", "commercial_hybrid_value"):
            logger.warning("commercial_hybrid_value overwrites energy_charge_cost from %s", last_source)
        cost = round(max(0.0, baseline_energy_charge_cost - commercial_hybrid_value["annual_energy_value"]), 2)
    return cost


def _validate_user_side_storage_value_models(data: dict[str, Any]) -> None:
    market = data.get("market_data", {}) or {}
    arbitrage_mode = str(((market.get("arbitrage_plan") or {}).get("mode") or "")).strip().lower()
    commercial_mode = str(((market.get("commercial_hybrid_plan") or {}).get("mode") or "")).strip().lower()
    active_models: list[str] = []
    if arbitrage_mode in {"spot_intraday", "rule_based", "annual_cycle_value"}:
        active_models.append(arbitrage_mode)
    if commercial_mode in {"mode_a", "mode_b"}:
        active_models.append(f"commercial_hybrid:{commercial_mode}")
    if len(active_models) > 1:
        raise ValueError(
            "Multiple user-side storage value models are configured simultaneously: "
            + ", ".join(active_models)
            + ". Configure exactly one of arbitrage_plan.mode or commercial_hybrid_plan.mode."
        )


def _is_power_trading_business_scenario(data: dict[str, Any]) -> bool:
    market = data.get("market_data", {}) or {}
    mode = str(market.get("market_mode") or "").strip().lower()
    return bool(market.get("market_price_series")) or any(token in mode for token in ("spot", "trading", "market_price"))


def _has_spot_intraday_plan(data: dict[str, Any]) -> bool:
    plan = (data.get("market_data", {}) or {}).get("arbitrage_plan") or {}
    return str(plan.get("mode") or "").strip().lower() == "spot_intraday"


def _market_summary(data: dict[str, Any], profile: dict[str, Any] | None) -> str:
    market_mode = data.get("market_data", {}).get("market_mode") or "unspecified"
    if _has_spot_intraday_plan(data):
        return "当前电力交易高级场景仅按日内实时价格逐日寻优，优先提取满足价差阈值的多循环 2h 充电 / 2h 放电窗口。"
    if _is_power_trading_business_scenario(data):
        return "当前电力交易高级场景先只支持日内实时套利；已识别到交易价序列，但未启用 spot_intraday 套利计划时，仅输出基础交易价差视角。"
    if profile:
        return f"按 {market_mode} 机制建模，并参考 {profile.get('verification_status')} 省级 profile 处理市场差异。"
    return f"按 {market_mode} 机制建模，省级差异待补充。"


def _assumptions(data: dict[str, Any], scenario: str) -> list[str]:
    assumptions = [
        "无第三方校证时，结论为预可研/前置分析口径。",
        "省级 profile 未覆盖的细则需人工补充复核。",
    ]
    if _is_power_trading_business_scenario(data):
        assumptions.append("电力交易高级场景当前仅覆盖 spot_intraday 日内实时套利，不含中长期、代购电或偏差结算精细建模。")
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
    if _is_power_trading_business_scenario(data) and not _has_spot_intraday_plan(data):
        gaps.append("market_data.arbitrage_plan.mode = spot_intraday")
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
    if _is_power_trading_business_scenario(data) and not _has_spot_intraday_plan(data):
        risks.append("当前已命中电力交易工商业储能场景，但高级交易能力暂只覆盖 spot_intraday 日内实时套利；其他交易机制后续再补。")
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
