# Claude Code 并行开发流程

*记录时间：2026-03-29*

---

## 核心能力测试结果

| 功能 | 状态 | 说明 |
|------|------|------|
| sessions_spawn 后台调用 | ✅ 正常 | 子Agent独立运行，5秒完成简单任务 |
| model 参数切换模型 | ✅ 正常 | 可指定 minimax-cn/MiniMax-M2.7 等模型 |
| 子Agent结果自动返回 | ✅ 正常 | 任务完成后自动推送到当前会话 |

---

## 基本用法

### 1. 发起后台任务

```javascript
sessions_spawn({
  task: "任务描述",
  runtime: "subagent",
  label: "任务标签",           // 可追踪的唯一标识
  runTimeoutSeconds: 600,       // 超时时间（秒）
})
```

### 2. 带模型切换的后台任务

```javascript
sessions_spawn({
  task: "任务描述",
  runtime: "subagent",
  model: "minimax-cn/MiniMax-M2.7",  // 指定模型
  label: "任务标签",
  runTimeoutSeconds: 600,
})
```

### 3. 完整参数

```javascript
sessions_spawn({
  task: "任务描述",
  runtime: "subagent",
  model: "minimax-cn/MiniMax-M2.7",   // 模型名称
  label: "claude-code-xxx",           // 任务标签（必须唯一）
  runTimeoutSeconds: 600,              // 超时时间
  mode: "run",                         // "run"=一次性任务，"session"=持久会话
  cleanup: "delete",                   // "delete"=完成后删除，"keep"=保留
})
```

---

## 模型切换说明

| 配置位置 | 切换方式 | 用途 |
|---------|---------|------|
| `sessions_spawn(model:)` | 运行时指定 | 单次任务换模型 |
| `~/.claude/settings.json` | 配置文件 | 切换 Claude Code 默认模型 |

### 切换 Claude Code 默认模型（官方/MiniMax）

```bash
# 切换到 MiniMax 模型（执行用）
cp ~/.claude/settings-minimax.json ~/.claude/settings.json

# 切换回官方模型（架构/验收用）
# 使用 timesniper 或手动还原
```

---

## 工作流程

```
雪子下发任务
    ↓
1️⃣ 确认需求（用户没说"去做吧"就不行动）
    ↓
2️⃣ 任务拆分（每个模块 5-10 分钟）
    ↓
3️⃣ sessions_spawn 启动模块1（后台）
    ↓
4️⃣ 模块1完成 → git commit
    ↓
5️⃣ sessions_spawn 启动模块2（后台）
    ↓
...（以此类推）
    ↓
6️⃣ 每完成一个 → 汇报给雪子
    ↓
⚠️ 遇到问题 → 立即汇报，不憋着
```

---

## ⚠️ 铁律

1. **禁止在 exec 里直接运行 Claude Code**（会被超时杀流程）
2. **必须用 sessions_spawn 后台运行**
3. **每个模块完成后立即 git commit**（防丢进度）
4. **做到哪发到哪，不要等全部完成**
5. **遇到问题立即汇报**

---

## 适用场景

- ✅ 大型Web应用开发（多模块）
- ✅ 需要架构审查的复杂项目
- ✅ 需要并行执行的独立任务

## 不适用场景

- ❌ 简单问答（直接回答）
- ❌ 已有明确步骤的任务（直接执行）
- ❌ 紧急小修小改（快速处理）

---

*此文档由雪子助手维护 - 2026-03-29*
