---
name: security-scanner
description: 技能包安全检查工具 - 安装前扫描潜在风险，检测恶意代码和敏感操作
metadata:
  openclaw:
    requires:
      bins: [python3]
---

# Security Scanner - 技能包安全检查

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
