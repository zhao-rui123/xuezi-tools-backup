# AI Coder

安全的 Python CLI 工具，统一调用本地 Claude Code 和韩国 Codex。

## 功能

- **双平台支持**：本地 Claude (MiniMax/Opus) + 韩国 Codex (GPT-5.4)
- **安全设计**：防命令注入、严格 SSH 验证、输入净化
- **Session 管理**：创建、关闭、状态查询
- **后台模式**：`--no-wait` 不阻塞执行
- **Skills 支持**：OMC/OMX 技能调用
- **工作流模板**：预定义开发流程（自动驾驶、代码审查、调研）
- **自动重试**：失败自动重试
- **健康检查**：`ai-coder doctor` 诊断工具

## 安装

```bash
cd ~/.openclaw/workspace/ai_coder
pip3 install -e .
```

## 使用

```bash
# 本地执行（默认）
python3 -m ai_coder exec "任务" -s session名 --wait

# 韩国执行
python3 -m ai_coder exec "任务" -p kr -s session名 --wait

# 健康检查
python3 -m ai_coder doctor
```

## 工作流模板

AI Coder 内置工作流模板系统，支持预定义的多步骤自动化流程。

### Phase 2 新特性

**并行步骤**：同一工作流中多个 Agent 同时执行，效率提升 3 倍+
```yaml
- name: 并行审查
  parallel: true
  agents:
    - name: 质量审查
      prompt: ...
      agent: code-reviewer
    - name: 安全审查
      prompt: ...
      agent: security-reviewer
    - name: 性能审查
      prompt: ...
      agent: analyst
```

**步骤结果上下文传递**：后续步骤自动使用前序步骤输出
```yaml
- name: 初步扫描
  id: scan
  agent: explore

- name: 质量审查
  prompt: 基于扫描结果：{{scan.output}}
  agent: code-reviewer
```

**执行记录持久化**：每个工作流运行生成唯一 Run ID，可随时查看历史记录
```bash
ai_coder workflow log <run-id>          # 查看日志
ai_coder workflow log <run-id> --follow # 实时跟踪
ai_coder workflow log <run-id> --step 3 # 只看第3步
ai_coder workflow runs                   # 最近运行列表
```

### Phase 3 新特性

**Direct Injection（实时指令注入）**：工作流执行中可随时注入新指令
```bash
# 向运行中的 workflow 注入指令
ai_coder workflow inject <run-id> "新的指令"
ai_coder workflow inject <run-id> "添加单元测试" --step 3

# 查看待处理注入
ai_coder workflow pending <run-id>
```

**CEO Agent（智能任务分解）**：自动分解复杂目标为结构化子任务
```bash
# 自动分解 + 执行
ai_coder ceo run "帮我开发一个用户认证系统"

# 只分解不执行
ai_coder ceo decompose "帮我开发一个用户认证系统"
```

支持的自动分解模式：
- `user-auth`: 用户认证系统（注册/登录/JWT）
- `rest-api`: REST API 开发
- `web-app`: Web 应用开发

### 查看可用模板

```bash
python3 -m ai_coder workflow list
```

输出示例：
```
可用工作流模板：

  Autopilot 自动驾驶开发
    描述：全自主开发流程，自动规划、执行、验证，直到代码整洁交付
    6 步骤 | agent=executor

  Code Review 代码审查（并行版）
    描述：多维度代码审查，质量+安全+性能并行执行，结果自动汇总
    3 步骤 | agent=code-reviewer
```

### 运行工作流（带进度条）

```bash
# 自动驾驶开发
python3 -m ai_coder workflow run autopilot \
  --params '{"task": "构建一个 REST API", "code_path": "./src"}'

# 代码审查（并行执行）
python3 -m ai_coder workflow run review \
  --params '{"code_path": "./src"}'
```

执行时显示进度条：
```
[██░░░░] 1/3：初步扫描
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
...
[███░░] 2/3：并行审查
  ⚡ 并行执行 3 个 Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 并行步骤完成
=== 质量审查 ===
...
=== 安全审查 ===
...
=== 性能审查 ===
...
[██████] 工作流完成！
Run ID: abc12345
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 模板参数

| 模板 | 关键参数 | 说明 |
|------|---------|------|
| `autopilot` | `task` | 要完成的任务描述 |
| `autopilot` | `code_path` | 代码路径（可选） |
| `review` | `code_path` | 代码路径 |
| `review` | `review_scope` | 审查范围（可选，默认全部） |
| `research` | `topic` | 调研主题 |
| `bugfix` | `bug_description` | Bug描述 |
| `bugfix` | `code_path` | 代码路径 |
| `bugfix` | `reproduce_steps` | 复现步骤（可选） |
| `refactor` | `code_path` | 代码路径 |
| `refactor` | `refactor_goal` | 重构目标（可选，默认改进代码质量） |

参数使用 `{{var}}` 或 `{{var|默认值}}` 语法在工作流定义中使用。

### 自定义工作流

在 `ai_coder/workflows/` 目录下创建 `.flow` 文件：

```yaml
name: 我的自定义流程
description: 描述信息
steps:
  - name: 步骤1
    id: step1  # 用于后续步骤引用
    prompt: |
      执行任务 {{task}}，输出结果
    agent: executor
    parallel: false
  - name: 并行步骤
    parallel: true
    agents:
      - name: Agent A
        id: agent_a
        prompt: 基于 {{step1.output}} 执行
        agent: code-reviewer
      - name: Agent B
        id: agent_b
        prompt: 基于 {{step1.output}} 执行
        agent: security-reviewer
  - name: 步骤3
    prompt: |
      综合结果：{{agent_a.output}} + {{agent_b.output}}
    agent: architect
agent: executor
parallel: false
```

## 配置

### 环境变量

```bash
# 韩国服务器（使用 -p kr 时必须）
export AI_CODER_KR_HOST="43.108.18.71"
export AI_CODER_KR_USER="ccuser"
export AI_CODER_KR_SSH_KEY="~/.ssh/id_ed25519"
```

## 命令

| 命令 | 说明 |
|------|------|
| `doctor` | 健康检查 |
| `exec` | 执行单次任务 |
| `session-new NAME` | 创建 session |
| `session-close NAME` | 关闭 session |
| `status -s NAME` | 查询状态 |
| `skills` | 列出 skills |
| `workflow list` | 列出所有工作流模板 |
| `workflow run <name>` | 运行指定工作流 |
| `workflow log <run-id>` | 查看运行日志 |
| `workflow log <run-id> --follow` | 实时跟踪日志 |
| `workflow log <run-id> --step N` | 只看指定步骤 |
| `workflow inject <run-id> <prompt>` | 向运行中的 workflow 注入指令 |
| `workflow pending <run-id>` | 查看待处理注入指令 |
| `workflow runs` | 最近运行列表 |
| `workflow export <name> --file <path>` | 导出工作流到文件 |
| `workflow import <file>` | 从文件导入工作流 |
| `workflow import <url> --url` | 从URL导入工作流 |
| `ceo run <goal>` | CEO Agent 自动分解并执行 |
| `ceo decompose <goal>` | CEO Agent 只分解不执行 |

## 子 Agent 调用

```python
sessions_spawn({
    "task": "cd ~/.openclaw/workspace/ai_coder && python3 -m ai_coder exec '任务' -s SESSION --wait",
    "runtime": "subagent",
    "runTimeoutSeconds": 300
})
```
