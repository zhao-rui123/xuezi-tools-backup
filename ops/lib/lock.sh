#!/usr/bin/env bash
#===============================================================================
# lock.sh - 锁文件管理函数库
#===============================================================================
# 用法: source "$OPS_DIR/lib/lock.sh"
#===============================================================================

if [ -z "${OPS_DIR:-}" ]; then
    SCRIPT="${BASH_SOURCE[0]}"
    while [ -L "$SCRIPT" ]; do
        SCRIPT="$(readlink "$SCRIPT")"
    done
    OPS_DIR="$(cd -P "$(dirname "$SCRIPT")/.." && pwd)"
fi

LOCK_DIR="${OPS_DIR}/lock"
mkdir -p "$LOCK_DIR"

# 获取锁（不阻塞，立即返回）
# 返回 0=获取成功，1=已被锁定
lock_acquire() {
    local lock_file="${1:-}"
    local lock_path="$LOCK_DIR/$(basename "$lock_file" .lock).lock"
    local timeout="${2:-0}"
    local start_time
    start_time=$(date +%s)

    [ -z "$lock_file" ] && { echo "ERROR: lock_acquire 需要锁文件名" >&2; return 1; }

    while true; do
        # 尝试创建锁文件（原子操作）
        if mkdir "$lock_path" 2>/dev/null; then
            # 写入 PID 和时间
            cat > "$lock_path/pid" << EOF
PID=$$
PPID=$PPID
USER=$USER
HOST=$(hostname)
STARTED=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
TRACE_ID=${TRACE_ID:-unknown}
EOF
            return 0
        fi

        # 检查锁是否过期（超过 timeout 分钟）
        if [ "$timeout" -gt 0 ]; then
            local age
            age=$(($(date +%s) - start_time))
            if [ "$age" -gt "$((timeout * 60))" ]; then
                log_warn "锁 $lock_path 已等待 ${age}s，超时，强制获取"
                rm -rf "$lock_path"
                continue
            fi
        fi

        # 检查锁是否陈旧（超过 60 分钟未更新）
        if [ -f "$lock_path/pid" ]; then
            local mtime age_seconds
            mtime=$(stat -f "%m" "$lock_path/pid" 2>/dev/null || stat -c "%Y" "$lock_path/pid" 2>/dev/null)
            age_seconds=$(($(date +%s) - mtime))
            if [ "$age_seconds" -gt 3600 ]; then
                log_warn "锁 $lock_path 已陈旧（${age_seconds}s），强制删除"
                rm -rf "$lock_path"
                continue
            fi
        fi

        return 1
    done
}

# 释放锁
lock_release() {
    local lock_file="${1:-}"
    local lock_path="$LOCK_DIR/$(basename "$lock_file" .lock).lock"

    [ -z "$lock_file" ] && { echo "ERROR: lock_release 需要锁文件名" >&2; return 1; }

    if [ -d "$lock_path" ]; then
        rm -rf "$lock_path"
        return 0
    fi
    return 1
}

# 检查锁是否存在
lock_exists() {
    local lock_file="${1:-}"
    local lock_path="$LOCK_DIR/$(basename "$lock_file" .lock).lock"
    [ -d "$lock_path" ]
}

# 检查锁并显示状态
lock_status() {
    local lock_file="${1:-}"
    local lock_path="$LOCK_DIR/$(basename "$lock_file" .lock).lock"

    if [ -d "$lock_path" ]; then
        echo "LOCKED"
        if [ -f "$lock_path/pid" ]; then
            cat "$lock_path/pid"
        fi
        return 0
    else
        echo "UNLOCKED"
        return 1
    fi
}

# 清理所有陈旧锁（超过 60 分钟）
lock_cleanup() {
    local count=0
    for lock_path in "$LOCK_DIR"/*.lock; do
        [ -f "$lock_path" ] && continue
        [ -d "$lock_path" ] || continue
        if [ -f "$lock_path/pid" ]; then
            local mtime age_seconds
            mtime=$(stat -f "%m" "$lock_path/pid" 2>/dev/null || stat -c "%Y" "$lock_path/pid" 2>/dev/null)
            age_seconds=$(($(date +%s) - mtime))
            if [ "$age_seconds" -gt 3600 ]; then
                log_info "清理陈旧锁: $(basename "$lock_path") (${age_seconds}s)"
                rm -rf "$lock_path"
                count=$((count + 1))
            fi
        fi
    done
    [ "$count" -gt 0 ] && log_info "共清理 $count 个陈旧锁"
}

# 强制释放锁（用于调试）
lock_force_release() {
    local lock_file="${1:-}"
    local lock_path="$LOCK_DIR/$(basename "$lock_file" .lock).lock"
    rm -rf "$lock_path" && echo "已强制释放: $lock_path"
}
