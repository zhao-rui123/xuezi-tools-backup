from __future__ import annotations

from typing import Any


FIXED_TOU_KEYWORDS = [
    "分时电价",
    "尖峰",
    "峰段",
    "平段",
    "谷段",
    "深谷",
]

MARKET_BASED_KEYWORDS = [
    "市场化交易",
    "市场交易",
    "现货交易",
    "中长期交易",
    "代理购电",
]


def classify_market_policy_mode(data: dict[str, Any], policy_sources: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    market = data.setdefault("market_data", {})
    if market.get("market_policy_mode"):
        return data

    text_parts = []
    for source in policy_sources or []:
        if not isinstance(source, dict):
            continue
        title = str(source.get("title") or "")
        text = str(source.get("text") or "")
        text_parts.append(title)
        text_parts.append(text[:3000])
    scope = " ".join(text_parts)

    fixed_hits = sum(1 for keyword in FIXED_TOU_KEYWORDS if keyword in scope)
    market_hits = sum(1 for keyword in MARKET_BASED_KEYWORDS if keyword in scope)

    if fixed_hits >= 2 and fixed_hits >= market_hits:
        market["market_policy_mode"] = "fixed_tou_policy"
    elif market_hits >= 1:
        market["market_policy_mode"] = "market_based"
    else:
        market["market_policy_mode"] = "unknown"
    return data
