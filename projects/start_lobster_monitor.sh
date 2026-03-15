#!/bin/bash
# 启动小龙虾之家监控

echo "🦞 启动小龙虾之家自动更新..."

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要安装Python3"
    exit 1
fi

# 启动后台进程
nohup python3 /Users/zhaoruicn/.openclaw/workspace/projects/lobster_auto_update.py > /tmp/lobster_monitor.log 2>&1 &

# 保存PID
echo $! > /tmp/lobster_monitor.pid

echo "✅ 自动更新已启动！"
echo "PID: $(cat /tmp/lobster_monitor.pid)"
echo "日志: tail -f /tmp/lobster_monitor.log"
echo ""
echo "每10分钟自动同步数据到服务器"
