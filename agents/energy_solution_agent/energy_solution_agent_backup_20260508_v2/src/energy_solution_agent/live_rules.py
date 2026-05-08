from __future__ import annotations

import datetime as dt
import html
import re
import urllib.error
from copy import deepcopy
from typing import Any

from .network_http import http_get_text


USER_AGENT = "energy-solution-agent/0.1"

PRICE_ALIASES = {
    "super_peak": ["尖峰", "尖峰时段", "灏栧嘲"],
    "peak": ["峰", "峰段", "峰时段", "高峰", "宄?", "宄版"],
    "flat": ["平", "平段", "平时段", "骞?", "骞虫"],
    "valley": ["谷", "谷段", "谷时段", "低谷", "璋?", "璋锋"],
    "deep_valley": ["深谷", "娣辫胺"],
}

SCHEDULE_ALIASES = {
    "super_peak": ["尖峰", "尖峰时段", "灏栧嘲"],
    "peak": ["高峰", "峰段", "峰时段", "峰", "宄?", "宄版"],
    "flat": ["平段", "平时段", "平", "骞?", "骞虫"],
    "valley": ["谷段", "谷时段", "谷", "低谷", "璋?", "璋锋"],
    "deep_valley": ["深谷", "娣辫胺"],
}


def fetch_live_rule_patch(profile: dict[str, Any] | None, timeout: float = 8.0, proxy_url: str | None = None) -> dict[str, Any]:
    if not profile:
        return {
            "enabled": True,
            "status": "no_profile",
            "checked_at": _utc_now(),
            "sources": [],
            "notes": ["未命中省级 profile，无法执行在线规则刷新。"],
            "structured_patch": {},
        }

    links = []
    for link in profile.get("source_links", []):
        if not link:
            continue
        if isinstance(link, dict):
            url = link.get("url")
            if url:
                links.append(url)
        else:
            links.append(str(link))
    if not links:
        return {
            "enabled": True,
            "status": "no_sources",
            "checked_at": _utc_now(),
            "sources": [],
            "notes": ["该省份 profile 未配置在线来源链接。"],
            "structured_patch": {},
        }

    notes: list[str] = []
    sources: list[dict[str, Any]] = []
    patches: list[dict[str, Any]] = []
    ok_count = 0
    for link in links[:5]:
        fetched = _fetch_url(link, timeout=timeout, proxy_url=proxy_url)
        sources.append({
            "url": fetched.get("url"),
            "status_code": fetched.get("status_code"),
            "title": fetched.get("title"),
            "ok": fetched.get("ok"),
        })
        if fetched["ok"]:
            ok_count += 1
            text = fetched["text"]
            notes.extend(_extract_rule_notes(text))
            patches.append(extract_structured_rule_patch(text))

    status = "ok" if ok_count > 0 else "failed"
    if ok_count > 0 and not notes:
        notes.append("已抓取官方来源，但未自动提取到更细规则要点，建议人工复核原文。")
    return {
        "enabled": True,
        "status": status,
        "checked_at": _utc_now(),
        "sources": sources,
        "notes": _dedupe(notes),
        "structured_patch": _merge_patches(patches),
    }


def apply_live_rule_patch(market: dict[str, Any], patch: dict[str, Any] | None) -> dict[str, Any]:
    if not patch:
        return market
    result = deepcopy(market)
    for key, value in patch.items():
        if value in (None, "", [], {}):
            continue
        result[key] = value
    return result


def extract_structured_rule_patch(text: str) -> dict[str, Any]:
    text = text or ""
    patch: dict[str, Any] = {}

    tou_prices = _extract_tou_prices(text)
    if tou_prices:
        patch["tou_tariff"] = tou_prices

    tou_schedule = _extract_hour_schedule(text)
    if tou_schedule:
        patch["tou_schedule"] = tou_schedule

    market_mode = _extract_market_mode(text)
    if market_mode:
        patch["market_mode"] = market_mode

    demand_rule = _extract_demand_rule(text)
    if demand_rule:
        patch["demand_charge_rule"] = demand_rule

    capacity_rule = _extract_capacity_rule(text)
    if capacity_rule:
        patch["capacity_charge_rule"] = capacity_rule

    charge_mode = _extract_charge_mode(text)
    if charge_mode:
        patch["demand_charge_mode"] = charge_mode

    demand_rate = _extract_rate(text, "需量")
    if demand_rate is not None:
        patch["demand_charge_rate_per_kw_month"] = demand_rate

    capacity_rate = _extract_rate(text, "容量")
    if capacity_rate is not None:
        patch["capacity_charge_rate_per_kw_month"] = capacity_rate

    contract_capacity = _extract_capacity_value(text, ["合同容量", "契约容量", "鍚堝悓瀹归噺", "濂戠害瀹归噺"])
    if contract_capacity is not None:
        patch["contract_capacity_kw"] = contract_capacity

    transformer_capacity = _extract_capacity_value(text, ["变压器容量", "鍙樺帇鍣ㄥ閲?"])
    if transformer_capacity is not None:
        patch["transformer_capacity_kva"] = transformer_capacity

    if any(token in text for token in ("绿电", "缁跨數")):
        patch["green_power_trade_rule"] = "green_power_enabled"
    if any(token in text for token in ("绿证", "缁胯瘉")):
        patch["certificate_rule"] = "green_certificate_enabled"
    if any(token in text for token in ("辅助服务", "杈呭姪鏈嶅姟")):
        patch["ancillary_service_mode"] = "capacity"
    if any(token in text for token in ("需求响应", "闇€姹傚搷搴?")):
        patch["demand_response_mode"] = "event_based"

    seasonal = _extract_seasonal_schedule_hints(text)
    if seasonal:
        patch["tou_schedule_seasonal"] = seasonal
        patch["monthly_tou_policy_history"] = _build_monthly_tou_policy_history_from_seasonal(seasonal)

    return patch


def _fetch_url(url: str, timeout: float, proxy_url: str | None = None) -> dict[str, Any]:
    try:
        text, content_type = http_get_text(url, user_agent=USER_AGENT, timeout=timeout, proxy_url=proxy_url)
        clean = _clean_text(text)
        return {
            "url": url,
            "ok": True,
            "status_code": 200,
            "content_type": content_type,
            "title": _extract_title(text),
            "text": clean[:50000],
        }
    except urllib.error.URLError as exc:
        return {"url": url, "ok": False, "status_code": None, "content_type": "", "title": "", "text": "", "error": str(exc)}
    except Exception as exc:  # pragma: no cover
        return {"url": url, "ok": False, "status_code": None, "content_type": "", "title": "", "text": "", "error": str(exc)}


def _extract_title(text: str) -> str:
    match = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return html.unescape(re.sub(r"\s+", " ", match.group(1)).strip())


def _clean_text(text: str) -> str:
    stripped = re.sub(r"<script.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    stripped = re.sub(r"<style.*?</style>", " ", stripped, flags=re.IGNORECASE | re.DOTALL)
    stripped = re.sub(r"<[^>]+>", " ", stripped)
    stripped = html.unescape(stripped)
    return re.sub(r"\s+", " ", stripped).strip()


def _extract_rule_notes(text: str) -> list[str]:
    keywords = [
        "分时电价",
        "尖峰",
        "深谷",
        "现货",
        "实时",
        "中长期",
        "代理购电",
        "需量",
        "容量电费",
        "绿电",
        "绿证",
        "辅助服务",
        "需求响应",
        "偏差考核",
    ]
    notes: list[str] = []
    for keyword in keywords:
        index = text.find(keyword)
        if index >= 0:
            start = max(0, index - 36)
            end = min(len(text), index + 96)
            notes.append(f"{keyword}：{text[start:end].strip()}")
    return notes[:10]


def _extract_tou_prices(text: str) -> list[dict[str, float]]:
    prices: list[dict[str, float]] = []
    for period, aliases in PRICE_ALIASES.items():
        for alias in aliases:
            match = re.search(re.escape(alias) + r".{0,24}?([0-9]+(?:\.[0-9]+)?)\s*(?:元)", text)
            if match and not any(item["period"] == period for item in prices):
                price = float(match.group(1))
                # Sanity check: Chinese TOU prices typically 0.2–1.5 yuan/kWh
                if 0.1 <= price <= 2.0:
                    prices.append({"period": period, "price": price})
                break
    return prices


def _extract_hour_schedule(text: str) -> dict[str, list[int]]:
    """Extract TOU hour schedule from text.

    First-match-wins: for each period the first alias that yields hours
    is taken and later aliases are skipped via ``break``. The alias order
    in SCHEDULE_ALIASES therefore determines priority.
    """
    schedule: dict[str, list[int]] = {}
    for period, aliases in SCHEDULE_ALIASES.items():
        for alias in aliases:
            hours = _extract_hours_after_keyword(text, alias)
            if hours:
                schedule[period] = hours
                break
    return schedule


def _extract_hours_after_keyword(text: str, keyword: str) -> list[int]:
    index = text.find(keyword)
    if index < 0:
        return []
    snippet = text[index : index + 160]
    matches = re.findall(
        r"([0-2]?\d)\s*[:：]?\s*00?\s*(?:-|至|到|\u2013|\u2014)\s*([0-2]?\d)\s*[:：]?\s*00?",
        snippet,
    )
    hours: list[int] = []
    for start_raw, end_raw in matches:
        start = int(start_raw)
        end = int(end_raw)
        if 0 <= start <= 23 and 0 <= end <= 24:
            hours.extend(_expand_range(start, end))
    return sorted(set(hour for hour in hours if 0 <= hour <= 23))


def _expand_range(start: int, end: int) -> list[int]:
    if end == start:
        return [start]
    if end > start:
        return list(range(start, end))
    return list(range(start, 24)) + list(range(0, end))


def _extract_market_mode(text: str) -> str | None:
    if any(token in text for token in ("现货", "实时", "鐜拌揣", "瀹炴椂")):
        return "market_price_series"
    if any(token in text for token in ("中长期", "涓暱鏈?")):
        return "medium_long_term"
    if any(token in text for token in ("代理购电", "浠ｇ悊璐數")):
        return "proxy_purchase"
    return None


def _extract_demand_rule(text: str) -> str | None:
    if any(token in text for token in ("需量电费", "闇€閲忕數璐?")):
        return "需量电费"
    return None


def _extract_capacity_rule(text: str) -> str | None:
    if any(token in text for token in ("容量电费", "瀹归噺鐢佃垂")):
        return "容量电费"
    return None


def _extract_charge_mode(text: str) -> str | None:
    if any(token in text for token in ("变压器容量", "按变压器容量", "鍙樺帇鍣ㄥ閲?", "鎸夊彉鍘嬪櫒瀹归噺")):
        return "transformer_capacity"
    if any(token in text for token in ("合同容量", "契约容量", "鍚堝悓瀹归噺", "濂戠害瀹归噺")):
        return "contract_capacity"
    if any(token in text for token in ("最大需量", "按需量", "鏈€澶ч渶閲?", "鎸夐渶閲?")):
        return "max_demand"
    return None


def _extract_rate(text: str, keyword: str) -> float | None:
    match = re.search(re.escape(keyword) + r".{0,24}?([0-9]+(?:\.[0-9]+)?)\s*(?:元|鍏?)", text)
    return float(match.group(1)) if match else None


def _extract_capacity_value(text: str, keywords: list[str]) -> float | None:
    for keyword in keywords:
        match = re.search(re.escape(keyword) + r".{0,20}?([0-9]+(?:\.[0-9]+)?)\s*(?:kW|kVA|千瓦|千伏安|鍗冪摝|鍗冧紡瀹?)", text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def _extract_seasonal_schedule_hints(text: str) -> dict[str, dict[str, list[int]]]:
    seasonal: dict[str, dict[str, list[int]]] = {}
    if any(token in text for token in ("夏季", "澶忓")) and any(token in text for token in ("尖峰", "峰", "灏栧嘲", "宄?")):
        seasonal["summer"] = {
            "peak": [10, 11, 14, 15, 16, 17, 18, 19, 20],
            "flat": [8, 9, 12, 13, 21, 22],
            "valley": [0, 1, 2, 3, 4, 5, 6, 7, 23],
        }
    if any(token in text for token in ("冬季", "鍐")) and any(token in text for token in ("峰", "宄?")):
        seasonal["winter"] = {
            "peak": [9, 10, 11, 16, 17, 18, 19],
            "flat": [8, 12, 13, 14, 15, 20, 21],
            "valley": [0, 1, 2, 3, 4, 5, 6, 7, 22, 23],
        }
    return seasonal


def _merge_patches(patches: list[dict[str, Any]]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for patch in patches:
        for key, value in patch.items():
            if key not in merged or merged[key] in (None, "", [], {}):
                merged[key] = value
    return merged


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _build_monthly_tou_policy_history_from_seasonal(seasonal: dict[str, dict[str, list[int]]]) -> list[dict[str, Any]]:
    season_month_map = {
        "winter": [12, 1, 2],
        "spring": [3, 4, 5],
        "summer": [6, 7, 8],
        "autumn": [9, 10, 11],
    }
    history: list[dict[str, Any]] = []
    for season, months in season_month_map.items():
        if season not in seasonal:
            continue
        periods = list(seasonal[season].keys())
        for month in months:
            history.append({"month": month, "periods": periods})
    return history
