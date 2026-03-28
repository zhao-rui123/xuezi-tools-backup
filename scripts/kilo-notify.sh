#!/bin/bash
#
# 统一的定时任务通知入口
# 所有定时任务都通过这个脚本发送通知
#

TASK_NAME="$1"
STATUS="$2"
DETAILS="${3:-}"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 发送通知的通用函数
send_notification() {
    local task="$1"
    local status="$2"
    local details="$3"
    
    # 使用Kilo Agent发送
    python3 ~/.openclaw/workspace/skills/multi-agent-suite/agents/kilo_notification.py \
        --alert "$task: $status" \
        --alert-type "$([ "$status" = "成功" ] && echo info || echo error)" \
        2>/dev/null
    
    log "通知已发送: $task - $status"
}

# 主程序
case "$TASK_NAME" in
    "daily-backup")
        if [ "$STATUS" = "success" ]; then
            send_notification "每日备份" "成功" "$DETAILS"
        else
            send_notification "每日备份" "失败" "$DETAILS"
        fi
        ;;
        
    "health-check")
        send_notification "健康检查" "$STATUS" "$DETAILS"
        ;;
        
    "system-maintenance")
        send_notification "系统维护" "$STATUS" "$DETAILS"
        ;;
        
    "backup-check")
        send_notification "备份检查" "$STATUS" "$DETAILS"
        ;;
        
    "file-cleanup")
        send_notification "文件清理" "$STATUS" "$DETAILS"
        ;;
        
    "knowledge-sync")
        send_notification "知识同步" "$STATUS" "$DETAILS"
        ;;
        
    "evolution-report")
        send_notification "进化报告" "$STATUS" "$DETAILS"
        ;;
        
    *)
        log "未知的任务类型: $TASK_NAME"
        send_notification "$TASK_NAME" "$STATUS" "$DETAILS"
        ;;
esac
