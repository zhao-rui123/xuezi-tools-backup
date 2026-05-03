from __future__ import annotations

import json
import unittest
from pathlib import Path

from energy_solution_agent.benchmark import run_benchmarks
from energy_solution_agent.engine import analyze_project
from energy_solution_agent.live_rules import apply_live_rule_patch, extract_structured_rule_patch


ZERO_CARBON_EXAMPLE = Path(r"D:\Codex\应用\energy_solution_agent\examples\zero_carbon_factory_input.json")
CHARGING_EXAMPLE = Path(r"D:\Codex\应用\energy_solution_agent\examples\charging_station_input.json")
MARKET_EXAMPLE = Path(r"D:\Codex\应用\energy_solution_agent\examples\market_storage_input.json")
SERIES_EXAMPLE = Path(r"D:\Codex\应用\energy_solution_agent\examples\series_ingest_input.json")
DATA_CENTER_EXAMPLE = Path(r"D:\Codex\应用\energy_solution_agent\examples\data_center_input.json")
STEEL_EXAMPLE = Path(r"D:\Codex\应用\energy_solution_agent\examples\steel_factory_input.json")


class EngineTest(unittest.TestCase):
    def test_zero_carbon_factory_example(self) -> None:
        payload = json.loads(ZERO_CARBON_EXAMPLE.read_text(encoding="utf-8"))
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "zero_carbon_factory")
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
        self.assertIn("零碳", report)
        self.assertIn("江苏", report)
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
        self.assertIn("充电", report)
        self.assertIn("data_completeness_grade", diagnostics)

    def test_market_storage_example(self) -> None:
        payload = json.loads(MARKET_EXAMPLE.read_text(encoding="utf-8"))
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "user_side_storage")
        self.assertEqual(output["dispatch_results"]["storage_strategy_mode"], "market_responding")
        self.assertIsNotNone(output["financial_results"]["annual_ancillary_service_revenue"])
        self.assertIsNotNone(output["financial_results"]["annual_demand_response_revenue"])
        self.assertGreaterEqual(len(output["dispatch_results"]["monthly_storage_revenue_breakdown"]), 12)
        self.assertIn(output["market_and_settlement"]["province_profile_status"], {"verified", "partial"})
        self.assertIn("储能", report)

    def test_series_ingest_example(self) -> None:
        payload = json.loads(SERIES_EXAMPLE.read_text(encoding="utf-8"))
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "user_side_storage")
        self.assertIsNotNone(output["resource_results"]["wind_p50_generation_mwh"])
        self.assertIn(output["resource_results"]["pv_resource_accuracy"], {"high", "medium"})
        self.assertIn("项目概况", report)

    def test_data_center_example(self) -> None:
        payload = json.loads(DATA_CENTER_EXAMPLE.read_text(encoding="utf-8"))
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "zero_carbon_factory")
        self.assertEqual(output["carbon_results"]["industry_template"]["scope2_weight"], 0.95)
        self.assertTrue(output["applicability"]["thermal_system_recommended"])
        self.assertIn("数据中心", report)

    def test_steel_factory_example(self) -> None:
        payload = json.loads(STEEL_EXAMPLE.read_text(encoding="utf-8"))
        output, diagnostics, report = analyze_project(payload)
        self.assertEqual(output["project_summary"]["scenario_type"], "zero_carbon_factory")
        self.assertEqual(output["carbon_results"]["industry_template"]["scope1_weight"], 0.65)
        self.assertIn("钢铁", report)

    def test_benchmark_runner(self) -> None:
        rows = run_benchmarks(Path(r"D:\Codex\应用\energy_solution_agent\examples"))
        self.assertGreaterEqual(len(rows["benchmarks"]), 6)
        self.assertTrue(any(row["scenario"] == "zero_carbon_factory" for row in rows["benchmarks"]))
        self.assertIn("total_cases", rows["summary"])
        self.assertIn("quality_gate_pass_rate", rows["summary"])
        self.assertIn("max_data_gaps", rows["summary"])

    def test_live_rule_structured_patch(self) -> None:
        text = "夏季尖峰电价1.23元/千瓦时，峰电价0.98元，平段0.66元，谷段0.31元；峰时段10:00-12:00、14:00-21:00，谷时段00:00-07:00；执行需量电费30元/kW；鼓励绿电交易和辅助服务。"
        patch = extract_structured_rule_patch(text)
        self.assertTrue(patch.get("tou_tariff"))
        self.assertEqual(patch.get("demand_charge_rule"), "需量电费")
        self.assertEqual(patch.get("demand_charge_rate_per_kw_month"), 30.0)
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


if __name__ == "__main__":
    unittest.main()
