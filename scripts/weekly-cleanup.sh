#!/bin/bash
# OpenClaw + Claude Code 每周系统清理脚本
# 执行时间：每周日03:00

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

LOG_FILE="/Users/zhaoruicn/.openclaw/ops/logs/tasks/ouc_cleanup.log"

log() {
    echo "$(date '+%Y-%m-%dT%H:%M:%S%z') - $1" | tee -a "$LOG_FILE"
}

log "========== Weekly Cleanup Started =========="

# 1. OUC备份目录清理
log "[1/4] 清理OUC备份目录..."
BACKUP_DIR="/Volumes/cu/ocu/skills-backup"
if [ -d "$BACKUP_DIR" ]; then
    # 保留最新3个压缩包
    count=$(ls -1t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
    if [ "${count:-0}" -gt 3 ]; then
        ls -1t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null
        log "  清理完成，保留最新3个"
    else
        log "  无需清理"
    fi
    
    # 清理archived目录超过7天的文件
    find "$BACKUP_DIR/archived" -type f -mtime +7 -delete 2>/dev/null
    log "  archived目录已清理"
else
    log "  OUC目录不存在，跳过"
fi

# 2. OpenClaw Workspace清理
log "[2/4] 清理Workspace超过7天的文件..."
WORKSPACE="/Users/zhaoruicn/.openclaw/workspace"
cd "$WORKSPACE" || exit 1

# 删除超过7天的文档文件
find . -maxdepth 1 -type f \( -name "*.docx" -o -name "*.xlsx" -o -name "*.pptx" -o -name "*.html" -o -name "*.pdf" \) -mtime +7 -delete 2>/dev/null
find . -maxdepth 1 -type f -name "test*.png" -mtime +7 -delete 2>/dev/null
find . -maxdepth 1 -type f -name "test*.jpg" -mtime +7 -delete 2>/dev/null
find . -maxdepth 1 -type f -name "*-for-trae.zip" -delete 2>/dev/null
log "  Workspace清理完成"

# 3. Claude Code缓存清理
log "[3/4] 清理Claude Code缓存..."
CC_CACHE="/Users/zhaoruicn/.claude/plugins/cache"
if [ -d "$CC_CACHE" ]; then
    rm -rf "$CC_CACHE"/* 2>/dev/null
    log "  Claude Code缓存已清理"
else
    log "  Claude缓存目录不存在"
fi

# 清理CC backups旧版本
CC_BACKUPS="/Users/zhaoruicn/.claude/backups"
if [ -d "$CC_BACKUPS" ]; then
    count=$(ls -1t "$CC_BACKUPS"/*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
    if [ "${count:-0}" -gt 3 ]; then
        ls -1t "$CC_BACKUPS"/*.tar.gz 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null
        log "  Claude backups清理完成，保留最新3个"
    fi
fi

# 4. 废弃项目检测
log "[4/4] 检测废弃项目..."
if [ -d "/Users/zhaoruicn/.openclaw/workspace/xuezi-kb-tauri" ]; then
    log "  发现废弃项目 xuezi-kb-tauri，建议删除"
fi

# 检测skills-backup里的archived等大目录
BACKUP_CHECK="/Volumes/cu/ocu/skills-backup"
if [ -d "$BACKUP_CHECK" ]; then
    for dir in core archived; do
        if [ -d "$BACKUP_CHECK/$dir" ]; then
            size=$(du -sh "$BACKUP_CHECK/$dir" 2>/dev/null | cut -f1)
            log "  发现大目录 skills-backup/$dir ($size)，建议排除"
        fi
    done
fi

log "========== Weekly Cleanup Complete =========="
