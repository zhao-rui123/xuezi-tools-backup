#!/bin/bash
# 启动追踪器

cd "$(dirname "$0")"
echo "🏠 启动小龙虾房子追踪器 v2.0..."

# 检查是否已在运行
if pgrep -f "tracker.py" > /dev/null; then
    echo "⚠️ 追踪器已在运行"
    exit 0
fi

# 启动
nohup python3 tracker.py > /tmp/lobster_tracker.log 2>&1 &
echo $! > /tmp/lobster_tracker.pid

echo "✅ 追踪器已启动"
echo "   PID: $(cat /tmp/lobster_tracker.pid)"
echo "   日志: /tmp/lobster_tracker.log"
