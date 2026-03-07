#!/bin/bash
# OpenClaw 恢复脚本
# 支持从每日备份或月度归档恢复

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

BACKUP_DIR="/Volumes/cu/ocu"
ARCHIVE_DIR="$BACKUP_DIR/archives"
OPENCLAW_DIR="/Users/zhaoruicn/.openclaw"

show_help() {
    echo "OpenClaw 恢复工具"
    echo ""
    echo "用法:"
    echo "  $0 list                    # 列出可用备份"
    echo "  $0 restore-daily           # 从每日备份恢复（恢复 memory 和 skills）"
    echo "  $0 restore-archive <日期>  # 从月度归档恢复（完整恢复）"
    echo "  $0 restore-config          # 仅恢复配置文件"
    echo ""
    echo "示例:"
    echo "  $0 restore-archive 2026-03-01"
    echo ""
}

list_backups() {
    echo "=== 每日备份 ==="
    echo "Memory: $BACKUP_DIR/memory/"
    echo "Skills: $BACKUP_DIR/skills/"
    echo "Workspace Skills: $BACKUP_DIR/workspace-skills/"
    echo "Config: $BACKUP_DIR/openclaw-config/"
    
    echo ""
    echo "=== 月度归档 ==="
    if [ -d "$ARCHIVE_DIR" ]; then
        ls -lh "$ARCHIVE_DIR"/openclaw-archive-*.tar.gz 2>/dev/null | tail -5
    else
        echo "无归档文件"
    fi
}

restore_daily() {
    echo "从每日备份恢复..."
    
    # 检查备份是否存在
    if [ ! -d "$BACKUP_DIR/memory" ]; then
        echo "错误: 未找到备份目录 $BACKUP_DIR/memory"
        exit 1
    fi
    
    # 停止 OpenClaw
    echo "1. 停止 OpenClaw Gateway..."
    openclaw gateway stop 2>/dev/null || true
    sleep 2
    
    # 备份当前（安全）
    echo "2. 备份当前数据（安全）..."
    if [ -d "$OPENCLAW_DIR" ]; then
        mv "$OPENCLAW_DIR" "$OPENCLAW_DIR-backup-$(date +%Y%m%d_%H%M%S)"
    fi
    
    # 恢复 memory
    echo "3. 恢复 Memory..."
    mkdir -p "$OPENCLAW_DIR/workspace/memory"
    cp -r "$BACKUP_DIR/memory/"* "$OPENCLAW_DIR/workspace/memory/" 2>/dev/null || true
    
    # 恢复 skills
    echo "4. 恢复 Skills..."
    mkdir -p "$OPENCLAW_DIR/skills"
    cp -r "$BACKUP_DIR/skills/"* "$OPENCLAW_DIR/skills/" 2>/dev/null || true
    
    # 恢复 workspace skills
    echo "5. 恢复 Workspace Skills..."
    mkdir -p "$OPENCLAW_DIR/workspace/skills"
    cp -r "$BACKUP_DIR/workspace-skills/"* "$OPENCLAW_DIR/workspace/skills/" 2>/dev/null || true
    
    # 恢复配置
    echo "6. 恢复配置文件..."
    if [ -d "$BACKUP_DIR/openclaw-config" ]; then
        cp -r "$BACKUP_DIR/openclaw-config/"* "$OPENCLAW_DIR/" 2>/dev/null || true
    fi
    
    # 启动
    echo "7. 启动 OpenClaw..."
    openclaw gateway start
    
    echo ""
    echo "✅ 恢复完成！"
    echo "验证: openclaw status"
}

restore_archive() {
    local date=$1
    local archive_file="$ARCHIVE_DIR/openclaw-archive-$date.tar.gz"
    
    if [ -z "$date" ]; then
        echo "错误: 请指定日期，例如: $0 restore-archive 2026-03-01"
        exit 1
    fi
    
    if [ ! -f "$archive_file" ]; then
        echo "错误: 未找到归档文件: $archive_file"
        echo "可用归档:"
        ls "$ARCHIVE_DIR"/openclaw-archive-*.tar.gz 2>/dev/null
        exit 1
    fi
    
    echo "从归档恢复: $archive_file"
    echo ""
    
    # 确认
    read -p "这将覆盖当前 OpenClaw 目录，是否继续? (y/N) " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "已取消"
        exit 0
    fi
    
    # 停止 OpenClaw
    echo "1. 停止 OpenClaw Gateway..."
    openclaw gateway stop 2>/dev/null || true
    sleep 2
    
    # 备份当前
    echo "2. 备份当前数据..."
    if [ -d "$OPENCLAW_DIR" ]; then
        mv "$OPENCLAW_DIR" "$OPENCLAW_DIR-backup-$(date +%Y%m%d_%H%M%S)"
    fi
    
    # 解压归档
    echo "3. 解压归档..."
    cd "$HOME"
    tar -xzf "$archive_file"
    
    if [ $? -ne 0 ]; then
        echo "错误: 解压失败"
        exit 1
    fi
    
    # 启动
    echo "4. 启动 OpenClaw..."
    openclaw gateway start
    
    echo ""
    echo "✅ 恢复完成！"
    echo "验证: openclaw status"
}

restore_config() {
    echo "仅恢复配置文件..."
    
    if [ ! -d "$BACKUP_DIR/openclaw-config" ]; then
        echo "错误: 未找到配置备份"
        exit 1
    fi
    
    echo "1. 停止 OpenClaw..."
    openclaw gateway stop 2>/dev/null || true
    sleep 2
    
    echo "2. 恢复配置文件..."
    cp -r "$BACKUP_DIR/openclaw-config/"* "$OPENCLAW_DIR/" 2>/dev/null || true
    
    echo "3. 启动 OpenClaw..."
    openclaw gateway start
    
    echo "✅ 配置恢复完成"
}

# 主程序
case "$1" in
    list)
        list_backups
        ;;
    restore-daily)
        restore_daily
        ;;
    restore-archive)
        restore_archive "$2"
        ;;
    restore-config)
        restore_config
        ;;
    *)
        show_help
        ;;
esac
