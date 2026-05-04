#!/usr/bin/env python3
"""对比不同储能规模在EMC模式下的IRR"""
import sys
from pathlib import Path
agent_dir = Path.home() / ".openclaw/workspace/agents/energy_solution_agent/energy_solution_agent"
sys.path.insert(0, str(agent_dir / "src"))
from energy_solution_agent.engine import analyze_project
import json

scenarios = {
    "2MW/4MWh": {"power_kw": 2000, "energy_kwh": 4000},
    "3.75MW/7.5MWh": {"power_kw": 3750, "energy_kwh": 7500},
    "4MW/8MWh": {"power_kw": 4000, "energy_kwh": 8000},
    "5MW/10MWh": {"power_kw": 5000, "energy_kwh": 10000},
    "5.5MW/11MWh(Agent最优)": {"power_kw": 5488, "energy_kwh": 10976},
}

results = {}
for name, cfg in scenarios.items():
    input_data = {
        "project_info": {
            "project_name": "盛泰EMC规模对比",
            "scenario_type": "user_side_storage",
            "lat": 36.65, "lon": 117.0,
            "resource_mode": "auto_fetch",
        },
        "resource_data": {"solar": {}, "wind": {}},
        "load_data": {
            "annual_consumption_mwh": 15000,
            "peak_load_kw": 20840,
            "valley_load_kw": 7953,
            "load_factor": 0.73,
            "load_profile_monthly": {
                "2025-12": {"days": 8, "daily_avg_kwh": 386005, "peak_kw": 19760},
                "2026-01": {"days": 31, "daily_avg_kwh": 423432, "peak_kw": 21107},
                "2026-02": {"days": 28, "daily_avg_kwh": 406279, "peak_kw": 20737}
            }
        },
        "market_data": {
            "market_mode": "tou_tariff",
            "shandong_tou": {
                "peak_hours": [[8,11],[14,17]],
                "shoulder_hours": [[7,8],[11,14],[17,18]],
                "valley_hours": [[23,7]],
                "peak_price_rmb_per_kwh": 0.92,
                "shoulder_price_rmb_per_kwh": 0.64,
                "valley_price_rmb_per_kwh": 0.31,
                "demand_charge_rmb_per_kw_month": 33
            }
        },
        "equipment": {
            "storage": {
                "power_candidate_kw": [cfg["power_kw"]],
                "energy_candidate_kwh": [cfg["energy_kwh"]],
                "selected_power_kw": cfg["power_kw"],
                "selected_energy_kwh": cfg["energy_kwh"],
                "battery_type": "LFP",
                "roundtrip_efficiency": 0.85,
                "annual_degradation": 0.02,
                "battery_cycles_per_year": 600
            },
            "solar": {"pv_mwp": 2.0}
        },
        "financial": {
            "project_years": 15,
            "discount_rate": 0.08,
            "capex_per_kwh": 1600,
            "opex_pct_of_capex": 1.5,
            "optimization_target": "irr",
            "is_overseas_project": False,
            "tax_rate_pct": 25,
            "residual_value_pct": 5,
            "emc": {"investor_share_pct": 90},
            "vpp_revenue_annual_rmb": 320000
        },
        "network_and_design": {"grid_connection_kv": 110, "transformer_capacity_kva": 40000}
    }
    
    result, dispatch, scenario = analyze_project(input_data)
    fin = result.get("financial_results", {})
    sim = result.get("simulation_results", {})
    
    results[name] = {
        "irr": fin.get("irr", 0),
        "payback": fin.get("payback_years", 0),
        "npv": fin.get("npv", 0),
        "annual_revenue": fin.get("annual_savings_or_revenue", 0),
        "capex": fin.get("capex_total", 0),
        "pv_gen": sim.get("annual_pv_generation_mwh", 0),
        "storage_cycles": dispatch.get("storage_equivalent_full_cycles_per_year", 0)
    }
    print(f"{name}: IRR={fin.get('irr',0)*100:.2f}%, 回收期={fin.get('payback_years',0)}年, NPV={fin.get('npv',0)/10000:.0f}万")

print("\n=== 对比汇总 ===")
print(f"{'规模':<25} {'IRR':>8} {'回收期':>8} {'NPV(万)':>10} {'CAPEX(万)':>10}")
for name, r in results.items():
    print(f"{name:<25} {r['irr']*100:>7.2f}% {r['payback']:>7.1f}y {r['npv']/10000:>10.0f} {r['capex']/10000:>10.0f}")