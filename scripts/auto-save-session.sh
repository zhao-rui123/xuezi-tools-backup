#!/bin/bash
# 自动保存当前会话状态
# 可以加入定时任务或关键操作后调用

cd /Users/zhaoruicn/.openclaw/workspace

# 获取当前会话的任务描述（从最近记忆文件提取）
TODAY=$(date '+%Y-%m-%d')
MEMORY_FILE="memory/${TODAY}.md"

if [ -f "$MEMORY_FILE" ]; then
    # 提取第一行非空内容作为任务描述
    TASK=$(grep -v "^$\|^#" "$MEMORY_FILE" | head -1 | cut -c1-50)
else
    TASK="日常对话"
fi

# 保存快照
python3 scripts/session-snapshot.py save "$TASK" >> /tmp/session-snapshot.log 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 会话自动保存完成" >> /tmp/session-snapshot.log