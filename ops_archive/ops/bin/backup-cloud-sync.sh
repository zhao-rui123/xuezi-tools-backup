#!/usr/bin/env bash
#===============================================================================
# backup-cloud-sync.sh - 云端备份同步
#===============================================================================
# 改造自 cloud-backup-sync.sh，集成到 ops 架构
#===============================================================================

set -euo pipefail

SCRIPT="${BASH_SOURCE[0]}"
while [ -L "$SCRIPT" ]; do
    SCRIPT="$(readlink "$SCRIPT")"
done
OPS_DIR="$(cd -P "$(dirname "$SCRIPT")/.." && pwd)"
export OPS_DIR

source "$OPS_DIR/lib/logger.sh"
source "$OPS_DIR/config/backup.conf"

# 参数解析
TRACE_ID="${TRACE_ID:-$(date '+%Y%m%d_%H%M%S')-unknown}"
LOG_FILE="$BACKUP_LOG_DIR/${TRACE_ID}-cloud.log"

# 日志函数
clog() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [cloud-sync] $1" | tee -a "$LOG_FILE"
}

#===============================================================
# 检查前置条件
#===============================================================
check_prerequisites() {
    clog "检查前置条件..."

    # 检查本地备份
    if [ ! -f "$BACKUP_LOCAL_DIR/latest" ]; then
        clog "❌ 本地备份不存在，跳过云端同步"
        return 1
    fi

    # 检查 SSH 密钥
    if [ ! -f "$BACKUP_CLOUD_SSH_KEY" ]; then
        clog "❌ SSH 密钥不存在: $BACKUP_CLOUD_SSH_KEY"
        return 1
    fi

    # 检查远程目录
    if ! ssh -i "$BACKUP_CLOUD_SSH_KEY" \
        -o ConnectTimeout=30 \
        -o StrictHostKeyChecking=no \
        "$BACKUP_CLOUD_HOST" \
        "test -d '$BACKUP_CLOUD_DIR'" 2>/dev/null; then
        clog "❌ 远程目录不存在: $BACKUP_CLOUD_DIR"
        return 1
    fi

    clog "✅ 前置检查通过"
    return 0
}

#===============================================================
# 执行云端同步
#===============================================================
do_sync() {
    local latest_file
    latest_file=$(readlink -f "$BACKUP_LOCAL_DIR/latest")
    local archive_name
    archive_name=$(basename "$latest_file")

    clog "开始云端同步: $archive_name..."

    # 执行 rsync
    if rsync -avz \
        -e "ssh -i $BACKUP_CLOUD_SSH_KEY -o ConnectTimeout=30 -o StrictHostKeyChecking=no" \
        --timeout=120 \
        "$latest_file" \
        "$BACKUP_CLOUD_HOST:$BACKUP_CLOUD_DIR/" 2>&1 | tail -5 | tee -a "$LOG_FILE"; then

        clog "✅ 云端同步成功: $archive_name"
        return 0
    else
        clog "❌ 云端同步失败"
        return 1
    fi
}

#===============================================================
# 清理远程旧备份
#===============================================================
cleanup_remote() {
    clog "清理远程过期备份（保留 ${BACKUP_CLOUD_RETENTION_DAYS} 天）..."

    local keep_num=$((BACKUP_CLOUD_RETENTION_DAYS + 1))
    ssh -i "$BACKUP_CLOUD_SSH_KEY" \
        -o ConnectTimeout=30 \
        -o StrictHostKeyChecking=no \
        "$BACKUP_CLOUD_HOST" \
        "cd '$BACKUP_CLOUD_DIR' && ls -1t openclaw-backup-*.tar.gz 2>/dev/null | tail -n +$keep_num | xargs -r rm -f" 2>/dev/null

    local remote_count
    remote_count=$(ssh -i "$BACKUP_CLOUD_SSH_KEY" \
        -o ConnectTimeout=30 \
        "$BACKUP_CLOUD_HOST" \
        "ls -1t '$BACKUP_CLOUD_DIR'/openclaw-backup-*.tar.gz 2>/dev/null | wc -l" 2>/dev/null)

    clog "远程端当前备份数量: $remote_count"
}

#===============================================================
# 发送通知
#===============================================================
send_notification() {
    local status="$1"
    local size="$2"
    local archive_name="$3"

    if [ "$status" = "success" ]; then
        clog "发送成功通知"
    else
        clog "发送失败通知"
    fi
}

#===============================================================
# 更新状态文件
#===============================================================
update_status() {
    local status="$1"
    local error="${2:-}"

    local status_file="$BACKUP_STATUS_DIR/${TRACE_ID}.json"
    if [ -f "$status_file" ]; then
        # 使用 python 更新 JSON
        python3 << PYEOF
import json, sys
try:
    with open('$status_file', 'r') as f:
        d = json.load(f)
    d['cloud_status'] = '$status'
    d['cloud_synced'] = ${status}success
    if '$error':
        d['cloud_error'] = '$error'
    with open('$status_file', 'w') as f:
        json.dump(d, f, indent=2)
except Exception as e:
    print(f'Status update error: {e}', file=sys.stderr)
PYEOF
    fi
}

#===============================================================
# 主程序
#===============================================================
main() {
    clog "========== 云端同步开始 | trace=$TRACE_ID =========="

    if ! check_prerequisites; then
        update_status "failed" "prerequisites_failed"
        exit 1
    fi

    local latest_file
    latest_file=$(readlink -f "$BACKUP_LOCAL_DIR/latest")
    local archive_name
    archive_name=$(basename "$latest_file")

    if ! do_sync; then
        update_status "failed" "sync_failed"
        send_notification "failure" "unknown" "$archive_name"
        exit 1
    fi

    local size
    size=$(du -h "$latest_file" | cut -f1)

    cleanup_remote
    update_status "success"
    send_notification "success" "$size" "$archive_name"

    clog "========== 云端同步完成 =========="
    exit 0
}

main "$@"
