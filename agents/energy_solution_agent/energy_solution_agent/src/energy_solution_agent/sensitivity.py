"""真实场景重跑型敏感性分析：单变量重跑 + 双变量热力图 + 蒙特卡洛近似"""
from __future__ import annotations
import copy
import random
from typing import Any, Callable

_RUNNER: Callable[..., tuple[dict[str, Any], dict[str, Any], str]] | None = None


def set_sensitivity_runner(runner: Callable[..., tuple[dict[str, Any], dict[str, Any], str]]) -> None:
    global _RUNNER
    _RUNNER = runner


def _rerun(payload: dict[str, Any], enable_live_rules: bool = False) -> dict[str, Any] | None:
    if _RUNNER is None:
        return None
    out, _, _ = _RUNNER(payload, enable_live_rules=enable_live_rules, sensitivity_depth=0)
    return out


def run_sensitivity(output: dict[str, Any], payload: dict[str, Any], enable_live_rules: bool = False) -> list[dict[str, Any]]:
    fin = output.get("financial_results", {})
    carbon = output.get("carbon_results", {})
    revenue = float(fin.get("annual_savings_or_revenue") or 0.0)
    irr = fin.get("irr")
    capex = float(fin.get("capex_total") or 0.0)
    base_reduction = float(carbon.get("annual_reduction_tco2e") or 0.0)
    results: list[dict[str, Any]] = []

    # ── 单变量真实重跑 ──
    scenarios = []
    market_mode = str(payload.get("market_data", {}).get("market_mode") or "").lower()
    if market_mode in {"offgrid_internal", "ppa"}:
        scenarios.append(("替代电价下降10%", ("market_data", "fuel_cost_per_kwh"), 0.9))
        scenarios.append(("替代电价上升10%", ("market_data", "fuel_cost_per_kwh"), 1.1))
    scenarios.append(("设备投资上升10%", ("financial", "capex", "pv_cost_per_w"), 1.1))
    scenarios.append(("发电量下降10%", ("resource_data", "solar", "p50_factor"), 0.9))

    for label, path, factor in scenarios:
        test = copy.deepcopy(payload)
        target = test
        for key in path[:-1]:
            target = target.setdefault(key, {})
        leaf = path[-1]
        current = target.get(leaf)
        if current is None:
            # 对CAPEX全体一起放大
            if label.startswith("设备投资"):
                for cap_key in ["pv_cost_per_w", "wind_cost_per_w", "storage_system_cost_per_kwh"]:
                    if cap_key in test.get("financial", {}).get("capex", {}):
                        test["financial"]["capex"][cap_key] *= factor
            elif label.startswith("发电量"):
                test.setdefault("resource_data", {}).setdefault("wind", {}).setdefault("p50_factor", 1.0)
                test.setdefault("resource_data", {}).setdefault("solar", {}).setdefault("p50_factor", 1.0)
                test["resource_data"]["solar"]["p50_factor"] *= factor
                test["resource_data"]["wind"]["p50_factor"] *= factor
        else:
            target[leaf] = current * factor
        rerun = _rerun(test, enable_live_rules=enable_live_rules)
        if rerun:
            rerun_fin = rerun.get("financial_results", {})
            rerun_rev = float(rerun_fin.get("annual_savings_or_revenue") or 0.0)
            results.append({
                "factor": label,
                "impact_on_annual_revenue": round(rerun_rev - revenue, 2),
                "impact_on_irr": round((float(rerun_fin.get("irr") or 0.0) - float(irr or 0.0)) * 100, 2),
                "irr_after": rerun_fin.get("irr"),
                "npv_after": rerun_fin.get("npv"),
            })

    # ── 双变量热力图（CAPEX × 发电量） — 真实重跑小网格 ──
    capex_factors = [0.9, 1.0, 1.1]
    gen_factors = [0.9, 1.0, 1.1]
    heatmap = []
    for cf in capex_factors:
        row = []
        for gf in gen_factors:
            test = copy.deepcopy(payload)
            # CAPEX 扰动
            for cap_key in ["pv_cost_per_w", "wind_cost_per_w", "storage_system_cost_per_kwh"]:
                if cap_key in test.get("financial", {}).get("capex", {}):
                    test["financial"]["capex"][cap_key] *= cf
            # 发电量扰动
            test.setdefault("resource_data", {}).setdefault("solar", {}).setdefault("p50_factor", 1.0)
            test.setdefault("resource_data", {}).setdefault("wind", {}).setdefault("p50_factor", 1.0)
            test["resource_data"]["solar"]["p50_factor"] *= gf
            test["resource_data"]["wind"]["p50_factor"] *= gf
            rerun = _rerun(test, enable_live_rules=enable_live_rules)
            row.append(round(float(rerun.get("financial_results", {}).get("irr") or 0.0), 4) if rerun else None)
        heatmap.append({
            "capex_factor": cf,
            "gen_factors": gen_factors,
            "irr_values": row,
        })
    results.append({
        "factor": "双变量敏感性（CAPEX × 发电量）",
        "heatmap": heatmap,
        "irr_impact": "heatmap",
    })

    # ── 蒙特卡洛 IRR 模拟（轻量近似保留） ──
    if irr and capex > 0:
        random.seed(random.randint(0, 999999))
        samples = []
        for _ in range(500):
            capex_noise = random.gauss(1.0, 0.08)
            gen_noise = random.gauss(1.0, 0.06)
            price_noise = random.gauss(1.0, 0.05)
            combined = (gen_noise * price_noise) / capex_noise
            sampled_irr = irr * combined
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
                "confidence": f"{p50*100:.1f}% 中位数，90%概率 ≥{p10*100:.1f}%",
            },
            "irr_impact": "monte_carlo",
        })

    # 绿电覆盖率提示项（真实重跑）
    if base_reduction > 0:
        test = copy.deepcopy(payload)
        test.setdefault("resource_data", {}).setdefault("solar", {}).setdefault("p50_factor", 1.0)
        test.setdefault("resource_data", {}).setdefault("wind", {}).setdefault("p50_factor", 1.0)
        test["resource_data"]["solar"]["p50_factor"] *= 0.95
        test["resource_data"]["wind"]["p50_factor"] *= 0.95
        rerun = _rerun(test, enable_live_rules=enable_live_rules)
        if rerun:
            new_reduction = float(rerun.get("carbon_results", {}).get("annual_reduction_tco2e") or 0.0)
            results.append({
                "factor": "绿电覆盖率下降5%",
                "impact_on_annual_revenue": round(float(rerun.get("financial_results", {}).get("annual_savings_or_revenue") or 0.0) - revenue, 2),
                "impact_on_irr": round((float(rerun.get("financial_results", {}).get("irr") or 0.0) - float(irr or 0.0)) * 100, 2),
                "impact_on_carbon_reduction": round(new_reduction - base_reduction, 2),
                "irr_after": rerun.get("financial_results", {}).get("irr"),
            })

    return results
