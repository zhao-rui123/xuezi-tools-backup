#!/bin/bash
# 自动保存当前会话状态
# 改进版：同时保存任务描述和最近对话摘要

cd /Users/zhaoruicn/.openclaw/workspace

TODAY=$(date '+%Y-%m-%d')
MEMORY_FILE="memory/${TODAY}.md"

# 1. 从memory文件提取当天任务标题
if [ -f "$MEMORY_FILE" ]; then
    TASK=$(grep "^## " "$MEMORY_FILE" | head -1 | sed 's/^## *//' | cut -c1-80)
    if [ -z "$TASK" ]; then
        TASK=$(grep "^# " "$MEMORY_FILE" | head -1 | sed 's/^# *//' | cut -c1-80)
    fi
    [ -z "$TASK" ] && TASK="日常对话"
else
    TASK="日常对话"
fi

# 2. 尝试从会话历史获取最近的用户请求
# 检查是否有最近的对话记录
RECENT_TASK=""
if [ -f "memory/snapshots/snapshot_${TODAY}_"*".json" ]; then
    # 取最新的时间戳快照
    LATEST=$(ls -t memory/snapshots/snapshot_${TODAY}_*.json 2>/dev/null | head -1)
    if [ -n "$LATEST" ]; then
        # 检查是否有session_history
        HISTORY=$(cat "$LATEST" | grep -o '"current_task":"[^"]*"' | head -1)
        if [ -n "$HISTORY" ]; then
            RECENT_TASK=$(echo "$HISTORY" | sed 's/"current_task":"//;s/"//')
        fi
    fi
fi

# 3. 如果有最近的会话任务，用它覆盖（更准确）
if [ -n "$RECENT_TASK" ] && [ "$RECENT_TASK" != "" ]; then
    TASK="$RECENT_TASK"
fi

# 保存快照
python3 scripts/session-snapshot.py save "$TASK" >> /tmp/session-snapshot.log 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 会话自动保存完成: $TASK" >> /tmp/session-snapshot.log
