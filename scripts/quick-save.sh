#!/bin/bash
# 快速保存会话快照
# 用法: ss "任务描述"  或  save-session "任务描述"

TASK="${1:-快速保存}"
python3 ~/.openclaw/workspace/scripts/session-snapshot.py save "$TASK"
echo "✅ 已保存: $TASK"
