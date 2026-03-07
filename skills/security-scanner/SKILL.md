---
name: security-scanner
description: 技能包安全检查工具 + 轻量级安全增强（危险操作确认、审计日志）
metadata:
  openclaw:
    requires:
      bins: [python3]
---

# Security Scanner - 安全检查与增强

## 🛡️ 功能概述

### 1. 技能包安全扫描（原有）
- 扫描危险代码模式
- 检测可疑文件操作
- 检查硬编码凭证

### 2. 危险操作确认（新增）
在执行敏感操作前自动要求二次确认：
- `rm -rf` 删除文件/目录
- `chmod 777` 修改权限
- `curl | sh` 执行网络脚本
- 直接安装未经验证的技能包

### 3. 审计日志（新增）
记录关键操作便于追溯：
- 文件操作（删除、修改）
- 命令执行
- 消息发送
- 技能包安装/卸载
- 自动保留30天，过期自动清理

---

## 🚀 快速开始

### 启用安全增强

```bash
cd ~/.openclaw/workspace/skills/security-scanner
./scripts/enable-safety.sh
```

### 测试危险操作确认

```bash
# 尝试删除文件（会触发确认）
rm -rf ~/.openclaw/test.txt

# 提示: 🛡️ 检测到危险操作: 删除文件/目录
#       确认要永久删除 ~/.openclaw/test.txt 吗？(yes/no):
```

### 查看审计日志

```bash
# 查看最近24小时报告
python3 audit_logger.py report

# 查看最近7天
python3 audit_logger.py report 168

# 清理旧日志
python3 audit_logger.py cleanup
```

---

## 📊 审计日志内容

日志位置: `~/.openclaw/.logs/audit.log`

```json
{"timestamp": "2026-03-07 15:30:00", "action": "file_delete", "details": "path: ~/.openclaw/test.txt, result: success", "level": "WARNING", "session": "abc123"}
{"timestamp": "2026-03-07 15:31:00", "action": "command_execute", "details": "cmd: ls -la, status: executed", "level": "INFO", "session": "abc123"}
```

---

## ⚙️ 配置说明

### 危险操作白名单

某些路径被认为是安全的，不需要确认：
- `/tmp/`
- `~/.openclaw/workspace/temp/`
- `~/.openclaw/.cache/`

### 关键保护文件

这些文件删除前会自动备份：
- `MEMORY.md`
- `USER.md`
- `openclaw.json`
- `models.json`

---

## 📝 日志管理

### 自动清理

日志默认保留 **30天**，超过自动删除。

### 手动清理

```bash
python3 audit_logger.py cleanup
```

### 生成报告

```bash
python3 audit_logger.py report 24  # 最近24小时
```

---

## 🔒 安全级别

| 功能 | 影响 | 建议 |
|------|------|------|
| 危险操作确认 | 中等（多一步确认） | ✅ 启用 |
| 审计日志 | 无感知 | ✅ 启用 |
| 关键文件备份 | 低（自动） | ✅ 启用 |

**注意**: 这些措施对系统稳定性影响极小，主要用于防止误操作。

---

## 🎯 使用场景

### 场景1: 防止误删文件
```
用户: 删除 xxx
系统: 🛡️ 检测到危险操作: 删除文件/目录
      确认要永久删除 xxx 吗？(yes/no): 
用户: no
系统: ❌ 操作已取消
```

### 场景2: 事后追溯
```bash
# 发现文件不见了
python3 audit_logger.py report 24

# 输出:
# 📊 审计报告（最近24小时）
# ==================================================
# 总操作数: 15
# 错误数: 0
# 
# 操作分布:
#   - file_delete: 2次
#   - command_execute: 10次
#   - message_send: 3次
```

---

**安全第一，但不要过度！** 🛡️

## 🛡️ 功能概述

安装技能包之前进行安全检查，防范潜在风险：
- 🔍 扫描危险代码模式
- ⚠️ 检测可疑文件操作
- 🔑 检查硬编码凭证
- 🌐 识别网络数据外泄风险
- 📊 生成安全评估报告

## 为什么需要安全检查？

技能包拥有系统访问权限，可能：
- 读取敏感文件（SSH密钥、配置文件）
- 执行系统命令
- 发送数据到外部服务器
- 修改系统设置

**安装前扫描 = 多一层保护**

## 使用方法

### 扫描本地技能包

```bash
cd ~/.openclaw/workspace/skills/security-scanner
python3 security_scanner.py /path/to/skill
```

### 扫描示例

```bash
# 扫描 stock-analysis-pro
python3 security_scanner.py ~/.openclaw/workspace/skills/stock-analysis-pro

# 扫描刚下载的技能包
python3 security_scanner.py ~/Downloads/some-skill
```

## 扫描内容

### 🔴 严重问题（Critical）

| 检查项 | 说明 | 风险等级 |
|--------|------|----------|
| 代码执行 | eval(), exec(), os.system() | 🔴 高危 |
| 硬编码密码 | password = "xxx" | 🔴 高危 |
| 硬编码Token | api_key = "xxx" | 🔴 高危 |
| SSH密钥访问 | ~/.ssh/ | 🔴 高危 |
| AWS凭证访问 | ~/.aws/ | 🔴 高危 |

### 🟡 警告（Warning）

| 检查项 | 说明 | 风险等级 |
|--------|------|----------|
| 网络请求 | curl, wget, fetch | 🟡 中危 |
| 系统命令 | subprocess.call() | 🟡 中危 |
| 强制删除 | rm -rf | 🟡 中危 |
| 系统文件写入 | > /etc/xxx | 🟡 中危 |
| 权限修改 | chmod 777 | 🟡 中危 |

### 🔵 信息（Info）

| 检查项 | 说明 | 风险等级 |
|--------|------|----------|
| 脚本执行权限 | +x 权限 | 🔵 低危 |
| 缺少文档 | 无SKILL.md | 🔵 低危 |
| 敏感词 | 文档含password等 | 🔵 低危 |

## 输出示例

### ✅ 安全通过
```
======================================================================
✅ 安全检查通过
======================================================================

扫描文件: 15 个
发现问题: 0 个

该技能包看起来是安全的，可以安装。
======================================================================
```

### ⚠️ 发现问题
```
======================================================================
🔒 技能包安全检查报告
======================================================================

扫描路径: /path/to/skill
扫描文件: 15 个

问题统计:
  🔴 严重: 1 个
  🟡 警告: 2 个
  🔵 信息: 1 个

🔴 严重问题（建议不要安装）:
  [code_execution] 使用eval执行代码
    位置: script.py:25
  
🟡 警告（建议审查）:
  [network_exfil] HTTP请求可能泄露数据
    位置: fetcher.py
  [file_operations] 强制递归删除
    位置: cleanup.sh

⚠️ 建议: 发现严重安全问题，不建议安装此技能包！
======================================================================
```

## 使用建议

### 下载新技能包时

```bash
# 1. 下载技能包
cd /tmp
git clone https://github.com/xxx/some-skill.git

# 2. 安全检查
~/.openclaw/workspace/skills/security-scanner/security_scanner.py some-skill

# 3. 检查通过后再安装
# 有问题则删除，不安装
```

### 安装前自动检查

可以添加到安装脚本：
```bash
#!/bin/bash
SKILL_PATH=$1

# 安全检查
python3 ~/.openclaw/workspace/skills/security-scanner/security_scanner.py "$SKILL_PATH"
if [ $? -ne 0 ]; then
    echo "❌ 安全检查未通过，取消安装"
    exit 1
fi

# 继续安装...
```

## 与 ClawHub 集成

未来可以集成到 `clawhub install` 命令：
```bash
# 安装前自动扫描
clawhub install some-skill --security-check
```

## 局限性

- 基于模式匹配，可能有误报/漏报
- 无法检测逻辑层面的恶意行为
- 建议结合人工审查

## 安全等级说明

| 等级 | 建议 |
|------|------|
| ✅ 无问题 | 可以安装 |
| 🔵 仅信息 | 可以安装，注意提示 |
| 🟡 有警告 | 审查后决定是否安装 |
| 🔴 有严重问题 | **不建议安装** |

---

**安全第一，扫描先行！** 🛡️
