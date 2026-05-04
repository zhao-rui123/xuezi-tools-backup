#!/usr/bin/env python3
import sys, json
from pathlib import Path

agent_dir = Path.home() / ".openclaw/workspace/agents/energy_solution_agent/energy_solution_agent"
sys.path.insert(0, str(agent_dir / "src"))

from energy_solution_agent.engine import analyze_project

input_file = agent_dir / "examples/shengtai_storage_input.json"
output_file = agent_dir / "out/shengtai_result.json"
report_file = agent_dir / "out/shengtai_report.md"

agent_dir.joinpath("out").mkdir(exist_ok=True)

with open(input_file) as f:
    data = json.load(f)

result, dispatch_results, scenario = analyze_project(data)

with open(output_file, "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

# Generate markdown report
report = f"""# 山东盛泰药业用户侧储能项目 分析报告

## 项目基本信息
- 场景：{result.get('project_summary',{}).get('scenario_type','user_side_storage')}
- 地点：山东济南
- 数据天数：主线67天 / 支线80天

## 负荷特征
- 日均用电：41.2 万kWh/天
- 最大峰值：20840 kW
- 平均峰值：18066 kW
- 最小谷值：7953 kW
- 年负荷：约1.5亿kWh/年

## 推荐方案

### 储能规模
"""
sol = result.get("recommended_solution", {})
fin = result.get("financial_results", {})

report += f"""
- 储能功率：{sol.get('storage_power_mw','待定')} MW
- 储能能量：{sol.get('storage_energy_mwh','待定')} MWh
- 电池类型：LFP

### 经济指标
"""
if fin:
    report += f"""
- IRR：{fin.get('irr', 'N/A')}%
- 回收期：{fin.get('payback_years', 'N/A')} 年
- NPV：{fin.get('npv', 'N/A')} 万元
- 年收益：{fin.get('annual_savings_or_revenue', 'N/A')} 万元
"""
else:
    report += "\n- 等待详细计算结果...\n"

report += f"""

## 财务摘要
{json.dumps(result.get('financial_results', {}), indent=2, ensure_ascii=False)}
"""

with open(report_file, "w") as f:
    f.write(report)

print(json.dumps({
    "status": "ok",
    "output": str(output_file),
    "report": str(report_file),
    "result": result
}, indent=2, ensure_ascii=False))