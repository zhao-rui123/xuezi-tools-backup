from __future__ import annotations

from typing import Any

from .constants import REPORT_TITLE


def build_report(output: dict[str, Any], diagnostics: dict[str, Any]) -> str:
    summary = output.get("project_summary", {})
    solution = output.get("recommended_solution", {})
    sim = output.get("simulation_results", {})
    dispatch = output.get("dispatch_results", {})
    fin = output.get("financial_results", {})
    carbon = output.get("carbon_results", {})
    market = output.get("market_and_settlement", {})
    resource = output.get("resource_results", {})
    sensitivity = output.get("sensitivity_results", [])

    lines = [
        f"# {REPORT_TITLE}",
        "",
        "## 项目概况",
        f"- 项目名称：{summary.get('project_name', 'N/A')}",
        f"- 场景类型：{summary.get('scenario_type', 'N/A')}",
        f"- 场景能力分类：{summary.get('scenario_detail_label')}",
        f"- 运行玩法：{summary.get('operation_mode')}",
        f"- 分析模式：{summary.get('analysis_mode')}",
        f"- 省份/区域：{summary.get('province', 'N/A')}",
        f"- 数据完整度：{diagnostics.get('data_completeness_grade', 'N/A')}",
        f"- 数据质量等级：{output.get('data_quality_results', {}).get('level', 'N/A')} / {output.get('data_quality_results', {}).get('score', 'N/A')}",
        f"- 省级规则状态：{market.get('province_profile_status')}",
        f"- 政策模式：{market.get('market_policy_mode')}",
        f"- 电网区域：{market.get('profile_grid_region')}",
        "",
        "## 推荐方案",
        f"- 光伏：{solution.get('pv_mwp') or 0} MWp",
        f"- 风电：{solution.get('wind_mw') or 0} MW",
        f"- 储能：{solution.get('storage_power_mw') or 0} MW / {solution.get('storage_energy_mwh') or 0} MWh",
        f"- 储能实际值：{solution.get('raw_storage_power_mw') or 0} MW / {solution.get('raw_storage_energy_mwh') or 0} MWh",
        f"- 充电容量：{solution.get('charging_capacity_mw') or 0} MW",
        f"- 供冷容量：{solution.get('cooling_capacity_rt') or 0} RT",
        f"- 供热容量：{solution.get('heating_capacity_mwth') or 0} MWth",
        "",
        "## 核心测算",
        f"- 年光伏发电量：{sim.get('annual_pv_generation_mwh')}",
        f"- 年风电发电量：{sim.get('annual_wind_generation_mwh')}",
        f"- 年新能源直供电量：{sim.get('annual_renewable_direct_use_mwh')}",
        f"- 年新能源富余电量：{sim.get('annual_renewable_surplus_mwh')}",
        f"- 年新能源转储电量：{sim.get('annual_renewable_to_storage_mwh')}",
        f"- 年新能源供负荷电量：{sim.get('annual_renewable_to_load_mwh')}",
        f"- 年电网供负荷电量：{sim.get('annual_grid_to_load_mwh')}",
        f"- 年电网充储电量：{sim.get('annual_grid_to_storage_mwh')}",
        f"- 年储能放电量：{sim.get('annual_storage_discharge_mwh')}",
        f"- 年储能充电量：{sim.get('annual_storage_charge_mwh')}",
        f"- 年充电量：{sim.get('annual_charging_energy_mwh')}",
        f"- 年供冷量：{sim.get('annual_cooling_energy_mwh')}",
        f"- 年供热量：{sim.get('annual_heating_energy_mwh')}",
        f"- 年购电量：{sim.get('annual_grid_purchase_mwh')}",
        f"- 年外送电量：{sim.get('annual_export_mwh')}",
        f"- 年弃电量：{sim.get('annual_curtailment_mwh')}",
        "",
        "## 市场规则要点",
    ]
    for item in market.get("market_rule_notes", []):
        lines.append(f"- {item}")
    if market.get("live_rule_effective_patch"):
        lines.append(f"- 在线规则生效字段：{', '.join(sorted(market['live_rule_effective_patch'].keys()))}")

    lines.extend(
        [
            "",
            "## 资源评估",
            f"- 光伏资源口径：{resource.get('pv_resource_basis')} / {resource.get('pv_resource_accuracy')}",
            f"- 光伏 P50/P90：{resource.get('pv_p50_generation_mwh')} / {resource.get('pv_p90_generation_mwh')}",
            f"- 光伏倾角/方位角/跟踪/温度修正：{resource.get('pv_tilt_factor')} / {resource.get('pv_azimuth_factor')} / {resource.get('pv_tracking_factor')} / {resource.get('pv_temperature_factor')}",
            f"- 光伏有效 PR：{resource.get('pv_pr_effective')}",
            f"- 光伏 LCOE：{resource.get('pv_lcoe_per_kwh')}",
            f"- 风电资源口径：{resource.get('wind_resource_basis')} / {resource.get('wind_resource_accuracy')}",
            f"- 风电 P50/P90：{resource.get('wind_p50_generation_mwh')} / {resource.get('wind_p90_generation_mwh')}",
            f"- 风电功率曲线：{resource.get('wind_power_curve_used')}",
            f"- 风电净折减系数：{resource.get('wind_net_factor')}",
            f"- 风电 LCOE：{resource.get('wind_lcoe_per_kwh')}",
            "",
            "## 调度结果",
            f"- 基线峰值购电功率：{dispatch.get('baseline_peak_grid_kw')}",
            f"- 储能后峰值购电功率：{dispatch.get('post_storage_peak_grid_kw')}",
            f"- 估算削峰量：{dispatch.get('estimated_peak_reduction_kw')}",
            f"- 日储能循环次数：{dispatch.get('daily_storage_cycles')}",
            f"- 储能策略模式：{dispatch.get('storage_strategy_mode')}",
            f"- 玩法路由原因：{dispatch.get('operation_mode_routing_reason')}",
            f"- 储能容量测算口径：{dispatch.get('storage_sizing_basis')}",
            f"- 净负荷测算峰值：{dispatch.get('sizing_net_load_peak_kw')}",
            f"- 新能源转储电量：{dispatch.get('renewable_to_storage_mwh')}",
            f"- 新能源供负荷电量：{dispatch.get('renewable_to_load_mwh')}",
            f"- 电网供负荷电量：{dispatch.get('grid_to_load_mwh')}",
            f"- 电网充储电量：{dispatch.get('grid_to_storage_mwh')}",
            f"- 弃电量：{dispatch.get('curtailed_renewable_mwh')}",
            f"- 年储能吞吐量：{dispatch.get('storage_annual_throughput_mwh')}",
            f"- 年等效满循环：{dispatch.get('storage_equivalent_full_cycles_per_year')}",
            f"- 估算寿命年限：{dispatch.get('storage_life_years_estimate')}",
            f"- 绿电/新能源充电占比：{dispatch.get('storage_charge_from_renewables_ratio')}",
            f"- 有效往返效率：{dispatch.get('storage_effective_round_trip_efficiency')}",
            f"- 预留 SOC / 保供 SOC：{dispatch.get('storage_reserved_soc_ratio')} / {dispatch.get('storage_backup_soc_ratio')}",
            f"- 年衰减率 / 寿命末容量比：{dispatch.get('storage_degradation_per_year')} / {dispatch.get('storage_end_of_life_capacity_ratio')}",
            f"- 充电排队指数：{dispatch.get('charging_queue_index')}",
            f"- 充电多车型多样性系数：{dispatch.get('charging_diversity_factor')}",
            f"- 年锅炉燃料当量：{dispatch.get('thermal_annual_boiler_fuel_equivalent_mwh')}",
            f"- 冷/热峰值需求：{dispatch.get('thermal_cooling_peak_kwth')} / {dispatch.get('thermal_heating_peak_kwth')}",
            "",
            "## 财务结果",
            f"- 年收益/节费：{fin.get('annual_savings_or_revenue')}",
            f"- 税模型：{fin.get('tax_model')}",
            f"- 年税费合计：{fin.get('annual_tax_total')}",
            f"- 年企业所得税：{fin.get('annual_income_tax')}",
            f"- 年增值税（应纳）：{fin.get('annual_vat_payable')}",
            f"- 年附加税（城建+教育）：{fin.get('annual_vat_surcharges_only')}",
            f"- 年增值税及附加合计：{fin.get('annual_vat_and_surcharges')}",
            f"- 期初进项留抵税额：{fin.get('initial_input_vat_credit')}",
            f"- 年电量电费：{fin.get('annual_energy_charge_cost')}",
            f"- 年需量电费：{fin.get('annual_demand_charge_cost')}",
            f"- 年辅助服务收益：{fin.get('annual_ancillary_service_revenue')}",
            f"- 年需求响应收益：{fin.get('annual_demand_response_revenue')}",
            f"- 年外送收益：{fin.get('annual_export_revenue')}",
            f"- 储能更换年份/成本：{fin.get('storage_replacement_year')} / {fin.get('storage_replacement_cost')}",
            f"- 运维递增率：{fin.get('opex_escalation_rate')}",
            f"- 项目 IRR：{fin.get('irr')}",
            f"- 回收期：{fin.get('payback_years')}",
            f"- NPV：{fin.get('npv')}",
            f"- 单位减碳成本：{fin.get('abatement_cost_per_tco2e')}",
            "",
            "## 碳结果",
            f"- 基线排放：{carbon.get('baseline_emissions_tco2e')}",
            f"- 项目后排放：{carbon.get('post_project_emissions_tco2e')}",
            f"- 年减排量：{carbon.get('annual_reduction_tco2e')}",
            f"- 声明边界：{carbon.get('claim_boundary_summary')}",
        ]
    )

    if carbon.get("carbon_path_breakdown"):
        lines.extend(["", "## 减排路径拆分"])
        for item in carbon["carbon_path_breakdown"]:
            lines.append(f"- {item.get('path', 'N/A')}：减排 {item.get('reduction_tco2e', 'N/A')} tCO2e，占比 {item.get('share', 'N/A')}")
    if carbon.get("industry_template"):
        lines.extend(["", "## 行业模板建议"])
        for path in carbon["industry_template"].get("major_paths", []):
            lines.append(f"- 推荐路径：{path}")
        for item in carbon["industry_template"].get("hard_to_abate", []):
            lines.append(f"- 难减排项：{item}")
    if dispatch.get("monthly_storage_revenue_breakdown"):
        lines.extend(["", "## 储能月度视图"])
        for item in dispatch["monthly_storage_revenue_breakdown"]:
            lines.append(
                f"- {item.get('month', 'N/A')}月：充电 {item.get('charge_mwh', 'N/A')} MWh，放电 {item.get('discharge_mwh', 'N/A')} MWh，毛收益 {item.get('gross_margin', 'N/A')}"
            )
    if dispatch.get("daily_cycle_schedule"):
        lines.extend(["", "## 日内循环明细"])
        for day in dispatch["daily_cycle_schedule"]:
            lines.append(f"- {day.get('date')}：{day.get('cycle_count')} 次循环，日毛收益 {day.get('gross_margin')}")
            for cycle in day.get("cycles", []):
                lines.append(
                    f"- 循环{cycle.get('cycle_index')}：充电 {cycle.get('charge_window')} / 放电 {cycle.get('discharge_window')} / 价差 {cycle.get('spread_yuan_per_mwh')} 元/MWh / 毛收益 {cycle.get('gross_margin')}"
                )
    if market.get("trading_execution_summary") or market.get("trading_settlement_summary"):
        lines.extend(
            [
                "",
                "## 电力交易结算视角",
                f"- 价差基准：{market.get('trading_charge_benchmark_price_per_kwh')} -> {market.get('trading_discharge_benchmark_price_per_kwh')} 元/kWh",
                f"- 交易价差：{market.get('trading_price_spread_per_kwh')} 元/kWh",
                f"- 价格波动指数：{market.get('trading_volatility_index')}",
                f"- 最优/最弱月份：{market.get('trading_best_month')} / {market.get('trading_worst_month')}",
                f"- 执行摘要：{market.get('trading_execution_summary')}",
                f"- 结算摘要：{market.get('trading_settlement_summary')}",
            ]
        )
    if market.get("cooptimization_execution_summary"):
        lines.extend(
            [
                "",
                "## 源网荷储协同优化摘要",
                f"- 回测天数：{market.get('historical_backtest_days')}",
                f"- 回测充电价均值：{market.get('historical_backtest_charge_price_avg')}",
                f"- 回测放电价均值：{market.get('historical_backtest_discharge_price_avg')}",
                f"- {market.get('cooptimization_execution_summary')}",
            ]
        )
    if market.get("spot_trading_cycle_summary"):
        lines.extend(
            [
                "",
                "## 日内实时套利计划",
                f"- 天数覆盖：{market.get('spot_trading_days_covered')}",
                f"- 总循环数：{market.get('spot_trading_total_cycles')}",
                f"- 平均价差：{market.get('spot_trading_average_spread_yuan_per_mwh')} 元/MWh",
                f"- 摘要：{market.get('spot_trading_cycle_summary')}",
            ]
        )
        for item in market.get("daily_spot_arbitrage_schedule", []):
            cycle_text = "；".join(
                f"充电 {cycle.get('charge_window')} / 放电 {cycle.get('discharge_window')} / 价差 {cycle.get('spread_yuan_per_mwh')} 元/MWh"
                for cycle in item.get("cycles", [])
            )
            lines.append(f"- {item.get('date')}：{cycle_text or '无满足阈值的循环'}")
    if dispatch.get("charging_segment_summary"):
        lines.extend(["", "## 充电结构摘要"])
        for item in dispatch["charging_segment_summary"]:
            lines.append(f"- {item.get('vehicle_type', 'N/A')}：日充电量 {item.get('daily_energy_kwh', 'N/A')} kWh，估算峰值 {item.get('peak_kw', 'N/A')} kW")

    lines.extend(["", "## 风险与缺口"])
    for item in output.get("data_gaps", []):
        lines.append(f"- 数据缺口：{item}")
    for item in output.get("risks", []):
        lines.append(f"- 风险：{item}")
    if output.get("data_quality_results", {}).get("checks"):
        lines.extend(["", "## 数据质量检查"])
        for item in output.get("data_quality_results", {}).get("checks", []):
            lines.append(f"- {item.get('name', 'N/A')}：{item.get('status', 'N/A')} - {item.get('message', 'N/A')}")

    if sensitivity:
        lines.extend(["", "## 敏感性分析"])
        for item in sensitivity:
            lines.append(f"- {item.get('factor', 'N/A')}：年度收益影响 {item.get('impact_on_annual_revenue', 'N/A')}，IRR 敏感度 {item.get('impact_on_irr', 'N/A')}")

    return "\n".join(lines) + "\n"
