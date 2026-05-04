#!/usr/bin/env python3
"""能源解决方案 Agent Wrapper — 飞书触发 → 自动执行"""
import sys, json, subprocess, tempfile, shutil
from pathlib import Path

AGENT_DIR = Path.home() / ".openclaw/workspace/agents/energy_solution_agent/energy_solution_agent"
TEMPLATES_DIR = AGENT_DIR / "examples"

TEMPLATES = {
    "零碳工厂": "zero_carbon_factory_input.json",
    "钢铁工厂": "steel_factory_input.json",
    "充电站": "charging_station_input.json",
    "数据中心": "data_center_input.json",
    "市场储能": "market_storage_input.json",
    "用户侧储能": "jingye_storage_input.json",
}

def run_agent(input_path, output_dir):
    """执行 agent 分析"""
    out_json = output_dir / "result.json"
    out_md = output_dir / "report.md"
    env = {"PYTHONPATH": "src", "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"}
    result = subprocess.run(
        ["python3", "-m", "energy_solution_agent", "analyze",
         "--input", str(input_path),
         "--output", str(out_json),
         "--report", str(out_md)],
        cwd=AGENT_DIR,
        capture_output=True, text=True, timeout=120,
        env=env,
    )
    if result.returncode != 0:
        return {"error": result.stderr[:500]}
    return json.loads(out_json.read_text())

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "用法: run_energy_agent.py <场景类型|template> [参数JSON]"}))
        return

    scene = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 用模板或自定义输入
        if scene in TEMPLATES:
            src = TEMPLATES_DIR / TEMPLATES[scene]
            if not src.exists():
                print(json.dumps({"error": f"模板 {scene} 不存在"}))
                return
            inp = json.loads(src.read_text())
        else:
            inp = params

        # 合并用户参数覆盖
        if params:
            inp.update(params)

        input_path = tmp / "input.json"
        input_path.write_text(json.dumps(inp, ensure_ascii=False))

        result = run_agent(input_path, tmp)

        if "error" in result:
            print(json.dumps({"error": result["error"]}))
            return

        # 提取关键结果
        fin = result.get("financial_results", {})
        sol = result.get("recommended_solution", {})
        dispatch = result.get("dispatch_results", {})

        summary = {
            "status": "ok",
            "scenario": result.get("project_summary", {}).get("scenario_type"),
            "pv_mwp": sol.get("pv_mwp"),
            "wind_mw": sol.get("wind_mw"),
            "storage": f"{sol.get('storage_power_mw')}MW/{sol.get('storage_energy_mwh')}MWh",
            "cycles_per_year": dispatch.get("storage_equivalent_full_cycles_per_year"),
            "irr": fin.get("irr"),
            "payback": fin.get("payback_years"),
            "npv": fin.get("npv"),
            "revenue": fin.get("annual_savings_or_revenue"),
            "report_path": str(tmp / "report.md"),
        }
        print(json.dumps(summary, ensure_ascii=False))

if __name__ == "__main__":
    main()
