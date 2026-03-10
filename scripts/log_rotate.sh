#!/bin/bash
# 日志轮转脚本
# 每天执行，清理过期日志

LOG_DIR="/tmp"
WORKSPACE_LOG_DIR="/Users/zhaoruicn/.openclaw/workspace/logs"
RETENTION_DAYS=30

echo "[$(date)] 开始日志轮转..."

# 1. 清理 /tmp 下的日志文件（保留30天）
find $LOG_DIR -name "*.log" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null
echo "  ✅ 清理 /tmp 下 ${RETENTION_DAYS} 天前的日志"

# 2. 清理 workspace/logs 下的日志
if [ -d "$WORKSPACE_LOG_DIR" ]; then
    find $WORKSPACE_LOG_DIR -name "*.log" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null
    echo "  ✅ 清理 workspace/logs 下 ${RETENTION_DAYS} 天前的日志"
fi

# 3. 清理股票通知文件（保留7天）
find $LOG_DIR -name "stock_notification_*.txt" -type f -mtime +7 -delete 2>/dev/null
echo "  ✅ 清理股票通知文件（7天前）"

# 4. 压缩大日志文件（超过10MB）
find $LOG_DIR -name "*.log" -type f -size +10M 2>/dev/null | while read logfile; do
    if [ ! -f "${logfile}.gz" ]; then
        gzip -c "$logfile" > "${logfile}.gz"
        > "$logfile"  # 清空原文件
        echo "  ✅ 压缩大日志: $(basename $logfile)"
    fi
done

# 5. 清理旧压缩文件（保留90天）
find $LOG_DIR -name "*.log.gz" -type f -mtime +90 -delete 2>/dev/null
echo "  ✅ 清理90天前的压缩日志"

# 6. 统计当前日志大小
echo ""
echo "📊 当前日志统计:"
echo "  /tmp 日志总大小: $(du -sh $LOG_DIR 2>/dev/null | cut -f1)"
echo "  日志文件数量: $(find $LOG_DIR -name '*.log' -type f 2>/dev/null | wc -l) 个"

# 发送飞书通知 - 使用广播专员
MESSAGE="📝 日志轮转完成 ($(date '+%Y-%m-%d %H:%M'))

✅ 清理完成:
• ${RETENTION_DAYS}天前日志已清理
• 股票通知文件(7天前)已清理
• 大日志文件已压缩
• 90天前压缩日志已清理

📊 当前状态:
• /tmp 日志总大小: $(du -sh $LOG_DIR 2>/dev/null | cut -f1)
• 日志文件数量: $(find $LOG_DIR -name '*.log' -type f 2>/dev/null | wc -l) 个

---
🤖 广播专员 | $(date '+%H:%M')"

python3 /Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py \
    --task send \
    --message "$MESSAGE" \
    --target group \
    2>/dev/null

echo ""
echo "[$(date)] 日志轮转完成"
