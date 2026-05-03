"""增强型敏感性分析：双变量热力图 + 蒙特卡洛"""
from __future__ import annotations
import random
from typing import Any


def run_sensitivity(output: dict[str, Any]) -> list[dict[str, Any]]:
    fin = output.get("financial_results", {})
    carbon = output.get("carbon_results", {})
    revenue = float(fin.get("annual_savings_or_revenue") or 0.0)
    reduction = float(carbon.get("annual_reduction_tco2e") or 0.0)
    irr = fin.get("irr")
    capex = float(fin.get("capex_total") or 0.0)

    results = [
        {
            "factor": "峰谷价差下降10%",
            "impact_on_annual_revenue": round(revenue * -0.08, 2),
            "irr_impact": "medium",
        },
        {
            "factor": "设备投资上升10%",
            "impact_on_annual_revenue": 0.0,
            "irr_impact": "high",
        },
        {
            "factor": "年可调用天数下降10%",
            "impact_on_annual_revenue": round(revenue * -0.06, 2),
            "irr_impact": "medium",
        },
    ]
    if reduction > 0:
        results.append({
            "factor": "绿电覆盖率下降10%",
            "impact_on_annual_revenue": round(reduction * -5, 2),
            "irr_impact": "medium",
        })

    # ── 双变量热力图（CAPEX × 发电量） ──
    capex_factors = [0.8, 0.9, 1.0, 1.1, 1.2]
    gen_factors = [0.8, 0.9, 1.0, 1.1, 1.2]
    heatmap = []
    for cf in capex_factors:
        row = []
        for gf in gen_factors:
            adj_irr = (irr or 0.15) * (gf / cf) if cf > 0 else None
            row.append(round(adj_irr, 4) if adj_irr else None)
        heatmap.append({
            "capex_factor": cf,
            "gen_factors": gen_factors,
            "irr_values": row,
        })
    if heatmap:
        results.append({
            "factor": "双变量敏感性（CAPEX × 发电量）",
            "heatmap": heatmap,
            "irr_impact": "heatmap",
        })

    # ── 蒙特卡洛 IRR 模拟 ──
    if irr and capex > 0:
        random.seed(42)
        samples = []
        for _ in range(500):
            capex_noise = random.gauss(1.0, 0.08)  # CAPEX ±8% 标准差
            gen_noise = random.gauss(1.0, 0.06)     # 发电量 ±6% 标准差
            price_noise = random.gauss(1.0, 0.05)   # 电价 ±5% 标准差
            sampled_irr = irr * (gen_noise * price_noise / capex_noise)
            samples.append(min(max(sampled_irr, 0.0), 0.60))

        samples.sort()
        p10 = round(samples[int(len(samples) * 0.10)], 4)
        p50 = round(samples[int(len(samples) * 0.50)], 4)
        p90 = round(samples[int(len(samples) * 0.90)], 4)

        results.append({
            "factor": "蒙特卡洛 IRR 分布（500次模拟）",
            "monte_carlo": {
                "p10": p10,
                "p50": p50,
                "p90": p90,
                "samples": len(samples),
                "confidence": f"{p50*100:.1f}% 中位数，90%概率 ≥{p10*100:.1f}%"
            },
            "irr_impact": "monte_carlo",
        })

    return results
