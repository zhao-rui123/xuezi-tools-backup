from __future__ import annotations

from pathlib import Path
from typing import Any

from .constants import SPEC_BUNDLE
from .utils import read_json


def _load_profile_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = read_json(path)
    return payload.get("profiles", [])


def load_province_profiles() -> dict[str, dict[str, Any]]:
    profiles: dict[str, dict[str, Any]] = {}
    for name in ("province_profiles_first_batch.json", "province_profiles_second_batch.json"):
        for item in _load_profile_file(SPEC_BUNDLE / name):
            profiles[item["province_name"]] = item
    return profiles


def get_province_profile(province: str | None) -> dict[str, Any] | None:
    if not province:
        return None
    return load_province_profiles().get(province)
