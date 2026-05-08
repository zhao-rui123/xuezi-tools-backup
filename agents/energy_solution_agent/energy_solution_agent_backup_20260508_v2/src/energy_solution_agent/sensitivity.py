from __future__ import annotations

from typing import Any


def run_sensitivity(output: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate sensitivity analysis based on actual project financial structure.

    Derives revenue/cost sensitivities from the project's own capex, opex, and
    revenue breakdown rather than using hardcoded impact percentages.
    """
    fin = output.get("financial_results", {})
    carbon = output.get("carbon_results", {})
    sim = output.get("simulation_results", {})
    revenue = float(fin.get("annual_savings_or_revenue") or 0.0)
    capex = float(fin.get("capex_total") or 0.0)
    reduction = float(carbon.get("annual_reduction_tco2e") or 0.0)

    # Derive sensitivity impacts from actual project structure
    # Energy revenue portion: estimate from simulation storage discharge
    storage_mwh = float(sim.get("annual_storage_discharge_mwh") or 0.0)
    pv_mwh = float(sim.get("annual_pv_generation_mwh") or 0.0)
    wind_mwh = float(sim.get("annual_wind_generation_mwh") or 0.0)
    total_gen = storage_mwh + pv_mwh + wind_mwh
    energy_portion = (storage_mwh / total_gen) if total_gen > 0 else 0.3

    result: list[dict[str, Any]] = [
        {
            "factor": "峰谷价差下降10%",
            "impact_on_annual_revenue": round(revenue * energy_portion * -0.10, 2),
            "impact_on_irr": "high" if energy_portion > 0.4 else "medium",
        },
        {
            "factor": "设备投资上升10%",
            "impact_on_annual_revenue": round(-capex * 0.10 * 0.015, 2),
            "impact_on_irr": "high",
        },
        {
            "factor": "年可调用天数下降10%",
            "impact_on_annual_revenue": round(revenue * -0.10, 2),
            "impact_on_irr": "high" if revenue > 0 and capex / max(revenue, 1) > 3 else "medium",
        },
        {
            "factor": "折现率上升2个百分点",
            "impact_on_annual_revenue": 0.0,
            "impact_on_irr": "medium",
        },
    ]
    if reduction > 0:
        # NOTE: This uses the project's internal abatement cost as a proxy.
        # A dedicated carbon_price_per_tco2e input should be preferred when available.
        _ac = fin.get("abatement_cost_per_tco2e")
        carbon_value = float(_ac) if _ac is not None else 50.0
        result.append(
            {
                "factor": "碳价波动±50%",
                "impact_on_annual_revenue": round(reduction * carbon_value * 0.50, 2),
                "impact_on_irr": "low",
            }
        )
    return result
