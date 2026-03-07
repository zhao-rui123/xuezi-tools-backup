#!/bin/bash
# OpenClaw 完整备份脚本（增强版）
# 支持：Memory + Skills + 系统配置 + Workspace Skills

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

BACKUP_DIR="/Volumes/cu/ocu"
LOG_FILE="/tmp/backup_memory.log"
MAX_RETRIES=3
RETRY_DELAY=5

# 源目录
MEMORY_SOURCE="/Users/zhaoruicn/.openclaw/workspace/memory"
SKILLS_SOURCE="/Users/zhaoruicn/.openclaw/skills"
WORKSPACE_SKILLS_SOURCE="/Users/zhaoruicn/.openclaw/workspace/skills"
OPENCLAW_CONFIG="/Users/zhaoruicn/.openclaw"

# 日志函数
log() {
    local msg="$(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

# 检查源目录
check_source() {
    local source_dir=$1
    local name=$2
    
    if [ ! -d "$source_dir" ]; then
        log "WARNING: $name 目录不存在: $source_dir"
        return 1
    fi
    
    local file_count=$(find "$source_dir" -type f 2>/dev/null | wc -l)
    if [ "$file_count" -eq 0 ]; then
        log "WARNING: $name 目录为空: $source_dir"
        return 1
    fi
    
    log "INFO: $name 检查通过，包含 $file_count 个文件"
    return 0
}

# 执行备份
perform_backup() {
    local source_dir=$1
    local dest_dir=$2
    local name=$3
    local attempt=$4
    
    log "Starting $name backup (attempt $attempt/$MAX_RETRIES)..."
    
    mkdir -p "$dest_dir"
    
    local rsync_output=$(rsync -avu "$source_dir/" "$dest_dir/" 2>&1)
    local rsync_exit=$?
    
    local transfer_count=$(echo "$rsync_output" | grep -E '^>' | wc -l)
    
    if [ $rsync_exit -eq 0 ]; then
        if [ "$transfer_count" -eq 0 ]; then
            log "INFO: $name 已是最新，无需更新"
        else
            log "SUCCESS: $name 备份完成，传输 $transfer_count 个文件"
        fi
        return 0
    else
        log "ERROR: $name backup failed (exit $rsync_exit)"
        return 1
    fi
}

# 备份 OpenClaw 配置
backup_openclaw_config() {
    log "Starting OpenClaw config backup..."
    
    local config_backup_dir="$BACKUP_DIR/openclaw-config"
    mkdir -p "$config_backup_dir"
    
    # 备份关键配置文件
    local files_to_backup=(
        "openclaw.json"
        "agents/main/agent/models.json"
        "agents/main/agent/auth-profiles.json"
    )
    
    local backup_count=0
    for file in "${files_to_backup[@]}"; do
        local src="$OPENCLAW_CONFIG/$file"
        local dest_dir="$config_backup_dir/$(dirname $file)"
        
        if [ -f "$src" ]; then
            mkdir -p "$dest_dir"
            cp "$src" "$dest_dir/"
            ((backup_count++))
            log "INFO: 备份配置 $file"
        fi
    done
    
    # 备份 cron 配置
    if [ -d "$OPENCLAW_CONFIG/cron" ]; then
        cp -r "$OPENCLAW_CONFIG/cron" "$config_backup_dir/"
        log "INFO: 备份 cron 配置"
        ((backup_count++))
    fi
    
    log "SUCCESS: OpenClaw 配置备份完成 ($backup_count 项)"
}

# 带重试的备份
backup_with_retry() {
    local source_dir=$1
    local dest_dir=$2
    local name=$3
    
    if ! check_source "$source_dir" "$name"; then
        return 1
    fi
    
    for attempt in $(seq 1 $MAX_RETRIES); do
        if perform_backup "$source_dir" "$dest_dir" "$name" "$attempt"; then
            return 0
        fi
        
        if [ $attempt -lt $MAX_RETRIES ]; then
            log "Waiting ${RETRY_DELAY}s before retry..."
            sleep $RETRY_DELAY
        fi
    done
    
    log "FAILED: $name backup failed after $MAX_RETRIES attempts"
    return 1
}

# 发送通知
send_notify() {
    local status=$1
    local memory_info=$2
    local skills_info=$3
    local ws_skills_info=$4
    local config_info=$5
    local timestamp=$(date '+%Y-%m-%d %H:%M')
    local notify_script="/Users/zhaoruicn/.openclaw/workspace/scripts/feishu-notify.sh"
    
    if [ "$status" = "success" ]; then
        "$notify_script" send "✅ 每日备份完成 ($timestamp)

📁 Memory: $memory_info
📁 Skills: $skills_info  
📁 Workspace Skills: $ws_skills_info
⚙️ Config: $config_info

备份位置: /Volumes/cu/ocu/"
    else
        "$notify_script" send "❌ 每日备份失败 ($timestamp)

请检查日志: /tmp/backup_memory.log"
    fi
}

# ============ 主程序 ============

log "========== Daily Backup Started =========="

# 检查磁盘
if [ ! -d "$BACKUP_DIR" ]; then
    log "FATAL: Backup directory not mounted: $BACKUP_DIR"
    send_notify "failed" "磁盘未挂载" "-" "-" "-"
    exit 1
fi

# 备份 Memory
memory_success=false
memory_info="0个文件"
if backup_with_retry "$MEMORY_SOURCE" "$BACKUP_DIR/memory" "Memory"; then
    memory_success=true
    memory_files=$(find "$BACKUP_DIR/memory" -type f 2>/dev/null | wc -l)
    memory_info="$memory_files个文件"
fi

# 备份 Skills
skills_success=false
skills_info="0个文件"
if backup_with_retry "$SKILLS_SOURCE" "$BACKUP_DIR/skills" "Skills"; then
    skills_success=true
    skills_files=$(find "$BACKUP_DIR/skills" -type f 2>/dev/null | wc -l)
    skills_info="$skills_files个文件"
fi

# 备份 Workspace Skills
ws_skills_success=false
ws_skills_info="0个文件"
if backup_with_retry "$WORKSPACE_SKILLS_SOURCE" "$BACKUP_DIR/workspace-skills" "Workspace Skills"; then
    ws_skills_success=true
    ws_skills_files=$(find "$BACKUP_DIR/workspace-skills" -type f 2>/dev/null | wc -l)
    ws_skills_info="$ws_skills_files个文件"
    
    # 额外生成 tar.gz 压缩包（用于分享和恢复）
    log "Creating tar.gz archive for skills..."
    mkdir -p "$BACKUP_DIR/skills-backup"
    DATE=$(date +%Y%m%d_%H%M%S)
    BACKUP_NAME="skills-backup-${DATE}.tar.gz"
    LATEST_LINK="$BACKUP_DIR/skills-backup/latest"
    
    tar -czf "$BACKUP_DIR/skills-backup/$BACKUP_NAME" \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.DS_Store' \
        --exclude='*.backup' \
        -C "$BACKUP_DIR" \
        workspace-skills/ 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS: tar.gz archive created: $BACKUP_NAME"
        # 更新 latest 链接
        rm -f "$LATEST_LINK"
        ln -s "$BACKUP_DIR/skills-backup/$BACKUP_NAME" "$LATEST_LINK"
        # 清理旧备份（保留最近30个）
        local count=$(ls -1 "$BACKUP_DIR/skills-backup"/skills-backup-*.tar.gz 2>/dev/null | wc -l)
        if [ $count -gt 30 ]; then
            log "Cleaning old tar.gz backups (keeping 30)..."
            ls -1t "$BACKUP_DIR/skills-backup"/skills-backup-*.tar.gz | tail -n +31 | xargs rm -f
        fi
        ws_skills_info="$ws_skills_info + tar.gz"
    else
        log "WARNING: Failed to create tar.gz archive"
    fi
fi

# 备份 OpenClaw 配置
backup_openclaw_config
config_info="已备份"

# 汇总
log "========== Backup Summary =========="
if [ "$memory_success" = true ] && [ "$skills_success" = true ] && [ "$ws_skills_success" = true ]; then
    log "ALL BACKUPS COMPLETED SUCCESSFULLY"
    send_notify "success" "$memory_info" "$skills_info" "$ws_skills_info" "$config_info"
    exit 0
else
    [ "$memory_success" = false ] && log "FAILED: Memory backup"
    [ "$skills_success" = false ] && log "FAILED: Skills backup"
    [ "$ws_skills_success" = false ] && log "FAILED: Workspace Skills backup"
    send_notify "failed" "$memory_info" "$skills_info" "$ws_skills_info" "$config_info"
    exit 1
fi
