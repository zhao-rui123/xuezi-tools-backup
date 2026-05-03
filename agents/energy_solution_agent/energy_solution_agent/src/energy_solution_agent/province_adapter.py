from __future__ import annotations

from typing import Any


def build_market_context(
    profile: dict[str, Any] | None,
    market: dict[str, Any],
    live_patch: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not profile:
        context = {
            "province_profile_status": "missing",
            "market_rule_notes": ["未命中省级 profile，当前按通用规则和输入数据测算。"],
            "profile_market_stage": "",
            "profile_grid_region": "",
            "live_rule_refresh_enabled": bool(live_patch),
            "live_rule_refresh_status": live_patch.get("status") if live_patch else "disabled",
            "live_rule_last_checked_at": live_patch.get("checked_at") if live_patch else "",
            "live_rule_sources": live_patch.get("sources") if live_patch else [],
        }
        if live_patch and live_patch.get("notes"):
            context["market_rule_notes"].extend(live_patch["notes"])
        return context

    notes: list[str] = []
    if profile.get("market_stage_summary"):
        notes.append(str(profile["market_stage_summary"]))
    if profile.get("spot_market_status"):
        notes.append(str(profile["spot_market_status"]))
    if profile.get("tou_rule_status"):
        notes.append(str(profile["tou_rule_status"]))
    if profile.get("energy_storage_dispatch_summary"):
        notes.append(str(profile["energy_storage_dispatch_summary"]))

    if not market.get("province_policy_profile"):
        market["province_policy_profile"] = profile.get("province_name", "")

    context = {
        "province_profile_status": profile.get("verification_status") or "unknown",
        "market_rule_notes": notes,
        "profile_market_stage": profile.get("market_stage_summary") or "",
        "profile_grid_region": profile.get("grid_region") or "",
        "live_rule_refresh_enabled": bool(live_patch),
        "live_rule_refresh_status": live_patch.get("status") if live_patch else "disabled",
        "live_rule_last_checked_at": live_patch.get("checked_at") if live_patch else "",
        "live_rule_sources": live_patch.get("sources") if live_patch else [],
    }
    if live_patch and live_patch.get("notes"):
        context["market_rule_notes"].extend(live_patch["notes"])
    return context
