#!/bin/bash

# 文件清理脚本
# 按策略清理临时文件、旧报告、缓存等

WORKSPACE="$HOME/.openclaw/workspace"
LOG_FILE="/tmp/file-cleanup.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') - 文件清理开始" >> "$LOG_FILE"

# 1. 清理14天前的截图
echo "[1/5] 清理旧截图..." >> "$LOG_FILE"
if [ -d "$WORKSPACE/tmp/screenshots" ]; then
    count=$(find "$WORKSPACE/tmp/screenshots" -name "*.png" -mtime +14 | wc -l)
    find "$WORKSPACE/tmp/screenshots" -name "*.png" -mtime +14 -delete
    echo "  已删除 $count 个旧截图" >> "$LOG_FILE"
fi

# 2. 清理14天前的下载文件
echo "[2/5] 清理旧下载文件..." >> "$LOG_FILE"
if [ -d "$WORKSPACE/tmp/downloads" ]; then
    count=$(find "$WORKSPACE/tmp/downloads" -type f -mtime +14 | wc -l)
    find "$WORKSPACE/tmp/downloads" -type f -mtime +14 -delete
    echo "  已删除 $count 个旧下载文件" >> "$LOG_FILE"
fi

# 3. 清理60天前的报告
echo "[3/5] 清理旧报告..." >> "$LOG_FILE"
if [ -d "$WORKSPACE/reports" ]; then
    count=$(find "$WORKSPACE/reports" -type f -mtime +60 | wc -l)
    find "$WORKSPACE/reports" -type f -mtime +60 -delete
    echo "  已删除 $count 个旧报告" >> "$LOG_FILE"
fi

# 4. 清理60天前的日志备份
echo "[4/5] 清理旧日志备份..." >> "$LOG_FILE"
if [ -d "$WORKSPACE/tmp/logs" ]; then
    count=$(find "$WORKSPACE/tmp/logs" -name "*.log" -mtime +60 | wc -l)
    find "$WORKSPACE/tmp/logs" -name "*.log" -mtime +60 -delete
    echo "  已删除 $count 个旧日志" >> "$LOG_FILE"
fi

# 5. 清理空目录
echo "[5/5] 清理空目录..." >> "$LOG_FILE"
find "$WORKSPACE/tmp" -type d -empty -delete 2>/dev/null

# 生成清理摘要
SUMMARY=$(cat <<EOF
$(date '+%Y-%m-%d %H:%M:%S') - 文件清理摘要:
$(grep "已删除" "$LOG_FILE" | tail -4)
EOF
)

echo "$(date '+%Y-%m-%d %H:%M:%S') - 文件清理完成" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 发送飞书通知 - 使用广播专员
MESSAGE="🧹 文件清理完成 ($(date '+%Y-%m-%d %H:%M'))

✅ 清理项目:
• 14天前截图
• 14天前下载文件  
• 60天前报告
• 60天前日志备份
• 空目录

$(grep "已删除" "$LOG_FILE" | tail -4)

---
🤖 广播专员 | $(date '+%H:%M')"

python3 /Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py \
    --task send \
    --message "$MESSAGE" \
    --target group \
    2>/dev/null

echo "✅ 清理通知已发送" >> "$LOG_FILE"
