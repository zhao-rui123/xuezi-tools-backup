#!/usr/bin/env python3
import sys, json
from pathlib import Path

agent_dir = Path.home() / ".openclaw/workspace/agents/energy_solution_agent/energy_solution_agent"
sys.path.insert(0, str(agent_dir / "src"))

from energy_solution_agent.engine import analyze_project

input_file = agent_dir / "examples/shengtai_competitor_input.json"
output_file = agent_dir / "out/shengtai_competitor_result.json"

with open(input_file) as f:
    data = json.load(f)

result, dispatch_results, scenario = analyze_project(data)

with open(output_file, "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

fin = result.get("financial_results", {})
sol = result.get("recommended_solution", {})

print("=== 对方参数方案 复算结果 ===")
print(f"储能: {sol.get('storage_power_mw','?')}MW / {sol.get('storage_energy_mwh','?')}MWh")
print(f"光伏: {sol.get('pv_mwp','?')}MWp")
print(f"IRR: {fin.get('irr', 'N/A')}")
print(f"回收期: {fin.get('payback_years', 'N/A')}年")
print(f"NPV: {fin.get('npv', 'N/A')}万元")
print(f"年收益: {fin.get('annual_savings_or_revenue', 'N/A')}万元")
print(f"CAPEX: {fin.get('capex_total', 'N/A')}元")
print(f"Dispatch年吞吐量: {dispatch_results.get('storage_annual_throughput_mwh', 'N/A')}MWh")
print(f"循环次数/年: {dispatch_results.get('storage_equivalent_full_cycles_per_year', 'N/A')}")

# Also save for comparison
summary = {
    "scenario": "对方方案参数验证",
    "storage_mw": sol.get('storage_power_mw'),
    "storage_mwh": sol.get('storage_energy_mwh'),
    "pv_mwp": sol.get('pv_mwp'),
    "irr": fin.get('irr'),
    "payback_years": fin.get('payback_years'),
    "npv": fin.get('npv'),
    "annual_revenue": fin.get('annual_savings_or_revenue'),
    "capex_total": fin.get('capex_total'),
    "dispatch_throughput_mwh": dispatch_results.get('storage_annual_throughput_mwh'),
    "cycles_per_year": dispatch_results.get('storage_equivalent_full_cycles_per_year')
}
print(f"\nJSON: {json.dumps(summary, ensure_ascii=False)}")