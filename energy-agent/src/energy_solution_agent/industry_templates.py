from __future__ import annotations

from typing import Any


INDUSTRY_TEMPLATES: dict[str, dict[str, Any]] = {
    "钢铁": {
        "major_paths": ["余热回收", "电炉电气化", "绿电替代", "能效提升", "工序协同优化"],
        "scope1_weight": 0.65,
        "scope2_weight": 0.35,
        "hard_to_abate": ["高温热", "焦化/烧结工序", "直接燃料使用"],
        "priority_actions": ["先做余热与工序能效", "再做电气化与绿电替代"],
    },
    "电子制造": {
        "major_paths": ["洁净空调系统优化", "高效机电设备", "绿电替代", "储能削峰", "数字化能碳管理"],
        "scope1_weight": 0.12,
        "scope2_weight": 0.88,
        "hard_to_abate": ["洁净环境高耗电", "空调与工艺冷却负荷"],
        "priority_actions": ["先做空调冷站和洁净系统优化", "再做绿电与储能协同"],
    },
    "化工": {
        "major_paths": ["蒸汽系统优化", "余热回收", "燃料替代", "绿电替代", "流程强化"],
        "scope1_weight": 0.70,
        "scope2_weight": 0.30,
        "hard_to_abate": ["工艺过程排放", "高温蒸汽需求", "连续生产切换难度"],
        "priority_actions": ["先查工艺蒸汽与燃料替代空间", "再做绿电和用电侧优化"],
    },
    "数据中心": {
        "major_paths": ["高效制冷", "绿电覆盖", "储能与UPS协同", "IT负载优化", "能碳数字化"],
        "scope1_weight": 0.05,
        "scope2_weight": 0.95,
        "hard_to_abate": ["供电可靠性刚性要求", "全年高负荷运行"],
        "priority_actions": ["先做制冷和UPS协同", "再做绿电覆盖与储能策略"],
    },
    "水泥": {
        "major_paths": ["熟料系统能效提升", "替代燃料", "余热发电", "绿电替代", "低碳原料替代"],
        "scope1_weight": 0.72,
        "scope2_weight": 0.28,
        "hard_to_abate": ["工艺过程排放", "高温窑炉热需求", "连续工况调节空间有限"],
        "priority_actions": ["先做窑系统和替代燃料", "再做余热发电与绿电替代"],
    },
    "纺织": {
        "major_paths": ["空压与机电系统节能", "蒸汽系统优化", "热泵替代", "光伏+储能", "绿色电力采购"],
        "scope1_weight": 0.30,
        "scope2_weight": 0.70,
        "hard_to_abate": ["蒸汽与热水需求", "多班次负荷波动", "染整工序热负荷"],
        "priority_actions": ["先做蒸汽和热水系统优化", "再做光伏储能与绿电采购"],
    },
    "食品饮料": {
        "major_paths": ["冷站优化", "蒸汽系统优化", "热回收", "高效电机与制冷", "绿电替代"],
        "scope1_weight": 0.35,
        "scope2_weight": 0.65,
        "hard_to_abate": ["蒸汽与热水需求", "冷链刚性需求", "连续生产与清洗工况"],
        "priority_actions": ["先做冷站与蒸汽系统", "再做热回收与绿电替代"],
    },
    "医药": {
        "major_paths": ["洁净空调系统优化", "蒸汽与纯化系统节能", "热泵替代", "光储协同", "数字化能碳管理"],
        "scope1_weight": 0.22,
        "scope2_weight": 0.78,
        "hard_to_abate": ["洁净环境高能耗", "合规性限制设备切换", "冷热负荷稳定性要求高"],
        "priority_actions": ["先做洁净空调与纯化系统", "再做热泵与光储协同"],
    },
    "电池制造": {
        "major_paths": ["干燥房与空调优化", "高效机电", "绿电覆盖", "储能削峰", "工序能效提升"],
        "scope1_weight": 0.10,
        "scope2_weight": 0.90,
        "hard_to_abate": ["干燥与恒温恒湿系统高耗能", "产线连续运行", "良率与能耗耦合"],
        "priority_actions": ["先做干燥房和空调", "再做绿电覆盖与储能削峰"],
    },
    "汽车制造": {
        "major_paths": ["焊装涂装能效提升", "空压站优化", "光储充一体化", "绿电替代", "涂装热源低碳化"],
        "scope1_weight": 0.28,
        "scope2_weight": 0.72,
        "hard_to_abate": ["涂装热负荷", "多车间多班次波动", "物流与充电耦合"],
        "priority_actions": ["先做涂装和空压站", "再做光储充与绿电替代"],
    },
    "半导体": {
        "major_paths": ["洁净室空调优化", "工艺冷却系统优化", "绿电覆盖", "储能削峰", "废热回收与数字化监控"],
        "scope1_weight": 0.08,
        "scope2_weight": 0.92,
        "hard_to_abate": ["洁净环境刚性高", "恒温恒湿与工艺冷却耦合", "连续运行停机成本高"],
        "priority_actions": ["先做洁净室与冷却系统", "再做绿电与储能削峰"],
    },
    "园区综合能源": {
        "major_paths": ["光储充协同", "冷热联供", "负荷柔性调节", "绿电采购", "能碳一体化管理"],
        "scope1_weight": 0.18,
        "scope2_weight": 0.82,
        "hard_to_abate": ["多主体协调", "冷热电边界复杂", "负荷类型多样"],
        "priority_actions": ["先做负荷与冷热边界梳理", "再做光储充与能碳一体化"],
    },
}


def get_industry_template(industry_type: str | None) -> dict[str, Any]:
    if not industry_type:
        return {}
    return INDUSTRY_TEMPLATES.get(industry_type, {})
