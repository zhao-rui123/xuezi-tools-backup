from __future__ import annotations

import re
from typing import Any

from .live_rules import (
    _build_monthly_tou_policy_history_from_seasonal,
    _extract_seasonal_schedule_hints,
    _fetch_url,
    extract_structured_rule_patch,
)
from .network_http import get_proxy_url


def enrich_with_monthly_tou_policy_history(
    data: dict[str, Any],
    profile: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    market = data.setdefault("market_data", {})
    proxy_url = get_proxy_url(data.get("network"))
    meta = {
        "tou_policy_fetch_attempted": False,
        "tou_policy_fetch_status": "skipped",
        "tou_policy_fetch_sources": [],
        "tou_policy_fetch_proxy": proxy_url or "",
    }
    if market.get("monthly_tou_policy_history"):
        meta["tou_policy_fetch_status"] = "not_needed"
        return data, meta

    links = _normalize_policy_link_entries(market.get("tou_policy_history_links") or [])
    if not links and profile:
        links = _normalize_policy_link_entries(profile.get("source_links", []) if profile else [])
    if not links:
        meta["tou_policy_fetch_status"] = "no_sources"
        return data, meta

    history: list[dict[str, Any]] = []
    for entry in links[:12]:
        meta["tou_policy_fetch_attempted"] = True
        fetched = _fetch_url(entry["url"], timeout=8.0, proxy_url=proxy_url)
        meta["tou_policy_fetch_sources"].append({
            "url": fetched.get("url"),
            "status_code": fetched.get("status_code"),
            "title": fetched.get("title"),
            "ok": fetched.get("ok"),
        })
        if not fetched.get("ok"):
            continue
        history.extend(_extract_month_history_from_fetched(entry, fetched))

    if history:
        deduped = _dedupe_month_history(history)
        market["monthly_tou_policy_history"] = deduped
        meta["tou_policy_fetch_status"] = "fetched"
    else:
        meta["tou_policy_fetch_status"] = "failed"
    return data, meta


def _dedupe_month_history(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[int, dict[str, Any]] = {}
    for item in items:
        month_raw = item.get("month")
        if month_raw is None:
            continue
        month = int(month_raw)
        if not 1 <= month <= 12:
            continue
        current = seen.get(month)
        candidate = {
            "month": month,
            "periods": list(dict.fromkeys(str(period) for period in (item.get("periods") or []))),
            "prices": item.get("prices") or [],
            "schedule": item.get("schedule") or {},
            "source_url": item.get("source_url") or "",
            "title": item.get("title") or "",
        }
        if current is None or _history_item_score(candidate) > _history_item_score(current):
            seen[month] = candidate
    return [seen[month] for month in sorted(seen)]


def _history_item_score(item: dict[str, Any]) -> tuple[int, int, int]:
    return (
        len(item.get("prices") or []),
        len(item.get("schedule") or {}),
        len(item.get("periods") or []),
    )


def _normalize_policy_link_entries(entries: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for entry in entries:
        if isinstance(entry, str) and entry:
            normalized.append({"url": entry})
        elif isinstance(entry, dict) and entry.get("url"):
            normalized.append(dict(entry))
    return normalized


def _extract_month_history_from_fetched(entry: dict[str, Any], fetched: dict[str, Any]) -> list[dict[str, Any]]:
    text = str(fetched.get("text") or "")
    title = str(fetched.get("title") or "")
    patch = extract_structured_rule_patch(text)
    months = _infer_months(entry, title, text)
    history: list[dict[str, Any]] = []
    if months:
        for month in months:
            history.append(
                {
                    "month": month,
                    "periods": _periods_from_patch(patch),
                    "prices": patch.get("tou_tariff") or [],
                    "schedule": patch.get("tou_schedule") or {},
                    "source_url": entry["url"],
                    "title": title,
                }
            )
        return history
    seasonal = _extract_seasonal_schedule_hints(text)
    if seasonal:
        for item in _build_monthly_tou_policy_history_from_seasonal(seasonal):
            history.append(
                {
                    "month": int(item["month"]),
                    "periods": item.get("periods") or [],
                    "prices": patch.get("tou_tariff") or [],
                    "schedule": patch.get("tou_schedule") or {},
                    "source_url": entry["url"],
                    "title": title,
                }
            )
    return history


def _periods_from_patch(patch: dict[str, Any]) -> list[str]:
    if patch.get("tou_schedule"):
        return list(patch["tou_schedule"].keys())
    if patch.get("tou_tariff"):
        return [str(item.get("period")) for item in patch["tou_tariff"] if item.get("period")]
    return []


def _infer_months(entry: dict[str, Any], title: str, text: str) -> list[int]:
    explicit_months = entry.get("months")
    if isinstance(explicit_months, (list, tuple)):
        return sorted({int(month) for month in explicit_months if 1 <= int(month) <= 12})
    explicit_month = entry.get("month")
    if explicit_month is not None:
        month = int(explicit_month)
        return [month] if 1 <= month <= 12 else []

    scope = " ".join(part for part in [entry.get("url", ""), title, text[:500]] if part)
    month_matches = re.findall(r"(?:20\d{2}[-年/])?\s*(1[0-2]|0?[1-9])\s*月", scope)
    months = sorted({int(match) for match in month_matches if 1 <= int(match) <= 12})
    if months:
        return months
    url_month = re.findall(r"20\d{2}[-_/]?(1[0-2]|0?[1-9])", entry.get("url", ""))
    months = sorted({int(match) for match in url_month if 1 <= int(match) <= 12})
    return months
