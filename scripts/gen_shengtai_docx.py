#!/usr/bin/env python3
import sys, json
from pathlib import Path

agent_dir = Path.home() / ".openclaw/workspace/agents/energy_solution_agent/energy_solution_agent"
sys.path.insert(0, str(agent_dir / "src"))

from energy_solution_agent.report_to_docx import build_docx as generate_docx
from energy_solution_agent.report_charts import build_report_charts as generate_all_charts

result_file = agent_dir / "out/shengtai_result.json"
docx_file = agent_dir / "out/盛泰药业储能方案报告.docx"

with open(result_file) as f:
    result = json.load(f)

# Generate charts first
chart_dir = agent_dir / "out/charts"
chart_dir.mkdir(exist_ok=True)

chart_paths = generate_all_charts(result, str(chart_dir))
print(f"Charts: {chart_paths}")

# Generate docx
docx_path = generate_docx(result)
print(f"Docx: {docx_path}")