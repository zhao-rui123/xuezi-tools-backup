#!/bin/bash
# =============================================================================
# 飞书通知脚本 v4 - 使用 memory-suite-v4 通知系统
# 统一通知机制，所有定时任务使用此脚本发送通知
# =============================================================================

set -e

# 参数
TITLE="${1:-系统通知}"
MESSAGE="${2:-}"
LEVEL="${3:-info}"
TARGET="${4:-group}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查参数
if [ -z "$MESSAGE" ]; then
    echo -e "${RED}错误: 消息内容不能为空${NC}"
    echo "用法: $0 <标题> <消息内容> [级别] [目标]"
    echo "  级别: info|warning|error (默认: info)"
    echo "  目标: user|group (默认: group)"
    exit 1
fi

# 使用 v4 notifier.py 发送通知
NOTIFIER_PY="/Users/zhaoruicn/.openclaw/workspace/skills/memory-suite-v4/integration/notifier.py"

if [ -f "$NOTIFIER_PY" ]; then
    # 使用 Python 发送通知
    python3 -c "
import sys
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/skills/memory-suite-v4/integration')
from notifier import Notifier

notifier = Notifier()
result = notifier.send('$TITLE', '''$MESSAGE''', '$LEVEL')
print('✅ 通知已记录' if result else '❌ 通知记录失败')
" 2>/dev/null || true
fi

# 同时发送到飞书群聊 (使用 Kilo 广播专员)
echo -e "${GREEN}发送通知: [$LEVEL] $TITLE${NC}"

# 构建消息内容
FULL_MESSAGE="[$LEVEL] $TITLE

$MESSAGE

⏰ $(date '+%Y-%m-%d %H:%M:%S')"

# 使用 Kilo 广播专员发送
BROADCASTER_PY="/Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py"

if [ -f "$BROADCASTER_PY" ]; then
    python3 "$BROADCASTER_PY" \
        --task send \
        --message "$FULL_MESSAGE" \
        --target "$TARGET" \
        2>/dev/null && echo -e "${GREEN}✅ 飞书通知发送成功${NC}" || echo -e "${YELLOW}⚠️ 飞书通知发送失败${NC}"
else
    echo -e "${YELLOW}⚠️ 广播专员未找到，仅记录到日志${NC}"
fi

# 记录到系统日志
logger -t "feishu-notify-v4" "[$LEVEL] $TITLE: $MESSAGE"

exit 0
