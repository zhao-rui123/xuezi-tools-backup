#!/bin/bash
# 飞书通知脚本 - 使用Kilo广播专员

TITLE="$1"
MESSAGE="$2"
LEVEL="${3:-normal}"

if [ -z "$TITLE" ] || [ -z "$MESSAGE" ]; then
    echo "Usage: $0 <title> <message> [level]"
    exit 1
fi

# 使用Kilo广播专员发送
python3 /Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py \
    --task send \
    --message "[$LEVEL] $TITLE

$MESSAGE" \
    --target group \
    2>/dev/null
