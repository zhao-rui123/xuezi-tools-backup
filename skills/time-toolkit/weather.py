#!/usr/bin/env python3
"""
天气查询模块 - 为time-toolkit添加天气功能
"""

import urllib.request
import json
from typing import Dict, Optional

def get_weather(city: str = "Beijing") -> Optional[Dict]:
    """
    获取天气信息（使用Open-Meteo免费API）
    无需API Key
    """
    try:
        # 先获取城市坐标
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        
        req = urllib.request.Request(geo_url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        response = urllib.request.urlopen(req, timeout=10)
        geo_data = json.loads(response.read().decode('utf-8'))
        
        if not geo_data.get('results'):
            return None
        
        lat = geo_data['results'][0]['latitude']
        lon = geo_data['results'][0]['longitude']
        city_name = geo_data['results'][0]['name']
        
        # 获取天气
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code&"
            f"daily=temperature_2m_max,temperature_2m_min,weather_code&"
            f"timezone=auto"
        )
        
        req = urllib.request.Request(weather_url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        response = urllib.request.urlopen(req, timeout=10)
        weather_data = json.loads(response.read().decode('utf-8'))
        
        # 天气代码映射
        weather_codes = {
            0: "晴", 1: " mainly clear", 2: " partly cloudy", 3: " overcast",
            45: "雾", 48: "雾凇",
            51: "毛毛雨", 53: "中度毛毛雨", 55: "强毛毛雨",
            61: "小雨", 63: "中雨", 65: "大雨",
            71: "小雪", 73: "中雪", 75: "大雪",
            80: "阵雨", 81: "强阵雨", 82: "暴雨",
            95: "雷雨", 96: "雷雨伴冰雹", 99: "强雷雨伴冰雹",
        }
        
        current = weather_data.get('current', {})
        daily = weather_data.get('daily', {})
        
        weather_code = current.get('weather_code', 0)
        weather_desc = weather_codes.get(weather_code, "未知")
        
        return {
            'city': city_name,
            'temperature': current.get('temperature_2m'),
            'feels_like': current.get('apparent_temperature'),
            'humidity': current.get('relative_humidity_2m'),
            'weather': weather_desc,
            'unit': weather_data.get('current_units', {}).get('temperature_2m', '°C'),
            'daily_max': daily.get('temperature_2m_max', [None])[0],
            'daily_min': daily.get('temperature_2m_min', [None])[0],
        }
        
    except Exception as e:
        print(f"获取天气失败: {e}")
        return None

def format_weather(data: Dict) -> str:
    """格式化天气信息"""
    if not data:
        return "❌ 无法获取天气信息"
    
    lines = [
        f"\n{'='*60}",
        f"🌤️  {data['city']}天气",
        f"{'='*60}",
        f"",
        f"当前温度: {data['temperature']}{data['unit']}",
        f"体感温度: {data['feels_like']}{data['unit']}",
        f"天气状况: {data['weather']}",
        f"相对湿度: {data['humidity']}%",
    ]
    
    if data.get('daily_max') and data.get('daily_min'):
        lines.append(f"今日最高: {data['daily_max']}{data['unit']}")
        lines.append(f"今日最低: {data['daily_min']}{data['unit']}")
    
    # 穿衣建议
    temp = data.get('temperature', 20)
    if temp >= 30:
        advice = "🔥 天气炎热，注意防暑"
    elif temp >= 25:
        advice = "☀️ 天气较热，建议短袖"
    elif temp >= 15:
        advice = "🌤️ 天气舒适，正常穿着"
    elif temp >= 5:
        advice = "🧥 天气较凉，建议外套"
    else:
        advice = "❄️ 天气寒冷，注意保暖"
    
    lines.extend([
        f"",
        f"💡 {advice}",
        f"{'='*60}",
    ])
    
    return "\n".join(lines)

def quick_weather(city: str = "Beijing") -> str:
    """快速获取天气"""
    data = get_weather(city)
    return format_weather(data)

if __name__ == "__main__":
    import sys
    
    city = sys.argv[1] if len(sys.argv) > 1 else "Beijing"
    print(quick_weather(city))
