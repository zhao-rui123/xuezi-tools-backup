from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any

USER_AGENT = "energy-solution-agent/1.0"


def auto_fetch_resources(data: dict[str, Any], timeout: float = 20.0) -> dict[str, Any]:
    """自动拉取资源数据（第一版：NASA POWER + Open-Meteo）

    触发条件：
    - project_info.resource_mode == "auto_fetch"
    - resource_data.site_latitude_deg / site_longitude_deg 或 project_info.lat/lon 存在
    """
    project = data.get("project_info", {})
    resource = data.setdefault("resource_data", {})
    solar = resource.setdefault("solar", {})
    wind = resource.setdefault("wind", {})

    mode = str(project.get("resource_mode") or resource.get("resource_mode") or "").lower()
    if mode != "auto_fetch":
        return data

    lat = _pick_float(
        solar.get("site_latitude_deg"),
        wind.get("site_latitude_deg"),
        project.get("lat"),
        project.get("latitude"),
    )
    lon = _pick_float(
        solar.get("site_longitude_deg"),
        wind.get("site_longitude_deg"),
        project.get("lon"),
        project.get("longitude"),
    )
    if lat is None or lon is None:
        return data

    # NASA POWER: 年总辐照（kWh/m²） + 月度辐照 + 8760小时辐照
    if not solar.get("annual_irradiation_kwh_per_m2") or not solar.get("hourly_irradiance_kwh_per_m2"):
        nasa = _fetch_nasa_power(lat, lon, timeout=timeout)
        if nasa:
            solar.setdefault("annual_irradiation_kwh_per_m2", nasa.get("annual_ghi_kwh_m2"))
            solar.setdefault("monthly_irradiation_kwh_per_m2", nasa.get("monthly_ghi_kwh_m2"))
            if nasa.get("hourly_ghi_kwh_m2"):
                solar.setdefault("hourly_irradiance_kwh_per_m2", nasa.get("hourly_ghi_kwh_m2"))
            solar.setdefault("resource_source", "NASA POWER")

    # Open-Meteo: 年均风速 + 8760风速序列 + 温度序列
    openmeteo = _fetch_open_meteo(lat, lon, timeout=timeout)
    if openmeteo:
        if not wind.get("wind_speed_series_mps"):
            wind.setdefault("wind_speed_series_mps", openmeteo.get("wind_speed_8760_mps"))
            wind.setdefault("annual_avg_speed_mps", openmeteo.get("annual_avg_wind_speed_mps"))
            wind.setdefault("resource_source", "Open-Meteo")
        if not solar.get("temperature_profile_c"):
            solar.setdefault("temperature_profile_c", openmeteo.get("temperature_profile_24h_c"))
        if not solar.get("temperature_series_c") and openmeteo.get("temperature_8760_c"):
            solar.setdefault("temperature_series_c", openmeteo.get("temperature_8760_c"))

    return data


def _pick_float(*values: Any) -> float | None:
    for v in values:
        if v is None:
            continue
        try:
            return float(v)
        except (TypeError, ValueError):
            continue
    return None


def _http_json(url: str, timeout: float = 20.0) -> dict[str, Any] | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _fetch_nasa_power(lat: float, lon: float, timeout: float = 20.0) -> dict[str, Any] | None:
    daily_params = {
        "parameters": "ALLSKY_SFC_SW_DWN",
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "format": "JSON",
        "start": "20200101",
        "end": "20201231",
    }
    daily_url = "https://power.larc.nasa.gov/api/temporal/daily/point?" + urllib.parse.urlencode(daily_params)
    payload = _http_json(daily_url, timeout=timeout)
    if not payload:
        return None
    daily = payload.get("properties", {}).get("parameter", {}).get("ALLSKY_SFC_SW_DWN", {})
    if not daily:
        return None
    monthly = [0.0] * 12
    annual = 0.0
    for date_key, val in daily.items():
        try:
            month = int(str(date_key)[4:6])
            ghi = float(val)
        except Exception:
            continue
        annual += ghi
        if 1 <= month <= 12:
            monthly[month - 1] += ghi

    # 补抓 hourly GHI（单位 kWh/m²/hour）
    hourly_params = {
        "parameters": "ALLSKY_SFC_SW_DWN",
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "format": "JSON",
        "start": "20200101",
        "end": "20201231",
        "time-standard": "UTC",
    }
    hourly_url = "https://power.larc.nasa.gov/api/temporal/hourly/point?" + urllib.parse.urlencode(hourly_params)
    hourly_payload = _http_json(hourly_url, timeout=timeout)
    hourly_series = []
    if hourly_payload:
        hourly = hourly_payload.get("properties", {}).get("parameter", {}).get("ALLSKY_SFC_SW_DWN", {})
        if hourly:
            for _, val in sorted(hourly.items()):
                try:
                    hourly_series.append(float(val))
                except Exception:
                    continue

    return {
        "annual_ghi_kwh_m2": round(annual, 2),
        "monthly_ghi_kwh_m2": [round(v, 2) for v in monthly],
        "hourly_ghi_kwh_m2": hourly_series[:8760] if hourly_series else None,
    }


def _fetch_open_meteo(lat: float, lon: float, timeout: float = 20.0) -> dict[str, Any] | None:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,wind_speed_10m",
        "timezone": "UTC",
        "start_date": "2020-01-01",
        "end_date": "2020-12-31",
    }
    url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)
    payload = _http_json(url, timeout=timeout)
    if not payload:
        return None
    hourly = payload.get("hourly", {})
    temp = hourly.get("temperature_2m") or []
    wind = hourly.get("wind_speed_10m") or []
    if not wind:
        return None
    wind_vals = [float(v) for v in wind[:8760]]
    temp_vals = [float(v) for v in temp[:8760]] if temp else []
    avg_wind = sum(wind_vals) / len(wind_vals) if wind_vals else 0.0
    temp_24h = temp_vals[:24] if temp_vals else []
    return {
        "wind_speed_8760_mps": wind_vals,
        "annual_avg_wind_speed_mps": round(avg_wind, 3),
        "temperature_profile_24h_c": temp_24h,
        "temperature_8760_c": temp_vals[:8760] if temp_vals else None,
    }
