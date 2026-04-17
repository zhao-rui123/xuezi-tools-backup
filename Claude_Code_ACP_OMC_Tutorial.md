# Claude Code ACP & OMC 完整使用教程

*最后更新：2026-04-10*

---

## 目录

1. [环境准备](#1-环境准备)
2. [ACP 调用 Claude Code](#2-acp-调用-claude-code)
3. [OMC 执行模式详解](#3-omc-执行模式详解)
4. [19个专业Agent](#4-19个专业agent)
5. [Team团队协作](#5-team团队协作)
6. [脚本工具集](#6-脚本工具集)
7. [使用场景速查](#7-使用场景速查)
8. [常见问题](#8-常见问题)

---

## 1. 环境准备

### 1.1 必须条件

```bash
# 1. 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 2. 安装 acpx (ACP CLI工具)
npm install -g acpx
# 验证安装
acpx --version  # 应显示 0.5.3

# 3. 安装 omc (多Agent编排层)
npm install -g oh-my-claude-sisyphus
# 验证安装
omc --version  # 应显示版本号
```

### 1.2 重要前提

**⚠️ ACP调用前必须关闭 Claude GUI**

Claude GUI 和 acpx 不能同时运行，否则会冲突。

### 1.3 环境变量配置

```bash
# 在 ~/.claude/settings.json 中配置

# Opus 模型配置
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://timesniper.club",
    "ANTHROPIC_AUTH_TOKEN": "你的Opus-Token",
    "ANTHROPIC_MODEL": "claude-opus-4-6"
  }
}

# MiniMax 模型配置
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.minimaxi.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "你的MiniMax-Token",
    "ANTHROPIC_MODEL": "MiniMax-M2.7"
  }
}
```

### 1.4 模型切换脚本

```bash
# 切换到 Opus (架构/验收)
cc-model-switch.sh opus

# 切换到 MiniMax (执行开发)
cc-model-switch.sh minimax

# 查看当前状态
cc-model-switch.sh status
```

---

## 2. ACP 调用 Claude Code

### 2.1 acpx 核心命令

```bash
# 基本调用格式
acpx claude -s <session> "你的任务"

# 常用选项
acpx claude -s <session> "任务" --approve-all    # 自动批准所有操作
acpx claude -s <session> "任务" --no-wait        # 后台运行，不等待完成

# 示例
acpx claude -s my-task "用 autopilot 开发一个计算器"
```

### 2.2 会话管理

```bash
# 创建新会话
acpx claude sessions new --name <session-name>

# 列出所有会话
acpx claude sessions list

# 查看会话详情
acpx claude sessions show <session-name>

# 删除会话
acpx claude sessions delete <session-name>

# 查看当前状态
acpx claude status
```

### 2.3 工作流程

#### 流程一：前台执行（实时监控）

```bash
# 1. 创建会话
acpx claude sessions new --name my-project

# 2. 执行任务
acpx claude -s my-project "开发一个REST API"

# 3. 查看结果
# 直接在终端查看输出
```

#### 流程二：后台执行（自动驾驶）

```bash
# 1. 创建会话
acpx claude sessions new --name bg-task

# 2. 后台执行（重要！做完可以继续做其他的）
acpx claude -s bg-task --no-wait "用 autopilot 开发 xxx"

# 3. 查看状态
acpx claude -s bg-task status

# 4. 查看结果
tail ~/.acpx/sessions/*.stream.ndjson

# 或者
cat ~/.acpx/sessions/bg-task/*.ndjson
```

#### 流程三：sessions_spawn 后台运行

```javascript
// 在 OpenClaw 中使用
sessions_spawn({
  task: "任务描述",
  runtime: "subagent",
  model: "minimax-cn/MiniMax-M2.7",
  runTimeoutSeconds: 600
})
```

### 2.4 实用命令模板

```bash
# 快速执行
acpx claude -s quick "echo 'Hello'" --approve-all

# 自动驾驶模式
acpx claude sessions new --name autopilot-task
acpx claude -s autopilot-task --no-wait "autopilot: 构建一个博客系统"

# 带超时设置
timeout 300 acpx claude -s my-task "你的任务"

# 查看所有活跃会话
acpx claude sessions list | grep -E "active|running"
```

---

## 3. OMC 执行模式详解

### 3.1 核心命令速查

| 命令 | 功能 |
|------|------|
| `omc` | 启动 Claude Code |
| `omc launch` | 启动 Claude Code (显式) |
| `omc launch --madmax` | 跳过权限确认启动 |
| `omc team N:agent "task"` | 启动N个Agent团队 |
| `omc ralphthon "任务"` | Hackathon全自主模式 |
| `omc autoresearch` | 自动研究模式 |
| `omc ask` | 多AI对比分析 |
| `omc config` | 查看配置 |
| `omc setup` | 同步安装组件 |
| `omc wait` | 速率限制处理 |
| `omc doctor` | 故障诊断 |
| `omc teleport '#issue'` | Git worktree隔离开发 |
| `omc update` | 检查更新 |

### 3.2 5种执行模式（关键词触发）

#### Autopilot - 全自主执行

```
触发词: autopilot:
功能: 从想法到代码，全自动执行
适用: 快速开发小功能
示例:
  "autopilot: 构建一个用户管理系统"
  "autopilot 开发一个博客网站"
```

#### Ralph - 持续循环模式

```
触发词: ralph:
功能: 持续执行直到完成，带架构师验证
适用: 需要多轮迭代的任务
示例:
  "ralph: 重构整个认证系统"
```

#### Ultrawork - 最大并行化

```
触发词: ulw: / ultrawork:
功能: 最大化并行处理，同时执行多个任务
适用: 修复多个bug、并行开发
示例:
  "ulw: 修复所有安全漏洞"
  "ultrawork: 实现登录、注册、找回密码三个功能"
```

#### Deep Interview - 需求澄清

```
触发词: deep-interview:
功能: 苏格拉底式提问，澄清模糊需求
适用: 需求不明确的任务
示例:
  "deep-interview: 我想做一个AI助手"
```

#### Team - 团队协作

```
触发词: team N:
功能: N个Agent协调完成复杂任务
适用: 复杂系统设计、大型项目
示例:
  "team 3:executor 并行开发三个模块"
  "team 2:architect 设计微服务架构"
```

### 3.3 Team Pipeline

```
team-plan → team-prd → team-exec → team-verify → team-fix (循环)
```

---

## 4. 19个专业Agent

| Agent | 模型 | 用途 |
|-------|------|------|
| `explore` | haiku | 代码库快速探索、文件查找 |
| `analyst` | opus | 需求分析，发现隐藏约束 |
| `planner` | opus | 战略规划，任务分解 |
| `architect` | opus | 系统设计，技术选型 |
| `debugger` | sonnet | 根因分析，失败诊断 |
| `executor` | sonnet | 专注执行，不委托他人 |
| `verifier` | sonnet | 验证证据，测试验收 |
| `code-reviewer` | opus | 代码审查，质量把关 |
| `security-reviewer` | sonnet | 安全审计，漏洞检测 |
| `test-engineer` | sonnet | 测试策略，覆盖率优化 |
| `designer` | sonnet | UI/UX设计（仅视觉相关） |
| `writer` | haiku | 文档写作，说明书 |
| `qa-tester` | sonnet | 手动测试，CLI测试 |
| `scientist` | sonnet | 数据分析，统计分析 |
| `git-master` | sonnet | Git策略，提交规范 |
| `document-specialist` | sonnet | 文档查找，官方文档 |
| `critic` | opus | 计划挑战，设计质疑 |
| `code-simplifier` | opus | 代码简化，优化重构 |
| `tracer` | sonnet | 因果追踪 |

### 4.1 Claude Code内调用Agent

```bash
# 在 Claude Code 会话中直接调用
/explore "查找所有控制器文件"
/planner "规划一个电商系统"
/architect "设计分布式缓存方案"
/debugger "分析这个内存泄漏"
/team 3:executor "并行实现三个模块"
```

### 4.2 模型路由原则

| 模型 | 用途 |
|------|------|
| **Opus** | 架构设计、深度分析、高风险审查 |
| **Sonnet** | 标准开发、调试、代码审查 |
| **Haiku** | 快速查找、轻量检查 |

---

## 5. Team团队协作

### 5.1 基本用法

```bash
# 3个Claude并行
omc team 3:claude "修复bug"

# 2个Codex架构师
omc team 2:codex:architect "设计认证系统"

# 1个Gemini研究
omc team 1:gemini "研究新技术方案"

# 多AI混合
omc team 1:codex,1:gemini "对比两种实现方案"
```

### 5.2 带角色指定

```bash
# 带具体角色
omc team 2:claude:executor "实现支付模块"
omc team 1:codex:critic "审查代码质量"
```

### 5.3 可用角色

```
architect      - 架构师
executor      - 执行者
planner       - 规划师
analyst       - 分析师
critic       - 批评者
debugger      - 调试员
verifier      - 验证者
code-reviewer - 代码审查员
security-reviewer - 安全审查员
test-engineer - 测试工程师
designer      - 设计师
writer        - 文档作者
scientist     - 科学家
```

### 5.4 Team管理

```bash
# 查看状态
omc team status <team-name>

# 关闭团队
omc team shutdown <team-name>

# 强制关闭
omc team shutdown <team-name> --force

# 发送消息
omc team api send-message --input '{"team_name":"my-team","from_worker":"worker-1","to_worker":"leader","body":"完成"}' --json
```

---

## 6. 脚本工具集

### 6.1 模型切换脚本

```bash
# 位置: ~/.openclaw/workspace/scripts/cc-model-switch.sh

# 切换到 Opus
cc-model-switch.sh opus

# 切换到 MiniMax
cc-model-switch.sh minimax

# 查看状态
cc-model-switch.sh status
```

### 6.2 自定义脚本模板

#### 快速执行脚本

```bash
#!/bin/bash
# quick-cc.sh - 快速执行Claude Code任务
NAME=${1:-quick-$(date +%H%M%S)}
TASK=$2

if [ -z "$TASK" ]; then
    echo "用法: quick-cc.sh <任务描述>"
    exit 1
fi

acpx claude sessions new --name "$NAME"
acpx claude -s "$NAME" --no-wait "autopilot: $TASK"
echo "会话已创建: $NAME"
```

#### 后台任务监控脚本

```bash
#!/bin/bash
# monitor-cc.sh - 监控Claude Code后台任务

SESSION=$1

if [ -z "$SESSION" ]; then
    echo "用法: monitor-cc.sh <session-name>"
    exit 1
fi

echo "监控会话: $SESSION"
echo "按 Ctrl+C 退出"
echo ""

# 持续监控状态
while true; do
    STATUS=$(acpx claude -s "$SESSION" status 2>/dev/null | grep -E "status|state" || echo "未知")
    CLEAR=$(clear)
    echo "$CLEAR$(date '+%H:%M:%S') - $STATUS"
    sleep 5
done
```

#### 会话清理脚本

```bash
#!/bin/bash
# cleanup-sessions.sh - 清理旧会话

BACKUP_DIR="$HOME/.claude/sessions/backups"
KEEP_DAYS=7

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份当前会话
tar -czf "$BACKUP_DIR/sessions-$(date +%Y%m%d).tar.gz" \
    $HOME/.acpx/sessions/ 2>/dev/null || true

# 删除7天前的备份
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$KEEP_DAYS -delete

echo "清理完成"
```

### 6.3 OMC辅助命令

```bash
# 速率限制处理
omc wait              # 查看状态和建议
omc wait --start      # 启动自动恢复守护
omc wait detect       # 扫描阻塞会话

# 配置管理
omc config            # 查看当前配置
omc config --validate  # 验证配置
omc config --paths    # 显示配置路径

# 故障诊断
omc doctor            # 诊断问题
omc doctor conflicts  # 检查插件冲突

# Git Worktree隔离开发
omc teleport '#42'           # 为PR创建隔离分支
omc teleport list            # 列出所有worktree
omc teleport remove ./path   # 删除worktree
```

---

## 7. 使用场景速查

| 场景 | 推荐命令 | 说明 |
|------|---------|------|
| 快速开发小功能 | `autopilot: 开发一个计算器` | 全自动 |
| 复杂系统设计 | `team 3:architect` | 团队协作 |
| 修复多个bug | `ulw: 修复所有bug` | 最大并行 |
| 需求不明确 | `deep-interview:` | 苏格拉底澄清 |
| Hackathon竞赛 | `omc ralphthon` | 全自主生命周期 |
| 深度研究 | `omc autoresearch` | 自动研究 |
| 多AI对比 | `omc ask claude` | 多模型比较 |
| 隔离分支开发 | `omc teleport '#issue'` | Git隔离 |
| 速率限制 | `omc wait --start` | 自动恢复 |

---

## 8. 常见问题

### Q1: acpx 和 Claude GUI 冲突？

**A:** 是的。ACP调用前必须关闭 Claude GUI窗口。

```bash
# 检查是否有GUI进程
ps aux | grep "Claude" | grep -v grep

# 如果有，关闭后再执行
```

### Q2: 任务被中断怎么办？

**A:** 使用 `--no-wait` 后台运行，或使用 sessions_spawn。

```bash
# 后台执行
acpx claude -s task --no-wait "你的任务"

# 恢复中断的hackathon
omc ralphthon --resume
```

### Q3: 内存占用过高？

**A:** 重启 Gateway 清理。

```bash
openclaw gateway restart
```

### Q4: 速率限制怎么办？

**A:** 使用 omc wait 自动处理。

```bash
omc wait --start  # 启动自动恢复守护
```

### Q5: 如何切换模型？

**A:** 使用 cc-model-switch.sh。

```bash
cc-model-switch.sh opus     # Opus 架构/验收
cc-model-switch.sh minimax  # MiniMax 执行开发
```

---

## 附录：关键文件位置

| 文件 | 位置 |
|------|------|
| Claude Code配置 | `~/.claude/settings.json` |
| OMC配置 | `~/.claude/CLAUDE.md` |
| Agents定义 | `~/.claude/agents/*.md` |
| Commands | `~/.claude/commands/` |
| Rules | `~/.claude/rules/` |
| OMC Skills | `~/.claude/skills/omc-reference/` |
| ACP Sessions | `~/.acpx/sessions/` |
| 模型切换脚本 | `~/.openclaw/workspace/scripts/cc-model-switch.sh` |

---

*此文档由雪子助手整理 - 2026-04-10*
