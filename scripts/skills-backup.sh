#!/bin/bash
# ============================================================
# 技能包外部存储自动备份脚本
# 备份路径: /Volumes/cu/ocu/skills-backup/
# ============================================================

set -e

# 配置
SOURCE_DIR="$HOME/.openclaw/workspace/skills"
BACKUP_DIR="/Volumes/cu/ocu/skills-backup"
LOG_FILE="$BACKUP_DIR/backup.log"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="skills-backup-${DATE}.tar.gz"
LATEST_LINK="$BACKUP_DIR/latest"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查外部存储是否挂载
check_mount() {
    if [ ! -d "$BACKUP_DIR" ]; then
        log "${RED}错误: 外部存储未挂载或未创建备份目录${NC}"
        mkdir -p "$BACKUP_DIR" 2>/dev/null || {
            log "${RED}无法创建备份目录: $BACKUP_DIR${NC}"
            exit 1
        }
    fi
}

# 检查源目录
check_source() {
    if [ ! -d "$SOURCE_DIR" ]; then
        log "${RED}错误: 源目录不存在: $SOURCE_DIR${NC}"
        exit 1
    fi
}

# 执行备份
do_backup() {
    log "${YELLOW}开始备份技能包...${NC}"
    
    # 创建备份
    tar -czf "$BACKUP_DIR/$BACKUP_NAME" \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.DS_Store' \
        --exclude='*.backup' \
        -C "$HOME/.openclaw/workspace" \
        skills/ 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "${GREEN}✅ 备份成功: $BACKUP_NAME${NC}"
        
        # 更新latest链接
        rm -f "$LATEST_LINK"
        ln -s "$BACKUP_DIR/$BACKUP_NAME" "$LATEST_LINK"
        
        # 显示备份大小
        SIZE=$(du -h "$BACKUP_DIR/$BACKUP_NAME" | cut -f1)
        log "${GREEN}📦 备份大小: $SIZE${NC}"
        
        # 清理旧备份（保留最近30个）
        clean_old_backups
        
        return 0
    else
        log "${RED}❌ 备份失败${NC}"
        return 1
    fi
}

# 清理旧备份
clean_old_backups() {
    local count=$(ls -1 "$BACKUP_DIR"/skills-backup-*.tar.gz 2>/dev/null | wc -l)
    if [ $count -gt 30 ]; then
        log "${YELLOW}清理旧备份 (保留最近30个)...${NC}"
        ls -1t "$BACKUP_DIR"/skills-backup-*.tar.gz | tail -n +31 | xargs rm -f
        log "${GREEN}✅ 已清理旧备份${NC}"
    fi
}

# 显示备份状态
show_status() {
    log "${YELLOW}=== 备份状态 ===${NC}"
    log "备份目录: $BACKUP_DIR"
    log "备份数量: $(ls -1 "$BACKUP_DIR"/skills-backup-*.tar.gz 2>/dev/null | wc -l)"
    log "最新备份: $(ls -1t "$BACKUP_DIR"/skills-backup-*.tar.gz 2>/dev/null | head -1)"
    log "磁盘使用: $(df -h "$BACKUP_DIR" | tail -1 | awk '{print $3 "/" $2 " (" $5 ")"}')"
}

# 主流程
main() {
    log "========================================"
    log "技能包备份任务开始"
    log "========================================"
    
    check_mount
    check_source
    do_backup
    show_status
    
    log "========================================"
    log "备份任务完成"
    log "========================================"
}

# 根据参数执行
 case "${1:-backup}" in
    backup)
        main
        ;;
    status)
        show_status
        ;;
    clean)
        log "${YELLOW}清理所有备份...${NC}"
        rm -f "$BACKUP_DIR"/skills-backup-*.tar.gz
        rm -f "$LATEST_LINK"
        log "${GREEN}✅ 已清理所有备份${NC}"
        ;;
    *)
        echo "用法: $0 [backup|status|clean]"
        echo "  backup - 执行备份 (默认)"
        echo "  status - 查看备份状态"
        echo "  clean  - 清理所有备份"
        exit 1
        ;;
esac
