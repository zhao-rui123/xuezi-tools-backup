#!/usr/bin/env bash
#===============================================================================
# logger.sh - 统一日志函数库
#===============================================================================
# 用法: source "$OPS_DIR/lib/logger.sh"
# 环境变量:
#   LOG_FILE     - 日志文件路径（可选，默认输出到 stdout）
#   LOG_LEVEL    - 日志级别 DEBUG|INFO|WARN|ERROR（默认 INFO）
#   LOG_JSON     - 是否输出 JSON 格式（默认 false）
#===============================================================================

# 确保 OPS_DIR 已定义
if [ -z "${OPS_DIR:-}" ]; then
    SCRIPT="${BASH_SOURCE[0]}"
    while [ -L "$SCRIPT" ]; do
        SCRIPT="$(readlink "$SCRIPT")"
    done
    OPS_DIR="$(cd -P "$(dirname "$SCRIPT")/.." && pwd)"
fi

# 防止重复加载导致 readonly 变量冲突
if [ -z "${_logger_init_done:-}" ]; then
    _logger_init_done=1

    # 日志级别常量
    readonly LOG_LEVELS="DEBUG INFO WARN ERROR"
    readonly LOG_LEVEL_DEBUG=0
    readonly LOG_LEVEL_INFO=1
    readonly LOG_LEVEL_WARN=2
    readonly LOG_LEVEL_ERROR=3
fi

# 默认值
: "${LOG_LEVEL:=INFO}"
: "${LOG_JSON:=false}"
: "${TRACE_ID:=$(date '+%Y%m%d_%H%M%S')-$(openssl rand -hex 3 2>/dev/null || echo "unknown")}"

# 日志级别转数字
_log_level_to_num() {
    case "$1" in
        DEBUG) echo $LOG_LEVEL_DEBUG ;;
        INFO)  echo $LOG_LEVEL_INFO ;;
        WARN)  echo $LOG_LEVEL_WARN ;;
        ERROR) echo $LOG_LEVEL_ERROR ;;
        *)     echo $LOG_LEVEL_INFO ;;
    esac
}

# 当前日志级别数字
_CURRENT_LOG_LEVEL_NUM=$(_log_level_to_num "$LOG_LEVEL")

# 是否应该输出
_should_log() {
    local level="$1"
    local num=$(_log_level_to_num "$level")
    [ "$num" -ge "$_CURRENT_LOG_LEVEL_NUM" ]
}

# 输出日志（内部函数）
_log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp="$(date '+%Y-%m-%dT%H:%M:%S.%3N%z')"

    if [ "$LOG_JSON" = "true" ]; then
        local json_msg
        json_msg=$(printf '%s' "$message" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' 2>/dev/null || echo "\"$message\"")
        printf '%s\n' "{\"timestamp\":\"$timestamp\",\"level\":\"$level\",\"trace_id\":\"$TRACE_ID\",\"message\":$json_msg}"
    else
        printf '%s [%s] [%s] %s\n' "$timestamp" "$TRACE_ID" "$level" "$message"
    fi

    # 同时写入日志文件
    if [ -n "${LOG_FILE:-}" ]; then
        mkdir -p "$(dirname "$LOG_FILE")"
        if [ "$LOG_JSON" = "true" ]; then
            printf '%s\n' "{\"timestamp\":\"$timestamp\",\"level\":\"$level\",\"trace_id\":\"$TRACE_ID\",\"message\":$json_msg}" >> "$LOG_FILE"
        else
            printf '%s [%s] [%s] %s\n' "$timestamp" "$TRACE_ID" "$level" "$message" >> "$LOG_FILE"
        fi
    fi
}

# 公开日志函数
log_debug() { _should_log DEBUG && _log DEBUG "$1"; }
log_info()  { _should_log INFO  && _log INFO  "$1"; }
log_warn()  { _should_log WARN  && _log WARN  "$1"; }
log_error() { _should_log ERROR && _log ERROR "$1"; }

# 别名（兼容旧脚本）
log()       { log_info "$1"; }

# 分隔线
log_separator() {
    log "=========================================="
}

# 等待动画（后台运行日志）
log_spinner() {
    local pid=$1
    local delay=0.2
    local chars='-\|/'
    while kill -0 "$pid" 2>/dev/null; do
        for char in $chars; do
            printf '\r[%s] 处理中... ' "$char" >&2
            sleep $delay
        done
    done
    printf '\r[✓] 完成                             \n' >&2
}

# 获取日志目录
log_get_log_dir() {
    echo "$OPS_DIR/logs"
}

# 日志轮转（保留 N 天）
log_rotate() {
    local log_dir="${1:-$OPS_DIR/logs}"
    local days="${2:-30}"
    local count
    count=$(find "$log_dir" -name "*.log" -type f 2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -gt 0 ]; then
        find "$log_dir" -name "*.log" -type f -mtime "+$days" -delete 2>/dev/null
        log_info "日志轮转完成，保留 $days 天，删除 $(find "$log_dir" -name "*.log" -type f -mtime "+$days" 2>/dev/null | wc -l | tr -d ' ') 个旧文件"
    fi
}
