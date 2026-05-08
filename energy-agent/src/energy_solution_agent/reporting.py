from __future__ import annotations

from typing import Any

from .constants import REPORT_TITLE


def build_report(output: dict[str, Any], diagnostics: dict[str, Any]) -> str:
    summary = output["project_summary"]
    solution = output["recommended_solution"]
    sim = output["simulation_results"]
    dispatch = output.get("dispatch_results", {})
    fin = output["financial_results"]
    carbon = output.get("carbon_results", {})
    market = output.get("market_and_settlement", {})
    resource = output.get("resource_results", {})
    sensitivity = output.get("sensitivity_results", [])

    lines = [
        f"# {REPORT_TITLE}",
        "",
        "## 项目概况",
        f"- 项目名称：{summary['project_name']}",
        f"- 场景类型：{summary['scenario_type']}",
        f"- 省份：{summary['province']}",
        f"- 数据完整度：{diagnostics['data_completeness_grade']}",
        f"- 数据质量等级：{output['data_quality_results']['level']} / {output['data_quality_results']['score']}",
        f"- 省级规则状态：{market.get('province_profile_status')}",
        f"- 电网区域：{market.get('profile_grid_region')}",
        "",
        "## 推荐方案",
        f"- 光伏：{solution.get('pv_mwp') or 0} MWp",
        f"- 风电：{solution.get('wind_mw') or 0} MW",
        f"- 储能：{solution.get('storage_power_mw') or 0} MW / {solution.get('storage_energy_mwh') or 0} MWh",
        f"- 充电容量：{solution.get('charging_capacity_mw') or 0} MW",
        f"- 供冷容量：{solution.get('cooling_capacity_rt') or 0} RT",
        f"- 供热容量：{solution.get('heating_capacity_mwth') or 0} MWth",
        "",
        "## 核心测算",
        f"- 年光伏发电量：{sim.get('annual_pv_generation_mwh')}",
        f"- 年风电发电量：{sim.get('annual_wind_generation_mwh')}",
        f"- 年储能放电量：{sim.get('annual_storage_discharge_mwh')}",
        f"- 年充电量：{sim.get('annual_charging_energy_mwh')}",
        f"- 年供冷量：{sim.get('annual_cooling_energy_mwh')}",
        f"- 年供热量：{sim.get('annual_heating_energy_mwh')}",
        f"- 年购电量：{sim.get('annual_grid_purchase_mwh')}",
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
            f"- 光伏倾角/方位角/温度修正：{resource.get('pv_tilt_factor')} / {resource.get('pv_azimuth_factor')} / {resource.get('pv_temperature_factor')}",
            f"- 光伏有效 PR：{resource.get('pv_pr_effective')}",
            f"- 风电资源口径：{resource.get('wind_resource_basis')} / {resource.get('wind_resource_accuracy')}",
            f"- 风电 P50/P90：{resource.get('wind_p50_generation_mwh')} / {resource.get('wind_p90_generation_mwh')}",
            f"- 风电功率曲线：{resource.get('wind_power_curve_used')}",
            "",
            "## 调度结果",
            f"- 基线峰值购电功率：{dispatch.get('baseline_peak_grid_kw')}",
            f"- 储能后峰值购电功率：{dispatch.get('post_storage_peak_grid_kw')}",
            f"- 估算削峰量：{dispatch.get('estimated_peak_reduction_kw')}",
            f"- 日储能循环次数：{dispatch.get('daily_storage_cycles')}",
            f"- 储能策略模式：{dispatch.get('storage_strategy_mode')}",
            f"- 年储能吞吐量：{dispatch.get('storage_annual_throughput_mwh')}",
            f"- 年等效满循环：{dispatch.get('storage_equivalent_full_cycles_per_year')}",
            f"- 估算寿命年限：{dispatch.get('storage_life_years_estimate')}",
            f"- 绿电/新能源充电占比：{dispatch.get('storage_charge_from_renewables_ratio')}",
            f"- 有效往返效率：{dispatch.get('storage_effective_round_trip_efficiency')}",
            f"- 预留SOC/保供SOC：{dispatch.get('storage_reserved_soc_ratio')} / {dispatch.get('storage_backup_soc_ratio')}",
            f"- 年衰减率/寿命末容量比：{dispatch.get('storage_degradation_per_year')} / {dispatch.get('storage_end_of_life_capacity_ratio')}",
            f"- 充电排队指数：{dispatch.get('charging_queue_index')}",
            f"- 充电多车型多样性系数：{dispatch.get('charging_diversity_factor')}",
            f"- 年锅炉燃料等价值：{dispatch.get('thermal_annual_boiler_fuel_equivalent_mwh')}",
            f"- 冷/热峰值需求：{dispatch.get('thermal_cooling_peak_kwth')} / {dispatch.get('thermal_heating_peak_kwth')}",
            "",
            "## 财务结果",
            f"- 年收益/节费：{fin.get('annual_savings_or_revenue')}",
            f"- 年电量电费：{fin.get('annual_energy_charge_cost')}",
            f"- 年需量电费：{fin.get('annual_demand_charge_cost')}",
            f"- 年辅助服务收益：{fin.get('annual_ancillary_service_revenue')}",
            f"- 年需求响应收益：{fin.get('annual_demand_response_revenue')}",
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
            lines.append(f"- {item['path']}：减排 {item['reduction_tco2e']} tCO2e，占比 {item['share']}")
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
                f"- {item['month']}月：充电 {item['charge_mwh']} MWh，放电 {item['discharge_mwh']} MWh，毛收益 {item['gross_margin']}"
            )
    if dispatch.get("charging_segment_summary"):
        lines.extend(["", "## 充电结构摘要"])
        for item in dispatch["charging_segment_summary"]:
            lines.append(
                f"- {item['vehicle_type']}：日充电量 {item['daily_energy_kwh']} kWh，估算峰值 {item['peak_kw']} kW"
            )

    lines.extend(["", "## 风险与缺口"])
    for item in output.get("data_gaps", []):
        lines.append(f"- 数据缺口：{item}")
    for item in output.get("risks", []):
        lines.append(f"- 风险：{item}")
    if output.get("data_quality_results", {}).get("checks"):
        lines.extend(["", "## 数据质量检查"])
        for item in output["data_quality_results"]["checks"]:
            lines.append(f"- {item['name']}：{item['status']} - {item['message']}")

    if sensitivity:
        lines.extend(["", "## 敏感性分析"])
        for item in sensitivity:
            lines.append(
                f"- {item['factor']}：年度收益影响 {item['impact_on_annual_revenue']}，IRR 敏感度 {item['impact_on_irr']}"
            )

    return "\n".join(lines) + "\n"
