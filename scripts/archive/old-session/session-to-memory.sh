#!/bin/bash
# 从session提取对话写入每日记忆文件
# 每天8点、16点、23点执行

export HOME="/Users/zhaoruicn"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

WORKSPACE="$HOME/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
SESSIONS_DIR="$HOME/.openclaw/agents/claude/sessions"
LOG_FILE="$WORKSPACE/ops/logs/tasks/session-to-memory.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

log "开始提取session到memory..."
python3 "$WORKSPACE/scripts/session-to-memory.py" 2>&1 | tee -a "$LOG_FILE"
