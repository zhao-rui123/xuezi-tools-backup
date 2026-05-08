from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from .network_http import get_proxy_url, http_get_json

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NASA_POWER_CLIMATOLOGY_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
NASA_POWER_HOURLY_URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"
DEFAULT_USER_AGENT = "energy-solution-agent/0.1 (+resource-fetch)"


def enrich_with_auto_resource_data(data: dict[str, Any], cache_dir: Path | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    meta = {
        "location_resolved": False,
        "resource_fetch_attempted": False,
        "resource_fetch_used_cache": False,
        "resource_fetch_status": "skipped",
        "resource_fetch_sources": [],
        "resource_fetch_proxy": "",
    }
    project = data.setdefault("project_info", {})
    solar = data.setdefault("resource_data", {}).setdefault("solar", {})
    wind = data.setdefault("resource_data", {}).setdefault("wind", {})
    proxy_url = get_proxy_url(data.get("network"))
    meta["resource_fetch_proxy"] = proxy_url or ""

    if _has_sufficient_resource_data(solar, wind):
        meta["resource_fetch_status"] = "not_needed"
        return data, meta

    latitude = _coerce_float(project.get("latitude") or project.get("latitude_deg"))
    longitude = _coerce_float(project.get("longitude") or project.get("longitude_deg"))
    resolved_name = project.get("resolved_location_name")

    if latitude is None or longitude is None:
        query = _build_location_query(project)
        if not query:
            meta["resource_fetch_status"] = "missing_location"
            return data, meta
        try:
            country = str((data.get("project_info", {}) or {}).get("country") or "").strip().lower()
            province = str((data.get("project_info", {}) or {}).get("province") or "").strip().lower()
            nominatim_country_codes = "cn" if (country in {"china", "prc", "cn", "中国", ""} and province not in {"", "overseas", "海外"}) else ""
            geocode = _cached_json(
                prefix="nominatim",
                key=query,
                cache_dir=cache_dir,
                loader=lambda: _fetch_nominatim(query, proxy_url=proxy_url, country_codes=nominatim_country_codes),
            )
        except Exception:
            meta["resource_fetch_attempted"] = True
            meta["resource_fetch_status"] = "geocode_failed"
            return data, meta
        meta["resource_fetch_attempted"] = True
        meta["resource_fetch_sources"].append(NOMINATIM_SEARCH_URL)
        meta["resource_fetch_used_cache"] = bool(geocode.get("_cache_hit"))
        latitude = _coerce_float(geocode.get("latitude"))
        longitude = _coerce_float(geocode.get("longitude"))
        resolved_name = str(geocode.get("display_name") or "") or None
        if latitude is None or longitude is None:
            meta["resource_fetch_status"] = "geocode_failed"
            return data, meta
        project["latitude"] = latitude
        project["longitude"] = longitude
        if resolved_name:
            project["resolved_location_name"] = resolved_name
        meta["location_resolved"] = True

    if latitude is not None:
        solar.setdefault("site_latitude_deg", latitude)
    if longitude is not None:
        solar.setdefault("site_longitude_deg", longitude)
        wind.setdefault("site_longitude_deg", longitude)
    if latitude is not None:
        wind.setdefault("site_latitude_deg", latitude)

    hourly_year = _resolve_public_resource_year(data)
    hourly_fetched = False
    try:
        if not _has_hourly_solar_data(solar) or not _has_hourly_wind_data(wind):
            hourly = _cached_json(
                prefix="nasa_power_hourly",
                key=f"{latitude:.6f},{longitude:.6f},{hourly_year}",
                cache_dir=cache_dir,
                loader=lambda: _fetch_nasa_power_hourly(latitude, longitude, hourly_year, proxy_url=proxy_url),
            )
            meta["resource_fetch_attempted"] = True
            meta["resource_fetch_sources"].append(NASA_POWER_HOURLY_URL)
            meta["resource_fetch_used_cache"] = meta["resource_fetch_used_cache"] or bool(hourly.get("_cache_hit"))
            if not _has_hourly_solar_data(solar):
                solar_hourly_irr = hourly.get("hourly_irradiance_kwh_per_m2") or []
                solar_hourly_temp = hourly.get("hourly_temperature_c") or []
                if solar_hourly_irr:
                    solar["hourly_irradiance_kwh_per_m2"] = solar_hourly_irr
                    hourly_fetched = True
                if solar_hourly_temp and not solar.get("hourly_temperature_c"):
                    solar["hourly_temperature_c"] = solar_hourly_temp
            if not _has_hourly_wind_data(wind):
                hourly_wind = hourly.get("hourly_wind_speed_50m_mps") or []
                if hourly_wind:
                    wind["wind_speed_series_mps"] = hourly_wind
                    wind.setdefault("source_height_m", 50.0)
                    hourly_fetched = True
    except Exception:
        meta["resource_fetch_hourly_failed"] = True

    try:
        climate = _cached_json(
            prefix="nasa_power",
            key=f"{latitude:.6f},{longitude:.6f}",
            cache_dir=cache_dir,
            loader=lambda: _fetch_nasa_power_climatology(latitude, longitude, proxy_url=proxy_url),
        )
    except Exception:
        meta["resource_fetch_attempted"] = True
        meta["resource_fetch_status"] = "resource_fetch_failed"
        return data, meta
    meta["resource_fetch_attempted"] = True
    meta["resource_fetch_sources"].append(NASA_POWER_CLIMATOLOGY_URL)
    meta["resource_fetch_used_cache"] = meta["resource_fetch_used_cache"] or bool(climate.get("_cache_hit"))

    monthly_irr = climate.get("monthly_irradiation_kwh_per_m2") or []
    annual_irr = climate.get("annual_irradiation_kwh_per_m2")
    monthly_temp = climate.get("monthly_temperature_c") or []
    avg_wind_50m = climate.get("annual_avg_speed_50m_mps")

    if monthly_irr and not solar.get("monthly_irradiation_kwh_per_m2"):
        solar["monthly_irradiation_kwh_per_m2"] = monthly_irr
    if annual_irr is not None and solar.get("annual_irradiation_kwh_per_m2") is None:
        solar["annual_irradiation_kwh_per_m2"] = annual_irr
    if monthly_temp and not solar.get("temperature_profile_c"):
        solar["temperature_profile_c"] = _monthly_to_daily_profile(monthly_temp)
    if avg_wind_50m is not None and wind.get("annual_avg_speed_mps") is None:
        wind["annual_avg_speed_mps"] = avg_wind_50m
    if wind.get("source_height_m") is None:
        wind["source_height_m"] = 50.0

    meta["resource_fetch_status"] = "fetched_hourly" if hourly_fetched else "fetched"
    return data, meta


def _has_sufficient_resource_data(solar: dict[str, Any], wind: dict[str, Any]) -> bool:
    has_solar = any(
        solar.get(key)
        for key in (
            "hourly_generation_profile_kw",
            "hourly_irradiance_kwh_per_m2",
            "daily_irradiance_kwh_per_m2",
            "monthly_irradiation_kwh_per_m2",
            "annual_irradiation_kwh_per_m2",
            "specific_yield_kwh_per_kwp_year",
        )
    )
    has_wind = any(
        wind.get(key)
        for key in (
            "hourly_generation_profile_kw",
            "wind_speed_series_mps",
            "hourly_wind_speed_series_mps",
            "daily_wind_speed_series_mps",
            "monthly_capacity_factor",
            "annual_avg_speed_mps",
            "capacity_factor_assumption",
            "expected_full_load_hours",
        )
    )
    return has_solar and has_wind


def _has_hourly_solar_data(solar: dict[str, Any]) -> bool:
    return bool(solar.get("hourly_generation_profile_kw") or solar.get("hourly_irradiance_kwh_per_m2"))


def _has_hourly_wind_data(wind: dict[str, Any]) -> bool:
    return bool(wind.get("hourly_generation_profile_kw") or wind.get("wind_speed_series_mps") or wind.get("hourly_wind_speed_series_mps"))


def _resolve_public_resource_year(data: dict[str, Any]) -> int:
    resource_data = data.get("resource_data", {}) or {}
    project = data.get("project_info", {}) or {}
    for value in (
        resource_data.get("public_resource_year"),
        project.get("resource_year"),
        project.get("weather_year"),
    ):
        try:
            if value not in (None, ""):
                year = int(value)
                if 1984 <= year <= date.today().year:
                    return year
        except (TypeError, ValueError):
            continue
    return date.today().year - 1


def _build_location_query(project: dict[str, Any]) -> str:
    for key in ("place_name", "location_name", "site_name"):
        value = str(project.get(key) or "").strip()
        if value:
            return value
    city = str(project.get("city") or "").strip()
    province = str(project.get("province") or "").strip()
    country = str(project.get("country") or "").strip()
    if city and country:
        return ", ".join(part for part in (city, province, country) if part and part.lower() not in {"overseas", "海外"})
    if country and province and province.lower() not in {"overseas", "海外"}:
        return ", ".join(part for part in (province, country) if part)
    return ""


def _fetch_nominatim(query: str, proxy_url: str | None = None, country_codes: str = "") -> dict[str, Any]:
    params: dict[str, Any] = {
        "q": query,
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1,
    }
    if country_codes:
        params["countrycodes"] = country_codes
    url = f"{NOMINATIM_SEARCH_URL}?{urlencode(params)}"
    payload = http_get_json(url, user_agent=DEFAULT_USER_AGENT, timeout=30.0, proxy_url=proxy_url)
    if not isinstance(payload, list) or not payload:
        return {}
    first = payload[0]
    return {
        "latitude": _coerce_float(first.get("lat")),
        "longitude": _coerce_float(first.get("lon")),
        "display_name": first.get("display_name"),
    }


def _fetch_nasa_power_climatology(latitude: float, longitude: float, proxy_url: str | None = None) -> dict[str, Any]:
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,T2M,WS50M",
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "format": "JSON",
    }
    url = f"{NASA_POWER_CLIMATOLOGY_URL}?{urlencode(params)}"
    payload = http_get_json(url, user_agent=DEFAULT_USER_AGENT, timeout=30.0, proxy_url=proxy_url)
    parameter = (((payload or {}).get("properties") or {}).get("parameter") or {})
    irradiance = parameter.get("ALLSKY_SFC_SW_DWN")
    irradiance = irradiance if isinstance(irradiance, dict) else {}
    temperature = parameter.get("T2M")
    temperature = temperature if isinstance(temperature, dict) else {}
    wind_speed = parameter.get("WS50M")
    wind_speed = wind_speed if isinstance(wind_speed, dict) else {}
    return {
        "monthly_irradiation_kwh_per_m2": _extract_month_values(irradiance),
        "annual_irradiation_kwh_per_m2": _coerce_float(irradiance.get("ANN")),
        "monthly_temperature_c": _extract_month_values(temperature),
        "annual_avg_speed_50m_mps": _coerce_float(wind_speed.get("ANN")),
    }


def _fetch_nasa_power_hourly(latitude: float, longitude: float, year: int, proxy_url: str | None = None) -> dict[str, Any]:
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,T2M,WS50M",
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "start": f"{year}0101",
        "end": f"{year}1231",
        "format": "JSON",
        "time-standard": "UTC",
    }
    url = f"{NASA_POWER_HOURLY_URL}?{urlencode(params)}"
    payload = http_get_json(url, user_agent=DEFAULT_USER_AGENT, timeout=60.0, proxy_url=proxy_url)
    parameter = (((payload or {}).get("properties") or {}).get("parameter") or {})
    irradiance_raw = parameter.get("ALLSKY_SFC_SW_DWN")
    irradiance_raw = irradiance_raw if isinstance(irradiance_raw, dict) else {}
    temperature_raw = parameter.get("T2M")
    temperature_raw = temperature_raw if isinstance(temperature_raw, dict) else {}
    wind_speed_raw = parameter.get("WS50M")
    wind_speed_raw = wind_speed_raw if isinstance(wind_speed_raw, dict) else {}
    irradiance = _extract_hour_values(irradiance_raw)
    temperature = _extract_hour_values(temperature_raw)
    wind_speed = _extract_hour_values(wind_speed_raw)
    return {
        "hourly_irradiance_kwh_per_m2": irradiance,
        "hourly_temperature_c": temperature,
        "hourly_wind_speed_50m_mps": wind_speed,
    }


def _extract_month_values(source: dict[str, Any]) -> list[float]:
    keys = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
    values = []
    for key in keys:
        value = _coerce_float(source.get(key))
        if value is None:
            return []
        values.append(value)
    return values


def _extract_hour_values(source: dict[str, Any]) -> list[float]:
    if not source:
        return []
    values: list[float] = []
    for key in sorted(source.keys()):
        if len(str(key)) != 10:
            continue
        value = _coerce_float(source.get(key))
        if value is None or value <= -900:
            return []
        values.append(value)
    if len(values) == 8784:
        values = _drop_leap_day(values)
    return values if len(values) == 8760 else []


def _drop_leap_day(values: list[float]) -> list[float]:
    feb_29_start = (31 + 28) * 24
    return values[:feb_29_start] + values[feb_29_start + 24 :]


def _monthly_to_daily_profile(monthly_values: list[float]) -> list[float]:
    if not monthly_values:
        return []
    return [float(value) for value in monthly_values]


def _cached_json(prefix: str, key: str, cache_dir: Path | None, loader: Any) -> dict[str, Any]:
    base_dir = cache_dir or (Path.cwd() / ".omx" / "cache" / "resource_fetch")
    base_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
    path = base_dir / f"{prefix}_{digest}.json"
    # TOCTOU risk: path may be modified between exists() check and write().
    # Acceptable for a read-only cache where concurrent writes are unlikely
    # and stale data is self-healing on the next fetch.
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["_cache_hit"] = True
        return payload
    payload = loader() or {}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    payload["_cache_hit"] = False
    return payload


def _coerce_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
