"""自然语言分析报告 — 生成结论性文字（大师级版）"""
from typing import Any


def generate_narrative(output: dict[str, Any]) -> str:
    f = output.get("financial_results", {})
    s = output.get("recommended_solution", {})
    d = output.get("dispatch_results", {})
    sim = output.get("simulation_results", {})
    carbon = output.get("carbon_results", {})
    proj = output.get("project_summary", {})
    res = output.get("resource_results", {})
    sens = output.get("sensitivity_results", [])
    gaps = output.get("data_gaps", [])
    risks = output.get("risks", [])

    lines = []

    # 1. 总体评价
    irr = f.get("irr")
    if irr:
        if irr > 0.30:
            grade = "优秀，极具投资价值"
        elif irr > 0.15:
            grade = "良好，具备投资条件"
        elif irr > 0.08:
            grade = "一般，需审慎评估"
        else:
            grade = "较差，不建议独立投资"
    else:
        grade = "经济性不足"

    name = proj.get("project_name", "本项目")
    scenario = proj.get("scenario_type", "未指定")
    lines.append(f"### 总体评价")
    lines.append(f"{name}（{scenario}）整体投资价值评为「{grade}」。")

    pv = s.get("pv_mwp") or 0
    w = s.get("wind_mw") or 0
    storage_p = s.get("storage_power_mw") or 0
    storage_e = s.get("storage_energy_mwh") or 0
    cycles = float(d.get("storage_equivalent_full_cycles_per_year") or 0)

    config = f"配置光伏{pv}MWp"
    if w:
        config += f"、风电{w}MW"
    if storage_p:
        config += f"、储能{storage_p}MW/{storage_e}MWh（年循环{cycles:.0f}次）"
    lines.append(f"项目{config}。")

    # 资源来源说明
    pv_src = res.get("pv_resource_source") or res.get("pv_resource_basis", "无")
    wind_src = res.get("wind_resource_source") or res.get("wind_resource_basis", "无")
    lines.append(f"光伏资源来源：{pv_src}；风资源来源：{wind_src}。")

    # 2. 财务分析
    npv = f.get("npv", 0)
    lines.append(f"\n### 财务分析")
    irr_str = f"{irr*100:.2f}%" if irr else "无"
    lines.append(f"项目全投资内部收益率 (IRR) 为 {irr_str}，净现值 (NPV) 为{npv/1e4:,.0f}万元。")
    if npv > 0:
        lines.append("项目在财务上可行。")
    elif npv < 0:
        lines.append("项目在财务上不可行，需调整边界条件或优化配置。")

    eq_irr = f.get("equity_irr")
    if eq_irr and irr and irr > 0:
        lines.append(f"考虑{float(f.get('debt_ratio', 0.7))*100:.0f}%负债融资后，权益IRR达到{eq_irr*100:.2f}%（杠杆倍数{eq_irr/irr:.1f}倍）。")

    pb = f.get("payback_years")
    if pb:
        dpb = f.get("dyn_payback_years")
        lines.append(f"静态回收期{pb:.0f}年{'（动态回收期' + f'{dpb:.0f}年）' if dpb else ''}。")

    dscr = f.get("dscr_min")
    if dscr:
        lines.append(f"偿债覆盖率 DSCR 为{dscr:.2f}，{'满足银行可贷标准（>1.2）' if dscr >= 1.2 else '不满足银行可贷标准，需优化融资结构'}。")

    lcoe = f.get("lcoe")
    lcos = f.get("lcos")
    if lcoe or lcos:
        detail = ""
        if lcoe: detail += f"系统LCOE={lcoe}元/kWh"
        if lcos: detail += f"{'；' if detail else ''}储能LCOS={lcos}元/kWh"
        lines.append(f"平准化成本：{detail}。")

    pv_lcoe = f.get("pv_lcoe")
    wind_lcoe = f.get("wind_lcoe")
    st_lcos = f.get("storage_lcos")
    if pv_lcoe or wind_lcoe or st_lcos:
        detail_parts = []
        if pv_lcoe: detail_parts.append(f"光伏={pv_lcoe}")
        if wind_lcoe: detail_parts.append(f"风电={wind_lcoe}")
        if st_lcos: detail_parts.append(f"储能={st_lcos}")
        lines.append(f"分项成本：" + "；".join(detail_parts))

    # 3. 收益结构
    revenue = sim.get("annual_savings_or_revenue", 0)
    baseline = f.get("baseline_annual_energy_cost")
    if baseline:
        lines.append(f"\n### 收益与能源成本")
        lines.append(f"项目投产后年能源成本由基线{baseline/1e4:,.0f}万元降至{f.get('annual_energy_charge_cost',0)/1e4:,.0f}万元，年节省{revenue/1e4:,.0f}万元。")

    coverage = sim.get("coverage_ratio")
    if coverage is not None:
        lines.append(f"绿电覆盖率{coverage*100:.1f}%。")

    sc_ratio = sim.get("renewable_self_consumption_ratio")
    if sc_ratio is not None:
        lines.append(f"新能源自行消纳率{sc_ratio*100:.1f}%。")

    # 4. 排放分析
    lines.append(f"\n### 排放分析")
    baseline_em = carbon.get("baseline_emissions_tco2e", 0)
    post_em = carbon.get("post_project_emissions_tco2e", 0)
    reduction = carbon.get("annual_reduction_tco2e", 0)
    lines.append(f"基线碳排放{baseline_em:,.0f} tCO₂e/年，项目后排放{post_em:,.0f} tCO₂e/年，年减排{reduction:,.0f} tCO₂e。")

    carbon_path = carbon.get("carbon_path_breakdown", [])
    if carbon_path:
        for item in carbon_path:
            lines.append(f"- 减排路径「{item.get('path')}」：减排{item.get('reduction_tco2e'):,.0f} tCO₂e，占比{item.get('share')*100:.1f}%。")

    # 5. 敏感性
    lines.append(f"\n### 敏感性分析")
    sens_irr = [it for it in sens if "impact_on_irr" in it]
    if sens_irr:
        for it in sens_irr[:3]:
            irr_delta = it.get("impact_on_irr")
            idx = f"IRR{irr_delta:+.2f}pct" if irr_delta else ""
            lines.append(f"- {it['factor']}：年收益影响{it['impact_on_annual_revenue']/1e4:.0f}万元{idx}。")

    mc_items = [it for it in sens if "monte_carlo" in it]
    if mc_items:
        mc = mc_items[0]["monte_carlo"]
        lines.append(f"- 蒙特卡洛模拟（500次）：P10={mc['p10']*100:.1f}%、P50={mc['p50']*100:.1f}%、P90={mc['p90']*100:.1f}%{mc['confidence']}。")

    # 6. 风险与数据缺口
    if risks or gaps:
        lines.append(f"\n### 注意事项")
    for g in gaps:
        lines.append(f"- 数据缺口：{g}")
    for r in risks:
        lines.append(f"- 提示：{r}")

    # 7. 结论建议
    lines.append(f"\n### 结论建议")
    if npv > 0 and irr and irr > 0.15:
        lines.append("建议按推荐方案推进，进一步完成正式可研。")
    elif npv > 0:
        lines.append("项目经济性可行，但需关注边界条件变化风险。")
    else:
        lines.append("当前方案经济性不足，建议通过调整配置（缩小规模、降低CAPEX或争取政策支持）重新评估。")
    lines.append(f"本报告基于当前输入条件生成，结论仅供前置方案参考，不替代正式可研或投决用报告。")

    return "\n".join(lines) + "\n"
