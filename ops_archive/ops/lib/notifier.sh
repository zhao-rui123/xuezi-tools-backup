#!/usr/bin/env bash
#===============================================================================
# notifier.sh - 统一通知函数库
#===============================================================================
# 用法: source "$OPS_DIR/lib/notifier.sh"
#===============================================================================

if [ -z "${OPS_DIR:-}" ]; then
    SCRIPT="${BASH_SOURCE[0]}"
    while [ -L "$SCRIPT" ]; do
        SCRIPT="$(readlink "$SCRIPT")"
    done
    OPS_DIR="$(cd -P "$(dirname "$SCRIPT")/.." && pwd)"
fi

# 加载依赖（logger.sh 已由调用方加载，此处可选加载作为兜底）
if declare -f log >/dev/null 2>&1; then
    : # log 函数已定义，跳过
    true
elif [ -f "$OPS_DIR/lib/logger.sh" ]; then
    source "$OPS_DIR/lib/logger.sh" 2>/dev/null || true
fi

# 飞书通知函数
# 用法: feishu_notify "消息内容" [level]
# level: INFO(默认) | WARN | ERROR | P0
feishu_notify() {
    local message="$1"
    local level="${2:-INFO}"
    local emoji="ℹ️"

    case "$level" in
        P0)    emoji="🚨" ;;
        ERROR) emoji="❌" ;;
        WARN)  emoji="⚠️" ;;
        INFO)  emoji="✅" ;;
    esac

    # 调用飞书广播脚本
    if [ -f "$HOME/.openclaw/workspace/agents/kilo/broadcaster.py" ]; then
        /usr/bin/python3 "$HOME/.openclaw/workspace/agents/kilo/broadcaster.py" \
            --task send \
            --message "$emoji $message" \
            --target group >> /tmp/feishu_notify.log 2>&1 || true
    fi
}

# 备份完成通知（精简格式）
# 用法: notify_backup_success trace_id size memory_count skills_count [cloud_status]
notify_backup_success() {
    local trace_id="$1"
    local size="$2"
    local memory_count="$3"
    local skills_count="$4"
    local cloud_status="${5:-☁️已同步}"
    local time
    time=$(date '+%H:%M')

    feishu_notify "💾 备份完成 | $time | Memory:$memory_count | Skills:$skills_count | $size | $cloud_status" "INFO"
}

# 备份失败告警
# 用法: notify_backup_failure trace_id error_message
notify_backup_failure() {
    local trace_id="$1"
    local error="$2"
    local time
    time=$(date '+%H:%M')

    feishu_notify "🚨【严重】备份失败 | $time
❌ 原因: $error
🕐 时间: $(date '+%Y-%m-%d %H:%M')
请立即处理！" "P0"
}

# 任务失败告警
# 用法: notify_task_failure task_name error_message
notify_task_failure() {
    local task_name="$1"
    local error="$2"

    feishu_notify "⚠️ 任务失败 | $task_name
❌ 原因: $error
🕐 时间: $(date '+%Y-%m-%d %H:%M')" "ERROR"
}

# 每日任务汇总
# 用法: notify_task_summary success_count failure_count details
notify_task_summary() {
    local success="$1"
    local failure="$2"
    local details="$3"

    local emoji="✅"
    [ "$failure" -gt 0 ] && emoji="⚠️"

    feishu_notify "📊 定时任务日报 | $(date '+%m-%d')

$emoji 成功: $success | ⚠️ 失败: $failure | 总计: $((success + failure))

$details" "INFO"
}

# 健康检查告警
# 用法: notify_health_alert check_item message
notify_health_alert() {
    local check_item="$1"
    local message="$2"

    feishu_notify "🏥 健康检查告警 | $check_item
⚠️ $message
🕐 时间: $(date '+%Y-%m-%d %H:%M')" "WARN"
}

# 调试日志（仅 DEBUG 模式）
notify_debug() {
    local message="$1"
    log_debug "[NOTIFIER] $message" 2>/dev/null || true
}
