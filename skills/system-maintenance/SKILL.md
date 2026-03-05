---
name: system-maintenance
description: OpenClaw system maintenance and health monitoring. Use when performing system cleanup, log rotation, session cleanup, or health checks. Covers automated maintenance tasks for the OpenClaw environment.
---

# 系统维护技能

## 维护脚本

**位置**: `~/.openclaw/workspace/scripts/system-maintenance.sh`

**功能**:
1. 日志轮转（gateway.log, gateway.err.log）
2. 清理孤儿会话文件
3. 检查磁盘空间
4. 检查 OpenClaw 状态
5. 清理旧备份（保留30天）

## 手动执行

```bash
bash ~/.openclaw/workspace/scripts/system-maintenance.sh
```

## 定时执行

### 添加到 crontab（每周执行）
```bash
# 每周日凌晨2点执行维护
0 2 * * 0 /Users/zhaoruicn/.openclaw/workspace/scripts/system-maintenance.sh >> /tmp/system-maintenance.log 2>&1
```

## 维护内容详解

### 1. 日志轮转
- 将当前日志备份到 `/Volumes/cu/ocu/system-maintenance/logs/`
- 创建新的空日志文件
- 保留30天的备份

### 2. 会话清理
- 删除 `.jsonl.reset.*` 文件（重置的历史）
- 删除 `.jsonl.deleted.*` 文件（已删除会话）
- 保留当前活跃的会话文件

### 3. 磁盘检查
- 检查主磁盘使用率
- 检查备份磁盘使用率
- 空间不足时警告

### 4. 服务检查
- 检查 Gateway 进程状态
- 未运行时提示

## 健康检查清单

### 每日检查
- [ ] Gateway 运行状态
- [ ] 磁盘空间 < 80%
- [ ] 备份任务执行成功

### 每周检查
- [ ] 执行维护脚本
- [ ] 检查日志大小
- [ ] 清理临时文件

### 每月检查
- [ ] 清理旧会话历史
- [ ] 检查技能包更新
- [ ] 备份配置审查

## 故障处理

### Gateway 未启动
```bash
openclaw gateway restart
```

### 磁盘空间不足
```bash
# 清理大文件
find ~/.openclaw/logs -name "*.log" -size +10M -delete

# 清理旧备份
find /Volumes/cu/ocu -name "*.bak" -mtime +30 -delete
```

### 会话文件过多
```bash
cd ~/.openclaw/agents/main/sessions/
rm -f *.jsonl.reset.* *.jsonl.deleted.*
```

---
*创建于: 2026-03-04*  
*执行频率: 每周一次*
