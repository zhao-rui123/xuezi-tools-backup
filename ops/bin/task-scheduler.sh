#!/usr/bin/env bash
#===============================================================================
# task-scheduler.sh - 统一任务调度中心
#===============================================================================
# 用法: task-scheduler.sh run [daily|weekly|monthly]
#===============================================================================

set -euo pipefail

SCRIPT="${BASH_SOURCE[0]}"
while [ -L "$SCRIPT" ]; do
    SCRIPT="$(readlink "$SCRIPT")"
done
OPS_DIR="$(cd -P "$(dirname "$SCRIPT")/.." && pwd)"
export OPS_DIR

source "$OPS_DIR/lib/logger.sh"
source "$OPS_DIR/lib/lock.sh"
source "$OPS_DIR/lib/notifier.sh"
source "$OPS_DIR/config/backup.conf"
source "$OPS_DIR/config/alerts.conf"

# 模式：daily | weekly | monthly
MODE="${1:-daily}"
TRACE_ID="$(date '+%Y%m%d_%H%M%S')"
LOG_DIR="$OPS_DIR/logs/tasks"
STATUS_DIR="$OPS_DIR/status/tasks"
TASKS_CONF="$OPS_DIR/config/tasks.conf"

mkdir -p "$LOG_DIR" "$STATUS_DIR"
LOG_FILE="$LOG_DIR/${TRACE_ID}-${MODE}.log"
LOCK_FILE="$OPS_DIR/lock/scheduler-${MODE}.lock"

log "=========================================="
log "任务调度开始 | mode=$MODE | trace=$TRACE_ID"
log "=========================================="

#===============================================================
# YAML 解析（简单实现，不依赖外部工具）
#===============================================================
parse_yaml() {
    local mode="$1"
    local section=""
    local in_section=false
    local tasks=()

    while IFS= read -r line; do
        # 跳过注释和空行
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$line" ]] && continue

        # 检测节
        if [[ "$line" =~ ^(daily|weekly|monthly): ]]; then
            section="${BASH_REMATCH[1]}"
            in_section=false
            continue
        fi

        # 检测子节（weekly.sunday 等）
        if [[ "$line" =~ ^[[:space:]]([a-z_]+):[[:space:]]*$ ]]; then
            section="${BASH_REMATCH[1]}"
            in_section=false
            continue
        fi

        # 忽略 scheduler: 块
        [[ "$section" == "" ]] && continue

        # 如果不在目标节，跳过
        if [[ "$mode" == "weekly" ]]; then
            [[ "$section" != "sunday" && "$section" != "monday" ]] && continue
        elif [[ "$mode" != "$section" ]]; then
            continue
        fi

        # 解析任务 ID
        if [[ "$line" =~ ^[[:space:]]+-[[:space:]]+id:[[:space:]]*\"?([a-z_]+)\"? ]]; then
            tasks+=("${BASH_REMATCH[1]}")
        fi
    done < "$TASKS_CONF"

    echo "${tasks[@]}"
}

#===============================================================
# 获取任务配置
#===============================================================
get_task_config() {
    local task_id="$1"
    local field="$2"
    local mode="$3"

    # 简单文本解析
    awk -v id="$task_id" -v field="$field" '
BEGIN { in_task=0 }
/^[[:space:]]*-[[:space:]]+id:/ {
    if ($3 == "\"" id "\"" || $3 == id) in_task=1
    else in_task=0
}
in_task && $1 == field ":" {
    # Remove leading/trailing whitespace and quotes
    gsub(/^[ \t]+|[ \t]+$/, "", $0)
    gsub(/^"|"$/, "", $0)
    gsub(/^\[|\]$/, "", $0)
    gsub(/, */, "|", $0)
    print $0
    exit
}
' "$TASKS_CONF"
}

#===============================================================
# 执行单个任务
#===============================================================
execute_task() {
    local task_id="$1"
    local task_name="$2"
    local script="$3"
    local args="$4"
    local cwd="$5"
    local timeout="$6"
    local task_trace="${TRACE_ID}-${task_id}"
    local task_log="$LOG_DIR/${task_trace}.log"
    local task_status="$STATUS_DIR/${task_trace}.json"

    log "[任务] 开始: $task_name (ID: $task_id)"

    # 保存任务状态
    cat > "$task_status" << EOF
{
  "task_id": "$task_id",
  "task_name": "$task_name",
  "trace_id": "$task_trace",
  "group": "unknown",
  "start_time": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "status": "RUNNING",
  "mode": "$MODE"
}
EOF

    local start_time
    start_time=$(date +%s)
    local exit_code=0

    # 构建命令
    local cmd=""
    if [[ "$script" == *.py ]]; then
        cmd="/opt/homebrew/bin/python3 $script"
    else
        cmd="bash $script"
    fi

    if [[ -n "$args" ]]; then
        # 替换参数中的占位符
        args="${args//|/ }"
        cmd="$cmd $args"
    fi

    # 执行
    if [[ -n "$cwd" ]]; then
        (cd "$cwd" && eval "$cmd" >> "$task_log" 2>&1) &
    else
        (eval "$cmd" >> "$task_log" 2>&1) &
    fi

    local pid=$!
    local elapsed=0

    # 等待完成（带超时）
    while kill -0 "$pid" 2>/dev/null; do
        sleep 5
        elapsed=$((elapsed + 5))
        if [ "$elapsed" -ge "$timeout" ]; then
            kill "$pid" 2>/dev/null
            log "[任务] 超时: $task_name (${timeout}s)"
            exit_code=124
            break
        fi
    done

    wait "$pid"
    exit_code=$?

    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # 更新状态
    local status="SUCCESS"
    if [ "$exit_code" -ne 0 ]; then
        status="FAILED"
        log "[任务] ❌ 失败: $task_name (exit=$exit_code, ${duration}s)"
    else
        log "[任务] ✅ 完成: $task_name (${duration}s)"
    fi

    # 更新状态文件
    cat > "$task_status" << EOF
{
  "task_id": "$task_id",
  "task_name": "$task_name",
  "trace_id": "$task_trace",
  "start_time": "$(date -u -d "@$start_time" '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -r "$start_time" -u '+%Y-%m-%dT%H:%M:%SZ')",
  "end_time": "$(date -u -d "@$end_time" '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -r "$end_time" -u '+%Y-%m-%dT%H:%M:%SZ')",
  "duration_seconds": $duration,
  "status": "$status",
  "exit_code": $exit_code
}
EOF

    echo "$task_id:$status:$exit_code"
}

#===============================================================
# 主程序
#===============================================================
main() {
    # 检查是否正在运行
    if lock_exists "scheduler-${MODE}"; then
        log "⚠️ 调度器正在运行中（mode=$MODE），跳过"
        exit 0
    fi

    # 获取锁
    lock_acquire "scheduler-${MODE}" || {
        log "⚠️ 无法获取调度器锁，跳过"
        exit 0
    }
    trap "lock_release 'scheduler-${MODE}'" EXIT

    # 获取当日星期几
    local day_of_week
    day_of_week=$(date +%u)  # 1=Monday, 7=Sunday

    # 根据模式确定要执行的任务
    local task_ids=()
    case "$MODE" in
        daily)
            task_ids=(backup_full stock_push memory_evolution memory_archive knowledge_graph log_rotate feishu_sync morning_greeting task_summary)
            ;;
        weekly)
            if [ "$day_of_week" -eq 7 ]; then  # Sunday
                task_ids=(system_maintenance ouc_cleanup)
            elif [ "$day_of_week" -eq 1 ]; then  # Monday
                task_ids=(file_cleanup security_scan health_check)
            fi
            ;;
        monthly)
            task_ids=(memory_deep_analyze backup_archive evolution_monthly evolution_report)
            ;;
    esac

    log "计划执行任务数: ${#task_ids[@]}"

    # 执行任务
    local results=()
    local success_count=0
    local failure_count=0

    for task_id in "${task_ids[@]}"; do
        local task_name script args cwd timeout
        task_name=$(get_task_config "$task_id" "name" "$MODE")
        script=$(get_task_config "$task_id" "script" "$MODE")
        args=$(get_task_config "$task_id" "args" "$MODE")
        cwd=$(get_task_config "$task_id" "cwd" "$MODE")
        timeout=$(get_task_config "$task_id" "timeout" "$MODE" | tr -d ' ')
        
        # 处理路径中的 ~
        cwd="${cwd/#\~/$HOME}"

        # 跳过未找到的任务
        if [ -z "$task_name" ]; then
            log "[跳过] 任务 $task_id 未找到"
            continue
        fi

        # 设置默认值
        timeout="${timeout:-300}"
        cwd="${cwd:-$HOME/.openclaw/workspace}"

        # 构建脚本路径
        if [[ "$script" == /* ]]; then
            script="$script"
        elif [[ "$script" == *.py ]]; then
            script="$HOME/.openclaw/workspace/$script"
        else
            script="$HOME/.openclaw/workspace/scripts/$script"
        fi

        if [ ! -f "$script" ]; then
            log "[跳过] 脚本不存在: $script"
            continue
        fi

        local result
        result=$(execute_task "$task_id" "$task_name" "$script" "$args" "$cwd" "$timeout")
        results+=("$result")

        if [[ "$result" == *":SUCCESS:"* ]]; then
            success_count=$((success_count + 1))
        else
            failure_count=$((failure_count + 1))
        fi
    done

    log "=========================================="
    log "任务调度完成 | 成功:$success_count | 失败:$failure_count"
    log "=========================================="

    # 发送汇总通知
    local details=""
    for r in "${results[@]}"; do
        IFS=':' read -r tid status ec <<< "$r"
        if [ "$status" != "SUCCESS" ]; then
            details="${details}• $tid ($status)\n"
        fi
    done

    if [ "$failure_count" -gt 0 ]; then
        notify_task_summary "$success_count" "$failure_count" "$details"
    fi
}

main "$@"
