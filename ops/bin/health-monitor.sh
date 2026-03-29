#!/usr/bin/env bash
#===============================================================================
# health-monitor.sh - 健康监控
#===============================================================================
# 整合现有健康检查脚本，每日/每周健康检查
#===============================================================================

set -euo pipefail

SCRIPT="${BASH_SOURCE[0]}"
while [ -L "$SCRIPT" ]; do
    SCRIPT="$(readlink "$SCRIPT")"
done
OPS_DIR="$(cd -P "$(dirname "$SCRIPT")/.." && pwd)"
export OPS_DIR

source "$OPS_DIR/lib/logger.sh"
source "$OPS_DIR/lib/notifier.sh"
source "$OPS_DIR/config/alerts.conf"

TRACE_ID="$(date '+%Y%m%d_%H%M%S')"
LOG_FILE="$OPS_DIR/logs/health/${TRACE_ID}.log"
STATUS_FILE="$OPS_DIR/status/health-${TRACE_ID}.json"

mkdir -p "$OPS_DIR/logs/health"

#===============================================================
# 日志
#===============================================================
hlog() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [health] $1" | tee -a "$LOG_FILE"
}

#===============================================================
# 检查磁盘空间
#===============================================================
check_disk() {
    hlog "[检查] 磁盘空间..."

    local issues=()

    # 本地磁盘
    local local_usage
    local_usage=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
    if [ "${local_usage:-0}" -ge "${ALERT_DISK_LOCAL_CRITICAL:-90}" ]; then
        issues+=("本地磁盘使用率 ${local_usage}% (严重)")
    elif [ "${local_usage:-0}" -ge "${ALERT_DISK_LOCAL_WARNING:-80}" ]; then
        issues+=("本地磁盘使用率 ${local_usage}%")
    fi

    # 备份磁盘
    if [ -d "/Volumes/cu/ocu" ]; then
        local backup_usage
        backup_usage=$(df /Volumes/cu/ocu | awk 'NR==2 {print $5}' | tr -d '%')
        if [ "${backup_usage:-0}" -ge "${ALERT_DISK_BACKUP_CRITICAL:-85}" ]; then
            issues+=("备份盘使用率 ${backup_usage}% (严重)")
        elif [ "${backup_usage:-0}" -ge "${ALERT_DISK_BACKUP_WARNING:-70}" ]; then
            issues+=("备份盘使用率 ${backup_usage}%")
        fi
    fi

    # 腾讯云磁盘
    local cloud_disk_info
    cloud_disk_info=$(ssh -i "$HOME/.ssh/id_ed25519" \
        -o ConnectTimeout=10 \
        -o StrictHostKeyChecking=no \
        "root@106.54.25.161" \
        "df -h /data" 2>/dev/null | tail -1)

    if [ -n "$cloud_disk_info" ]; then
        local cloud_usage
        cloud_usage=$(echo "$cloud_disk_info" | awk '{print $5}' | tr -d '%')
        if [ "${cloud_usage:-0}" -ge "${ALERT_DISK_CLOUD_CRITICAL:-90}" ]; then
            issues+=("腾讯云磁盘使用率 ${cloud_usage}% (严重)")
        elif [ "${cloud_usage:-0}" -ge "${ALERT_DISK_CLOUD_WARNING:-80}" ]; then
            issues+=("腾讯云磁盘使用率 ${cloud_usage}%")
        fi
    fi

    if [ ${#issues[@]} -gt 0 ]; then
        hlog "⚠️ 磁盘告警: ${issues[*]}"
        for issue in "${issues[@]}"; do
            notify_health_alert "磁盘空间" "$issue"
        done
        return 1
    fi

    hlog "✅ 磁盘空间正常"
    return 0
}

#===============================================================
# 检查内存
#===============================================================
check_memory() {
    hlog "[检查] 内存使用率..."

    local mem_usage
    mem_usage=$(vm_stat | awk '/Pages active/ {print $3}' | tr -d '.' 2>/dev/null)
    if [ -z "$mem_usage" ]; then
        mem_usage=$(top -l 1 | grep "PhysMem" | awk '{print $2}' | tr -d 'M')
    fi

    local mem_total
    mem_total=$(sysctl -n hw.memsize 2>/dev/null | awk '{print $1/1024/1024/1024}')
    local mem_used
    mem_used=$(memory_pressure 2>/dev/null | head -1 || echo "unknown")

    if [ "${mem_usage:-0}" -ge "${ALERT_MEMORY_CRITICAL:-90}" ]; then
        hlog "⚠️ 内存使用率 ${mem_usage}% (严重)"
        notify_health_alert "内存" "使用率 ${mem_usage}% (严重)"
        return 1
    elif [ "${mem_usage:-0}" -ge "${ALERT_MEMORY_WARNING:-80}" ]; then
        hlog "⚠️ 内存使用率 ${mem_usage}%"
        notify_health_alert "内存" "使用率 ${mem_usage}%"
        return 1
    fi

    hlog "✅ 内存使用率正常: ${mem_usage}%"
    return 0
}

#===============================================================
# 检查备份任务
#===============================================================
check_backup() {
    hlog "[检查] 备份任务状态..."

    local latest_backup_status="unknown"
    local latest_backup_file

    # 查找最新的备份状态
    latest_backup_file=$(ls -t "$OPS_DIR/status/backup"/*.json 2>/dev/null | head -1)

    if [ -n "$latest_backup_file" ] && [ -f "$latest_backup_file" ]; then
        latest_backup_status=$(python3 -c "
import json, sys
try:
    d=json.load(open('$latest_backup_file'))
    print(d.get('status','unknown'))
except: print('unknown')
" 2>/dev/null || echo "unknown")
    fi

    # 检查是否有今天的备份
    local today_backup_count=0
    today_backup_count=$(find "$OPS_DIR/status/backup" -name "*.json" -mtime -1 2>/dev/null | wc -l | tr -d ' ')

    if [ "$latest_backup_status" = "FAILED" ]; then
        hlog "⚠️ 备份任务失败"
        notify_health_alert "备份任务" "最新备份任务失败"
        return 1
    elif [ "$today_backup_count" -eq 0 ]; then
        hlog "⚠️ 今日无备份记录"
        notify_health_alert "备份任务" "今日无备份记录"
        return 1
    fi

    hlog "✅ 备份任务正常"
    return 0
}

#===============================================================
# 检查 cron 服务
#===============================================================
check_cron() {
    hlog "[检查] cron 服务状态..."

    # 检查是否有最近的 cron 任务日志
    local recent_cron_logs
    recent_cron_logs=$(find "$OPS_DIR/logs" -name "*.log" -mtime -1 2>/dev/null | wc -l | tr -d ' ')

    if [ "${recent_cron_logs:-0}" -eq 0 ]; then
        hlog "⚠️ 无近期任务日志"
        notify_health_alert "定时任务" "无近期任务日志"
        return 1
    fi

    hlog "✅ cron 服务正常"
    return 0
}

#===============================================================
# 检查 SSH 失败登录
#===============================================================
check_ssh() {
    hlog "[检查] SSH 失败登录..."

    local failed_logins
    failed_logins=$(last -100 | grep -i "failed" | wc -l | tr -d ' ')

    if [ "${failed_logins:-0}" -ge "${ALERT_SSH_FAILED_LOGIN:-100}" ]; then
        hlog "⚠️ SSH 失败登录过多: $failed_logins"
        notify_health_alert "SSH安全" "失败登录 $failed_logins 次"
        return 1
    fi

    hlog "✅ SSH 登录正常"
    return 0
}

#===============================================================
# 主程序
#===============================================================
main() {
    hlog "========== 健康检查开始 =========="

    local failed_checks=()
    local passed_checks=()

    check_disk && passed_checks+=("disk") || failed_checks+=("disk")
    check_memory && passed_checks+=("memory") || failed_checks+=("memory")
    check_backup && passed_checks+=("backup") || failed_checks+=("backup")
    check_cron && passed_checks+=("cron") || failed_checks+=("cron")
    check_ssh && passed_checks+=("ssh") || failed_checks+=("ssh")

    hlog "========== 健康检查完成 =========="
    hlog "通过: ${#passed_checks[@]} | 失败: ${#failed_checks[@]}"

    if [ ${#failed_checks[@]} -gt 0 ]; then
        hlog "失败项目: ${failed_checks[*]}"
        exit 1
    fi

    exit 0
}

main "$@"
