# Kilo Agent 定时任务通知配置
## 配置完成时间: 2026-03-09
## 更新: 2026-03-10 (改为直接发送模式)

---

## 🤖 Kilo (通知Agent)

**角色**: Notification Agent  
**别名**: 广播专员  
**群聊ID**: `oc_b14195eb990ab57ea573e696758ae3d5`

---

## ⚠️ 重要更新 (2026-03-10)

**变更**: 放弃队列模式，改为直接发送模式

**原因**: 队列模式需要额外的处理器定时任务，配置复杂且容易出问题

**新方案**:
- ✅ 健康检查: 使用 `broadcaster.py --task send` 直接发送到群聊
- ✅ 每日备份: 使用 `broadcaster.py --task send` 直接发送到群聊
- ✅ 无需队列，立即发送，简单可靠

---

## ✅ 已配置的定时任务

### 1. 每日备份 (22:00)
**脚本**: `~/.openclaw/workspace/skills/system-backup/scripts/daily-backup-v2.sh`
**状态**: ✅ 已配置Kilo通知

### 2. 健康检查 (09:00)
**脚本**: `~/.openclaw/workspace/scripts/daily-health-check.sh`
**状态**: ✅ 已配置Kilo通知

### 3. 备份检查 (22:05)
**脚本**: `~/.openclaw/workspace/scripts/backup-check.sh`
**状态**: ✅ 已配置Kilo通知

### 4. 系统维护 (周日 02:00)
**脚本**: `~/.openclaw/workspace/scripts/system-maintenance.sh`
**状态**: ✅ 已配置Kilo通知

### 5. 文件清理 (周一 03:00)
**脚本**: `~/.openclaw/workspace/scripts/file-cleanup.sh`
**状态**: ✅ 已配置Kilo通知

### 6. 股票推送 (工作日 16:30)
**脚本**: `~/.openclaw/workspace/scripts/stock_daily_push.sh`
**状态**: ✅ 已配置Kilo通知

### 7. 知识库维护 (周一 05:00)
**脚本**: `~/.openclaw/workspace/skills/knowledge-base/scripts/weekly-maintenance.sh`
**状态**: ✅ 已配置Kilo通知

### 8. 进化报告 (每月2号 09:00)
**脚本**: `~/.openclaw/workspace/skills/self-improvement/evolution_reporter.py`
**状态**: ✅ 已配置Kilo通知

### 9. 月度归档 (每月1号 03:00)
**脚本**: `~/.openclaw/workspace/skills/system-backup/scripts/monthly-archive.sh`
**状态**: ✅ 已配置Kilo通知

### 10. 系统扫描 (周一 04:00)
**脚本**: `~/.openclaw/workspace/skills/system-guard/scripts/weekly-scan.sh`
**状态**: ✅ 已配置Kilo通知

### 11. 日志轮转 (每天 03:00)
**脚本**: `~/.openclaw/workspace/scripts/log_rotate.sh`
**状态**: ✅ 已配置Kilo通知

### 12. 每日英语新闻 (每天 08:30)
**脚本**: `~/.openclaw/workspace/scripts/daily-english-news.sh`
**状态**: ✅ 已配置Kilo通知

---

## 📋 广播专员使用方法

### 直接发送通知
```bash
# 发送通知到群聊
python3 ~/.openclaw/workspace/agents/kilo/broadcaster.py \
    --task send \
    --message "通知内容" \
    --target group

# 发送通知到用户私聊
python3 ~/.openclaw/workspace/agents/kilo/broadcaster.py \
    --task send \
    --message "通知内容" \
    --target user
```

---

## 🔧 技术细节

### 直接发送模式 (当前使用)
- **优点**: 简单直接，立即发送，无需额外配置
- **缺点**: 如果发送失败，需要脚本自己处理重试
- **适用场景**: 实时通知、定时任务报告

### 队列模式 (已废弃)
- **优点**: 可堆积、可重试、可批量处理
- **缺点**: 需要额外的处理器定时任务
- **废弃原因**: 配置复杂，处理器定时任务容易遗漏

---

## 📝 更新记录

| 日期 | 变更 |
|------|------|
| 2026-03-09 | 初始配置，使用队列模式 |
| 2026-03-10 | 改为直接发送模式，简化配置 |

---

*配置时间: 2026-03-09*  
*更新时间: 2026-03-10*
