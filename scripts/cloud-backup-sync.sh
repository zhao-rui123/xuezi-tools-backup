#!/bin/bash
# 云端备份同步脚本
# 将本地备份同步到腾讯云服务器

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

BACKUP_DIR="/Volumes/cu/ocu/full-backups"
REMOTE_DIR="/data/openclaw-backups"
SSH_KEY="$HOME/.ssh/id_ed25519"
REMOTE_HOST="root@106.54.25.161"
LOG_FILE="/tmp/cloud-backup.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# 发送飞书通知
send_notify() {
    /usr/bin/python3 "$HOME/.openclaw/workspace/agents/kilo/broadcaster.py" \
        --task send --message "$1" 2>/dev/null
}

# 检查本地备份是否存在
if [ ! -f "$BACKUP_DIR/latest" ]; then
    log "❌ 本地备份不存在，跳过云端同步"
    send_notify "⚠️ 云端备份同步失败：本地备份不存在"
    exit 1
fi

# 检查远程目录是否存在
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 "$REMOTE_HOST" "test -d $REMOTE_DIR" 2>/dev/null; then
    log "远程目录不存在，创建中..."
    ssh -i "$SSH_KEY" "$REMOTE_HOST" "mkdir -p $REMOTE_DIR" 2>/dev/null
fi

# 同步备份
log "开始云端同步..."
latest_file=$(readlink -f "$BACKUP_DIR/latest")
archive_name=$(basename "$latest_file")

if rsync -avz --progress -e "ssh -i $SSH_KEY -o ConnectTimeout=30" \
    "$latest_file" "$REMOTE_HOST:$REMOTE_DIR/" 2>&1 | tail -5; then
    log "✅ 云端同步成功: $archive_name"
    size=$(du -h "$latest_file" | cut -f1)
    send_notify "☁️ 云端备份同步成功 | $archive_name | $size"
else
    log "❌ 云端同步失败"
    send_notify "⚠️ 云端备份同步失败，请检查"
    exit 1
fi
