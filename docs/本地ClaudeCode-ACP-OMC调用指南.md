# 本地 Claude Code + ACP + OMC 调用完全指南

> 本文档整合 acpx 调用、OMC 技能、本地工作流
> 更新：2026-04-17（验证 acpx + OMC 可用）

---

## 一、核心工具链

| 工具 | 版本 | 路径 | 用途 |
|------|------|------|------|
| Claude Code | 2.1.104 | `/opt/homebrew/bin/claude` | 主开发工具 |
| acpx | 0.5.3 | `/opt/homebrew/bin/acpx` | ACP 协议客户端，后台任务调度 |
| omc | 4.9.3 | `/opt/homebrew/bin/omc` | oh-my-claude-code 编排层 |

---

## 二、acpx 调用本地 Claude Code（推荐方式）

### 标准流程

```bash
# 1. 创建持久 session（一次性）
acpx claude sessions new --name my-session

# 2. 后台丢任务（--no-wait 模式，不阻塞）
cd ~/.openclaw/workspace
acpx claude -s my-session --no-wait "任务描述"

# 3. 查看状态
acpx claude -s my-session status

# 4. 查看结果
tail ~/.acpx/sessions/<session-id>.stream.ndjson
```

### 常用命令

| 命令 | 说明 |
|------|------|
| `acpx claude sessions new --name <name>` | 创建新 session |
| `acpx claude sessions list` | 列出所有 session |
| `acpx claude sessions close <name>` | 关闭 session |
| `acpx claude -s <name> --no-wait "prompt"` | 后台执行任务 |
| `acpx claude -s <name> status` | 查看 session 状态 |

### 关键要点

1. **必须使用 `--no-wait`**：任务在独立后台进程跑，完全不超时
2. **在 workspace 目录执行**：确保 cwd 正确
3. **模型配置**：通过 `~/.claude/settings.json` 设置

---

## 三、OMC 技能调用（通过 acpx）

### 触发 OMC Skills

```bash
# Autopilot - 全自主执行
cd ~/.openclaw/workspace
acpx claude -s my-session --no-wait "autopilot: 创建一个待办事项管理器"

# Deep Interview - 深度访谈
acpx claude -s my-session --no-wait "deep-interview: 我想开发一个股票分析工具"

# Plan - 战略规划
acpx claude -s my-session --no-wait "plan: 设计一个储能项目管理系统"

# Ralph - 持续循环直到完成
acpx claude -s my-session --no-wait "ralph: 修复所有代码中的 bug"

# Ultrawork - 并行执行
acpx claude -s my-session --no-wait "ultrawork: 并行处理这三个文件"

# Team - 多 Agent 协作
acpx claude -s my-session --no-wait "team 3:executor 并行开发三个模块"
```

### 可用 OMC Skills

| Skill | 触发词 | 功能 |
|-------|--------|------|
| Autopilot | `autopilot:` | 全自主执行 |
| Deep Interview | `deep-interview:` | 苏格拉底式深度访谈 |
| Plan | `plan:` / `ralplan:` | 战略规划、任务拆解 |
| Ralph | `ralph:` | 持续循环直到完成 |
| Ultrawork | `ultrawork:` / `ulw:` | 最大并行化执行 |
| Team | `team N:` | N 个 Agent 协调团队 |
| CCG | `ccg:` | Claude-Codex-Gemini 三模型合成 |

### OMC Agents（18个）

| Agent | 职责 |
|-------|------|
| explore | 代码库快速探索 |
| analyst | 需求分析 |
| planner | 战略规划 |
| architect | 架构设计 |
| debugger | 根因分析 |
| executor | 任务执行 |
| verifier | 完成验证 |
| code-reviewer | 代码审查 |
| security-reviewer | 安全审查 |
| test-engineer | 测试策略 |
| designer | UI/UX 设计 |
| writer | 文档编写 |
| qa-tester | CLI 测试 |
| scientist | 数据分析 |
| tracer | 因果追踪 |
| git-master | Git 管理 |
| code-simplifier | 代码简化 |
| critic | 计划审查 |

---

## 四、模型切换

### 当前配置（MiniMax M2.7）

```json
// ~/.claude/settings.json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.minimaxi.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "sk-cp-xxx",
    "ANTHROPIC_MODEL": "MiniMax-M2.7"
  }
}
```

### 切换到 Opus（架构设计/验收）

```bash
# 使用脚本切换
~/.openclaw/workspace/scripts/cc-model-switch.sh opus

# 或手动编辑 ~/.claude/settings.json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://timesniper.club",
    "ANTHROPIC_AUTH_TOKEN": "sk-OLqePftCUT0kOGggfgGtgeMOE3km0hPXwxUf6FTpFFL7mdsJ",
    "ANTHROPIC_MODEL": "claude-opus-4-6"
  }
}
```

### 切回 MiniMax（执行开发）

```bash
~/.openclaw/workspace/scripts/cc-model-switch.sh minimax
```

---

## 五、完整示例

### 示例 1：开发一个 Python 工具

```bash
# 创建 session
acpx claude sessions new --name py-dev

# 使用 autopilot 全自主开发
cd ~/.openclaw/workspace
acpx claude -s py-dev --no-wait "autopilot: 开发一个 JSON 格式化工具，支持美化输出和压缩"

# 查看状态
acpx claude -s py-dev status

# 查看生成的文件
ls -la ~/.openclaw/workspace/*.py
```

### 示例 2：代码审查

```bash
# 创建 session
acpx claude sessions new --name code-review

# 使用 code-reviewer Agent
cd ~/.openclaw/workspace
acpx claude -s code-review --no-wait "code-review: 审查 storage_calc.py 的代码质量"
```

### 示例 3：多 Agent 并行开发

```bash
# 创建 session
acpx claude sessions new --name team-dev

# 使用 team 模式
cd ~/.openclaw/workspace
acpx claude -s team-dev --no-wait "team 3:executor 并行开发：1)用户模块 2)订单模块 3)支付模块"
```

---

## 六、故障排查

### 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `agent needs reconnect` | session 断开 | 重新创建 session |
| `No acpx session found` | session 不存在 | 检查 session 名称 |
| 任务不执行 | 权限问题 | 添加 `--approve-all` |
| 模型不对 | 配置未生效 | 检查 `~/.claude/settings.json` |

### 诊断命令

```bash
# 检查 Claude Code 状态
claude --version

# 检查 acpx 状态
acpx --version

# 检查 OMC 状态
omc doctor conflicts

# 查看 session 列表
acpx claude sessions list

# 查看 OMC 信息
omc info
```

---

## 七、与韩国 Codex 对比

| 项目 | 本地 Claude Code | 韩国 Codex |
|------|------------------|------------|
| **模型** | MiniMax M2.7 / Opus | GPT-5.4 |
| **调用方式** | `acpx claude` | `acpx codex` |
| **网络** | 直连 | 韩国服务器代理 |
| **OMC** | ✅ 完整支持 | ❌ 未安装 |
| **适用场景** | 日常开发、OMC 工作流 | 复杂编程、英文任务 |

---

## 八、最佳实践

### 1. 任务分配策略

```
本地 Claude Code (MiniMax)
├── 日常开发任务
├── OMC 工作流（autopilot/ralph/team）
├── 中文处理
└── 快速迭代

韩国 Codex (GPT-5.4)
├── 复杂算法设计
├── 大型项目重构
├── 英文编程任务
└── 需要 GPT-5.4 的场景
```

### 2. 模型选择

| 场景 | 推荐模型 |
|------|---------|
| 架构设计 | Opus (via cc-model-switch.sh) |
| 验收审查 | Opus |
| 执行开发 | MiniMax M2.7 |
| OMC 工作流 | MiniMax M2.7 |
| 复杂英文编程 | 韩国 Codex GPT-5.4 |

### 3. 会话管理

- **用完即关**：长时间不用的 session 及时关闭
- **命名规范**：按任务类型命名（`py-dev`, `code-review`, `team-task`）
- **定期清理**：每周检查一次 session 列表

---

## 九、相关文档

- `docs/韩国CC-Codex后台调用指南.md` - 韩国服务器 Codex 调用
- `docs/CC本地干活流程.md` - 本地 CC 协作流程
- `docs/ClaudeCode-调用规范.md` - 调用规范总结
- `docs/claude-acp-usage.md` - ACP 基础用法

---

*本文档由雪子助手维护 - 最后更新：2026-04-17*
