from __future__ import annotations

import datetime as dt
import html
import re
import urllib.error
import urllib.request
from copy import deepcopy
from typing import Any


USER_AGENT = "energy-solution-agent/0.1"


def fetch_live_rule_patch(profile: dict[str, Any] | None, timeout: float = 8.0) -> dict[str, Any]:
    if not profile:
        return {
            "enabled": True,
            "status": "no_profile",
            "checked_at": _utc_now(),
            "sources": [],
            "notes": ["未命中省级 profile，无法执行官方规则在线刷新。"],
            "structured_patch": {},
        }

    links = [str(link) for link in profile.get("source_links", []) if link]
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
        fetched = _fetch_url(link, timeout=timeout)
        sources.append(fetched)
        if fetched["ok"]:
            ok_count += 1
            text = fetched["text"]
            notes.extend(_extract_rule_notes(text))
            patches.append(extract_structured_rule_patch(text))

    status = "ok" if ok_count > 0 else "failed"
    if ok_count > 0 and not notes:
        notes.append("已在线抓取官方来源，但未自动抽取出更细规则要点，建议人工复核原文。")
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

    contract_capacity = _extract_capacity_value(text, ["合同容量", "契约容量"])
    if contract_capacity is not None:
        patch["contract_capacity_kw"] = contract_capacity
    transformer_capacity = _extract_capacity_value(text, ["变压器容量"])
    if transformer_capacity is not None:
        patch["transformer_capacity_kva"] = transformer_capacity

    if "绿电" in text:
        patch["green_power_trade_rule"] = "green_power_enabled"
    if "绿证" in text:
        patch["certificate_rule"] = "green_certificate_enabled"
    if "辅助服务" in text:
        patch["ancillary_service_mode"] = "capacity"
    if "需求响应" in text:
        patch["demand_response_mode"] = "event_based"

    seasonal = _extract_seasonal_schedule_hints(text)
    if seasonal:
        patch["tou_schedule_seasonal"] = seasonal

    return patch


def _fetch_url(url: str, timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            content_type = response.headers.get("Content-Type", "")
            charset = response.headers.get_content_charset() or "utf-8"
            text = raw.decode(charset, errors="ignore")
            clean = _clean_text(text)
            title = _extract_title(text)
            return {
                "url": url,
                "ok": True,
                "status_code": getattr(response, "status", 200),
                "content_type": content_type,
                "title": title,
                "text": clean[:20000],
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
    stripped = re.sub(r"\s+", " ", stripped).strip()
    return stripped


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
    for key in keywords:
        idx = text.find(key)
        if idx >= 0:
            start = max(0, idx - 36)
            end = min(len(text), idx + 96)
            notes.append(f"{key}：{text[start:end].strip()}")
    return notes[:10]


def _extract_tou_prices(text: str) -> list[dict[str, float]]:
    prices: list[dict[str, float]] = []
    mappings = {
        "尖峰": "peak",
        "高峰": "peak",
        "峰段": "peak",
        "峰时段": "peak",
        "峰时": "peak",
        "平段": "flat",
        "平时段": "flat",
        "平时": "flat",
        "谷段": "valley",
        "低谷": "valley",
        "深谷": "deep_valley",
        "谷时段": "valley",
        "谷时": "valley",
    }
    for raw, period in mappings.items():
        match = re.search(raw + r".{0,24}?([0-9]+(?:\.[0-9]+)?)\s*元", text)
        if match:
            value = float(match.group(1))
            if not any(item["period"] == period for item in prices):
                prices.append({"period": period, "price": value})
    return prices


def _extract_hour_schedule(text: str) -> dict[str, list[int]]:
    schedule: dict[str, list[int]] = {}
    patterns = {
        "peak": ["尖峰", "高峰", "峰段", "峰时段", "峰时"],
        "flat": ["平段", "平时段", "平时"],
        "valley": ["谷段", "低谷", "谷时段", "谷时"],
        "deep_valley": ["深谷"],
    }
    for period, aliases in patterns.items():
        for alias in aliases:
            hours = _extract_hours_after_keyword(text, alias)
            if hours:
                schedule[period] = hours
                break
    return schedule


def _extract_hours_after_keyword(text: str, keyword: str) -> list[int]:
    idx = text.find(keyword)
    if idx < 0:
        return []
    snippet = text[idx : idx + 160]
    matches = re.findall(r"([0-2]?\d)\s*[:：]?\s*00?\s*(?:-|至|到|—)\s*([0-2]?\d)\s*[:：]?\s*00?", snippet)
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
    if "现货" in text or "实时" in text:
        return "market_price_series"
    if "中长期" in text:
        return "medium_long_term"
    if "代理购电" in text:
        return "proxy_purchase"
    return None


def _extract_demand_rule(text: str) -> str | None:
    if "需量" in text:
        return "需量电费"
    return None


def _extract_capacity_rule(text: str) -> str | None:
    if "容量电费" in text:
        return "容量电费"
    return None


def _extract_charge_mode(text: str) -> str | None:
    if "变压器容量" in text or "按变压器容量" in text:
        return "transformer_capacity"
    if "合同容量" in text or "契约容量" in text:
        return "contract_capacity"
    if "最大需量" in text or "按需量" in text:
        return "max_demand"
    return None


def _extract_rate(text: str, keyword: str) -> float | None:
    match = re.search(keyword + r".{0,24}?([0-9]+(?:\.[0-9]+)?)\s*元", text)
    if not match:
        return None
    return float(match.group(1))


def _extract_capacity_value(text: str, keywords: list[str]) -> float | None:
    for keyword in keywords:
        match = re.search(keyword + r".{0,20}?([0-9]+(?:\.[0-9]+)?)\s*(?:kW|kVA|千瓦|千伏安)", text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def _extract_seasonal_schedule_hints(text: str) -> dict[str, dict[str, list[int]]]:
    seasonal: dict[str, dict[str, list[int]]] = {}
    if "夏季" in text and ("尖峰" in text or "峰" in text):
        seasonal["summer"] = {
            "peak": [10, 11, 14, 15, 16, 17, 18, 19, 20],
            "flat": [8, 9, 12, 13, 21, 22],
            "valley": [0, 1, 2, 3, 4, 5, 6, 7, 23],
        }
    if "冬季" in text and "峰" in text:
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
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
