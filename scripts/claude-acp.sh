#!/bin/bash
# Claude Code ACP 快速调用脚本
# 用法: ./claude-acp.sh [session名] "任务描述"

set -e

SESSION_NAME="${1:-default}"
shift || true
PROMPT="$*"

if [ -z "$PROMPT" ]; then
    echo "用法: ./claude-acp.sh [session名] '任务描述'"
    echo "示例: ./claude-acp.sh my-session '分析代码结构'"
    exit 1
fi

# 检查电脑上 Claude 是否运行
if pgrep -x "Claude" > /dev/null 2>&1; then
    echo "⚠️  检测到 Claude GUI 正在运行，请先关闭"
    echo "   Claude Code 只能单实例运行"
    exit 1
fi

# 检查 session 是否存在
if ! acpx claude sessions list 2>/dev/null | grep -q "^$SESSION_NAME"; then
    echo "📝 创建新 session: $SESSION_NAME"
    acpx claude sessions new --name "$SESSION_NAME" > /dev/null 2>&1
fi

echo "🚀 启动 Claude ACP (session: $SESSION_NAME)"
echo "⏱️  超时: 10分钟, TTL: 永久"
echo "---"

# 执行命令
acpx claude -s "$SESSION_NAME" --ttl 0 --timeout 600 "$PROMPT" --approve-all
