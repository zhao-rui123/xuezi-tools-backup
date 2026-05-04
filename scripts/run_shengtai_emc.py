#!/usr/bin/env python3
import sys, json
from pathlib import Path

agent_dir = Path.home() / ".openclaw/workspace/agents/energy_solution_agent/energy_solution_agent"
sys.path.insert(0, str(agent_dir / "src"))

from energy_solution_agent.engine import analyze_project

input_file = agent_dir / "examples/shengtai_emc_input.json"
output_file = agent_dir / "out/shengtai_emc_result.json"

with open(input_file) as f:
    data = json.load(f)

result, dispatch, scenario = analyze_project(data)

with open(output_file, "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

fin = result.get("financial_results", {})
sol = result.get("recommended_solution", {})

print(f"IRR: {fin.get('irr','N/A')}")
print(f"回收期: {fin.get('payback_years','N/A')}年")
print(f"NPV: {fin.get('npv','N/A')}万元")
print(f"年收益: {fin.get('annual_savings_or_revenue','N/A')}万元")
print(f"CAPEX: {fin.get('capex_total','N/A')}元")
print(f"dispatch吞吐量: {dispatch.get('storage_annual_throughput_mwh','N/A')}MWh")