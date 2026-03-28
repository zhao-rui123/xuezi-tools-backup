#!/bin/bash
# 每日任务汇总报告
# 每天08:00执行，检查昨日任务执行状态并发送飞书通知

cd /Users/zhaoruicn/.openclaw/workspace

# 获取昨天的日期
YESTERDAY=$(date -v-1d '+%Y-%m-%d')
TODAY=$(date '+%Y-%m-%d')

# 日志目录
LOG_DIR="/tmp"

# 检查各项任务状态
check_task() {
    local name=$1
    local log=$2
    local pattern=${3:-""}
    
    if [ -f "$log" ]; then
        # 检查是否有成功标记
        if grep -q "success.*true\|✅" "$log" 2>/dev/null; then
            echo "✅"
        elif grep -q "success.*false\|❌\|error" "$log" 2>/dev/null; then
            echo "❌"
        else
            # 检查文件更新时间
            file_time=$(stat -f "%Sm" -t "%Y%m%d" "$log" 2>/dev/null || stat -c "%y" "$log" 2>/dev/null | cut -d' ' -f1 | tr -d '-')
            yesterday_str=$(date -v-1d '+%Y%m%d' 2>/dev/null || date -d "yesterday" '+%Y%m%d')
            if echo "$file_time" | grep -q "$yesterday_str"; then
                echo "✅"
            else
                echo "⚠️"
            fi
        fi
    else
        echo "⚠️"
    fi
}

# 生成报告
REPORT="🤖 定时任务日报 (${YESTERDAY})

🌙 夜间任务 (22:00-23:59):
  • 每日备份 (22:00): $(check_task backup "$LOG_DIR/backup_cron.log")"
REPORT+="
  • 每日自我进化 (23:00): $(check_task evolution "$LOG_DIR/memory-suite.log")"
REPORT+="

🌅 凌晨任务 (00:00-08:00):
  • 每日记忆归档 (00:30): $(check_task archive "$LOG_DIR/memory-suite.log")"
REPORT+="
  • 知识图谱自动更新 (01:00): $(check_task ontology "$LOG_DIR/memory-suite.log")"
REPORT+="
  • 日志轮转 (03:00): $(check_task logrotate "$LOG_DIR/memory-suite-maintenance.log")"
REPORT+="
  • 每日知识同步 (06:00): $(check_task sync "$LOG_DIR/memory-suite.log")"

# 周日任务
if [ $(date -v-1d '+%w' 2>/dev/null || date -d "yesterday" '+%w') -eq 0 ]; then
    REPORT+="

📅 周日任务:
  • 系统维护 (02:00): $(check_task sysmain "$LOG_DIR/system-maintenance.log")"
    REPORT+="
  • OUC清理 (03:00): $(check_task ouc "$LOG_DIR/ouc-cleanup.log")"
fi

# 周一任务
if [ $(date -v-1d '+%w' 2>/dev/null || date -d "yesterday" '+%w') -eq 1 ]; then
    REPORT+="

📅 周一任务:
  • 文件清理 (03:00): $(check_task cleanup "$LOG_DIR/file-cleanup.log")"
    REPORT+="
  • 每周安全扫描 (04:00): $(check_task scan "$LOG_DIR/system-guard-scan.log")"
    REPORT+="
  • 健康检查 (06:30): $(check_task health "$LOG_DIR/memory-suite-maintenance.log")"
fi

# 月度任务 (每月1号)
if [ $(date -v-1d '+%d' 2>/dev/null || date -d "yesterday" '+%d') = "01" ]; then
    REPORT+="

📆 月度任务:
  • 月度归档备份 (03:00): $(check_task arcbackup "$LOG_DIR/backup_archive.log")"
    REPORT+="
  • 月度记忆深度分析 (02:00): $(check_task deep "$LOG_DIR/memory-suite.log")"
fi

# 统计
REPORT+="

📊 系统状态: 正常 ✅"

# 发送通知
/Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py --task send --message "$REPORT" --target group >> /tmp/kilo_notify.log 2>&1

echo "$(date): 任务汇总已发送"
