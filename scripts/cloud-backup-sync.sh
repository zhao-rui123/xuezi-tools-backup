#!/bin/bash
# 云端备份同步脚本
# 将本地备份同步到腾讯云服务器，保留最近7天

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

BACKUP_DIR="/Volumes/cu/ocu/full-backups"
REMOTE_DIR="/data/openclaw-backups"
SSH_KEY="$HOME/.ssh/id_ed25519"
REMOTE_HOST="root@106.54.25.161"
LOG_FILE="/tmp/cloud-backup.log"
MAX_DAYS=7

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

# 获取最新备份文件
latest_file=$(readlink -f "$BACKUP_DIR/latest")
archive_name=$(basename "$latest_file")

# 同步备份
log "开始云端同步: $archive_name"
if rsync -avz -e "ssh -i $SSH_KEY -o ConnectTimeout=30" \
    "$latest_file" "$REMOTE_HOST:$REMOTE_DIR/" 2>&1 | tail -3; then
    log "✅ 云端同步成功: $archive_name"
    size=$(du -h "$latest_file" | cut -f1)
    send_notify "☁️ 云端备份同步成功 | $archive_name | $size"
else
    log "❌ 云端同步失败"
    send_notify "⚠️ 云端备份同步失败，请检查"
    exit 1
fi

# 清理远程端过期备份（保留最近7天）
log "清理远程端过期备份（保留最近$MAX_DAYS天）..."
ssh -i "$SSH_KEY" "$REMOTE_HOST" "cd $REMOTE_DIR && ls -1t openclaw-backup-*.tar.gz 2>/dev/null | tail -n +\$((MAX_DAYS+1)) | xargs -r rm -f" 2>/dev/null

# 显示远程端保留的备份
remote_count=$(ssh -i "$SSH_KEY" "$REMOTE_HOST" "ls -1t $REMOTE_DIR/openclaw-backup-*.tar.gz 2>/dev/null | wc -l" 2>/dev/null)
log "远程端当前备份数量: $remote_count"
