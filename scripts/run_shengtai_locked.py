#!/usr/bin/env python3
import sys, json
from pathlib import Path

agent_dir = Path.home() / ".openclaw/workspace/agents/energy_solution_agent/energy_solution_agent"
sys.path.insert(0, str(agent_dir / "src"))

from energy_solution_agent.engine import analyze_project

with open(agent_dir / "examples/shengtai_emc_locked.json") as f:
    data = json.load(f)

result, dispatch, scenario = analyze_project(data)

with open(agent_dir / "out/shengtai_emc_locked_result.json", "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

fin = result.get("financial_results", {})
sol = result.get("recommended_solution", {})
disp = result.get("dispatch_results", {})
sim = result.get("simulation_results", {})

print(f"=== 3.75MW/7.5MWh 锁死版本结果 ===")
print(f"储能: {sol.get('storage_power_mw','?')}MW / {sol.get('storage_energy_mwh','?')}MWh")
print(f"循环次数/年: {disp.get('storage_equivalent_full_cycles_per_year','?')}")
print(f"年放电量: {sim.get('annual_storage_discharge_mwh','?')}MWh")
print(f"年充电量: {sim.get('annual_storage_charge_mwh','?')}MWh")
print(f"IRR: {fin.get('irr','N/A')}")
print(f"回收期: {fin.get('payback_years','N/A')}年")
print(f"NPV: {fin.get('npv','N/A')}万元")
print(f"年收益: {fin.get('annual_savings_or_revenue','N/A')}万元")
print(f"CAPEX: {fin.get('capex_total','N/A')}元")