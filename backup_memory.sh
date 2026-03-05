#!/bin/bash

# OpenClaw 记忆文件和技能包备份脚本
# 包含执行检查和重试机制

BACKUP_DIR="/Volumes/cu/ocu"
MEMORY_SOURCE="$HOME/.openclaw/workspace/memory"
SKILLS_SOURCE="$HOME/.openclaw/skills"
LOG_FILE="$BACKUP_DIR/backups/backup.log"
MAX_RETRIES=3
RETRY_DELAY=5

# 飞书通知配置
FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/8c3b0f1e-2d4a-4b5c-9e6f-7a8b9c0d1e2f"

# 确保备份目录存在
mkdir -p "$BACKUP_DIR/memory"
mkdir -p "$BACKUP_DIR/skills"
mkdir -p "$BACKUP_DIR/backups"

# 日志函数
log() {
    local msg="$(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "$msg"
    # 尝试写入日志文件，失败则忽略（cron环境下可能没有权限）
    if [ -w "$BACKUP_DIR/backups" ] || [ ! -f "$LOG_FILE" ]; then
        echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
    fi
}

# 检查源目录是否存在
check_source() {
    local source_dir=$1
    local name=$2
    
    if [ ! -d "$source_dir" ]; then
        log "ERROR: $name 源目录不存在: $source_dir"
        return 1
    fi
    
    # 检查是否有文件需要备份
    local file_count=$(find "$source_dir" -type f 2>/dev/null | wc -l)
    if [ "$file_count" -eq 0 ]; then
        log "WARNING: $name 源目录为空: $source_dir"
        return 1
    fi
    
    return 0
}

# 执行备份并验证
perform_backup() {
    local source_dir=$1
    local dest_dir=$2
    local name=$3
    local attempt=$4
    
    log "Starting $name backup (attempt $attempt/$MAX_RETRIES)..."
    
    # 统计需要传输的文件数（新增或修改的）
    local transfer_count=$(rsync -avni --delete "$source_dir/" "$dest_dir/" 2>/dev/null | grep -E '^<' | wc -l)
    
    if [ "$transfer_count" -eq 0 ]; then
        log "INFO: $name 没有新文件需要备份（所有文件已是最新）"
        return 0
    fi
    
    log "INFO: $name 检测到 $transfer_count 个新文件/修改文件需要备份"
    
    # 使用 rsync 进行增量备份，只传输变化的文件
    if rsync -av --delete "$source_dir/" "$dest_dir/" >> "$LOG_FILE" 2>&1; then
        log "SUCCESS: $name 备份完成，传输了 $transfer_count 个文件"
        return 0
    else
        log "ERROR: $name backup failed with rsync error"
        return 1
    fi
}

# 带重试的备份函数
backup_with_retry() {
    local source_dir=$1
    local dest_dir=$2
    local name=$3
    
    # 首先检查源目录
    if ! check_source "$source_dir" "$name"; then
        return 1
    fi
    
    # 尝试备份（带重试）
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

# 发送飞书通知函数
send_feishu_notify() {
    local status=$1
    local memory_info=$2
    local skills_info=$3
    local timestamp=$(date '+%Y-%m-%d %H:%M')
    
    if [ "$status" = "success" ]; then
        curl -s -X POST "$FEISHU_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"✅ 备份完成 ($timestamp)\\nMemory: $memory_info\\nSkills: $skills_info\"}}" \
            > /dev/null 2>&1
    else
        curl -s -X POST "$FEISHU_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"❌ 备份失败 ($timestamp)\\nMemory: $memory_info\\nSkills: $skills_info\"}}" \
            > /dev/null 2>&1
    fi
}

# ============ 主程序 ============

log "========== Backup Job Started =========="

# 检查备份磁盘是否挂载
if [ ! -d "$BACKUP_DIR" ]; then
    log "FATAL ERROR: Backup directory not mounted: $BACKUP_DIR"
    exit 1
fi

# 备份记忆文件
memory_success=false
if backup_with_retry "$MEMORY_SOURCE" "$BACKUP_DIR/memory" "Memory"; then
    memory_success=true
fi

# 备份技能包
skills_success=false
if backup_with_retry "$SKILLS_SOURCE" "$BACKUP_DIR/skills" "Skills"; then
    skills_success=true
fi

# 汇总结果
log "========== Backup Summary =========="
if [ "$memory_success" = true ] && [ "$skills_success" = true ]; then
    log "ALL BACKUPS COMPLETED SUCCESSFULLY"
    # 发送成功通知
    memory_files=$(find "$BACKUP_DIR/memory" -type f 2>/dev/null | wc -l)
    skills_files=$(find "$BACKUP_DIR/skills" -type f 2>/dev/null | wc -l)
    send_feishu_notify "success" "$memory_files个文件" "$skills_files个文件"
    exit 0
else
    [ "$memory_success" = false ] && log "FAILED: Memory backup"
    [ "$skills_success" = false ] && log "FAILED: Skills backup"
    # 发送失败通知
    mem_status=$([ "$memory_success" = true ] && echo "成功" || echo "失败")
    skill_status=$([ "$skills_success" = true ] && echo "成功" || echo "失败")
    send_feishu_notify "failed" "$mem_status" "$skill_status"
    exit 1
fi
