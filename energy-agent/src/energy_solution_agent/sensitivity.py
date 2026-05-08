from __future__ import annotations

from typing import Any


def run_sensitivity(output: dict[str, Any]) -> list[dict[str, Any]]:
    fin = output.get("financial_results", {})
    carbon = output.get("carbon_results", {})
    revenue = float(fin.get("annual_savings_or_revenue") or 0.0)
    reduction = float(carbon.get("annual_reduction_tco2e") or 0.0)
    result = [
        {
            "factor": "峰谷价差下降10%",
            "impact_on_annual_revenue": round(revenue * -0.08, 2),
            "impact_on_irr": "medium",
        },
        {
            "factor": "设备投资上升10%",
            "impact_on_annual_revenue": 0.0,
            "impact_on_irr": "high",
        },
        {
            "factor": "年可调用天数下降10%",
            "impact_on_annual_revenue": round(revenue * -0.06, 2),
            "impact_on_irr": "medium",
        },
    ]
    if reduction > 0:
        result.append(
            {
                "factor": "绿电覆盖率下降10%",
                "impact_on_annual_revenue": round(reduction * -5, 2),
                "impact_on_irr": "medium",
            }
        )
    return result
