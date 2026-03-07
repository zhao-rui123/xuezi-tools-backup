# 技能包备份与恢复指南

## 📦 自动备份系统

### 备份位置
外部存储: `/Volumes/cu/ocu/`

### 备份频率
每天 22:00 自动执行

### 两种备份格式

| 格式 | 位置 | 说明 |
|------|------|------|
| **文件夹同步** | `workspace-skills/` | 实时同步，便于查看和快速恢复 |
| **tar.gz压缩包** | `skills-backup/*.tar.gz` | 历史版本，便于分享和迁移 |

### 查看最新备份
```bash
# 文件夹版本
ls -lah /Volumes/cu/ocu/workspace-skills/

# 压缩包版本
ls -lah /Volumes/cu/ocu/skills-backup/
```

---

## 🔄 恢复技能包

### 场景1: 恢复到新电脑（推荐用压缩包）

```bash
# 1. 使用 latest 链接恢复最新版本
cd ~/.openclaw/workspace
tar -xzvf /Volumes/cu/ocu/skills-backup/latest

# 2. 或者恢复特定日期
tar -xzvf /Volumes/cu/ocu/skills-backup/skills-backup-20260307_113116.tar.gz
```

### 场景2: 恢复单个文件

```bash
# 从文件夹版本复制特定文件
cp /Volumes/cu/ocu/workspace-skills/stock-analysis-pro/config/watchlist.py \
   ~/.openclaw/workspace/skills/stock-analysis-pro/config/
```

### 场景3: 恢复到历史版本

```bash
# 列出所有历史版本
ls -1t /Volumes/cu/ocu/skills-backup/skills-backup-*.tar.gz

# 选择特定日期恢复
tar -xzvf /Volumes/cu/ocu/skills-backup/skills-backup-20260306_220000.tar.gz \
    -C ~/.openclaw/workspace/
```

---

## 📊 备份管理

### 手动执行备份
```bash
~/.openclaw/workspace/skills/system-backup/scripts/daily-backup.sh
```

### 查看备份日志
```bash
# 查看最近备份日志
tail -50 /tmp/backup_cron.log

# 查看历史日志
cat /Volumes/cu/ocu/backup.log 2>/dev/null || echo "无历史日志"
```

---

## ⚠️ 注意事项

1. **外部存储必须挂载**: 备份时确保 `/Volumes/cu/ocu/` 已连接
2. **备份不含个人信息**: Cookie、API Key等需重新配置
3. **定时任务**: 每天22:00自动执行（system-backup套件）
4. **恢复后测试**: 恢复后运行技能包测试是否正常

---

## 📁 备份文件结构

```
/Volumes/cu/ocu/
├── memory/                    # Memory 备份
├── skills/                    # OpenClaw Skills 备份
├── workspace-skills/          # 技能包文件夹同步（最新）
├── skills-backup/             # 技能包压缩包（历史版本）
│   ├── skills-backup-20260307_220000.tar.gz
│   ├── skills-backup-20260306_220000.tar.gz
│   └── latest -> 指向最新版本
├── openclaw-config/           # OpenClaw 配置备份
└── monthly-archive/           # 月度归档
```
