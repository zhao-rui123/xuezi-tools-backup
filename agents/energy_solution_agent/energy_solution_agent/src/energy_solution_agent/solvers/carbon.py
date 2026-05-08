from __future__ import annotations

from typing import Any

from ..constants import DEFAULT_GAS_EMISSION_FACTOR, DEFAULT_GRID_EMISSION_FACTOR
from ..industry_templates import get_industry_template
from ..utils import clamp, safe_div

def estimate_carbon(data: dict[str, Any], simulation: dict[str, Any]) -> dict[str, Any]:
    carbon = data.get("carbon_data", {})
    industry_template = get_industry_template(carbon.get("industry_type"))
    baseline = carbon.get("baseline_emissions_tco2e")
    annual_grid_purchase = float(simulation.get("annual_grid_purchase_mwh") or 0.0)
    annual_pv = float(simulation.get("annual_pv_generation_mwh") or 0.0)
    annual_wind = float(simulation.get("annual_wind_generation_mwh") or 0.0)
    annual_heating = float(simulation.get("annual_heating_energy_mwh") or 0.0)
    green_power_ratio = safe_div(annual_pv + annual_wind, annual_grid_purchase + annual_pv + annual_wind) or 0.0

    if baseline is None:
        baseline = annual_grid_purchase * DEFAULT_GRID_EMISSION_FACTOR + annual_heating * DEFAULT_GAS_EMISSION_FACTOR * 0.18
    baseline = float(baseline)
    scope1_reduction = annual_heating * 0.06
    scope2_reduction = (annual_pv + annual_wind + float(simulation.get("annual_storage_discharge_mwh") or 0.0) * 0.15) * DEFAULT_GRID_EMISSION_FACTOR
    scope3_reduction = 0.0
    post_project = max(0.0, baseline - scope1_reduction - scope2_reduction - scope3_reduction)
    annual_reduction = baseline - post_project

    return {
        "baseline_emissions_tco2e": round(baseline, 2),
        "post_project_emissions_tco2e": round(post_project, 2),
        "annual_reduction_tco2e": round(annual_reduction, 2),
        "scope1_reduction_tco2e": round(scope1_reduction, 2),
        "scope2_reduction_tco2e": round(scope2_reduction, 2),
        "scope3_reduction_tco2e": round(scope3_reduction, 2),
        "green_power_coverage_ratio": round(clamp(green_power_ratio, 0.0, 1.0), 4),
        "claim_boundary_summary": _claim_boundary_summary(carbon),
        "carbon_path_breakdown": _carbon_path_breakdown(scope1_reduction, scope2_reduction, industry_template),
    }


def _claim_boundary_summary(carbon: dict[str, Any]) -> str:
    target = str(carbon.get("carbon_claim_target") or "").strip()
    boundary = str(carbon.get("boundary_definition") or "").strip()
    scope3_considered = bool(carbon.get("scope3_considered"))
    if target and boundary:
        return f"{target}；boundary={boundary}；scope3_considered={str(scope3_considered).lower()}"
    if boundary:
        return f"boundary={boundary}；scope3_considered={str(scope3_considered).lower()}"
    if target:
        return target
    return "需按范围一/二边界、环境属性归属和外部校证要求进一步确认零碳声明边界。"


def _carbon_path_breakdown(
    scope1_reduction: float,
    scope2_reduction: float,
    industry_template: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    total = scope1_reduction + scope2_reduction
    if total <= 0:
        return []
    industry_template = industry_template or {}
    priority_actions = industry_template.get("priority_actions") or []
    scope1_label = "工艺/热源替代与能效提升"
    scope2_label = "绿电/光伏/储能替代购电排放"
    if priority_actions:
        if float(industry_template.get("scope1_weight") or 0.0) >= float(industry_template.get("scope2_weight") or 0.0):
            scope1_label = f"{scope1_label}：{priority_actions[0]}"
            if len(priority_actions) > 1:
                scope2_label = f"{scope2_label}：{priority_actions[1]}"
        else:
            scope2_label = f"{scope2_label}：{priority_actions[0]}"
            if len(priority_actions) > 1:
                scope1_label = f"{scope1_label}：{priority_actions[1]}"
    rows = [
        {"bucket": "scope1", "path": scope1_label, "reduction_tco2e": round(scope1_reduction, 2), "share": round(scope1_reduction / total, 4)},
        {"bucket": "scope2", "path": scope2_label, "reduction_tco2e": round(scope2_reduction, 2), "share": round(scope2_reduction / total, 4)},
    ]
    scope1_weight = float(industry_template.get("scope1_weight") or 0.0)
    scope2_weight = float(industry_template.get("scope2_weight") or 0.0)
    if scope1_weight != scope2_weight:
        preferred_bucket = "scope1" if scope1_weight > scope2_weight else "scope2"
        rows.sort(key=lambda item: (0 if item["bucket"] == preferred_bucket else 1, -item["reduction_tco2e"]))
    else:
        rows.sort(key=lambda item: item["reduction_tco2e"], reverse=True)
    rows = [{"path": item["path"], "reduction_tco2e": item["reduction_tco2e"], "share": item["share"]} for item in rows]
    return rows


def assemble_design_notes(data: dict[str, Any], profile: dict[str, Any] | None, scenario: str, charging_peak_kw: float) -> dict[str, Any]:
    project = data.get("project_info", {})
    network = data.get("network_and_design", {})
    notes = [
        f"建议按 {project.get('grid_connection_mode') or '项目实际接入方式'} 复核接入边界。",
        "需复核变压器余量、保护配合、计量边界和防逆流要求。",
    ]
    if charging_peak_kw > 0:
        notes.append("充电场站场景需专项复核容量电费风险和有序充电策略。")
    if scenario == "zero_carbon_factory":
        notes.append("零碳工厂场景需同步复核工艺用能、冷热系统和碳核算边界。")
    if profile:
        notes.append(f"已命中省级 profile：{profile.get('province_name')} / {profile.get('verification_status')}")
    return {
        "recommended_voltage_level_kv": project.get("voltage_level_kv"),
        "recommended_connection_mode": project.get("grid_connection_mode") or "",
        "primary_system_notes": notes,
        "secondary_system_notes": [
            "需明确 EMS/PCS/BMS 或冷热控制系统与站控层接口。",
            "如参与市场或聚合控制，需明确通信与调度边界。",
        ],
        "required_studies": [
            "接入容量校核",
            "典型日或逐时负荷仿真",
        ],
        "required_approvals": [
            "内部立项/技术审查",
            "接入方案复核",
        ],
    }
