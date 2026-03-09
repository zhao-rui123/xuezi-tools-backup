# 记忆系统迁移记录

## 迁移时间
2026-03-08

## 迁移原因
将分散的多个记忆技能包整合为统一的记忆系统，简化使用和维护。

## 迁移内容

### 1. 定时任务更新

**旧任务:**
```bash
0 2 1 * * /Users/zhaoruicn/.openclaw/workspace/skills/memory-processor/memory_processor.py >> /tmp/memory-processor.log 2>&1
```

**新任务:**
```bash
0 2 1 * * /Users/zhaoruicn/.openclaw/workspace/skills/unified-memory/bin/ums analyze monthly >> /tmp/memory-processor.log 2>&1
```

### 2. 归档的旧技能包

| 技能包 | 状态 | 说明 |
|--------|------|------|
| memory-processor | 已归档 | 功能整合到 ums analyze |
| enhanced-memory | 已归档 | 功能整合到 ums recall |
| session-persistence | 已归档 | 功能整合到 ums session |
| context-management | 已归档 | 功能内置到 unified-memory |

**归档位置:** `~/.openclaw/workspace/skills/archived/`

### 3. 保留的数据

以下数据文件继续保留，不受影响：
- `memory/` - 每日记忆文件
- `memory/summary/` - 月度摘要
- `memory/permanent/` - 永久记忆
- `memory/index/` - 关键词和主题索引
- `.memory/enhanced/memories.json` - 增强记忆数据

## 新的使用方式

### 统一命令: `ums`

```bash
# 查看系统状态
ums status

# 每日记忆
ums daily save "内容"

# 月度分析
ums analyze monthly

# 增强记忆（主动存储）
ums recall store "内容" --importance 0.8

# 搜索记忆
ums recall search "关键词"

# 会话持久
ums session save
ums session restore
```

### 自动识别存储

在对话中自动识别并存储：
- "我喜欢..." → 自动存储为 preference
- "我决定..." → 自动存储为 decision
- "我叫..." → 自动存储为 identity
- "股票代码..." → 自动存储为 finance
- 等等

## 回滚方案

如需要恢复旧技能包：
```bash
# 从归档恢复
mv ~/.openclaw/workspace/skills/archived/memory-processor \
   ~/.openclaw/workspace/skills/

# 恢复定时任务
crontab -l | sed 's|ums analyze monthly|memory-processor/memory_processor.py|' | crontab -
```

## 验证状态

迁移后系统状态：
```
🧠 统一记忆系统
==================================================
📅 每日记忆: 22个文件
📊 智能分析: 1个月度摘要
💾 增强记忆: 5条记忆
🔄 会话持久: 就绪
==================================================
```

## 下次维护

- 每月1日自动执行月度分析
- 数据自动备份（system-backup）
- 如有问题，参考归档目录中的旧技能包

---
*迁移完成时间: 2026-03-08*
