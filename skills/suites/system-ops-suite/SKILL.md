---
name: system-ops-suite
description: |
  系统运维完整套件 - 整合备份、安全、维护、监控
  一站式系统运维解决方案
version: 1.0.0
---

# 系统运维套件 (System Operations Suite)

一站式系统运维解决方案，整合备份、安全、维护、监控全流程。

## 包含组件

| 组件 | 功能 | 路径 |
|------|------|------|
| **system-backup** | 系统和网站备份恢复 | `../system-backup/` |
| **system-guard** | 系统安全扫描和防护 | `../system-guard/` |
| **system-maintenance** | 系统维护和监控 | `../system-maintenance/` |

## 快速开始

### 一键系统检查
```bash
cd ~/.openclaw/workspace/skills/suites/system-ops-suite
python3 suite_runner.py --health-check
```

### 完整维护流程
```bash
python3 suite_runner.py --maintenance
```

## 功能特性

### 💾 备份恢复 (system-backup)
- OpenClaw 系统每日增量备份
- 月度完整归档
- 网站备份恢复
- 灾难恢复工具
- 自动轮换策略

### 🛡️ 安全扫描 (system-guard)
- 系统安全扫描
- 技能包安全检查
- 轻量级安全增强
- 危险操作确认
- 审计日志

### 🔧 维护监控 (system-maintenance)
- 日志轮转和清理
- 磁盘空间监控
- 服务器健康检查
- 每日健康报告
- 故障自动修复

## 定时任务配置

```bash
# 每日健康检查 (09:00)
0 9 * * * ~/.openclaw/workspace/skills/suites/system-ops-suite/scripts/daily_check.sh

# 系统维护 (每周日 02:00)
0 2 * * 0 ~/.openclaw/workspace/skills/suites/system-ops-suite/scripts/weekly_maintenance.sh

# 安全扫描 (每周一 04:00)
0 4 * * 1 ~/.openclaw/workspace/skills/suites/system-ops-suite/scripts/security_scan.sh

# 每日备份 (22:00)
0 22 * * * ~/.openclaw/workspace/skills/system-backup/scripts/daily-backup.sh
```

## 服务器配置

编辑 `config/server.json`:
```json
{
  "servers": [
    {
      "name": "腾讯云主站",
      "ip": "[你的服务器IP]",
      "user": "root",
      "website_dir": "/usr/share/nginx/html"
    }
  ]
}
```

## 告警阈值

| 指标 | 正常 | 警告 | 危险 |
|------|------|------|------|
| 磁盘空间 | < 70% | 70-85% | > 85% |
| 内存使用 | < 70% | 70-85% | > 85% |
| 备份延迟 | < 1天 | 1-2天 | > 2天 |

## 使用示例

### 系统健康检查
```bash
python3 suite_runner.py --health-check
```

### 完整维护
```bash
python3 suite_runner.py --maintenance
```

### 安全扫描
```bash
python3 suite_runner.py --security-scan
```

### 备份恢复
```bash
python3 suite_runner.py --backup
python3 suite_runner.py --restore [备份文件]
```

## 目录结构

```
system-ops-suite/
├── SKILL.md              # 本文档
├── suite_runner.py       # 套件统一入口
├── config/
│   └── server.json       # 服务器配置
└── scripts/
    ├── daily_check.sh    # 每日检查脚本
    ├── weekly_maintenance.sh  # 每周维护脚本
    └── security_scan.sh  # 安全扫描脚本
```

## 更新日志

### v1.0.0 (2026-03-09)
- ✅ 创建系统运维套件
- ✅ 整合3个运维相关技能包
- ✅ 统一入口和配置

---
*系统运维一站式解决方案*
