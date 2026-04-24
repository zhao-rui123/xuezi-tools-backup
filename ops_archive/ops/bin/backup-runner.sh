#!/usr/bin/env bash
#===============================================================================
# backup-runner.sh - 统一备份入口
#===============================================================================
# 用法: backup-runner.sh [--type full|archive] [--verify-only] [--no-cloud]
#===============================================================================

set -euo pipefail

# 设置基础路径
SCRIPT="${BASH_SOURCE[0]}"
while [ -L "$SCRIPT" ]; do
    SCRIPT="$(readlink "$SCRIPT")"
done
OPS_DIR="$(cd -P "$(dirname "$SCRIPT")/.." && pwd)"
export OPS_DIR

# 加载函数库
source "$OPS_DIR/lib/logger.sh"
source "$OPS_DIR/lib/lock.sh"
source "$OPS_DIR/lib/notifier.sh"
source "$OPS_DIR/config/backup.conf"

# 解析参数
TYPE="full"
VERIFY_ONLY="false"
SKIP_CLOUD="false"

while [ $# -gt 0 ]; do
    case "$1" in
        --type)     TYPE="$2"; shift 2 ;;
        --verify-only) VERIFY_ONLY="true"; shift ;;
        --no-cloud) SKIP_CLOUD="true"; shift ;;
        *)          shift ;;
    esac
done

# 核心变量
TRACE_ID="$(date '+%Y%m%d_%H%M%S')-$(openssl rand -hex 3 2>/dev/null || echo "$$")"
LOCK_FILE="$OPS_DIR/lock/backup.lock"
LOG_FILE="$BACKUP_LOG_DIR/${TRACE_ID}.log"
STATUS_FILE="$BACKUP_STATUS_DIR/${TRACE_ID}.json"
ARCHIVE_NAME="openclaw-backup-${TRACE_ID}.tar.gz"
ARCHIVE_PATH="$BACKUP_LOCAL_DIR/$ARCHIVE_NAME"

# 确保日志目录存在
mkdir -p "$BACKUP_LOG_DIR" "$BACKUP_STATUS_DIR"

#===============================================================
# 日志
#===============================================================
log "=========================================="
log "备份任务开始 | type=$TYPE | trace=$TRACE_ID"
log "=========================================="

#===============================================================
# 前置检查
#===============================================================
preflight_check() {
    log "[检查] 外部存储挂载"
    if [ ! -d "$BACKUP_LOCAL_DIR" ]; then
        log "[检查] ❌ 外部存储未挂载: $BACKUP_LOCAL_DIR"
        return 1
    fi
    log "[检查] ✅ 外部存储已挂载"

    log "[检查] 磁盘空间 (>10%)"
    local available
    available=$(df -k "$BACKUP_LOCAL_DIR" | awk 'NR==2 {print $4}')
    if [ "$available" -lt 1048576 ]; then
        log "[检查] ❌ 磁盘空间不足: ${available}KB < 1GB"
        return 1
    fi
    log "[检查] ✅ 磁盘空间充足: ${available}KB"

    log "[检查] 上一个任务状态"
    if lock_exists "backup"; then
        log "[检查] ❌ 备份任务正在运行中"
        return 1
    fi
    log "[检查] ✅ 无运行中任务"

    return 0
}

#===============================================================
# 保存状态
#===============================================================
save_status() {
    local status="$1"
    local error="${2:-null}"

    cat > "$STATUS_FILE" << EOF
{
  "trace_id": "$TRACE_ID",
  "type": "$TYPE",
  "status": "$status",
  "error": $error,
  "archive_name": "$ARCHIVE_NAME",
  "archive_path": "$ARCHIVE_PATH",
  "backup_dir": "$BACKUP_LOCAL_DIR",
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "cloud_enabled": $([ "$SKIP_CLOUD" = "false" ] && echo "true" || echo "false"),
  "verify_only": $([ "$VERIFY_ONLY" = "true" ] && echo "true" || echo "false"),
  "verify_step1": false,
  "verify_step2": false,
  "verify_step3": false,
  "verify_step4": false,
  "cloud_synced": false
}
EOF
}

#===============================================================
# 主程序
#===============================================================
main() {
    # 初始化状态
    save_status "RUNNING"

    # 前置检查
    if ! preflight_check; then
        save_status "FAILED" "\"preflight_check_failed\""
        notify_backup_failure "$TRACE_ID" "前置检查失败（外部存储未挂载或任务冲突）"
        exit 1
    fi

    # 获取锁
    if ! lock_acquire "backup"; then
        log "❌ 无法获取锁，备份已在运行"
        save_status "FAILED" "\"lock_failed\""
        notify_backup_failure "$TRACE_ID" "无法获取锁，备份已在运行"
        exit 1
    fi

    # 注册退出清理
    trap "lock_release 'backup'" EXIT

    local memory_count=0
    local skills_count=0
    local archive_size="unknown"

    # 执行备份（除非只验证）
    if [ "$VERIFY_ONLY" = "false" ]; then
        log "[步骤1] 执行本地备份..."
        if ! bash "$OPS_DIR/bin/backup-core.sh" \
            --type "$TYPE" \
            --trace "$TRACE_ID" \
            >> "$LOG_FILE" 2>&1; then
            log "❌ backup-core.sh 执行失败"
            save_status "FAILED" "\"backup_core_failed\""
            notify_backup_failure "$TRACE_ID" "backup-core.sh 执行失败"
            exit 1
        fi

        # 从状态文件读取统计
        if [ -f "$BACKUP_STATUS_DIR/${TRACE_ID}.json" ]; then
            memory_count=$(python3 -c "
import json
d=json.load(open('$BACKUP_STATUS_DIR/${TRACE_ID}.json'))
print(d.get('memory_count',0))
" 2>/dev/null || echo "0")
            skills_count=$(python3 -c "
import json
d=json.load(open('$BACKUP_STATUS_DIR/${TRACE_ID}.json'))
print(d.get('skills_count',0))
" 2>/dev/null || echo "0")
        fi

        archive_size=$(du -h "$BACKUP_LOCAL_DIR/latest" 2>/dev/null | cut -f1 || echo "unknown")
    fi

    # 第一重验证（文件存在+大小）
    log "[验证-1] 检查文件存在和大小..."
    ARCHIVE_PATH=$(readlink -f "$BACKUP_LOCAL_DIR/latest")
    if [ ! -f "$ARCHIVE_PATH" ]; then
        log "❌ [验证-1] 失败：备份文件不存在"
        save_status "FAILED" "\"verify_step1_failed\""
        exit 1
    fi
    local size_bytes
    size_bytes=$(stat -f "%z" "$ARCHIVE_PATH" 2>/dev/null || stat -c "%s" "$ARCHIVE_PATH" 2>/dev/null)
    if [ "$size_bytes" -lt "$BACKUP_MIN_SIZE" ]; then
        log "❌ [验证-1] 失败：备份大小不足"
        save_status "FAILED" "\"verify_step1_size_insufficient\""
        exit 1
    fi
    log "✅ [验证-1] 通过"
    save_status "SUCCESS"

    # 第二重验证（tar完整性）
    log "[验证-2] 检查 tar 完整性..."
    if ! tar -tzf "$ARCHIVE_PATH" > /dev/null 2>&1; then
        log "❌ [验证-2] 失败：tar 损坏"
        save_status "FAILED" "\"verify_step2_failed\""
        exit 1
    fi
    log "✅ [验证-2] 通过"

    # 第三重验证（可恢复性）
    log "[验证-3] 检查可恢复性..."
    local test_dir="/tmp/openclaw-recovery-test/${TRACE_ID}"
    mkdir -p "$test_dir"
    if ! tar -xzf "$ARCHIVE_PATH" -C "$test_dir" 2>/dev/null; then
        log "❌ [验证-3] 失败：解压测试失败"
        rm -rf "$test_dir"
        save_status "FAILED" "\"verify_step3_failed\""
        exit 1
    fi
    if [ ! -e "$test_dir/memory-backup" ] || [ ! -e "$test_dir/skills-backup" ]; then
        log "❌ [验证-3] 失败：缺少关键目录"
        rm -rf "$test_dir"
        save_status "FAILED" "\"verify_step3_missing_dirs\""
        exit 1
    fi
    rm -rf "$test_dir"
    log "✅ [验证-3] 通过"

    # 云端同步
    if [ "$SKIP_CLOUD" = "false" ] && [ "$VERIFY_ONLY" = "false" ]; then
        log "[步骤5] 云端同步..."
        if bash "$OPS_DIR/bin/backup-cloud-sync.sh" --trace "$TRACE_ID" >> "$LOG_FILE" 2>&1; then
            log "✅ 云端同步完成"
        else
            log "⚠️ 云端同步失败，但本地备份有效"
        fi

        # 第四重验证（云端）
        log "[验证-4] 检查云端同步..."
        local archive_name
        archive_name=$(basename "$ARCHIVE_PATH")
        local remote_result
        remote_result=$(ssh -i "$BACKUP_CLOUD_SSH_KEY" \
            -o ConnectTimeout=30 \
            "$BACKUP_CLOUD_HOST" \
            "ls -l '$BACKUP_CLOUD_DIR/$archive_name' 2>/dev/null" 2>&1)
        if echo "$remote_result" | grep -q "No such file"; then
            log "⚠️ [验证-4] 云端文件不存在"
        else
            log "✅ [验证-4] 云端同步验证通过"
        fi
    fi

    # 最终状态更新
    save_status "SUCCESS"

    log "=========================================="
    log "✅ 备份任务完成 | Memory:$memory_count | Skills:$skills_count | Size:$archive_size"
    log "=========================================="

    # 发送成功通知（精简）
    notify_backup_success "$TRACE_ID" "$archive_size" "$memory_count" "$skills_count" "☁️已同步"
}

main "$@"
