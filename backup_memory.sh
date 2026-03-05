#!/bin/bash

# OpenClaw 记忆文件和技能包备份脚本（修复版）
# 修复：改进文件检测逻辑，修复 cron 环境下的路径问题

BACKUP_DIR="/Volumes/cu/ocu"
MEMORY_SOURCE="/Users/zhaoruicn/.openclaw/workspace/memory"
SKILLS_SOURCE="/Users/zhaoruicn/.openclaw/skills"
LOG_FILE="/tmp/backup_memory.log"
MAX_RETRIES=3
RETRY_DELAY=5

# 飞书通知配置
FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/8c3b0f1e-2d4a-4b5c-9e6f-7a8b9c0d1e2f"

# 日志函数
log() {
    local msg="$(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

# 检查源目录是否存在
check_source() {
    local source_dir=$1
    local name=$2
    
    if [ ! -d "$source_dir" ]; then
        log "ERROR: $name 源目录不存在: $source_dir"
        return 1
    fi
    
    local file_count=$(find "$source_dir" -type f 2>/dev/null | wc -l)
    if [ "$file_count" -eq 0 ]; then
        log "WARNING: $name 源目录为空: $source_dir"
        return 1
    fi
    
    log "INFO: $name 源目录检查通过，包含 $file_count 个文件"
    return 0
}

# 执行备份
perform_backup() {
    local source_dir=$1
    local dest_dir=$2
    local name=$3
    local attempt=$4
    
    log "Starting $name backup (attempt $attempt/$MAX_RETRIES)..."
    
    # 确保目标目录存在
    mkdir -p "$dest_dir"
    
    # 直接执行 rsync，不使用 -n 预检测
    # -a: 归档模式 -v: 详细 -u: 只更新较新的文件
    local rsync_output=$(rsync -avu "$source_dir/" "$dest_dir/" 2>&1)
    local rsync_exit=$?
    
    # 统计传输的文件数（排除目录和空行）
    local transfer_count=$(echo "$rsync_output" | grep -E '^>' | wc -l)
    
    if [ $rsync_exit -eq 0 ]; then
        if [ "$transfer_count" -eq 0 ]; then
            log "INFO: $name 没有新文件需要备份（所有文件已是最新）"
        else
            log "SUCCESS: $name 备份完成，传输了 $transfer_count 个文件"
            # 记录传输的文件列表
            echo "$rsync_output" | grep -E '^>' >> "$LOG_FILE" 2>/dev/null || true
        fi
        return 0
    else
        log "ERROR: $name backup failed with rsync exit code $rsync_exit"
        log "ERROR: $rsync_output"
        return 1
    fi
}

# 带重试的备份函数
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
    send_feishu_notify "failed" "磁盘未挂载" "磁盘未挂载"
    exit 1
fi

# 备份记忆文件
memory_success=false
memory_info=""
if backup_with_retry "$MEMORY_SOURCE" "$BACKUP_DIR/memory" "Memory"; then
    memory_success=true
    memory_files=$(find "$BACKUP_DIR/memory" -type f 2>/dev/null | wc -l)
    memory_info="$memory_files个文件"
else
    memory_info="失败"
fi

# 备份技能包
skills_success=false
skills_info=""
if backup_with_retry "$SKILLS_SOURCE" "$BACKUP_DIR/skills" "Skills"; then
    skills_success=true
    skills_files=$(find "$BACKUP_DIR/skills" -type f 2>/dev/null | wc -l)
    skills_info="$skills_files个文件"
else
    skills_info="失败"
fi

# 汇总结果
log "========== Backup Summary =========="
if [ "$memory_success" = true ] && [ "$skills_success" = true ]; then
    log "ALL BACKUPS COMPLETED SUCCESSFULLY"
    send_feishu_notify "success" "$memory_info" "$skills_info"
    exit 0
else
    [ "$memory_success" = false ] && log "FAILED: Memory backup"
    [ "$skills_success" = false ] && log "FAILED: Skills backup"
    send_feishu_notify "failed" "$memory_info" "$skills_info"
    exit 1
fi
