#!/bin/bash
# 备份状态检查脚本 - 每天 22:05 执行
# 检查 22:00 的备份是否成功

# 设置环境变量（cron 环境需要）
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

LOG_FILE="/tmp/backup_memory.log"
CHECK_TIME=$(date '+%Y-%m-%d 22:00')

# 发送消息函数
send_message() {
    local message="$1"
    openclaw message send \
        --channel feishu \
        --target ou_5a7b7ec0339ffe0c1d5bb6c5bc162579 \
        --message "$message" 2>&1
}

# 检查日志中是否有今天的成功记录
if grep -q "$CHECK_TIME.*ALL BACKUPS COMPLETED SUCCESSFULLY" "$LOG_FILE" 2>/dev/null; then
    # 获取备份统计
    memory_files=$(find /Volumes/cu/ocu/memory -type f 2>/dev/null | wc -l)
    skills_files=$(find /Volumes/cu/ocu/skills -type f 2>/dev/null | wc -l)
    
    send_message "✅ 备份检查通过 ($(date '+%Y-%m-%d %H:%M'))

📁 Memory: $memory_files 个文件
📁 Skills: $skills_files 个文件

今日备份已完成，数据安全。"
else
    send_message "⚠️ 备份检查警告 ($(date '+%Y-%m-%d %H:%M'))

未检测到今日 22:00 备份成功记录

请检查日志: /tmp/backup_memory.log"
fi
