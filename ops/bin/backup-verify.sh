#!/usr/bin/env bash
#===============================================================================
# backup-verify.sh - 四重验证模块
#===============================================================================
# 用法: backup-verify.sh --trace <trace_id> [--step 1|2|3|4]
#   --step  指定只运行特定验证步骤（默认全部）
#   --trace trace_id（必需）
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
TRACE_ID=""
STEP="all"

while [ $# -gt 0 ]; do
    case "$1" in
        --trace) TRACE_ID="$2"; shift 2 ;;
        --step)  STEP="$2"; shift 2 ;;
        *)       shift ;;
    esac
done

if [ -z "$TRACE_ID" ]; then
    echo "ERROR: --trace 是必需参数"
    exit 1
fi

# 路径
ARCHIVE_PATH=""
VERIFY_LOG="$BACKUP_LOG_DIR/${TRACE_ID}-verify.log"
STATUS_FILE="$BACKUP_STATUS_DIR/${TRACE_ID}.json"

# 验证结果
VERIFY_STEP1=false
VERIFY_STEP2=false
VERIFY_STEP3=false
VERIFY_STEP4=false

#===============================================================
# 日志
#===============================================================
_vlog() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [verify] $1" | tee -a "$VERIFY_LOG"
}

#===============================================================
# 加载状态文件
#===============================================================
load_status() {
    if [ -f "$STATUS_FILE" ]; then
        ARCHIVE_PATH=$(python3 -c "
import json, sys
d=json.load(open('$STATUS_FILE'))
print(d.get('archive_path',''))
" 2>/dev/null || echo "")
    fi
    if [ -z "$ARCHIVE_PATH" ]; then
        # 从 latest 符号链接获取
        ARCHIVE_PATH="/Volumes/cu/ocu/full-backups/latest"
        if [ -L "$ARCHIVE_PATH" ]; then
            ARCHIVE_PATH=$(readlink -f "$ARCHIVE_PATH")
        fi
    fi
}

#===============================================================
# 第一重验证：文件存在 + 大小有效
#===============================================================
verify_step1() {
    _vlog "[验证-1] 检查文件存在和大小..."
    load_status

    if [ ! -f "$ARCHIVE_PATH" ]; then
        _vlog "❌ [验证-1] 失败：备份文件不存在: $ARCHIVE_PATH"
        return 1
    fi

    local size_bytes
    size_bytes=$(stat -f "%z" "$ARCHIVE_PATH" 2>/dev/null || stat -c "%s" "$ARCHIVE_PATH" 2>/dev/null)
    local size_kb=$((size_bytes / 1024))

    if [ "$size_bytes" -lt "$BACKUP_MIN_SIZE" ]; then
        _vlog "❌ [验证-1] 失败：备份大小 ${size_kb}KB < 最小要求 ${BACKUP_MIN_SIZE}KB"
        return 1
    fi

    local size_human
    size_human=$(du -h "$ARCHIVE_PATH" | cut -f1)
    _vlog "✅ [验证-1] 通过：文件存在，大小 ${size_human}"
    VERIFY_STEP1=true
    return 0
}

#===============================================================
# 第二重验证：tar 完整性
#===============================================================
verify_step2() {
    _vlog "[验证-2] 检查 tar 压缩完整性..."
    load_status

    if ! tar -tzf "$ARCHIVE_PATH" > /dev/null 2>&1; then
        _vlog "❌ [验证-2] 失败：tar 压缩包损坏或格式错误"
        return 1
    fi

    local file_count
    file_count=$(tar -tzf "$ARCHIVE_PATH" 2>/dev/null | wc -l | tr -d ' ')
    _vlog "✅ [验证-2] 通过：tar 完整，包含 $file_count 个文件"
    VERIFY_STEP2=true
    return 0
}

#===============================================================
# 第三重验证：可恢复性测试
#===============================================================
verify_step3() {
    _vlog "[验证-3] 检查可恢复性（解压测试）..."
    load_status

    local test_dir="$VERIFY_RECOVERY_TEST_DIR/${TRACE_ID}"
    mkdir -p "$test_dir"

    # 解压到临时目录
    if ! tar -xzf "$ARCHIVE_PATH" -C "$test_dir" 2>/dev/null; then
        _vlog "❌ [验证-3] 失败：解压失败"
        rm -rf "$test_dir"
        return 1
    fi

    # 检查关键文件存在
    local key_files=(
        "memory-backup"
        "skills-backup"
    )
    local missing=false
    for key in "${key_files[@]}"; do
        if [ ! -e "$test_dir/$key" ]; then
            _vlog "❌ [验证-3] 失败：缺少关键目录 $key"
            missing=true
        fi
    done

    if [ "$missing" = true ]; then
        rm -rf "$test_dir"
        return 1
    fi

    # 检查文件数量
    local recovered_count
    recovered_count=$(find "$test_dir" -type f 2>/dev/null | wc -l | tr -d ' ')
    _vlog "✅ [验证-3] 通过：可恢复，包含 $recovered_count 个文件"

    # 清理测试目录
    rm -rf "$test_dir"
    VERIFY_STEP3=true
    return 0
}

#===============================================================
# 第四重验证：云端文件存在和大小匹配
#===============================================================
verify_step4() {
    _vlog "[验证-4] 检查云端备份同步状态..."
    load_status

    if [ "$BACKUP_CLOUD_ENABLED" != "true" ]; then
        _vlog "⚠️ [验证-4] 跳过：云端同步未启用"
        VERIFY_STEP4=true
        return 0
    fi

    local local_size
    local_size=$(stat -f "%z" "$ARCHIVE_PATH" 2>/dev/null || stat -c "%s" "$ARCHIVE_PATH" 2>/dev/null)
    local archive_name
    archive_name=$(basename "$ARCHIVE_PATH")

    # 检查远程文件
    local remote_result
    remote_result=$(ssh -i "$BACKUP_CLOUD_SSH_KEY" \
        -o ConnectTimeout=30 \
        -o StrictHostKeyChecking=no \
        "$BACKUP_CLOUD_HOST" \
        "ls -l '$BACKUP_CLOUD_DIR/$archive_name' 2>/dev/null" 2>&1)

    if echo "$remote_result" | grep -q "No such file"; then
        _vlog "❌ [验证-4] 失败：云端文件不存在: $archive_name"
        return 1
    fi

    # 提取远程文件大小
    local remote_size
    remote_size=$(echo "$remote_result" | awk '{print $5}' | head -1)
    if [ -z "$remote_size" ]; then
        _vlog "⚠️ [验证-4] 警告：无法获取云端文件大小"
        VERIFY_STEP4=true
        return 0
    fi

    if [ "$local_size" != "$remote_size" ]; then
        _vlog "❌ [验证-4] 失败：大小不匹配 本地=$local_size 云端=$remote_size"
        return 1
    fi

    local size_human
    size_human=$(du -h "$ARCHIVE_PATH" | cut -f1)
    _vlog "✅ [验证-4] 通过：云端同步成功 (${size_human})"
    VERIFY_STEP4=true
    return 0
}

#===============================================================
# 更新状态文件
#===============================================================
update_status() {
    local step_name="$1"
    local status="$2"
    local error="${3:-}"

    if [ -f "$STATUS_FILE" ]; then
        # 使用 python 更新 JSON
        python3 -c "
import json, sys
try:
    with open('$STATUS_FILE', 'r') as f:
        d = json.load(f)
    d['verify_$step_name'] = $status
    if '$error':
        d['verify_${step_name}_error'] = '$error'
    with open('$STATUS_FILE', 'w') as f:
        json.dump(d, f, indent=2)
except Exception as e:
    print(f'Status update error: {e}', file=sys.stderr)
" 2>/dev/null || true
    fi
}

#===============================================================
# 验证云端（独立步骤，供 backup-runner 调用）
#===============================================================
verify_cloud() {
    verify_step4
}

#===============================================================
# 主程序
#===============================================================
main() {
    _vlog "========== 四重验证开始 | trace=$TRACE_ID =========="

    local failed=false

    # 第一重
    if [ "$STEP" = "all" ] || [ "$STEP" = "1" ]; then
        if ! verify_step1; then
            update_status "step1" "false"
            failed=true
        else
            update_status "step1" "true"
        fi
    fi

    # 第二重
    if [ "$STEP" = "all" ] || [ "$STEP" = "2" ]; then
        if ! verify_step2; then
            update_status "step2" "false"
            failed=true
        else
            update_status "step2" "true"
        fi
    fi

    # 第三重
    if [ "$STEP" = "all" ] || [ "$STEP" = "3" ]; then
        if ! verify_step3; then
            update_status "step3" "false"
            failed=true
        else
            update_status "step3" "true"
        fi
    fi

    # 第四重（云端，需要单独触发）
    if [ "$STEP" = "all" ] || [ "$STEP" = "4" ]; then
        if ! verify_step4; then
            update_status "step4" "false"
            failed=true
        else
            update_status "step4" "true"
        fi
    fi

    _vlog "========== 四重验证完成 =========="

    if [ "$failed" = true ]; then
        exit 1
    fi
    exit 0
}

main "$@"
