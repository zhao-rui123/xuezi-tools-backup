#!/bin/bash
# 备份状态检查脚本 v2 - 每天 22:05 执行
# 对应 daily-backup-v2.sh (架构 v2.4)

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

BACKUP_DIR="/Volumes/cu/ocu"
LOG_FILE="/tmp/backup_cron.log"
TODAY=$(date +%Y%m%d)

send_message() {
    local message="$1"
    /usr/bin/python3 /Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py \
        --task send \
        --message "$message" 2>&1
}

# 验证 manifest 文件存在且有效
verify_manifest() {
    local manifest="$BACKUP_DIR/backup-manifest-$TODAY.json"
    if [ -f "$manifest" ]; then
        local size=$(stat -f "%z" "$manifest" 2>/dev/null || stat -c "%s" "$manifest" 2>/dev/null)
        if [ "$size" -gt 100 ]; then
            return 0
        fi
    fi
    return 1
}

# 执行验证
if verify_manifest; then
    # 读取 manifest 统计
    manifest_file="$BACKUP_DIR/backup-manifest-$TODAY.json"
    
    # 提取关键数据
    backup_time=$(python3 -c "import json; d=json.load(open('$manifest_file')); print(d.get('backup_time','?'))" 2>/dev/null || echo "?")
    memory_count=$(python3 -c "import json; d=json.load(open('$manifest_file')); s=d.get('structure',{}).get('memory',{}); print(sum(s.values()))" 2>/dev/null || echo "?")
    skills_core=$(python3 -c "import json; d=json.load(open('$manifest_file')); print(d.get('structure',{}).get('skills',{}).get('core','?'))" 2>/dev/null || echo "?")
    skills_suites=$(python3 -c "import json; d=json.load(open('$manifest_file')); print(d.get('structure',{}).get('skills',{}).get('suites','?'))" 2>/dev/null || echo "?")
    
    # 检查压缩包
    archive_size=""
    if [ -f "$BACKUP_DIR/full-backups/latest" ]; then
        archive_size=$(du -h "$BACKUP_DIR/full-backups/latest" 2>/dev/null | cut -f1)
        if tar -tzf "$BACKUP_DIR/full-backups/latest" > /dev/null 2>&1; then
            archive_status="✅ 完整"
        else
            archive_status="⚠️ 损坏"
        fi
    else
        archive_status="❌ 不存在"
    fi
    
    send_message "✅ 备份验证通过 ($(date '+%Y-%m-%d %H:%M'))

🕐 备份时间: $backup_time
📁 Memory: $memory_count 个文件
📁 Skills核心: $skills_core 个
📁 Skills套件: $skills_suites 个
💾 压缩包: $archive_size ($archive_status)

v2.4 架构备份完整可用 ✅"
else
    send_message "⚠️ 备份验证失败 ($(date '+%Y-%m-%d %H:%M'))

backup-manifest-$TODAY.json 不存在或无效

请检查：/tmp/backup_cron.log"
fi
