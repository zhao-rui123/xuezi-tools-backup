---
name: system-guard
description: OpenClaw系统保护守卫 - 防止恶意技能包破坏系统，提供快照备份、沙箱测试、安全安装、自动回滚功能
metadata:
  openclaw:
    requires:
      bins: [python3]
---

# System Guard - 系统保护守卫

## 🛡️ 为什么需要系统保护？

技能包拥有系统访问权限，可能：
- 读取敏感文件（SSH密钥、配置文件）
- 执行系统命令
- 修改系统设置
- 导致OpenClaw崩溃

**System Guard = 安装前的多重保险**

## 核心功能

### 1. 系统快照 📸

安装前自动创建完整备份，出现问题可一键恢复。

```bash
# 手动创建快照
cd ~/.openclaw/workspace/skills/system-guard
python3 system_guard.py snapshot -d "安装xxx前备份"

# 查看所有快照
python3 system_guard.py list
```

### 2. 安全检查 🔍

自动调用 `security-scanner` 扫描技能包：
- 危险代码模式检测
- 可疑文件操作识别
- 硬编码凭证检查
- 网络数据外泄风险

### 3. 沙箱测试 🔬

在隔离环境测试技能包：
- 文件结构验证
- Python语法检查
- 危险文件检测
- 模拟导入测试

### 4. 安全安装 🛡️

完整的保护流程：
```
1. 创建系统快照（自动）
2. 安全检查（调用security-scanner）
3. 沙箱测试
4. 安装技能包
5. 简单验证
6. 如果失败 → 提示回滚
```

### 5. 自动回滚 ↩️

安装后如果系统异常，快速恢复到之前状态：

```bash
# 恢复到指定快照
python3 system_guard.py restore ~/.openclaw/.system-backups/snapshot_20260307_123000

# 查看可恢复的快照
python3 system_guard.py list
```

## 使用方法

### 快速安全安装（推荐）

```bash
# 使用安全安装脚本
cd ~/.openclaw/workspace/skills/system-guard/scripts
./safe-install.sh /path/to/new-skill
```

### Python调用

```python
from system_guard import safe_install_skill, create_system_snapshot

# 安全安装技能包
success = safe_install_skill('/path/to/new-skill')

# 手动创建快照
snapshot = create_system_snapshot("重要操作前备份")
```

### 命令行使用

```bash
cd ~/.openclaw/workspace/skills/system-guard

# 创建系统快照
python3 system_guard.py snapshot -d "重要操作前备份"

# 安全安装技能包
python3 system_guard.py install /path/to/new-skill

# 列出所有快照
python3 system_guard.py list

# 恢复系统到快照
python3 system_guard.py restore ~/.openclaw/.system-backups/snapshot_xxx

# 清理旧快照（保留最近10个）
python3 system_guard.py cleanup -k 10
```

## 保护机制详解

### 安装前自动备份

每次安全安装会自动创建快照，包含：
- ✅ 所有技能包 (`skills/`)
- ✅ OpenClaw配置文件 (`openclaw.json`等)
- ✅ 快照元数据 (时间、描述)

### 多层安全检查

| 层级 | 检查内容 | 发现问题时 |
|------|---------|-----------|
| 静态扫描 | 危险代码模式 | 警告/阻止安装 |
| 沙箱测试 | 语法错误、危险文件 | 阻止安装 |
| 安装验证 | SKILL.md存在性 | 警告 |

### 快照管理

快照存储在：`~/.openclaw/.system-backups/`

```
snapshot_20260307_120000/
├── snapshot.json      # 快照信息
├── skills/            # 技能包备份
└── config/            # 配置文件备份
```

## 典型场景

### 场景1: 安装陌生来源的技能包

```bash
# 下载了GitHub上的技能包
git clone https://github.com/xxx/unknown-skill.git

# 安全安装
./safe-install.sh ./unknown-skill

# 如果出现问题，查看日志并回滚
tail ~/.openclaw/.system-guard.log
python3 system_guard.py list
python3 system_guard.py restore ~/.openclaw/.system-backups/snapshot_xxx
```

### 场景2: 批量安装多个技能包

```bash
# 安装前创建一个总快照
python3 system_guard.py snapshot -d "批量安装前"

# 然后逐个安装（每个都会自动创建子快照）
./safe-install.sh ./skill1
./safe-install.sh ./skill2
./safe-install.sh ./skill3

# 如果出问题，可以回滚到批量安装前的状态
```

### 场景3: 升级现有技能包

```bash
# 升级前自动备份旧版本
./safe-install.sh ./new-version-of-existing-skill

# 如果新版本有问题，可以回滚恢复旧版本
```

## 与 security-scanner 的关系

```
┌─────────────────────────────────────────────────┐
│                 安全安装流程                      │
├─────────────────────────────────────────────────┤
│  1. 创建系统快照 ← system-guard                 │
│  2. 安全检查 ← 调用 security-scanner            │
│  3. 沙箱测试 ← system-guard                     │
│  4. 安装技能包                                  │
│  5. 验证                                        │
└─────────────────────────────────────────────────┘
```

## 自动清理

快照会占用磁盘空间，建议定期清理：

```bash
# 清理旧快照，只保留最近10个
python3 system_guard.py cleanup -k 10

# 添加到每周定时任务
crontab -e
# 添加: 0 3 * * 1 ~/.openclaw/workspace/skills/system-guard/system_guard.py cleanup
```

## 日志查看

```bash
# 查看系统守卫日志
cat ~/.openclaw/.system-guard.log

# 实时查看
tail -f ~/.openclaw/.system-guard.log
```

## 注意事项

- ⚠️ 系统快照只备份技能包和配置，**不备份会话历史**
- ⚠️ 快照会占用磁盘空间，建议定期清理
- ⚠️ 恢复系统会**覆盖**当前技能包和配置，谨慎操作
- ✅ 安全安装比普通安装慢，但更可靠

## 故障排查

### 问题: 安装后系统异常

**解决:**
```bash
# 1. 查看最新快照
python3 system_guard.py list

# 2. 恢复到安装前状态
python3 system_guard.py restore ~/.openclaw/.system-backups/snapshot_xxx

# 3. 重启OpenClaw Gateway
openclaw gateway restart
```

### 问题: 快照占用空间太大

**解决:**
```bash
# 清理旧快照
python3 system_guard.py cleanup -k 5

# 手动删除特定快照
rm -rf ~/.openclaw/.system-backups/snapshot_xxx
```

---

**安全第一，安装前记得快照！** 🛡️
