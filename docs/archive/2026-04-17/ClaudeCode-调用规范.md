# Claude Code 优化调用规范

*整理于 2026-04-04*

---

## 一、调用方式对比

| 方式 | 命令 | 超时 | 适用场景 |
|------|------|------|----------|
| **sessions_spawn** | sessions_spawn(task, runtime="subagent") | 受限制 | 简单任务、快速验证 |
| **openclaw cron** | openclaw cron add --message "..." | 持久化 | 复杂任务、需要深度思考 |
| **exec直接调** | claude --print --dangerously-skip-permissions "..." | 易被杀 | 快速测试 |

---

## 二、场景选择决策树

```
收到任务
    │
    ├─ 是否复杂？（多文件/新领域/需要深度思考）
    │   ├─ YES → openclaw cron 持久化
    │   └─ NO → sessions_spawn 直接调
    │
    └─ 是否架构设计/验收审查？
        ├─ YES → 切换 Opus 模型
        └─ NO → MiniMax M2.7
```

---

## 三、模型使用规则

| 场景 | 模型 | 说明 |
|------|------|------|
| 日常对话/调度 | MiniMax-M2.7 | 省钱、快速 |
| 架构设计/验收审查 | Opus | 深度思考、质量把关 |
| Claude Code执行 | MiniMax-M2.7 | 主力开发 |
| 深度思考任务 | CC + --thinking | Claude Code自带思考 |

---

## 四、openclaw cron 持久化模板

### 1. 复杂开发任务
```bash
openclaw cron add \
  --name "cc-dev-task" \
  --description "Claude Code复杂开发任务" \
  --session isolated \
  --timeout-seconds 3600 \
  --message "用Claude Code执行：<任务描述>"
```

### 2. 多步骤开发
```bash
openclaw cron add \
  --name "cc-multi-step" \
  --session isolated \
  --message "使用 team-exec 工作流：<需求描述>"
```

### 3. 定时任务（需要CC参与的）
```bash
openclaw cron add \
  --name "cc-weekly-task" \
  --cron "0 9 * * 0" \
  --tz "Asia/Shanghai" \
  --message "用Claude Code执行：<每周任务>"
```

---

## 五、Claude Code 调用方式

### 1. 快速测试（非交互）
```bash
claude --print --dangerously-skip-permissions "<命令>"
```

### 2. 深度思考（带思考模式）
```bash
claude --print --thinking=on --dangerously-skip-permissions "<任务>"
```

### 3. 持久化会话（后台运行）
```javascript
sessions_spawn({
  task: "任务描述",
  runtime: "subagent",
  runTimeoutSeconds: 600
})
```

### 4. OMC Agents调用
```bash
claude --print --dangerously-skip-permissions "oh-my-claude:team-exec <任务>"
```

---

## 六、oh-my-claude 能力清单

### Agents（15+）
- explore - 代码探索
- planner - 任务规划
- architect - 架构设计
- debugger - 调试
- executor - 执行
- verifier - 验证
- code-reviewer - 代码审查

### Team Pipeline
- team-plan → team-prd → team-exec → team-verify → team-fix

### Skills（20+）
- autopilot - 自动驾驶
- ralph - 快色任务
- ultrawork - 超工作
- ccg - 代码生成
- ultraqa - 质量保证
- deep-interview - 深度访谈

### 模型路由
- haiku - 快速任务
- sonnet - 标准任务
- opus - 深度任务

---

## 七、最佳实践

### 1. 任务拆分原则
- 简单任务（<5分钟）：sessions_spawn
- 复杂任务（需要多步骤）：openclaw cron
- 超大任务：拆分成多个cron子任务

### 2. 主动汇报
- 每完成一个阶段：向雪子汇报
- 遇到问题：立即汇报
- 完成后：推送结果

### 3. 错误处理
- 3次重试失败 → 升级处理
- 阻塞5分钟以上 → 升级处理
- 不确定时：先问雪子

### 4. 验证清单
- [ ] lsp_diagnostics
- [ ] 构建测试
- [ ] 功能验证
- [ ] 提交代码

---

## 八、示例工作流

### 场景：复杂储能项目开发

```
1. 雪子：有个储能项目想法...
   ↓
2. 我：需求确认 → 拆分模块
   ↓
3. openclaw cron + Opus → 架构设计
   ↓
4. openclaw cron + CC(MiniMax) → 执行开发
   ↓
5. openclaw cron + Opus → 验收审查
   ↓
6. 我 → 部署上线
   ↓
7. 推送结果给雪子
```

---

*此文档由雪子助手维护 - 最后更新：2026-04-04*
