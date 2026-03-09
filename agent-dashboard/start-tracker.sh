#!/bin/bash
# 启动任务看板状态追踪器

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/status_tracker.pid"

echo "🦞 启动小龙虾状态追踪器..."

# 检查是否已在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️ 状态追踪器已在运行 (PID: $OLD_PID)"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

# 启动追踪器
cd "$SCRIPT_DIR"
nohup python3 status_tracker.py > /tmp/agent_status.log 2>&1 &
echo $! > "$PID_FILE"

echo "✅ 状态追踪器已启动"
echo "   PID: $(cat $PID_FILE)"
echo "   日志: /tmp/agent_status.log"
echo ""
echo "使用方法:"
echo "  开始任务: python3 -c \"import status_tracker; status_tracker.start_task('任务名称')\""
echo "  完成任务: python3 -c \"import status_tracker; status_tracker.complete_task(1000)\""
