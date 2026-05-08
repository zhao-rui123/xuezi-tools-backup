from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from energy_solution_agent.cli import main as cli_main
from energy_solution_agent.benchmark import run_benchmarks
from energy_solution_agent.engine import analyze_project, _resolve_annual_energy_charge_cost
from energy_solution_agent.live_rules import apply_live_rule_patch, extract_structured_rule_patch


EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"
ZERO_CARBON_EXAMPLE = EXAMPLES_DIR / "zero_carbon_factory_input.json"
CHARGING_EXAMPLE = EXAMPLES_DIR / "charging_station_input.json"
MARKET_EXAMPLE = EXAMPLES_DIR / "market_storage_input.json"
SERIES_EXAMPLE = EXAMPLES_DIR / "series_ingest_input.json"
DATA_CENTER_EXAMPLE = EXAMPLES_DIR / "data_center_input.json"
STEEL_EXAMPLE = EXAMPLES_DIR / "steel_factory_input.json"
POWER_TRADING_EXAMPLE = EXAMPLES_DIR / "power_trading_storage_input.json"
SOURCE_GRID_LOAD_STORAGE_EXAMPLE = EXAMPLES_DIR / "source_grid_load_storage_input.json"


class EngineTest(unittest.TestCase):
    def test_zero_carbon_factory_example(self) -> None:
        payload = json.loads(ZERO_CARBON_EXAMPLE.read_text(encoding="utf-8"))
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "zero_carbon_factory")
        self.assertIn("scenario_detail_code", output["project_summary"])
        self.assertIn("scenario_detail_label", output["project_summary"])
        self.assertTrue(output["applicability"]["zero_carbon_factory_recommended"])
        self.assertIsNotNone(output["carbon_results"]["annual_reduction_tco2e"])
        self.assertGreaterEqual(len(output["alternative_solutions"]), 3)
        self.assertGreaterEqual(len(output["sensitivity_results"]), 3)
        self.assertIsNotNone(output["dispatch_results"]["estimated_peak_reduction_kw"])
        self.assertGreaterEqual(len(output["carbon_results"]["carbon_path_breakdown"]), 1)
        self.assertIn(output["resource_results"]["pv_resource_accuracy"], {"medium", "high"})
        self.assertIsNotNone(output["resource_results"]["pv_p50_generation_mwh"])
        self.assertIsNotNone(output["resource_results"]["pv_p90_generation_mwh"])
        self.assertTrue(output["resource_results"]["wind_power_curve_used"])
        self.assertIsNotNone(output["financial_results"]["annual_energy_charge_cost"])
        self.assertIsNotNone(output["financial_results"]["annual_demand_charge_cost"])
        self.assertIsNotNone(output["dispatch_results"]["storage_annual_throughput_mwh"])
        self.assertIsNotNone(output["dispatch_results"]["storage_equivalent_full_cycles_per_year"])
        self.assertIn(output["market_and_settlement"]["province_profile_status"], {"verified", "partial", "missing"})
        self.assertIn(output["data_quality_results"]["level"], {"high", "medium", "low"})
        self.assertTrue(report)
        self.assertIn("data_completeness_grade", diagnostics)

    def test_charging_station_example(self) -> None:
        payload = json.loads(CHARGING_EXAMPLE.read_text(encoding="utf-8"))
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "charging_station")
        self.assertTrue(output["applicability"]["charging_recommended"])
        self.assertIsNotNone(output["dispatch_results"]["charging_peak_kw"])
        self.assertIsNotNone(output["resource_results"]["pv_p50_generation_mwh"])
        self.assertIn(output["resource_results"]["pv_resource_accuracy"], {"medium", "high"})
        self.assertIsNotNone(output["financial_results"]["annual_energy_charge_cost"])
        self.assertIsNotNone(output["dispatch_results"]["charging_queue_index"])
        self.assertGreaterEqual(len(output["dispatch_results"]["charging_segment_summary"]), 1)
        self.assertTrue(output["market_and_settlement"]["market_rule_notes"])
        self.assertTrue(report)
        self.assertIn("data_completeness_grade", diagnostics)

    def test_market_storage_example(self) -> None:
        payload = json.loads(MARKET_EXAMPLE.read_text(encoding="utf-8"))
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "user_side_storage")
        self.assertEqual(output["project_summary"]["scenario_detail_code"], "source_grid_load_storage")
        self.assertEqual(output["project_summary"]["scenario_detail_label"], "源网荷储工商业场景")
        self.assertEqual(output["project_summary"]["operation_mode"], "renewable_market_cooptimization")
        self.assertGreater(output["market_and_settlement"]["trading_price_spread_per_kwh"], 0.0)
        self.assertTrue(output["market_and_settlement"]["trading_execution_summary"])
        self.assertEqual(output["dispatch_results"]["storage_strategy_mode"], "market_responding")
        self.assertIsNotNone(output["financial_results"]["annual_ancillary_service_revenue"])
        self.assertIsNotNone(output["financial_results"]["annual_demand_response_revenue"])
        self.assertGreaterEqual(len(output["dispatch_results"]["monthly_storage_revenue_breakdown"]), 12)
        self.assertIn(output["market_and_settlement"]["province_profile_status"], {"verified", "partial", "missing"})
        self.assertGreater(
            output["market_and_settlement"]["trading_discharge_benchmark_price_per_kwh"],
            output["market_and_settlement"]["trading_charge_benchmark_price_per_kwh"],
        )
        self.assertTrue(output["market_and_settlement"]["trading_settlement_summary"])
        self.assertTrue(report)
        self.assertIn("market_context", diagnostics)

    def test_ancillary_and_dr_revenue_updates_npv_and_irr(self) -> None:
        payload = json.loads(MARKET_EXAMPLE.read_text(encoding="utf-8"))
        base_output, _, _ = analyze_project(payload)

        payload["market_data"]["ancillary_service_rate_per_mw_year"] = 10_000
        payload["market_data"]["demand_response_rate_per_kw_year"] = 0.0
        payload["market_data"]["demand_response_events_per_year"] = 0.0
        boosted_output, _, _ = analyze_project(payload)

        self.assertGreater(
            boosted_output["financial_results"]["annual_savings_or_revenue"],
            base_output["financial_results"]["annual_savings_or_revenue"],
        )
        self.assertGreater(boosted_output["financial_results"]["npv"], base_output["financial_results"]["npv"])
        self.assertLess(boosted_output["financial_results"]["payback_years"], base_output["financial_results"]["payback_years"])
        self.assertGreater(boosted_output["financial_results"]["irr"], base_output["financial_results"]["irr"])

    def test_source_grid_load_storage_example(self) -> None:
        payload = json.loads(SOURCE_GRID_LOAD_STORAGE_EXAMPLE.read_text(encoding="utf-8"))
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "user_side_storage")
        self.assertEqual(output["project_summary"]["scenario_detail_code"], "source_grid_load_storage")
        self.assertEqual(output["project_summary"]["scenario_detail_label"], "源网荷储工商业场景")
        self.assertEqual(output["project_summary"]["operation_mode"], "renewable_tou_arbitrage")
        self.assertEqual(output["dispatch_results"]["storage_sizing_basis"], "net_load_after_pv_wind")
        self.assertIsNotNone(output["simulation_results"]["annual_renewable_direct_use_mwh"])
        self.assertIsNotNone(output["simulation_results"]["annual_renewable_surplus_mwh"])
        self.assertIsNotNone(output["dispatch_results"]["sizing_net_load_peak_kw"])
        self.assertTrue(output["applicability"]["pv_recommended"])
        self.assertTrue(report)
        self.assertIn("annual_dispatch", diagnostics)

    def test_power_trading_storage_example_can_size_from_load_curve_and_spot_windows(self) -> None:
        payload = json.loads(POWER_TRADING_EXAMPLE.read_text(encoding="utf-8"))
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_detail_code"], "power_trading_commercial_storage")
        self.assertIsNotNone(output["recommended_solution"]["raw_storage_power_mw"])
        self.assertIsNotNone(output["recommended_solution"]["raw_storage_energy_mwh"])
        self.assertGreater(output["market_and_settlement"]["spot_trading_total_cycles"], 0)
        self.assertEqual(output["dispatch_results"]["storage_sizing_basis"], "raw_load_curve")
        self.assertTrue(report)

    def test_microgrid_example_can_model_offgrid_backup_and_fuel_cost(self) -> None:
        payload = json.loads(
            (EXAMPLES_DIR / "mauritania_mine_input.json").read_text(encoding="utf-8")
        )
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "microgrid")
        self.assertEqual(output["project_summary"]["scenario_detail_code"], "reliability_offgrid_microgrid")
        self.assertTrue(output["applicability"]["microgrid_recommended"])
        self.assertEqual(output["market_and_settlement"]["market_mode"], "offgrid_internal")
        self.assertEqual(output["dispatch_results"]["storage_sizing_basis"], "offgrid_optimization")
        self.assertIsNotNone(output["financial_results"]["annual_energy_charge_cost"])
        self.assertGreater(output["financial_results"]["annual_energy_charge_cost"], 500_000)
        self.assertGreaterEqual(output["financial_results"]["annual_energy_charge_cost"], 0.0)
        self.assertTrue(report)
        self.assertIn("annual_dispatch", diagnostics)

    def test_microgrid_can_be_classified_as_economic_offgrid_scenario(self) -> None:
        payload = {
            "project_info": {
                "project_name": "economic-microgrid",
                "scenario_type": "microgrid",
                "province": "Overseas",
                "city": "Economic Site",
                "country": "Mauritania",
                "latitude": 23.196941,
                "longitude": -11.959593,
                "grid_operator": "Offgrid",
                "voltage_level_kv": 10,
                "grid_connection_mode": "microgrid",
                "target_priority": "economic_first",
                "storage_strategy_mode": "renewable_priority",
            },
            "resource_data": {
                "public_resource_year": 2025,
                "solar": {
                    "installed_capacity_mwp": 20,
                    "annual_irradiation_kwh_per_m2": 2263,
                    "tilt_deg": None,
                    "azimuth_deg": 180,
                    "performance_ratio": 0.82,
                },
                "wind": {
                    "installed_capacity_mw": 10,
                    "annual_avg_speed_mps": 6.59,
                    "capacity_factor_assumption": 0.42,
                    "power_curve": [],
                },
            },
            "load_data": {
                "annual_consumption_mwh": 100000,
                "peak_load_kw": 12000,
                "critical_load_kw": 0,
                "backup_hours_required": 0,
            },
            "market_data": {
                "market_mode": "offgrid_internal",
            },
            "equipment": {
                "storage": {
                    "power_candidate_kw": [0, 5000, 10000],
                    "energy_candidate_kwh": [0, 20000, 40000],
                },
                "conventional_backup": {
                    "enabled": True,
                    "minimum_output_kw": 0,
                    "fuel_cost_per_kwh": 0.32,
                },
            },
            "financial": {
                "project_years": 15,
                "discount_rate": 0.08,
                "capex": {
                    "storage_system_cost_per_kwh": 850,
                    "pv_cost_per_w": 3.1,
                    "wind_cost_per_w": 6.4,
                    "storage_replacement_cost_ratio": 0.52,
                },
                "opex": {
                    "annual_om_ratio": 0.018,
                    "annual_opex_escalation_rate": 0.02,
                },
                "degradation": {
                    "storage_capacity_fade_per_year": 0.022,
                    "pv_degradation_per_year": 0.005,
                    "wind_degradation_per_year": 0.003,
                },
            },
        }
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "microgrid")
        self.assertEqual(output["project_summary"]["scenario_detail_code"], "economic_offgrid_microgrid")
        self.assertEqual(output["market_and_settlement"]["market_mode"], "offgrid_internal")
        self.assertTrue(report)
        self.assertIn("annual_dispatch", diagnostics)

    def test_microgrid_can_be_classified_as_high_renewable_offgrid_scenario(self) -> None:
        payload = {
            "project_info": {
                "project_name": "high-renewable-microgrid",
                "scenario_type": "microgrid",
                "province": "Overseas",
                "city": "High Renewable Site",
                "country": "Mauritania",
                "latitude": 23.196941,
                "longitude": -11.959593,
                "grid_operator": "Offgrid",
                "voltage_level_kv": 10,
                "grid_connection_mode": "microgrid",
                "target_priority": "high_renewable",
                "renewable_penetration_target_ratio": 0.85,
                "storage_strategy_mode": "renewable_priority",
            },
            "resource_data": {
                "public_resource_year": 2025,
                "solar": {
                    "installed_capacity_mwp": 60,
                    "annual_irradiation_kwh_per_m2": 2263,
                    "tilt_deg": None,
                    "azimuth_deg": 180,
                    "performance_ratio": 0.82,
                },
                "wind": {
                    "installed_capacity_mw": 40,
                    "annual_avg_speed_mps": 6.59,
                    "capacity_factor_assumption": 0.42,
                    "power_curve": [],
                },
            },
            "load_data": {
                "annual_consumption_mwh": 100000,
                "peak_load_kw": 12000,
                "critical_load_kw": 0,
                "backup_hours_required": 0,
            },
            "market_data": {
                "market_mode": "offgrid_internal",
            },
            "equipment": {
                "storage": {
                    "power_candidate_kw": [0, 5000, 10000],
                    "energy_candidate_kwh": [0, 20000, 40000],
                },
                "conventional_backup": {
                    "enabled": True,
                    "minimum_output_kw": 0,
                    "fuel_cost_per_kwh": 0.32,
                },
            },
            "financial": {
                "project_years": 15,
                "discount_rate": 0.08,
                "capex": {
                    "storage_system_cost_per_kwh": 850,
                    "pv_cost_per_w": 3.1,
                    "wind_cost_per_w": 6.4,
                    "storage_replacement_cost_ratio": 0.52,
                },
                "opex": {
                    "annual_om_ratio": 0.018,
                    "annual_opex_escalation_rate": 0.02,
                },
                "degradation": {
                    "storage_capacity_fade_per_year": 0.022,
                    "pv_degradation_per_year": 0.005,
                    "wind_degradation_per_year": 0.003,
                },
            },
        }
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "microgrid")
        self.assertEqual(output["project_summary"]["scenario_detail_code"], "high_renewable_offgrid_microgrid")
        self.assertEqual(output["market_and_settlement"]["market_mode"], "offgrid_internal")
        self.assertTrue(report)
        self.assertIn("annual_dispatch", diagnostics)

    def test_user_side_storage_can_emit_raw_and_selected_product_storage_values(self) -> None:
        payload = json.loads(SERIES_EXAMPLE.read_text(encoding="utf-8"))
        payload["equipment"]["storage"]["selected_product_power_kw"] = 1500
        payload["equipment"]["storage"]["selected_product_energy_kwh"] = 3200
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "user_side_storage")
        self.assertIsNotNone(output["recommended_solution"]["raw_storage_power_mw"])
        self.assertIsNotNone(output["recommended_solution"]["raw_storage_energy_mwh"])
        self.assertEqual(output["recommended_solution"]["selected_product_power_mw"], 1.5)
        self.assertEqual(output["recommended_solution"]["selected_product_energy_mwh"], 3.2)
        self.assertEqual(output["recommended_solution"]["storage_power_mw"], 1.5)
        self.assertEqual(output["recommended_solution"]["storage_energy_mwh"], 3.2)
        self.assertIsNotNone(output["dispatch_results"]["storage_power_utilization_ratio"])
        self.assertIsNotNone(output["dispatch_results"]["storage_energy_utilization_ratio"])
        self.assertTrue(report)
        self.assertIn("scenario", diagnostics)

    def test_series_ingest_example(self) -> None:
        payload = json.loads(SERIES_EXAMPLE.read_text(encoding="utf-8"))
        payload["resource_data"] = {"solar": {}, "wind": {}}
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "user_side_storage")
        self.assertEqual(output["project_summary"]["scenario_detail_code"], "tou_commercial_storage")
        self.assertEqual(output["project_summary"]["scenario_detail_label"], "分时电价工商业储能场景")
        self.assertIsNone(output["resource_results"]["wind_p50_generation_mwh"])
        self.assertIsNone(output["resource_results"]["pv_resource_accuracy"])
        self.assertTrue(report)

    def test_user_side_storage_can_be_classified_as_power_trading_business_scenario(self) -> None:
        payload = json.loads(SERIES_EXAMPLE.read_text(encoding="utf-8"))
        payload["resource_data"] = {"solar": {}, "wind": {}}
        payload["market_data"]["market_mode"] = "market_price_series"
        payload["market_data"]["market_price_series"] = [0.25] * 6 + [0.45] * 6 + [0.95] * 6 + [0.55] * 6
        payload["market_data"].pop("tou_tariff", None)
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "user_side_storage")
        self.assertEqual(output["project_summary"]["scenario_detail_code"], "power_trading_commercial_storage")
        self.assertEqual(output["project_summary"]["scenario_detail_label"], "电力交易工商业储能场景")
        self.assertTrue(report)

    def test_power_trading_business_scenario_without_spot_intraday_plan_exposes_scope_boundary(self) -> None:
        payload = json.loads(SERIES_EXAMPLE.read_text(encoding="utf-8"))
        payload["resource_data"] = {"solar": {}, "wind": {}}
        payload["market_data"]["market_mode"] = "market_price_series"
        payload["market_data"]["market_price_series"] = [0.25] * 6 + [0.45] * 6 + [0.95] * 6 + [0.55] * 6
        payload["market_data"].pop("tou_tariff", None)
        payload["market_data"].pop("arbitrage_plan", None)
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_detail_code"], "power_trading_commercial_storage")
        self.assertIn("spot_intraday", output["recommended_solution"]["market_strategy_summary"])
        self.assertIn("spot_intraday", output["assumptions"][-1])
        self.assertIn("market_data.arbitrage_plan.mode = spot_intraday", output["data_gaps"])
        self.assertTrue(any("spot_intraday" in item for item in output["risks"]))
        self.assertTrue(report)

    def test_spot_intraday_mode_can_emit_daily_arbitrage_schedule(self) -> None:
        payload = json.loads(SERIES_EXAMPLE.read_text(encoding="utf-8"))
        payload["resource_data"] = {"solar": {}, "wind": {}}
        payload["market_data"]["market_mode"] = "market_price_series"
        payload["market_data"]["market_price_series"] = [0.10, 0.10, 0.55, 0.55, 0.12, 0.12, 0.48, 0.48] + [0.30] * 16
        payload["market_data"]["spot_price_daily_profiles"] = [
            {
                "date": "2026-01-01",
                "realtime_prices": [0.10, 0.10, 0.55, 0.55, 0.12, 0.12, 0.48, 0.48] + [0.30] * 16,
            }
        ]
        payload["market_data"]["arbitrage_plan"] = {
            "mode": "spot_intraday",
            "min_charge_hours": 2,
            "min_discharge_hours": 2,
            "min_spread_yuan_per_mwh": 250,
        }
        payload["equipment"]["storage"]["selected_product_power_kw"] = 1000
        payload["equipment"]["storage"]["selected_product_energy_kwh"] = 2000
        payload["market_data"].pop("tou_tariff", None)
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_detail_code"], "power_trading_commercial_storage")
        self.assertEqual(output["market_and_settlement"]["spot_trading_days_covered"], 1)
        self.assertEqual(output["market_and_settlement"]["spot_trading_total_cycles"], 2)
        self.assertEqual(output["market_and_settlement"]["daily_spot_arbitrage_schedule"][0]["cycles"][0]["charge_window"], "00:00-02:00")
        self.assertTrue(output["dispatch_results"]["daily_cycle_schedule"])
        self.assertEqual(output["dispatch_results"]["daily_cycle_schedule"][0]["cycle_count"], 2)
        self.assertTrue(report)

    def test_spot_intraday_energy_charge_override_uses_gross_margin(self) -> None:
        cost = _resolve_annual_energy_charge_cost(
            post_energy_charge_cost=2988277.11,
            baseline_energy_charge_cost=2966224.6,
            scenario="user_side_storage",
            rule_based_arbitrage=None,
            spot_intraday_value={"annual_gross_margin": 1186.03},
            annual_cycle_value=None,
            commercial_hybrid_value=None,
        )

        self.assertEqual(cost, 2965038.57)

    def test_source_grid_load_storage_can_reduce_raw_storage_size_with_same_tariff_logic(self) -> None:
        day = []
        for hour in range(24):
            if hour in {10, 11, 12}:
                day.extend([20.0] * 4)
            elif hour in {19, 20}:
                day.extend([110.0] * 4)
            else:
                day.extend([70.0] * 4)
        load_series = day * 31
        base_payload = {
            "project_info": {
                "project_name": "compare",
                "scenario_type": "source_grid_load_storage",
                "province": "湖北",
                "city": "武汉",
                "voltage_level_kv": 10,
            },
            "load_data": {
                "load_series_kw": load_series,
                "peak_load_kw": 110.0,
            },
            "market_data": {
                "market_mode": "tou_tariff",
                "tou_tariff": [
                    {"period": "peak", "price": 1.0},
                    {"period": "flat", "price": 0.6},
                    {"period": "valley", "price": 0.3},
                ],
                "monthly_tou_policy_history": [
                    {
                        "month": 1,
                        "periods": ["peak", "flat", "valley"],
                        "schedule": {
                            "peak": [19, 20],
                            "flat": [8, 9, 13, 14, 15, 16, 17, 18, 21],
                            "valley": [10, 11, 12, 0, 1, 2, 3, 4, 5, 6],
                        },
                    }
                ],
                "demand_charge_mode": "contract_capacity",
                "contract_capacity_kw": 120.0,
            },
            "equipment": {
                "storage": {
                    "sizing_target_day_coverage_ratio": 0.9,
                }
            },
            "resource_data": {
                "solar": {
                    "hourly_generation_profile_kw": [0, 0, 0, 0, 0, 0, 0, 10, 25, 40, 60, 60, 60, 45, 20, 5, 0, 0, 0, 0, 0, 0, 0, 0],
                    "installed_capacity_mwp": 0.3,
                },
                "wind": {},
            },
        }
        pure_payload = json.loads(json.dumps(base_payload))
        pure_payload["project_info"]["scenario_type"] = "user_side_storage"
        pure_payload["resource_data"] = {"solar": {}, "wind": {}}

        pure_output, _, _ = analyze_project(pure_payload)
        hybrid_output, _, _ = analyze_project(base_payload)

        self.assertEqual(hybrid_output["project_summary"]["scenario_detail_code"], "source_grid_load_storage")
        self.assertEqual(hybrid_output["project_summary"]["operation_mode"], "renewable_tou_arbitrage")
        self.assertLess(
            hybrid_output["recommended_solution"]["raw_storage_energy_mwh"],
            pure_output["recommended_solution"]["raw_storage_energy_mwh"],
        )
        self.assertLess(
            hybrid_output["dispatch_results"]["sizing_net_load_peak_kw"],
            pure_payload["load_data"]["peak_load_kw"],
        )

    def test_source_grid_load_storage_can_route_export_oriented_mode(self) -> None:
        payload = json.loads(SOURCE_GRID_LOAD_STORAGE_EXAMPLE.read_text(encoding="utf-8"))
        payload["market_data"]["allow_export_to_grid"] = True
        payload["market_data"]["export_price_per_kwh"] = 0.42
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_detail_code"], "source_grid_load_storage")
        self.assertEqual(output["project_summary"]["operation_mode"], "renewable_export_oriented")
        self.assertEqual(output["project_summary"]["analysis_mode"], "historical_backtest")
        self.assertEqual(output["dispatch_results"]["operation_mode"], "renewable_export_oriented")
        self.assertGreaterEqual(output["financial_results"]["annual_export_revenue"], 0.0)
        self.assertTrue(report)

    def test_market_cooptimization_can_shift_renewable_from_load_to_storage_in_low_price_window(self) -> None:
        load_series = ([80.0] * 4 + [120.0] * 8 + [80.0] * 4 + [120.0] * 8) * 365
        solar_profile = [0.0] * 4 + [100.0] * 8 + [0.0] * 12
        payload = {
            "project_info": {
                "project_name": "coopt",
                "scenario_type": "source_grid_load_storage",
                "province": "湖北",
                "city": "武汉",
                "voltage_level_kv": 10,
            },
            "load_data": {
                "load_series_kw": load_series,
                "peak_load_kw": 120.0,
            },
            "resource_data": {
                "solar": {
                    "hourly_generation_profile_kw": solar_profile,
                    "installed_capacity_mwp": 0.5,
                },
                "wind": {},
            },
            "market_data": {
                "market_mode": "market_price_series",
                "market_price_series": [0.55] * 4 + [0.12] * 8 + [0.65] * 4 + [1.05] * 8,
                "renewable_charge_threshold_price_per_kwh": 0.35,
                "cooptimization_min_sell_spread_per_kwh": 0.2,
                "contract_capacity_kw": 200.0,
                "demand_charge_mode": "contract_capacity",
            },
            "equipment": {
                "storage": {
                    "pcs_efficiency": 0.985,
                    "transformer_efficiency": 0.99,
                    "battery_charge_efficiency": 0.965,
                    "battery_discharge_efficiency": 0.965,
                    "sizing_target_day_coverage_ratio": 0.9,
                }
            },
        }
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["operation_mode"], "renewable_market_cooptimization")
        self.assertEqual(output["project_summary"]["analysis_mode"], "historical_backtest")
        self.assertEqual(output["dispatch_results"]["storage_sizing_basis"], "renewable_market_cooptimized_proxy")
        self.assertGreater(output["dispatch_results"]["renewable_to_storage_mwh"], 0.0)
        self.assertGreater(output["dispatch_results"]["grid_to_load_mwh"], 0.0)
        self.assertGreater(output["simulation_results"]["annual_renewable_to_storage_mwh"], 0.0)
        self.assertTrue(output["dispatch_results"]["daily_cycle_schedule"])
        first_cycle = output["dispatch_results"]["daily_cycle_schedule"][0]["cycles"][0]
        self.assertEqual(first_cycle["charge_window"], "04:00-08:00")
        self.assertEqual(first_cycle["discharge_window"], "12:00-19:00")
        expected_power = output["recommended_solution"]["raw_storage_energy_mwh"] / 2.0
        self.assertAlmostEqual(output["recommended_solution"]["raw_storage_power_mw"], expected_power, places=3)
        self.assertTrue(output["market_and_settlement"]["cooptimization_execution_summary"])
        self.assertIsNotNone(output["market_and_settlement"]["historical_backtest_days"])
        self.assertTrue(report)

    def test_export_oriented_mode_can_emit_export_revenue(self) -> None:
        load_series = ([20.0] * 8 + [40.0] * 8 + [20.0] * 8) * 365
        solar_profile = [0.0] * 4 + [120.0] * 10 + [10.0] * 10
        payload = {
            "project_info": {
                "project_name": "export",
                "scenario_type": "source_grid_load_storage",
                "province": "湖北",
                "city": "武汉",
                "voltage_level_kv": 10,
            },
            "load_data": {
                "load_series_kw": load_series,
                "peak_load_kw": 40.0,
            },
            "resource_data": {
                "solar": {
                    "hourly_generation_profile_kw": solar_profile,
                    "installed_capacity_mwp": 0.8,
                },
                "wind": {},
            },
            "market_data": {
                "market_mode": "market_price_series",
                "market_price_series": [0.25] * 8 + [0.35] * 6 + [0.9] * 4 + [0.45] * 6,
                "allow_export_to_grid": True,
                "export_price_per_kwh": 0.38,
                "renewable_charge_threshold_price_per_kwh": 0.2,
                "cooptimization_min_sell_spread_per_kwh": 0.2,
                "contract_capacity_kw": 120.0,
                "demand_charge_mode": "contract_capacity",
            },
            "equipment": {
                "storage": {
                    "pcs_efficiency": 0.985,
                    "transformer_efficiency": 0.99,
                    "battery_charge_efficiency": 0.965,
                    "battery_discharge_efficiency": 0.965,
                    "sizing_target_day_coverage_ratio": 0.9,
                }
            },
        }
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["operation_mode"], "renewable_export_oriented")
        self.assertGreater(output["simulation_results"]["annual_export_mwh"], 0.0)
        self.assertGreater(output["dispatch_results"]["renewable_to_storage_mwh"], 0.0)
        self.assertGreater(output["financial_results"]["annual_export_revenue"], 0.0)
        self.assertTrue(any("外送" in item for item in output["market_and_settlement"]["revenue_breakdown"]))
        self.assertTrue(output["market_and_settlement"]["cooptimization_execution_summary"])
        self.assertIsNotNone(output["market_and_settlement"]["historical_backtest_charge_price_avg"])
        self.assertTrue(report)

    def test_explicit_renewable_charge_threshold_overrides_default_lcoe_trigger(self) -> None:
        load_series = ([80.0] * 4 + [120.0] * 8 + [80.0] * 4 + [120.0] * 8) * 365
        solar_profile = [0.0] * 4 + [100.0] * 8 + [0.0] * 12
        payload = {
            "project_info": {
                "project_name": "override",
                "scenario_type": "source_grid_load_storage",
                "province": "湖北",
                "city": "武汉",
                "voltage_level_kv": 10,
            },
            "load_data": {
                "load_series_kw": load_series,
                "peak_load_kw": 120.0,
            },
            "resource_data": {
                "solar": {
                    "hourly_generation_profile_kw": solar_profile,
                    "installed_capacity_mwp": 0.5,
                },
                "wind": {},
            },
            "market_data": {
                "market_mode": "market_price_series",
                "market_price_series": [0.55] * 4 + [0.12] * 8 + [0.65] * 4 + [1.05] * 8,
                "renewable_charge_threshold_price_per_kwh": 0.05,
                "cooptimization_min_sell_spread_per_kwh": 0.2,
                "contract_capacity_kw": 200.0,
                "demand_charge_mode": "contract_capacity",
            },
            "equipment": {
                "storage": {
                    "pcs_efficiency": 0.985,
                    "transformer_efficiency": 0.99,
                    "battery_charge_efficiency": 0.965,
                    "battery_discharge_efficiency": 0.965,
                    "sizing_target_day_coverage_ratio": 0.9,
                }
            },
        }
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["operation_mode"], "renewable_market_cooptimization")
        self.assertEqual(output["project_summary"]["analysis_mode"], "historical_backtest")
        self.assertEqual(output["dispatch_results"]["renewable_to_storage_mwh"], 0.0)
        self.assertTrue(report)

    def test_data_center_example(self) -> None:
        payload = json.loads(DATA_CENTER_EXAMPLE.read_text(encoding="utf-8"))
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "zero_carbon_factory")
        self.assertEqual(output["carbon_results"]["industry_template"]["scope2_weight"], 0.95)
        self.assertIn("绿电", output["carbon_results"]["carbon_path_breakdown"][0]["path"])
        self.assertTrue(output["applicability"]["thermal_system_recommended"])
        self.assertTrue(report)

    def test_steel_factory_example(self) -> None:
        payload = json.loads(STEEL_EXAMPLE.read_text(encoding="utf-8"))
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "zero_carbon_factory")
        self.assertEqual(output["carbon_results"]["industry_template"]["scope1_weight"], 0.65)
        self.assertIn("工艺", output["carbon_results"]["carbon_path_breakdown"][0]["path"])
        self.assertIn("scope1_scope2", output["carbon_results"]["claim_boundary_summary"])
        self.assertTrue(report)

    def test_benchmark_runner(self) -> None:
        rows = run_benchmarks(EXAMPLES_DIR)
        self.assertGreaterEqual(len(rows["benchmarks"]), 7)
        self.assertTrue(any(row["scenario"] == "zero_carbon_factory" for row in rows["benchmarks"]))
        self.assertIn("total_cases", rows["summary"])
        self.assertIn("successful_cases", rows["summary"])
        self.assertIn("failed_cases", rows["summary"])
        self.assertIn("quality_gate_pass_rate", rows["summary"])
        self.assertIn("max_data_gaps", rows["summary"])

    def test_benchmark_runner_reports_failed_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / "good.json").write_text(ZERO_CARBON_EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
            (tmp / "bad.json").write_text("{bad json", encoding="utf-8")
            rows = run_benchmarks(tmp)

        self.assertEqual(rows["summary"]["successful_cases"], 1)
        self.assertEqual(rows["summary"]["failed_cases"], 1)
        self.assertEqual(rows["summary"]["total_attempted_cases"], 2)
        self.assertTrue(rows["summary"]["has_errors"])
        self.assertEqual(len(rows["errors"]), 1)

    def test_benchmark_cli_returns_nonzero_when_any_case_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / "good.json").write_text(ZERO_CARBON_EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
            (tmp / "bad.json").write_text("{bad json", encoding="utf-8")
            exit_code = cli_main(["benchmark", "--examples", str(tmp)])

        self.assertEqual(exit_code, 3)

    def test_user_side_storage_rejects_multiple_value_models(self) -> None:
        payload = json.loads(POWER_TRADING_EXAMPLE.read_text(encoding="utf-8"))
        payload["market_data"]["commercial_hybrid_plan"] = {
            "mode": "mode_a",
            "high_price": 0.85,
        }

        with self.assertRaisesRegex(ValueError, "Multiple user-side storage value models"):
            analyze_project(payload)

    def test_live_rule_structured_patch(self) -> None:
        text = "夏季尖峰电价1.23元/千瓦时，峰电价0.98元，平时段0.66元，谷时段0.31元；峰时段10:00-12:00、14:00-21:00，谷时段00:00-07:00；执行需量电费30元/kW；鼓励绿电交易和辅助服务。"
        patch = extract_structured_rule_patch(text)
        self.assertIsInstance(patch.get("tou_tariff"), list)
        self.assertGreater(len(patch["tou_tariff"]), 0)
        self.assertEqual(patch.get("green_power_trade_rule"), "green_power_enabled")
        self.assertTrue(patch.get("tou_schedule"))

    def test_live_rule_patch_application(self) -> None:
        market = {"market_mode": "tou_tariff", "tou_tariff": [{"period": "flat", "price": 0.72}]}
        patch = {
            "market_mode": "market_price_series",
            "demand_charge_rule": "需量电费",
            "demand_charge_rate_per_kw_month": 32.0,
        }
        merged = apply_live_rule_patch(market, patch)
        self.assertEqual(merged["market_mode"], "market_price_series")
        self.assertEqual(merged["demand_charge_rule"], "需量电费")
        self.assertEqual(merged["demand_charge_rate_per_kw_month"], 32.0)
