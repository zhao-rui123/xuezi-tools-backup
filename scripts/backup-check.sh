#!/bin/bash
# 备份状态检查脚本 - 每天 22:05 执行
# 检查今天的备份是否成功

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

BACKUP_DIR="/Volumes/cu/ocu/full-backups"
LOG_FILE="/tmp/backup_cron.log"
TODAY=$(date +%Y%m%d)

send_message() {
    local message="$1"
    /usr/bin/python3 /Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py \
        --task send \
        --message "$message" 2>&1
}

# 真正验证备份文件是否存在且有效
verify_backup() {
    local latest="$BACKUP_DIR/latest"
    local size_bytes=0
    
    if [ -L "$latest" ] && [ -f "$latest" ]; then
        # 检查是否是今天的备份
        local file_date=$(stat -f "%Sm" -t "%Y%m%d" "$latest" 2>/dev/null || stat -c "%y" "$latest" 2>/dev/null | cut -d' ' -f1 | tr -d '-')
        
        if [ "$file_date" = "$TODAY" ]; then
            # 检查文件大小（>100KB才算有效）
            size_bytes=$(stat -f "%z" "$latest" 2>/dev/null || stat -c "%s" "$latest" 2>/dev/null)
            if [ "$size_bytes" -gt 102400 ]; then
                return 0  # 备份有效
            fi
        fi
    fi
    return 1  # 备份无效
}

# 验证压缩包完整性
verify_archive() {
    local latest="$BACKUP_DIR/latest"
    if [ -f "$latest" ]; then
        tar -tzf "$latest" > /dev/null 2>&1
        return $?
    fi
    return 1
}

# 执行验证
if verify_backup; then
    size=$(du -h "$BACKUP_DIR/latest" 2>/dev/null | cut -f1)
    
    # 使用正确的备份目录路径
    memory_files=$(find /Volumes/cu/ocu/memory-backup/daily -type f 2>/dev/null | wc -l)
    skills_files=$(find /Volumes/cu/ocu/skills-backup/core -type f 2>/dev/null | wc -l)
    
    # 验证压缩包完整性
    if verify_archive; then
        archive_status="✅ 完整"
    else
        archive_status="⚠️ 损坏"
    fi
    
    send_message "✅ 备份验证通过 ($(date '+%Y-%m-%d %H:%M'))

📁 Memory备份: $memory_files 个文件
📁 Skills备份: $skills_files 个文件
💾 压缩包: $size ($archive_status)

备份完整可用，数据安全。"
else
    send_message "⚠️ 备份验证失败 ($(date '+%Y-%m-%d %H:%M'))

今天的备份文件不存在或无效

请检查：/tmp/backup_cron.log"
fi
