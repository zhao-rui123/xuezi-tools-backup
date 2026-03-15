#!/bin/bash
# 备份状态检查脚本 - 每天 22:05 执行
# 检查今天的备份是否成功

# 设置环境变量（cron 环境需要）
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

LOG_FILE="/tmp/backup_cron.log"
CHECK_TIME=$(date '+%Y-%m-%d')

# 发送消息函数
send_message() {
    local message="$1"
    /usr/bin/python3 /Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py \
        --task send \
        --message "$message" 2>&1
}

# 检查日志中是否有今天的成功记录
if grep -q "$CHECK_TIME.*ALL BACKUPS COMPLETED SUCCESSFULLY\|$CHECK_TIME.*备份完成" "$LOG_FILE" 2>/dev/null; then
    # 获取备份统计
    memory_files=$(find /Volumes/cu/ocu/memory -type f 2>/dev/null | wc -l)
    skills_files=$(find /Volumes/cu/ocu/skills -type f 2>/dev/null | wc -l)
    ws_skills_files=$(find /Volumes/cu/ocu/workspace-skills -type f 2>/dev/null | wc -l)
    
    # 检查是否有配置备份
    if [ -d "/Volumes/cu/ocu/openclaw-config" ]; then
        config_status="✓"
    else
        config_status="✗"
    fi
    
    send_message "✅ 备份检查通过 ($(date '+%Y-%m-%d %H:%M'))

📁 Memory: $memory_files 个文件
📁 Skills: $skills_files 个文件
📁 Workspace Skills: $ws_skills_files 个文件
⚙️ Config: $config_status

今日备份已完成，数据安全。"
else
    send_message "⚠️ 备份检查警告 ($(date '+%Y-%m-%d %H:%M'))

未检测到今日备份成功记录

请检查日志: /tmp/backup_cron.log"
fi
