# 发送通知
send_notification() {
    local memory_count=$1
    local skills_count=$2
    
    # 使用 Kilo Agent v2 发送通知到群聊
    log "使用 Kilo (通知Agent) 生成通知..."
    
    # 获取压缩包大小
    local backup_size="未知"
    if [ -f "$BACKUP_DIR/full-backups/latest" ]; then
        backup_size=$(du -h "$BACKUP_DIR/full-backups/latest" 2>/dev/null | cut -f1)
    fi
    
    python3 ~/.openclaw/workspace/skills/multi-agent-suite/agents/kilo_v2.py \
        --backup success \
        --backup-details "📊 备份统计:\n• Memory: $memory_count 个文件\n• Skills: $skills_count 个文件\n• 压缩包大小: $backup_size\n\n📄 清单: backup-manifest-$DATE.json" \
        2>/dev/null
    
    log "✅ Kilo 通知已生成"
}

# 清理旧备份
cleanup_old_backups() {
    log "清理旧备份..."
    
    # 保留最近30天的完整备份
    local count=$(ls -1 "$BACKUP_DIR/full-backups"/openclaw-backup-*.tar.gz 2>/dev/null | wc -l)
    if [ "$count" -gt 30 ]; then
        log "  清理旧备份（保留30个）..."
        ls -1t "$BACKUP_DIR/full-backups"/openclaw-backup-*.tar.gz | tail -n +31 | xargs rm -f
    fi
    
    log "✅ 清理完成"
}

# ============ 主程序 ============

log "========== 每日备份开始 (v2.1) =========="

# 检查磁盘
if [ ! -d "$BACKUP_DIR" ]; then
    log "FATAL: Backup directory not mounted: $BACKUP_DIR"
    exit 1
fi

# 1. 创建目录结构
setup_backup_structure

# 2. 备份 Memory
memory_count=$(backup_memory_categorized)

# 3. 备份 Skills  
skills_count=$(backup_skills_categorized)

# 4. 生成清单
generate_manifest

# 5. 创建压缩包
create_archive

# 6. 清理旧备份
cleanup_old_backups

# 7. 发送通知 (通过Kilo)
send_notification "$memory_count" "$skills_count"

log "========== 备份完成 =========="
