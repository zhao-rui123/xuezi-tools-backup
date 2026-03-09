---
name: session-persistence
description: Session state persistence across model switches. Use when saving work context before switching models or restoring context after a model switch. Ensures continuity of work.
---

# 会话持久化技能

## 问题

切换模型时：
- 当前工作上下文丢失
- 需要重新了解任务背景
- 效率降低

## 解决方案

**脚本**: `~/.openclaw/workspace/scripts/session-state.sh`

### 保存会话状态

```bash
bash ~/.openclaw/workspace/scripts/session-state.sh save
```

保存内容：
- 当前使用的模型
- 工作目录
- Git 变更状态
- 记忆文件数量

### 恢复会话状态

```bash
bash ~/.openclaw/workspace/scripts/session-state.sh restore
```

显示上次会话的上下文信息。

### 清理旧状态

```bash
bash ~/.openclaw/workspace/scripts/session-state.sh cleanup
```

删除7天前的状态文件。

## 模型切换工作流

```bash
# 1. 保存当前状态
bash ~/.openclaw/workspace/scripts/session-state.sh save

# 2. 切换模型
openclaw config set agents.defaults.model.primary "bailian/kimi-k2.5"
openclaw gateway restart

# 3. 恢复上下文（新模型执行）
bash ~/.openclaw/workspace/scripts/session-state.sh restore
```

## 自动化切换脚本

```bash
#!/bin/bash
# smart-model-switch.sh

TARGET_MODEL="$1"

# 保存状态
bash ~/.openclaw/workspace/scripts/session-state.sh save

# 切换模型
openclaw config set agents.defaults.model.primary "$TARGET_MODEL"
openclaw gateway restart

echo "模型已切换到: $TARGET_MODEL"
echo "请等待 Gateway 重启完成..."
sleep 3

# 新会话启动后，手动执行恢复
# bash ~/.openclaw/workspace/scripts/session-state.sh restore
```

## 使用建议

1. **切换前必做**: 保存状态 + 提交 Git
2. **切换后必做**: 读取 MEMORY.md + 知识库索引
3. **复杂任务**: 使用 `/new` 开启新会话，避免上下文混乱

## 状态文件位置

```
~/.openclaw/workspace/.session-states/state_YYYYMMDD_HHMMSS.json
```

---
*创建于: 2026-03-04*
