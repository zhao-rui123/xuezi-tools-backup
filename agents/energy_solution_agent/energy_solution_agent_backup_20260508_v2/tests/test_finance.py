from __future__ import annotations

import unittest

from energy_solution_agent.solvers.finance import _compute_irr, settlement_and_finance


class FinanceSolverTest(unittest.TestCase):
    def test_compute_irr_solves_standard_project_cashflows(self) -> None:
        cashflows = [-1000.0, 400.0, 400.0, 400.0]

        irr = _compute_irr(cashflows)

        self.assertIsNotNone(irr)
        assert irr is not None
        self.assertAlmostEqual(irr, 0.097, places=3)
        self.assertAlmostEqual(
            sum(cf / ((1.0 + irr) ** year) for year, cf in enumerate(cashflows)),
            0.0,
            places=4,
        )

    def test_compute_irr_returns_none_without_sign_change(self) -> None:
        self.assertIsNone(_compute_irr([100.0, 200.0, 300.0]))
        self.assertIsNone(_compute_irr([-100.0, -50.0, -10.0]))

    def test_settlement_and_finance_uses_storage_value_override(self) -> None:
        result = settlement_and_finance(
            data={
                "project_info": {"country": "China", "province": "Jiangsu"},
                "financial": {
                    "project_years": 10,
                    "discount_rate": 0.08,
                    "capex": {},
                    "opex": {},
                    "tax": {"model": "overseas_exempt"},
                },
                "market_data": {},
                "equipment": {},
                "load_data": {},
            },
            simulation={
                "annual_storage_discharge_mwh": 999.0,
                "annual_pv_generation_mwh": 0.0,
                "annual_wind_generation_mwh": 0.0,
                "annual_charging_energy_mwh": 0.0,
                "annual_export_mwh": 0.0,
                "storage_energy_mwh": 0.0,
                "pv_mwp": 0.0,
                "wind_mw": 0.0,
            },
            carbon={},
            storage_value_override=123456.0,
        )

        self.assertEqual(result["annual_savings_or_revenue"], 123456.0)
        self.assertEqual(result["revenue_breakdown"], ["储能节费/市场释放收益"])
        self.assertIsNone(result["irr"])
        self.assertEqual(result["tax_model"], "overseas_exempt")

    def test_settlement_and_finance_keeps_overseas_projects_tax_free(self) -> None:
        result = settlement_and_finance(
            data={
                "project_info": {"country": "Mauritania", "province": "Overseas"},
                "financial": {
                    "project_years": 15,
                    "discount_rate": 0.08,
                    "capex": {
                        "storage_system_cost_per_kwh": 800.0,
                        "pv_cost_per_w": 3.0,
                    },
                    "opex": {"annual_om_ratio": 0.02},
                    "tax": {"model": "overseas_exempt"},
                },
                "market_data": {
                    "tou_tariff": [{"period": "flat", "price": 0.8}],
                    "export_price_discount": 0.9,
                },
                "equipment": {},
                "load_data": {"annual_consumption_mwh": 1500.0},
            },
            simulation={
                "annual_storage_discharge_mwh": 120.0,
                "annual_pv_generation_mwh": 2000.0,
                "annual_wind_generation_mwh": 0.0,
                "annual_charging_energy_mwh": 0.0,
                "annual_export_mwh": 100.0,
                "storage_energy_mwh": 2.0,
                "pv_mwp": 1.0,
                "wind_mw": 0.0,
            },
            carbon={"annual_reduction_tco2e": 50.0},
        )

        self.assertEqual(result["tax_model"], "overseas_exempt")
        self.assertEqual(result["annual_tax_total"], 0.0)
        self.assertEqual(result["annual_income_tax"], 0.0)
        self.assertEqual(result["annual_vat_and_surcharges"], 0.0)
        self.assertEqual(result["initial_input_vat_credit"], 0.0)
        self.assertGreater(result["annual_export_revenue"], 0.0)


if __name__ == "__main__":
    unittest.main()
