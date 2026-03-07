---
name: time-toolkit
description: 时间管理工具包 - 网络对时、世界时钟、时区转换、天气查询
metadata:
  openclaw:
    requires:
      bins: [python3]
---

# Time Toolkit - 时间管理工具包

## 功能概述

- 🕐 **网络对时** - 检查系统时间与网络时间的差异
- 🌍 **世界时钟** - 显示多个时区的当前时间
- 🔄 **时区转换** - 转换任意时间到不同时区
- 🌤️ **天气查询** - 查询全球城市天气、穿衣建议

## 使用方法

### 1. 网络对时

**检查时间差异：**
```bash
cd ~/.openclaw/workspace/skills/time-toolkit
python3 time_sync.py check
```

**同步系统时间：**
```bash
python3 time_sync.py sync
```

### 2. 世界时钟

```bash
python3 world_clock.py
```

### 3. 时区转换

```bash
# 转换北京时间 14:30 到纽约时间
python3 world_clock.py convert 北京 14:30 纽约
```

### 4. 天气查询 🌤️

**查询天气：**
```bash
python3 weather.py           # 默认查询北京
python3 weather.py Shanghai  # 查询上海
python3 weather.py Tokyo     # 查询东京
python3 weather.py "New York" # 查询纽约
```

**输出示例：**
```
============================================================
🌤️  Beijing天气
============================================================

当前温度: 15°C
体感温度: 13°C
天气状况: 晴
相对湿度: 45%
今日最高: 18°C
今日最低: 8°C

💡 🌤️ 天气舒适，正常穿着
============================================================
```

**Python调用：**
```python
from weather import get_weather, quick_weather

# 获取天气数据
data = get_weather("Shanghai")
print(f"温度: {data['temperature']}°C")

# 快速获取格式化输出
print(quick_weather("Tokyo"))
```

## 支持的时区

- 北京 (Asia/Shanghai)
- 东京 (Asia/Tokyo)
- 悉尼 (Australia/Sydney)
- 伦敦 (Europe/London)
- 纽约 (America/New_York)
- 洛杉矶 (America/Los_Angeles)
- UTC

## 天气数据来源

- 使用 Open-Meteo 免费API
- 无需API Key
- 支持全球任意城市（按名称搜索）

## 定时检查

```bash
# 编辑 crontab
crontab -e

# 每天8点检查时间和天气
0 8 * * * ~/.openclaw/workspace/skills/time-toolkit/time_sync.py check >> /tmp/time_check.log 2>&1
0 8 * * * ~/.openclaw/workspace/skills/time-toolkit/weather.py >> /tmp/weather.log 2>&1
```
