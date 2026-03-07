---
name: time-toolkit
description: 时间管理工具包 - 网络对时、世界时钟、时区转换
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

输出示例：
```
======================================================================
🕐 世界时钟
======================================================================
🌍 北京     11:58:32 2026-03-07 Sat
🌍 东京     12:58:32 2026-03-07 Sat
🌍 悉尼     14:58:32 2026-03-07 Sat
🌍 伦敦     03:58:32 2026-03-07 Sat
🌍 纽约     22:58:32 2026-03-06 Fri
🌍 洛杉矶   19:58:32 2026-03-06 Fri
🌍 UTC      03:58:32 2026-03-07 Sat
======================================================================
```

### 3. 时区转换

```bash
# 转换北京时间 14:30 到纽约时间
python3 world_clock.py convert 北京 14:30 纽约

# 转换洛杉矶时间 9:00 到东京时间
python3 world_clock.py convert 洛杉矶 9:00 东京
```

## 支持的时区

- 北京 (Asia/Shanghai)
- 东京 (Asia/Tokyo)
- 悉尼 (Australia/Sydney)
- 伦敦 (Europe/London)
- 纽约 (America/New_York)
- 洛杉矶 (America/Los_Angeles)
- UTC

## 与系统时间的关系

**注意**：这个工具检查系统时间是否准确，但不会自动修改系统时间（需要管理员权限）。

在 macOS 上，建议：
1. 系统设置 → 日期与时间
2. 勾选「自动设置日期与时间」
3. 选择时间服务器如 `time.apple.com`

## 定时检查

可以添加到定时任务，每天检查时间：
```bash
# 编辑 crontab
crontab -e

# 添加（每天8点检查）
0 8 * * * ~/.openclaw/workspace/skills/time-toolkit/time_sync.py check >> /tmp/time_check.log 2>&1
```
