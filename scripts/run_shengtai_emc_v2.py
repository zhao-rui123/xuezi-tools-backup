#!/usr/bin/env python3
import sys, json
from pathlib import Path

agent_dir = Path.home() / ".openclaw/workspace/agents/energy_solution_agent/energy_solution_agent"
sys.path.insert(0, str(agent_dir / "src"))
from energy_solution_agent.engine import analyze_project

with open(agent_dir / "examples/shengtai_emc_v2_input.json") as f:
    data = json.load(f)

result, dispatch, scenario = analyze_project(data)

with open(agent_dir / "out/shengtai_emc_v2_result.json", "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

sol = result.get("recommended_solution", {})
fin = result.get("financial_results", {})
disp = result.get("dispatch_results", {})
sim = result.get("simulation_results", {})
rd = result.get("resource_results", {})

print("=== EMC v2 (真实市场价格) ===")
print(f"储能: {sol.get('storage_power_mw')}MW / {sol.get('storage_energy_mwh')}MWh")
print(f"光伏: {sol.get('pv_mwp')}MWp")
print(f"PV数据源: {rd.get('pv_resource_source')} ({rd.get('pv_resource_accuracy')})")
print(f"PV年发电量: {sim.get('annual_pv_generation_mwh')}MWh")
print(f"循环次数: {disp.get('storage_equivalent_full_cycles_per_year')}")
print(f"CAPEX: {fin.get('capex_total')/10000:.0f}万元")
print(f"年收益: {fin.get('annual_savings_or_revenue')/10000:.1f}万元")
print(f"IRR: {fin.get('irr')*100:.2f}%")
print(f"回收期: {fin.get('payback_years')}年")
print(f"NPV: {fin.get('npv')/10000:.0f}万元")