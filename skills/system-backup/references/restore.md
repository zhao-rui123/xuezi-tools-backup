# OpenClaw 系统备份恢复指南

## 快速恢复

### 场景1：从每日备份恢复（推荐日常使用）

适用于：误删文件、数据损坏、快速回滚

```bash
# 查看可用备份
~/.openclaw/workspace/skills/system-backup/scripts/restore.sh list

# 执行恢复
~/.openclaw/workspace/skills/system-backup/scripts/restore.sh restore-daily
```

这会恢复：
- Memory 文件（对话记录）
- Skills 技能包
- Workspace Skills
- OpenClaw 配置

### 场景2：从月度归档恢复（完整恢复）

适用于：系统重装、换机器、灾难恢复

```bash
# 查看可用归档
ls /Volumes/cu/ocu/archives/openclaw-archive-*.tar.gz

# 恢复指定日期的归档
~/.openclaw/workspace/skills/system-backup/scripts/restore.sh restore-archive 2026-03-01
```

### 场景3：仅恢复配置文件

适用于：配置错误、API key 变更

```bash
~/.openclaw/workspace/skills/system-backup/scripts/restore.sh restore-config
```

---

## 手动恢复步骤

如果自动脚本无法使用，可以手动恢复：

### 从每日备份手动恢复

```bash
# 1. 停止 OpenClaw
openclaw gateway stop

# 2. 备份当前（安全）
mv ~/.openclaw ~/.openclaw-old-$(date +%Y%m%d)

# 3. 恢复文件
mkdir -p ~/.openclaw/workspace/memory
cp -r /Volumes/cu/ocu/memory/* ~/.openclaw/workspace/memory/

mkdir -p ~/.openclaw/skills
cp -r /Volumes/cu/ocu/skills/* ~/.openclaw/skills/

mkdir -p ~/.openclaw/workspace/skills
cp -r /Volumes/cu/ocu/workspace-skills/* ~/.openclaw/workspace/skills/

# 4. 恢复配置
cp -r /Volumes/cu/ocu/openclaw-config/* ~/.openclaw/

# 5. 启动
openclaw gateway start

# 6. 验证
openclaw status
```

### 从月度归档手动恢复

```bash
# 1. 停止 OpenClaw
openclaw gateway stop

# 2. 备份当前
mv ~/.openclaw ~/.openclaw-old-$(date +%Y%m%d)

# 3. 解压归档
cd ~
tar -xzf /Volumes/cu/ocu/archives/openclaw-archive-2026-03-01.tar.gz

# 4. 启动
openclaw gateway start
```

---

## 回滚（恢复失败时）

如果恢复后出现问题，可以回滚到恢复前的状态：

```bash
# 1. 停止
openclaw gateway stop

# 2. 删除恢复的数据
rm -rf ~/.openclaw

# 3. 恢复备份
mv ~/.openclaw-old-XXXXXX ~/.openclaw

# 4. 启动
openclaw gateway start
```

---

## 备份内容说明

### 每日备份包含

| 目录 | 内容 | 用途 |
|------|------|------|
| `/memory/` | 对话记录、每日笔记 | 恢复上下文 |
| `/skills/` | 系统技能包 | 恢复功能 |
| `/workspace-skills/` | 自定义技能包 | 恢复自定义功能 |
| `/openclaw-config/` | 配置文件、cron | 恢复系统设置 |

### 月度归档包含

完整的 `~/.openclaw/` 目录：
- openclaw.json（主配置）
- credentials/（API keys）
- agents/（Agent 配置）
- workspace/（Memory、skills、项目文件）
- telegram/（Telegram 会话）
- cron/（定时任务）
- channels/（频道配置）

排除项（不备份）：
- completions/（API 缓存，可自动重建）
- *.log（日志文件）
- node_modules/（依赖，可重新安装）

---

## 定时任务

### 每日备份（已配置）
```cron
0 22 * * * ~/.openclaw/workspace/skills/system-backup/scripts/daily-backup.sh
```

### 月度归档（已配置）
```cron
0 3 1 * * ~/.openclaw/workspace/skills/system-backup/scripts/monthly-archive.sh
```

---

## 故障排查

### 备份失败

1. 检查磁盘挂载：`ls /Volumes/cu/ocu/`
2. 检查日志：`tail /tmp/backup_memory.log`
3. 手动执行：`bash ~/.openclaw/workspace/skills/system-backup/scripts/daily-backup.sh`

### 恢复失败

1. 检查备份是否存在：`ls /Volumes/cu/ocu/memory/`
2. 检查权限：`ls -la ~/.openclaw/`
3. 查看详细日志：脚本执行时会显示具体错误

### Gateway 无法启动

```bash
# 检查配置
openclaw doctor

# 重置 Gateway
openclaw gateway stop
rm -rf ~/.openclaw/completions
openclaw gateway start
```

---

## 最佳实践

1. **定期检查备份**：每月查看备份目录，确认备份正常
2. **测试恢复流程**：每季度测试一次恢复，确保备份可用
3. **异地备份**：重要数据可额外复制到云存储
4. **敏感数据**：API keys 和 credentials 已包含在备份中，注意备份介质安全

---

## 联系支持

如有问题，检查日志文件：
- 每日备份：`/tmp/backup_memory.log`
- 月度归档：`/tmp/backup_archive.log`
