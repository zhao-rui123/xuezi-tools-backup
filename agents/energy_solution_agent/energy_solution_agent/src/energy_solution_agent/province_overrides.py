from __future__ import annotations

from copy import deepcopy
from typing import Any


PROVINCE_MARKET_OVERRIDES: dict[str, dict[str, Any]] = {
    "江苏": {
        "market_data": {
            "province_policy_profile": "江苏",
            "monthly_price_multipliers": [0.92, 0.92, 0.96, 1.00, 1.02, 1.05, 1.10, 1.10, 1.04, 1.00, 0.97, 0.94],
            "tou_schedule_seasonal": {
                "summer": {"peak": [10, 11, 14, 15, 16, 17, 18, 19, 20], "flat": [8, 9, 12, 13, 21, 22], "valley": [0, 1, 2, 3, 4, 5, 6, 7, 23]},
                "winter": {"peak": [9, 10, 11, 16, 17, 18, 19], "flat": [8, 12, 13, 14, 15, 20, 21], "valley": [0, 1, 2, 3, 4, 5, 6, 7, 22, 23]}
            }
        }
    },
    "山东": {
        "market_data": {
            "province_policy_profile": "山东",
            "demand_charge_mode": "contract_capacity",
            "monthly_price_multipliers": [0.96, 0.95, 0.98, 1.00, 1.02, 1.04, 1.07, 1.08, 1.03, 1.00, 0.98, 0.97]
        }
    },
    "广东": {
        "market_data": {
            "province_policy_profile": "广东",
            "tou_schedule_weekend_default": {"flat": list(range(24))},
            "monthly_price_multipliers": [0.97, 0.97, 0.99, 1.00, 1.01, 1.03, 1.05, 1.05, 1.02, 1.00, 0.99, 0.98]
        }
    },
    "福建": {
        "market_data": {
            "province_policy_profile": "福建",
            "monthly_price_multipliers": [0.95, 0.95, 0.98, 1.00, 1.03, 1.05, 1.08, 1.08, 1.03, 1.00, 0.97, 0.95]
        }
    },
    "湖北": {
        "market_data": {
            "province_policy_profile": "湖北",
            "tou_schedule_seasonal": {
                "summer": {"peak": [9, 10, 11, 15, 16, 17, 18, 19, 20], "flat": [8, 12, 13, 14, 21, 22], "valley": [0, 1, 2, 3, 4, 5, 6, 7, 23]}
            }
        }
    }
}




# 各省强制配储政策（2025-2026年执行标准）
PROVINCE_STORAGE_MANDATES: dict[str, dict[str, Any]] = {
    "山东": {"ratio_pct": 10, "hours": 2, "mode": "new_energy"},
    "河南": {"ratio_pct": 20, "hours": 4, "mode": "new_energy"},
    "河北": {"ratio_pct": 10, "hours": 2, "mode": "new_energy"},
    "江苏": {"ratio_pct": 8,  "hours": 2, "mode": "new_energy"},
    "浙江": {"ratio_pct": 10, "hours": 2, "mode": "new_energy"},
    "广东": {"ratio_pct": 10, "hours": 2, "mode": "new_energy"},
    "安徽": {"ratio_pct": 10, "hours": 1, "mode": "new_energy"},
    "湖北": {"ratio_pct": 10, "hours": 2, "mode": "new_energy"},
    "湖南": {"ratio_pct": 15, "hours": 2, "mode": "new_energy"},
    "福建": {"ratio_pct": 10, "hours": 2, "mode": "new_energy"},
    "广西": {"ratio_pct": 10, "hours": 2, "mode": "new_energy"},
    "内蒙古": {"ratio_pct": 15, "hours": 2, "mode": "new_energy"},
}


def apply_storage_mandate(data: dict[str, Any]) -> dict[str, Any]:
    """检查省分配储政策，自动调整储能规模"""
    province = data.get("project_info", {}).get("province", "")
    if province not in PROVINCE_STORAGE_MANDATES:
        return data
    mandate = PROVINCE_STORAGE_MANDATES[province]
    pv_mwp = float(data.get("resource_data", {}).get("solar", {}).get("available_area_m2", 0)) / 6500
    wind_mw = 0.0
    # 如果已有储能候选，确保不低于政策要求
    equip = data.get("equipment", {})
    storage = equip.get("storage", {})
    required_mwh = (pv_mwp + wind_mw) * mandate["ratio_pct"] / 100 * mandate["hours"]
    if required_mwh > 0:
        candidate = storage.get("energy_candidate_kwh", [])
        if not candidate or max(candidate) < required_mwh * 1000:
            data["equipment"]["storage"]["energy_candidate_kwh"] = [required_mwh * 1000]
            data["equipment"]["storage"]["power_candidate_kw"] = [required_mwh * 1000 / mandate["hours"]]
    return data


def apply_province_overrides(data: dict[str, Any]) -> dict[str, Any]:
    province = (data.get("project_info", {}) or {}).get("province")
    if not province or province not in PROVINCE_MARKET_OVERRIDES:
        return data
    result = deepcopy(data)
    override = PROVINCE_MARKET_OVERRIDES[province]
    for top_key, payload in override.items():
        target = result.setdefault(top_key, {})
        if isinstance(target, dict) and isinstance(payload, dict):
            for key, value in payload.items():
                target.setdefault(key, value)
    return result
