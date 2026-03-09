#!/bin/bash
# 停止任务看板状态追踪器

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/status_tracker.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️ 状态追踪器未在运行"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "🛑 停止状态追踪器 (PID: $PID)..."
    kill "$PID" 2>/dev/null || true
    sleep 1
    
    # 强制终止如果还在运行
    if ps -p "$PID" > /dev/null 2>&1; then
        kill -9 "$PID" 2>/dev/null || true
    fi
    
    rm -f "$PID_FILE"
    echo "✅ 已停止"
else
    echo "⚠️ 进程已不存在"
    rm -f "$PID_FILE"
fi
