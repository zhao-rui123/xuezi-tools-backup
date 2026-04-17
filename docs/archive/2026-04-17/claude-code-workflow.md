# Claude Code 三层模型工作流

> 适用于 OpenClaw 多 Agent 开发，其他 AI 模型可参考此流程

## 核心原则

| 任务类型 | 模型 | 说明 |
|---------|------|------|
| **架构设计** | Opus | 系统设计、技术选型、架构决策 |
| **验收审查** | Opus | 质量把关、代码评审、测试验证 |
| **执行开发** | MiniMax | 主力开发干活、调试修复 |

**关键：Opus 只负责架构和验收，其他全部用 MiniMax**

---

## 完整工作流程

```
雪子需求
    ↓
1️⃣ 【架构设计】Opus (Claude Code ACP)
   ├─ 模型切换: cc-model-switch.sh opus
   ├─ 创建 session: acpx claude sessions new --name arch
   ├─ 执行: acpx claude -s arch "架构设计任务" --approve-all
   └─ 输出: 架构文档、模块划分、任务清单
    ↓
2️⃣ 【执行开发】MiniMax (Claude Code ACP)
   ├─ 模型切换: cc-model-switch.sh minimax
   ├─ 创建 session: acpx claude sessions new --name dev
   ├─ 执行: acpx claude -s dev "开发任务" --approve-all
   └─ 输出: 完成的代码
    ↓
3️⃣ 【验收审查】Opus (Claude Code ACP)
   ├─ 模型切换: cc-model-switch.sh opus
   ├─ 创建 session: acpx claude sessions new --name review
   ├─ 执行: acpx claude -s review "验收任务" --approve-all
   └─ 输出: 通过/返工决定
    ↓
4️⃣ 【部署上线】OpenClaw 子 Agent
   └─ 执行部署脚本
```

---

## 快速命令

### 1. 模型切换

```bash
# 切换到 Opus（架构/验收）
~/.openclaw/workspace/scripts/cc-model-switch.sh opus

# 切换到 MiniMax（执行开发）
~/.openclaw/workspace/scripts/cc-model-switch.sh minimax

# 查看当前模型
~/.openclaw/workspace/scripts/cc-model-switch.sh status
```

### 2. 创建 Session

```bash
# 架构设计 session（永久保持）
acpx claude sessions new --name arch

# 开发 session（永久保持）
acpx claude sessions new --name dev

# 验收 session（永久保持）
acpx claude sessions new --name review
```

### 3. 执行任务

```bash
# 架构设计（Opus）
acpx claude -s arch --ttl 0 --timeout 600 "架构设计任务" --approve-all

# 执行开发（MiniMax）
acpx claude -s dev --ttl 0 --timeout 600 "开发任务" --approve-all

# 验收审查（Opus）
acpx claude -s review --ttl 0 --timeout 600 "验收任务" --approve-all
```

### 4. 后台自动驾驶模式（重要！）

使用 `--no-wait` 可以启动后台任务，做完一件事后我可以继续做其他的：

```bash
# 启动后台任务（立即返回，不阻塞）
acpx claude -s my-session --no-wait "用 autopilot 模式，开发一个完整的 xxx 系统"

# 我可以做其他事，acpx 在后台自动运行

# 查看状态
acpx claude -s my-session status

# 查看结果
tail ~/.acpx/sessions/<session-id>.stream.ndjson | grep -o '"text":"[^"]*"' | tail -10
```

**优势：**
| 对比 | 普通调用 | --no-wait 后台调用 |
|------|----------|-------------------|
| 我能否同时做其他事 | ❌ 等待完成 | ✅ 可以 |
| 监控方式 | 被动等待 | 随时查状态 |
| 适用场景 | 需要实时交互 | autopilot 自动驾驶 |

**工作流：**
```
我：启动后台 autopilot
    ↓
acpx：自动驾驶运行
    ↓
我：继续做其他事
    ↓
acpx：跑完
    ↓
我：查 stream.ndjson 结果
```

**示例：**
```bash
# 启动后台开发任务
acpx claude sessions new --name big-project
acpx claude -s big-project --no-wait "用 autopilot 开发储能项目测算工具"

# 我可以继续做其他事...

# 之后查看进度
acpx claude -s big-project status

# 查看结果
tail ~/.acpx/sessions/*.stream.ndjson | grep result
```

---

## OpenClaw 集成

### sessions_spawn 调用

```javascript
// 架构设计 → Opus
sessions_spawn({
  task: "架构设计任务",
  runtime: "acp",
  agentId: "claude",
  runTimeoutSeconds: 600
})

// 执行开发 → MiniMax
sessions_spawn({
  task: "开发任务",
  runtime: "acp",
  agentId: "claude",
  runTimeoutSeconds: 600
})
```

### 快捷脚本调用

```bash
# 一键调用（自动处理模型切换和 session）
~/.openclaw/workspace/scripts/claude-acp.sh arch "架构设计任务"
```

---

## 关键注意事项

### ⚠️ 必须关闭电脑的 Claude GUI
Claude Code 只能单实例运行，acpx 调用前必须先关闭 GUI 版 Claude。

### ⚠️ Session 管理
- 默认 TTL 300秒（5分钟空闲后关闭）
- 长时间任务使用 `--ttl 0` 永久保持
- 不同阶段用不同 session（arch/dev/review）

### ⚠️ 模型配置优先级
- acpx 环境变量会被 `~/.claude/settings.json` 覆盖
- 必须通过 `cc-model-switch.sh` 切换模型配置

---

## 文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| 模型切换脚本 | `~/.openclaw/workspace/scripts/cc-model-switch.sh` | opus/minimax 切换 |
| ACP 调用脚本 | `~/.openclaw/workspace/scripts/claude-acp.sh` | 一键调用 Claude |
| 使用文档 | `~/.openclaw/workspace/docs/claude-acp-usage.md` | ACP 详细用法 |
| 工作流文档 | `~/.openclaw/workspace/docs/claude-code-workflow.md` | 本文件 |
| Claude 配置 | `~/.claude/settings.json` | 模型配置 |
| acpx 配置 | `~/.acpx/config.json` | acpx agent 配置 |

---

## 给其他 AI 模型的参考

如果你是其他 AI 模型，需要调用 Claude Code：

1. **检查 Claude GUI 是否运行**
   ```bash
   pgrep -x "Claude" && echo "请先关闭 Claude GUI"
   ```

2. **切换模型配置**
   ```bash
   ~/.openclaw/workspace/scripts/cc-model-switch.sh opus   # 或 minimax
   ```

3. **调用 Claude Code**
   ```bash
   acpx claude -s <session名> --ttl 0 "任务描述" --approve-all
   ```

4. **处理结果**
   - 读取输出
   - 根据结果决定下一步（继续/切换模型/完成）

---

*最后更新: 2026-04-09*
