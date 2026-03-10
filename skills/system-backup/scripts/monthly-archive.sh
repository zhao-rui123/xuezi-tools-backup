#!/bin/bash
# OpenClaw 月度归档备份脚本
# 每月1号执行，打包整个 OpenClaw 目录为 tar.gz

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

# 配置
BACKUP_DIR="/Volumes/cu/ocu"
ARCHIVE_DIR="$BACKUP_DIR/archives"
OPENCLAW_DIR="/Users/zhaoruicn/.openclaw"
DATE=$(date +%Y-%m-%d)
ARCHIVE_NAME="openclaw-archive-$DATE.tar.gz"
ARCHIVE_PATH="$ARCHIVE_DIR/$ARCHIVE_NAME"
LOG_FILE="/tmp/backup_archive.log"
KEEP_COUNT=6  # 保留最近6个月（半年）

# 日志函数
log() {
    local msg="$(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

# 发送通知
send_notify() {
    local status=$1
    local size=$2
    local count=$3
    local timestamp=$(date '+%Y-%m-%d %H:%M')
    
    if [ "$status" = "success" ]; then
        MESSAGE="📦 月度归档备份完成 ($timestamp)

文件名: $ARCHIVE_NAME
大小: $size
位置: /Volumes/cu/ocu/archives/
保留: 最近 $count 个归档

包含:
- 完整 OpenClaw 配置
- 所有技能包
- Memory 和 Workspace
- API 密钥和认证信息

---
🤖 广播专员 | $(date '+%H:%M')"
    else
        MESSAGE="❌ 月度归档备份失败 ($timestamp)

请检查日志: /tmp/backup_archive.log

---
🤖 广播专员 | $(date '+%H:%M')"
    fi
    
    # 使用 broadcaster.py 发送
    python3 /Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py \
        --task send \
        --message "$MESSAGE" \
        --target group \
        2>/dev/null
}

# 主程序
log "========== Monthly Archive Backup Started =========="

# 检查磁盘
if [ ! -d "$BACKUP_DIR" ]; then
    log "FATAL: Backup directory not mounted: $BACKUP_DIR"
    send_notify "failed" "-" "-"
    exit 1
fi

# 创建归档目录
mkdir -p "$ARCHIVE_DIR"

# 检查是否已存在今天的归档
if [ -f "$ARCHIVE_PATH" ]; then
    log "INFO: 今天的归档已存在，跳过"
    send_notify "success" "$(du -h $ARCHIVE_PATH | cut -f1)" "$KEEP_COUNT"
    exit 0
fi

log "Creating archive: $ARCHIVE_PATH"

# 创建压缩包（排除大文件和缓存）
tar -czf "$ARCHIVE_PATH" \
    --exclude='completions' \
    --exclude='*.log' \
    --exclude='node_modules' \
    --exclude='.git/objects' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    -C "$HOME" .openclaw/ 2>> "$LOG_FILE"

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$ARCHIVE_PATH" | cut -f1)
    log "SUCCESS: Archive created: $ARCHIVE_PATH ($SIZE)"
    
    # 清理旧归档（保留最近 N 个）
    log "Rotating archives (keeping last $KEEP_COUNT)..."
    ls -t "$ARCHIVE_DIR"/openclaw-archive-*.tar.gz 2>/dev/null | tail -n +$((KEEP_COUNT + 1)) | while read old_archive; do
        log "Removing old archive: $old_archive"
        rm "$old_archive"
    done
    
    REMAINING=$(ls "$ARCHIVE_DIR"/openclaw-archive-*.tar.gz 2>/dev/null | wc -l)
    log "INFO: $REMAINING archives remaining"
    
    send_notify "success" "$SIZE" "$REMAINING"
    exit 0
else
    log "ERROR: Archive creation failed"
    send_notify "failed" "-" "-"
    exit 1
fi
