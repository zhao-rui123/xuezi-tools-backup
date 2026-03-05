---
name: context-management
description: Session context and token management. Use when managing long conversations, optimizing token usage, or handling context window limits. Covers compaction settings and best practices for efficient context usage.
---

# 上下文管理技能

## 当前配置

**压缩模式**: `safeguard`  
**作用**: 自动在必要时压缩会话历史，保留重要信息

## 配置位置

```bash
# 查看当前配置
openclaw config get agents.defaults.compaction

# 输出: {"mode": "safeguard"}
```

## 压缩模式说明

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `off` | 不压缩 | 短会话，不需要 |
| `safeguard` | 智能压缩 | ✅ 推荐，平衡性能和成本 |
| `aggressive` | 积极压缩 | 超长会话，节省成本 |

## 当前状态检查

### 检查会话压缩情况
```bash
# 查看会话统计
openclaw status

# 关注字段:
# - Tokens: 78k/262k (30%) · 🗄️ 708% cached
# - compactionCount: 0 (压缩次数)
```

### 解释
- **78k/262k**: 已使用 78k tokens，上限 262k
- **30%**: 使用率
- **708% cached**: 缓存命中率（高表示重复内容多）
- **compactionCount**: 已执行压缩次数

## 优化建议

### 1. 长会话管理
当会话超过 100k tokens 时：
- 考虑开启新会话 (`/new`)
- 或将当前结果保存到文件

### 2. 减少上下文消耗
- 使用 `/compact` 手动压缩
- 避免重复发送大段内容
- 将大内容保存为文件，发送文件路径

### 3. 监控 token 使用
```bash
# 定期查看状态
openclaw status | grep -A2 "Tokens"
```

## 手动压缩

```bash
# 立即压缩当前会话
/compact

# 或
openclaw session compact
```

## 最佳实践

1. **长任务分段**: 复杂任务拆分为多个会话
2. **及时保存**: 重要结果立即保存到文件
3. **使用知识库**: 将常用信息放入知识库，减少上下文携带
4. **定期 /new**: 每天或每任务结束后开启新会话

## 成本控制

当前模型成本：
| 模型 | Input | Output | Cache Read |
|------|-------|--------|-----------|
| kimi-for-coding | 免费 | 免费 | 免费 |

**注意**: 虽然当前免费，但良好的上下文管理习惯有助于：
- 提高响应速度
- 减少错误率
- 为未来付费模型做准备

---
*创建于: 2026-03-04*  
*当前模式: safeguard*
