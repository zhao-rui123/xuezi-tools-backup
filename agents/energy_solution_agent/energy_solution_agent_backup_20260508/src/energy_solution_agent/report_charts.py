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

    # 4. 现金流曲线图
    fin = result_json.get("financial_results", {})
    cap = float(fin.get("capex_total") or 0)
    rev = float(fin.get("annual_savings_or_revenue") or 0)
    if cap > 0 and rev > 0:
        proj_yrs = int(fin.get("project_years") or 15)
        disc = float(fin.get("discount_rate") or 0.08)
        yrs = list(range(proj_yrs + 1))
        cum_cf = [-cap]
        for y in range(1, proj_yrs + 1):
            cum_cf.append(cum_cf[-1] + rev * 0.9 ** (y-1) / (1+disc)**y)
        if cum_cf:
            plt.figure(figsize=(9, 4.8))
            plt.plot(yrs, cum_cf, marker="o", color="#4F81BD", linewidth=2)
            plt.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
            plt.title("项目折现现金流累计曲线")
            plt.xlabel("年份")
            plt.ylabel("累计折现现金流 (元)")
            plt.tight_layout()
            fp = out_path / "chart_cashflow.png"
            plt.savefig(fp, dpi=180)
            plt.close()
            charts["cashflow"] = str(fp)

    # 5. 敏感性 Tornado 图
    sens = result_json.get("sensitivity_results", []) or []
    tornado_labels = []
    tornado_values = []
    irr_after_vals = []
    for item in sens:
        if isinstance(item, dict) and isinstance(item.get("impact_on_annual_revenue"), (int, float)):
            tornado_labels.append(str(item.get("factor") or "未命名"))
            tornado_values.append(float(item.get("impact_on_annual_revenue")) / 1e4)
            # 获取扰动后IRR用于注释
            ia = item.get("irr_after")
            irr_after_vals.append(ia if ia else None)
    if tornado_labels and tornado_values:
        pairs = sorted(zip(tornado_labels, tornado_values, irr_after_vals), key=lambda x: abs(x[1]))
        labels = [p[0] for p in pairs]
        values = [p[1] for p in pairs]
        colors = ["#C0504D" if v < 0 else "#9BBB59" for v in values]
        plt.figure(figsize=(9, 5.5))
        bars = plt.barh(labels, values, color=colors, edgecolor="white")
        # 在柱上标注扰动后IRR
        for bar, v, ia_val in zip(bars, values, [p[2] for p in pairs]):
            if ia_val:
                label = f"IRR后{ia_val*100:.1f}%"
            else:
                label = ""
            if v >= 0:
                plt.text(bar.get_width() + max(values)*0.02, bar.get_y() + bar.get_height()/2, label, va="center", fontsize=8)
            else:
                plt.text(bar.get_width() + bar.get_width()*0.05 - max(values)*0.02, bar.get_y() + bar.get_height()/2, label, va="center", ha="right", fontsize=8)
        plt.title("敏感性 Tornado 图（年收益影响）")
        plt.xlabel("万元/年")
        plt.tight_layout()
        fp = out_path / "chart_tornado.png"
        plt.savefig(fp, dpi=180)
        plt.close()
        charts["tornado"] = str(fp)

    return charts
