---
name: daily-health-check
description: Daily health check and monitoring report for OpenClaw system, cloud server, and backup status. Use when reviewing system health, checking service status, or monitoring infrastructure.
---

# 每日健康检查技能

## 检查脚本

**位置**: `~/.openclaw/workspace/scripts/daily-health-check.sh`

**检查内容**:
1. **OpenClaw 状态** — Gateway、磁盘空间、会话数量
2. **云服务器状态** — 可访问性、磁盘、Nginx
3. **备份状态** — 本地备份、GitHub 同步
4. **今日统计** — 记忆文件、Git 变更

## 执行检查

### 手动执行
```bash
bash ~/.openclaw/workspace/scripts/daily-health-check.sh
```

### 定时执行（每天早上9点）
```bash
# 添加到 crontab
0 9 * * * /Users/zhaoruicn/.openclaw/workspace/scripts/daily-health-check.sh >> /tmp/daily-health.log 2>&1
```

## 报告示例

```
📊 每日健康检查报告
日期: 2026-03-04 09:00
================================

🔧 OpenClaw 状态
  ✅ Gateway: 运行中
  ✅ 磁盘空间: 22%
  ℹ️ 活跃会话: 3 个

☁️ 云服务器 (106.54.25.161)
  ✅ 服务器: 可访问
  ✅ 磁盘空间: 52%
  ✅ Nginx: 运行中

💾 备份状态
  ✅ 本地备份: 21 个文件
  ℹ️ 最新备份: 2026-03-04.md
  ✅ GitHub: a4521c1 最新提交

📈 今日统计
  ✅ 今日记忆: 45 行
  ✅ 工作区: 已同步

================================
```

## 状态说明

| 图标 | 含义 |
|------|------|
| ✅ | 正常 |
| ⚠️ | 警告（需关注） |
| ❌ | 错误（需处理） |
| ℹ️ | 信息 |

## 告警阈值

| 指标 | 正常 | 警告 | 危险 |
|------|------|------|------|
| 磁盘空间 | < 70% | 70-85% | > 85% |
| 内存使用 | < 70% | 70-85% | > 85% |
| 备份延迟 | < 1天 | 1-2天 | > 2天 |

## 故障响应

### Gateway 未运行
```bash
openclaw gateway restart
```

### 磁盘空间不足
```bash
# 清理日志
rm ~/.openclaw/logs/gateway.log.*.bak

# 清理旧备份
find /Volumes/cu/ocu -name "*.bak" -mtime +30 -delete
```

### 服务器无法访问
```bash
# 检查网络
ping 106.54.25.161

# 检查服务
sshpass -p 'Zr123456' ssh root@106.54.25.161 "systemctl status nginx"
```

## 历史报告

报告保存在 `/tmp/daily-health-report-YYYYMMDD.txt`

保留最近7天的报告，自动清理旧文件。

---
*创建于: 2026-03-04*  
*执行频率: 每日一次*
