"""自然语言分析报告 — 生成结论性文字"""
from typing import Any

def generate_narrative(output: dict[str, Any]) -> str:
    f = output.get("financial_results", {})
    s = output.get("recommended_solution", {})
    d = output.get("dispatch_results", {})
    sim = output.get("simulation_results", {})
    carbon = output.get("carbon_results", {})
    proj = output.get("project_summary", {})
    sens = output.get("sensitivity_results", [])

    lines = []

    # 1. 总体评价
    irr = f.get("irr")
    if irr:
        if irr > 0.30: grade = "优秀，极具投资价值"
        elif irr > 0.15: grade = "良好，具备投资条件"
        elif irr > 0.08: grade = "一般，需审慎评估"
        else: grade = "较差，不建议投资"
    else: grade = "经济性不足"

    name = proj.get("project_name", "本项目")
    lines.append(f"### 总体评价")
    lines.append(f"{name}整体投资价值评为「{grade}」。")

    # 核心指标
    pv = s.get("pv_mwp") or 0
    w = s.get("wind_mw") or 0
    storage = f"{s.get('storage_power_mw') or 0}MW/{s.get('storage_energy_mwh') or 0}MWh"
    cycles = d.get("storage_equivalent_full_cycles_per_year") or 0
    lines.append(f"项目配置光伏{pv}MWp{'、风电' + str(w) + 'MW' if w else ''}，储能{storage}，年循环{cycles:.0f}次。")

    # 2. 财务分析
    lines.append(f"\n### 财务分析")
    irr_str = f"{irr*100:.2f}%" if irr else "无"
    lines.append(f"项目全投资内部收益率 (IRR) 为 {irr_str}。")

    eq_irr = f.get("equity_irr")
    if eq_irr:
        lines.append(f"考虑{float(f.get('debt_ratio', 0.7))*100:.0f}%负债融资后，权益IRR达到{eq_irr*100:.2f}%，杠杆倍数为{eq_irr/irr:.1f}倍。")

    npv = f.get("npv", 0)
    lines.append(f"净现值 (NPV) 为{npv/1e4:,.0f}万元{'，项目在财务上可行' if npv > 0 else '，项目在财务上不可行' if npv < 0 else '，项目收支平衡'}。")

    pb = f.get("payback_years")
    if pb:
        dpb = f.get("dyn_payback_years")
        lines.append(f"静态投资回收期{pb:.0f}年{'，动态回收期' + f'{dpb:.0f}年' if dpb else ''}。")

    lcoe = f.get("lcoe")
    if lcoe:
        lines.append(f"平准化度电成本 (LCOE) 为{lcoe:.4f}元/kWh。")

    dscr = f.get("dscr_min")
    if dscr:
        bankable = "满足银行放贷条件 (DSCR>1.2)" if dscr > 1.2 else "偿债能力偏紧"
        lines.append(f"最低偿债覆盖率 (DSCR) 为{dscr:.2f}，{bankable}。")

    # 3. 绿电与碳
    coverage = sim.get("coverage_ratio", 0)
    lines.append(f"\n### 绿电与碳减排")
    lines.append(f"项目绿电覆盖率为{coverage*100:.1f}%")

    red = carbon.get("annual_reduction_tco2e", 0)
    if red:
        ccer = f.get("ccer_total_value", 0)
        gec = f.get("gec_revenue_annual", 0)
        lines.append(f"年减排{red:,.0f}tCO₂e")
        if ccer: lines.append(f"全周期CCER碳资产价值约{ccer/1e4:,.0f}万元")
        if gec: lines.append(f"年绿证 (GEC) 收益约{gec/1e4:,.1f}万元")

    # 4. 风险提示
    lines.append(f"\n### 风险分析")

    for item in sens:
        if 'monte_carlo' in item:
            mc = item['monte_carlo']
            lines.append(f"蒙特卡洛模拟显示：IRR中位数{mc['p50']*100:.1f}%，90%概率不低于{mc['p10']*100:.1f}%。")
        elif 'heatmap' in item:
            hm = item['heatmap']
            base_row = [r for r in hm if abs(r['capex_factor'] - 1.0) < 0.01]
            if base_row:
                irrs = base_row[0]['irr_values']
                gen_80 = irrs[0]
                gen_120 = irrs[-1]
                if gen_80 and gen_120:
                    lines.append(f"双变量敏感性：发电量下降20%时IRR约{gen_80*100:.1f}%，上升20%时约{gen_120*100:.1f}%。")

    # 5. 横向对比
    lines.append(f"\n### 行业对比")
    if irr:
        if irr > 0.25: lines.append(f"该项目IRR显著高于行业平均水平（通常8-12%），投资价值突出。")
        elif irr > 0.12: lines.append(f"该项目IRR处于行业中游水平。")
        else: lines.append(f"该项目IRR低于行业平均水平，需关注成本控制和收益提升空间。")
    if lcoe:
        if lcoe < 0.25: lines.append(f"LCOE {lcoe:.4f}元/kWh 低于全国工商业电价均价（约0.65元/kWh），具有成本优势。")

    # 6. 建议
    lines.append(f"\n### 建议")
    recommendations = []
    if cycles and cycles < 200:
        recommendations.append("储能年循环次数偏低，建议优化调度策略或评估是否有必要配置当前储能规模。")
    if dscr and dscr < 1.2:
        recommendations.append("DSCR低于银行可贷标准(1.2)，建议增加资本金比例或寻求更低成本的融资方案。")
    if coverage and coverage < 0.5:
        recommendations.append("绿电覆盖率低于50%，存在大量购电成本，建议评估增配新能源容量的经济性。")
    if not recommendations:
        recommendations.append("项目指标良好，建议加快推进立项和接入系统设计。")
        recommendations.append("重点监控电价政策和碳市场变化，两项因素对项目收益影响最大。")
    for r in recommendations:
        lines.append(f"- {r}")

    return "\n".join(lines)
