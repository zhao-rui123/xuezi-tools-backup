from __future__ import annotations

from copy import deepcopy
from typing import Any

from .utils import deep_merge


DEFAULT_INPUT: dict[str, Any] = {
    "project_info": {},
    "resource_data": {"solar": {}, "wind": {}},
    "load_data": {},
    "charging_data": {},
    "thermal_system": {},
    "carbon_data": {},
    "market_data": {},
    "network_and_design": {},
    "equipment": {"pv": {}, "wind": {}, "storage": {}, "conventional_backup": {}, "charging": {}, "thermal": {}},
    "financial": {},
    "deliverables": {},
}


def normalize_input(data: dict[str, Any]) -> dict[str, Any]:
    return deep_merge(deepcopy(DEFAULT_INPUT), data)
