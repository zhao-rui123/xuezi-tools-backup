from __future__ import annotations

from pathlib import Path
from typing import Any


def build_report_charts(result_json: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    """生成报告图表 PNG，返回 {chart_name: path}。

    说明：
    - 优先使用 matplotlib
    - 若环境无 matplotlib，则静默跳过
    """
    try:
        import matplotlib.pyplot as plt  # type: ignore
        from matplotlib import font_manager, rcParams  # type: ignore
    except Exception:
        return {}

    # 中文字体优先适配（macOS 常见字体）
    for font_name in ["PingFang SC", "Hiragino Sans GB", "STHeiti", "Arial Unicode MS"]:
        try:
            font_manager.findfont(font_name, fallback_to_default=False)
            rcParams["font.sans-serif"] = [font_name]
            rcParams["axes.unicode_minus"] = False
            break
        except Exception:
            continue

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    charts: dict[str, str] = {}

    # 数据
    d = result_json.get("dispatch_results", {})
    f = result_json.get("financial_results", {})
    market = result_json.get("market_and_settlement", {})
    monthly = d.get("monthly_storage_revenue_breakdown", []) or []
    revenue_breakdown = market.get("revenue_breakdown", []) or []

    # 1. 储能月度充放电图
    if monthly:
        months = [str(m.get("month")) for m in monthly]
        charge = [float(m.get("charge_mwh") or 0.0) for m in monthly]
        discharge = [float(m.get("discharge_mwh") or 0.0) for m in monthly]
        plt.figure(figsize=(9, 4.8))
        x = range(len(months))
        width = 0.38
        plt.bar([i - width/2 for i in x], charge, width=width, label="充电量(MWh)", color="#4F81BD")
        plt.bar([i + width/2 for i in x], discharge, width=width, label="放电量(MWh)", color="#C0504D")
        plt.xticks(list(x), months)
        plt.title("储能月度充放电量")
        plt.xlabel("月份")
        plt.ylabel("MWh")
        plt.legend()
        plt.tight_layout()
        fp = out_path / "chart_storage_monthly.png"
        plt.savefig(fp, dpi=180)
        plt.close()
        charts["storage_monthly"] = str(fp)

    # 2. 收益结构图
    if revenue_breakdown:
        labels = []
        values = []
        for item in revenue_breakdown:
            if isinstance(item, dict):
                labels.append(str(item.get("name") or "未命名"))
                values.append(float(item.get("amount") or 0.0) / 1e4)  # 万元
        if labels and values:
            plt.figure(figsize=(8, 4.8))
            plt.bar(labels, values, color=["#4F81BD", "#9BBB59", "#C0504D", "#8064A2", "#F79646", "#7F7F7F"][:len(labels)])
            plt.title("收益结构拆解")
            plt.ylabel("万元/年")
            plt.xticks(rotation=20)
            plt.tight_layout()
            fp = out_path / "chart_revenue_breakdown.png"
            plt.savefig(fp, dpi=180)
            plt.close()
            charts["revenue_breakdown"] = str(fp)

    # 3. CAPEX构成图
    capex_labels = ["光伏", "风电", "储能"]
    pv_cost = float(f.get("pv_lcoe") or 0.0)
    wind_cost = float(f.get("wind_lcoe") or 0.0)
    storage_cost = float(f.get("storage_lcos") or 0.0)
    if pv_cost or wind_cost or storage_cost:
        # 这里用平准化成本做相对可视化，避免当前financial_results没有直接分项CAPEX字段
        vals = [pv_cost, wind_cost, storage_cost]
        plt.figure(figsize=(6.8, 4.8))
        plt.pie(vals, labels=capex_labels, autopct="%1.1f%%", startangle=120, colors=["#4F81BD", "#9BBB59", "#C0504D"])
        plt.title("技术成本结构（LCOE/LCOS相对占比）")
        plt.tight_layout()
        fp = out_path / "chart_cost_structure.png"
        plt.savefig(fp, dpi=180)
        plt.close()
        charts["cost_structure"] = str(fp)

    # 4. 敏感性 Tornado 图
    sens = result_json.get("sensitivity_results", []) or []
    tornado_labels = []
    tornado_values = []
    for item in sens:
        if isinstance(item, dict) and isinstance(item.get("impact_on_annual_revenue"), (int, float)):
            tornado_labels.append(str(item.get("factor") or "未命名"))
            tornado_values.append(float(item.get("impact_on_annual_revenue")) / 1e4)
    if tornado_labels and tornado_values:
        pairs = sorted(zip(tornado_labels, tornado_values), key=lambda x: abs(x[1]))
        labels = [p[0] for p in pairs]
        values = [p[1] for p in pairs]
        colors = ["#C0504D" if v < 0 else "#9BBB59" for v in values]
        plt.figure(figsize=(8.5, 5.2))
        plt.barh(labels, values, color=colors)
        plt.title("敏感性 Tornado 图（年收益影响）")
        plt.xlabel("万元/年")
        plt.tight_layout()
        fp = out_path / "chart_tornado.png"
        plt.savefig(fp, dpi=180)
        plt.close()
        charts["tornado"] = str(fp)

    return charts
