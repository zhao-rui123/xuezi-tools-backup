#!/bin/bash
# 停止追踪器

if [ -f /tmp/lobster_tracker.pid ]; then
    PID=$(cat /tmp/lobster_tracker.pid)
    echo "🛑 停止追踪器 (PID: $PID)..."
    kill $PID 2>/dev/null || true
    rm -f /tmp/lobster_tracker.pid
    echo "✅ 已停止"
else
    echo "⚠️ 追踪器未在运行"
fi
