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


def apply_province_overrides(data: dict[str, Any]) -> dict[str, Any]:
    province = (data.get("project_info", {}) or {}).get("province")
    if not province or province not in PROVINCE_MARKET_OVERRIDES:
        return data
    result = deepcopy(data)  # NOTE: deepcopy is intentional to avoid mutating the caller's input; consider shallow copy if data depth is known.
    override = PROVINCE_MARKET_OVERRIDES[province]
    for top_key, payload in override.items():
        target = result.setdefault(top_key, {})
        if isinstance(target, dict) and isinstance(payload, dict):
            for key, value in payload.items():
                target.setdefault(key, value)
    return result
