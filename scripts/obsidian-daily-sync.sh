#!/bin/bash
# Obsidian每日工作日志同步脚本
# 每天23:10执行，通知雪子助手整理工作日志

export HOME="/Users/zhaoruicn"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

MEMORY_DIR="$HOME/.openclaw/workspace/memory"
TODAY_DISPLAY=$(date +%Y.%m.%d)
TODAY_ISO=$(date +%Y-%m-%d)
MEMORY_FILE="$MEMORY_DIR/${TODAY_ISO}.md"
LOG_FILE="$HOME/.openclaw/workspace/ops/logs/tasks/obsidian_sync.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

main() {
    log "开始发送整理通知..."

    if [ ! -f "$MEMORY_FILE" ]; then
        log "今日memory文件不存在: $MEMORY_FILE"
        exit 1
    fi

    # 发飞书私聊通知雪子
    log "发送飞书通知..."
    env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy \
    openclaw message send \
        --channel feishu \
        --target "ou_5a7b7ec0339ffe0c1d5bb6c5bc162579" \
        --message "📝 ${TODAY_DISPLAY} 的memory已归档，快去整理工作日志！" 2>&1

    if [ $? -eq 0 ]; then
        log "飞书通知发送成功"
    else
        log "飞书通知发送失败"
    fi
}

main
