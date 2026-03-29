#!/bin/bash
# 备份脚本 - 带重试机制
# 如果首次备份失败，30分钟后重试一次

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

BACKUP_SCRIPT="/Users/zhaoruicn/.openclaw/workspace/skills/system-backup/scripts/daily-backup-v2.sh"
LOG_FILE="/tmp/backup_cron.log"
MAX_RETRIES=1
RETRY_DELAY=1800  # 30分钟

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 执行备份
run_backup() {
    log "开始执行备份..."
    bash "$BACKUP_SCRIPT" >> "$LOG_FILE" 2>&1
    return $?
}

# 验证备份
verify_backup() {
    local latest="/Volumes/cu/ocu/full-backups/latest"
    local today=$(date +%Y%m%d)
    
    if [ -L "$latest" ] && [ -f "$latest" ]; then
        local file_date=$(stat -f "%Sm" -t "%Y%m%d" "$latest" 2>/dev/null || stat -c "%y" "$latest" 2>/dev/null | cut -d' ' -f1 | tr -d '-')
        if [ "$file_date" = "$today" ]; then
            local size_bytes=$(stat -f "%z" "$latest" 2>/dev/null || stat -c "%s" "$latest" 2>/dev/null)
            [ "$size_bytes" -gt 102400 ]
            return $?
        fi
    fi
    return 1
}

# 主逻辑
retry=0
while [ $retry -le $MAX_RETRIES ]; do
    if run_backup; then
        if verify_backup; then
            log "✅ 备份成功"
            exit 0
        else
            log "⚠️ 备份脚本运行但验证失败，准备重试..."
        fi
    else
        log "❌ 备份脚本执行失败，准备重试..."
    fi
    
    if [ $retry -lt $MAX_RETRIES ]; then
        log "等待 ${RETRY_DELAY}秒 后重试... (第$((retry+1))次尝试)"
        sleep $RETRY_DELAY
    fi
    retry=$((retry+1))
done

log "❌ 备份失败，已达到最大重试次数"
exit 1
