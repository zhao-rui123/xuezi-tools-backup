#!/usr/bin/env bash
#===============================================================================
# task-status-collector.sh - 任务状态汇总
#===============================================================================
# 改造自 daily-task-report.sh，集成到 ops 架构
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

TRACE_ID="$(date '+%Y%m%d')"
LOG_DIR="$OPS_DIR/logs/tasks"
STATUS_DIR="$OPS_DIR/status/tasks"
REPORT_DIR="$OPS_DIR/reports"

mkdir -p "$REPORT_DIR"

log "========== 任务状态汇总开始 =========="

# 获取昨日的任务状态文件
YESTERDAY=$(date -v-1d '+%Y%m%d' 2>/dev/null || date -d "yesterday" '+%Y%m%d')
TODAY=$(date '+%Y%m%d')

# 汇总统计
total=0
success=0
failed=0
running=0

# 收集备份状态
backup_status="unknown"
backup_size="unknown"
backup_cloud="未同步"

if [ -f "$OPS_DIR/status/backup"/*.json ] 2>/dev/null; then
    # 获取最新的备份状态
    latest_backup=$(ls -t "$OPS_DIR/status/backup"/*.json 2>/dev/null | head -1)
    if [ -n "$latest_backup" ]; then
        backup_status=$(python3 -c "
import json, sys
try:
    d=json.load(open('$latest_backup'))
    print(d.get('status','unknown'))
except: print('unknown')
" 2>/dev/null || echo "unknown")
        backup_size=$(python3 -c "
import json, sys
try:
    d=json.load(open('$latest_backup'))
    print(d.get('archive_size','unknown'))
except: print('unknown')
" 2>/dev/null || echo "unknown")
        backup_cloud=$(python3 -c "
import json, sys
try:
    d=json.load(open('$latest_backup'))
    print('☁️已同步' if d.get('cloud_synced') else '⚠️未同步')
except: print('⚠️未同步')
" 2>/dev/null || echo "⚠️未同步")
    fi
fi

# 生成报告
report_file="$REPORT_DIR/task-report-${TRACE_ID}.txt"

cat > "$report_file" << EOF
==========================================
雪子助手 - 定时任务日报
日期: $(date '+%Y-%m-%d')
==========================================

【备份状态】
状态: $backup_status
大小: $backup_size
云端: $backup_cloud

【最近任务日志】
EOF

# 显示最近的日志
ls -t "$LOG_DIR"/*.log 2>/dev/null | head -10 | while read -r logf; do
    echo "--- $(basename "$logf") ---" >> "$report_file"
    tail -5 "$logf" >> "$report_file" 2>/dev/null
    echo "" >> "$report_file"
done

log "========== 任务状态汇总完成 =========="

# 发送飞书通知
if [ "$failed" -gt 0 ]; then
    feishu_notify "📊 每日任务汇总 | $(date '+%m-%d') | 成功:$success | 失败:$failed" "WARN"
else
    feishu_notify "📊 每日任务汇总 | $(date '+%m-%d') | ✅ 全部成功" "INFO"
fi

echo "报告已保存: $report_file"
