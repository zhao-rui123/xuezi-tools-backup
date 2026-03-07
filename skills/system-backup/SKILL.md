---
name: system-backup
description: Comprehensive backup and restore system for OpenClaw. Use when setting up automated backups, performing manual backups, or restoring from backup. Handles daily incremental backups of memory/skills and monthly full archives with rotation. Supports complete disaster recovery.
---

# System Backup - OpenClaw 系统备份恢复套件

全面的 OpenClaw 备份解决方案，支持每日增量备份和月度完整归档，包含完整的恢复文档。

## 功能特性

### 1. 每日增量备份
- **Memory** - 对话记录和每日笔记
- **Skills** - 系统技能包
- **Workspace Skills** - 自定义技能包
- **OpenClaw Config** - 配置、cron、认证信息

### 2. 月度归档备份
- 完整的 `~/.openclaw/` 目录打包
- tar.gz 压缩格式
- 自动保留最近 6 个月
- 适合灾难恢复和系统迁移

### 3. 恢复工具
- 从每日备份快速恢复
- 从月度归档完整恢复
- 仅恢复配置文件
- 自动回滚支持

## 快速开始

### 安装

脚本已配置定时任务，无需手动安装。

### 手动执行备份

```bash
# 每日备份
~/.openclaw/workspace/skills/system-backup/scripts/daily-backup.sh

# 月度归档
~/.openclaw/workspace/skills/system-backup/scripts/monthly-archive.sh
```

### 恢复数据

```bash
# 查看可用备份
~/.openclaw/workspace/skills/system-backup/scripts/restore.sh list

# 从每日备份恢复
~/.openclaw/workspace/skills/system-backup/scripts/restore.sh restore-daily

# 从月度归档恢复（指定日期）
~/.openclaw/workspace/skills/system-backup/scripts/restore.sh restore-archive 2026-03-01

# 仅恢复配置
~/.openclaw/workspace/skills/system-backup/scripts/restore.sh restore-config
```

## 备份内容

### 每日备份（/Volumes/cu/ocu/）

```
memory/              - 对话记录和笔记
skills/              - 系统技能包
workspace-skills/    - 自定义技能包
openclaw-config/     - 配置文件和 cron
```

### 月度归档（/Volumes/cu/ocu/archives/）

```
openclaw-archive-YYYY-MM-DD.tar.gz
```

包含完整的 `~/.openclaw/` 目录。

## 定时任务

### 每日备份
```cron
0 22 * * * ~/.openclaw/workspace/skills/system-backup/scripts/daily-backup.sh
```

每晚 22:00 执行，飞书通知结果。

### 月度归档
```cron
0 3 1 * * ~/.openclaw/workspace/skills/system-backup/scripts/monthly-archive.sh
```

每月 1 号凌晨 3:00 执行，打包完整备份。

## 恢复场景

| 场景 | 推荐恢复方式 | 说明 |
|------|-------------|------|
| 误删文件 | 每日备份 | 快速恢复 |
| 配置错误 | 仅恢复配置 | 保留数据 |
| 系统重装 | 月度归档 | 完整恢复 |
| 换机器 | 月度归档 | 迁移环境 |
| 数据损坏 | 每日备份 | 回滚到之前 |

## 详细文档

- [恢复指南](references/restore.md) - 完整的恢复步骤和故障排查

## 脚本参考

| 脚本 | 用途 | 示例 |
|------|------|------|
| `daily-backup.sh` | 每日增量备份 | `./daily-backup.sh` |
| `monthly-archive.sh` | 月度归档 | `./monthly-archive.sh` |
| `restore.sh` | 恢复工具 | `./restore.sh restore-daily` |

## 备份策略

### 保留策略
- **每日备份**：长期保留（受磁盘空间限制）
- **月度归档**：保留最近 6 个月

### 排除项
- `completions/` - API 缓存（可重建）
- `*.log` - 日志文件
- `node_modules/` - 依赖（可重新安装）
- `__pycache__/` - Python 缓存

## 故障排查

### 备份失败
1. 检查磁盘挂载：`ls /Volumes/cu/ocu/`
2. 查看日志：`tail /tmp/backup_memory.log`
3. 手动测试：`bash scripts/daily-backup.sh`

### 恢复失败
参见 [恢复指南](references/restore.md) 的故障排查章节。

## 安全建议

1. 备份包含 API keys，请妥善保管备份介质
2. 定期检查备份完整性
3. 考虑异地备份（云存储）
4. 测试恢复流程，确保备份可用

## 与原版差异

相比原 `backup_memory.sh`：
- ✅ 扩展备份范围（config、cron）
- ✅ 新增月度归档功能
- ✅ 完整的恢复脚本和文档
- ✅ 支持多种恢复场景
- ✅ 自动轮换策略
