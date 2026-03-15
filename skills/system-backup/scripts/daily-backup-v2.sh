#!/bin/bash
#
# 重新整理的每日备份脚本 v2.2
# 清晰的目录结构 + 备份清单 + Kilo通知
#

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/YOUR_USERNAME"

BACKUP_DIR="/Volumes/cu/ocu"
LOG_FILE="/tmp/backup_memory.log"
DATE=$(date +%Y%m%d)
DATETIME=$(date +%Y%m%d_%H%M%S)

# 源目录
MEMORY_SOURCE="/Users/YOUR_USERNAME/.openclaw/workspace/memory"
WORKSPACE_SKILLS_SOURCE="/Users/YOUR_USERNAME/.openclaw/workspace/skills"

# 日志函数
log() {
    local msg="$(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

# 创建清晰的备份目录结构
setup_backup_structure() {
    log "创建备份目录结构..."
    
    # Memory 备份结构
    mkdir -p "$BACKUP_DIR/memory-backup/daily"
    mkdir -p "$BACKUP_DIR/memory-backup/archive"
    mkdir -p "$BACKUP_DIR/memory-backup/snapshots"
    mkdir -p "$BACKUP_DIR/memory-backup/evolution"
    mkdir -p "$BACKUP_DIR/memory-backup/reports"
    mkdir -p "$BACKUP_DIR/memory-backup/knowledge"
    mkdir -p "$BACKUP_DIR/memory-backup/index"
    mkdir -p "$BACKUP_DIR/memory-backup/config"
    
    # Skills 备份结构
    mkdir -p "$BACKUP_DIR/skills-backup/core"
    mkdir -p "$BACKUP_DIR/skills-backup/archived"
    mkdir -p "$BACKUP_DIR/skills-backup/suites"
    
    log "✅ 目录结构创建完成"
}

# 分类备份 Memory 文件
backup_memory_categorized() {
    # log "开始分类备份 Memory..."
    
    local memory_src="$MEMORY_SOURCE"
    local memory_dst="$BACKUP_DIR/memory-backup"
    local file_count=0
    
    # 1. 每日记忆文件
    # log "备份每日记忆..."
    for file in "$memory_src"/2*.md; do
        if [ -f "$file" ]; then
            cp "$file" "$memory_dst/daily/" 2>/dev/null
            ((file_count++))
        fi
    done
    
    # 2. 归档文件
    # log "备份归档文件..."
    if [ -d "$memory_src/archive" ]; then
        cp -r "$memory_src/archive"/* "$memory_dst/archive/" 2>/dev/null
        local archive_count=$(find "$memory_src/archive" -type f 2>/dev/null | wc -l)
        file_count=$((file_count + archive_count))
    fi
    
    # 3. 会话快照
    # log "备份会话快照..."
    if [ -d "$memory_src/session_states" ]; then
        cp -r "$memory_src/session_states"/* "$memory_dst/snapshots/" 2>/dev/null
    fi
    
    # 4. 进化系统
    # log "备份进化系统..."
    if [ -d "$memory_src/evolution" ]; then
        cp -r "$memory_src/evolution"/* "$memory_dst/evolution/" 2>/dev/null
    fi
    
    # 5. 报告文件
    # log "备份报告文件..."
    for file in "$memory_src"/*report*.json "$memory_src"/*report*.md; do
        if [ -f "$file" ]; then
            cp "$file" "$memory_dst/reports/" 2>/dev/null
            ((file_count++))
        fi
    done
    
    # 6. 知识图谱
    # log "备份知识图谱..."
    if [ -d "$memory_src/knowledge_graph" ]; then
        cp -r "$memory_src/knowledge_graph"/* "$memory_dst/knowledge/" 2>/dev/null
    fi
    
    # 7. 搜索索引
    # log "备份搜索索引..."
    if [ -d "$memory_src/index" ]; then
        cp -r "$memory_src/index"/* "$memory_dst/index/" 2>/dev/null
    fi
    
    # 8. 配置文件
    # log "备份配置文件..."
    for file in "$memory_src"/*.json; do
        if [ -f "$file" ]; then
            cp "$file" "$memory_dst/config/" 2>/dev/null
            ((file_count++))
        fi
    done
    
    log "✅ Memory 备份完成: $file_count 个文件"
    echo "$file_count"
}

# 分类备份 Skills
backup_skills_categorized() {
    # log "开始分类备份 Skills..."
    
    local skills_src="$WORKSPACE_SKILLS_SOURCE"
    local skills_dst="$BACKUP_DIR/skills-backup"
    local total_count=0
    
    # 遍历所有技能包
    for skill_dir in "$skills_src"/*/; do
        if [ -d "$skill_dir" ]; then
            local skill_name=$(basename "$skill_dir")
            local file_count=$(find "$skill_dir" -type f 2>/dev/null | wc -l)
            
            # 分类
            if [ "$skill_name" = "archived" ]; then
                # 已归档技能
                cp -r "$skill_dir" "$skills_dst/archived/" 2>/dev/null
                log "  📁 [归档] $skill_name: $file_count 个文件"
            elif [[ "$skill_name" == *"-suite" ]]; then
                # 套件
                cp -r "$skill_dir" "$skills_dst/suites/" 2>/dev/null
                log "  📦 [套件] $skill_name: $file_count 个文件"
            else
                # 核心技能
                cp -r "$skill_dir" "$skills_dst/core/" 2>/dev/null
                log "  🔧 [核心] $skill_name: $file_count 个文件"
            fi
            
            total_count=$((total_count + file_count))
        fi
    done
    
    log "✅ Skills 备份完成: $total_count 个文件"
    echo "$total_count"
}

# 生成备份清单
generate_manifest() {
    log "生成备份清单..."
    
    local manifest_file="$BACKUP_DIR/backup-manifest-$DATE.json"
    
    # 统计各类文件数量
    local daily_count=$(find "$BACKUP_DIR/memory-backup/daily" -type f 2>/dev/null | wc -l)
    local archive_count=$(find "$BACKUP_DIR/memory-backup/archive" -type f 2>/dev/null | wc -l)
    local core_count=$(find "$BACKUP_DIR/skills-backup/core" -type f 2>/dev/null | wc -l)
    local archived_count=$(find "$BACKUP_DIR/skills-backup/archived" -type f 2>/dev/null | wc -l)
    
    cat > "$manifest_file" << EOF
{
  "backup_date": "$DATE",
  "backup_time": "$(date '+%H:%M:%S')",
  "version": "2.2",
  "structure": {
    "memory": {
      "daily_notes": $daily_count,
      "archive": $archive_count,
      "snapshots": $(find "$BACKUP_DIR/memory-backup/snapshots" -type f 2>/dev/null | wc -l),
      "evolution": $(find "$BACKUP_DIR/memory-backup/evolution" -type f 2>/dev/null | wc -l),
      "reports": $(find "$BACKUP_DIR/memory-backup/reports" -type f 2>/dev/null | wc -l),
      "knowledge": $(find "$BACKUP_DIR/memory-backup/knowledge" -type f 2>/dev/null | wc -l),
      "index": $(find "$BACKUP_DIR/memory-backup/index" -type f 2>/dev/null | wc -l),
      "config": $(find "$BACKUP_DIR/memory-backup/config" -type f 2>/dev/null | wc -l)
    },
    "skills": {
      "core": $core_count,
      "archived": $archived_count,
      "suites": $(find "$BACKUP_DIR/skills-backup/suites" -type f 2>/dev/null | wc -l)
    }
  }
}
EOF
    
    log "✅ 备份清单生成: $manifest_file"
}

# 创建压缩包
create_archive() {
    log "创建压缩包..."
    
    mkdir -p "$BACKUP_DIR/full-backups"
    local archive_name="openclaw-backup-${DATETIME}.tar.gz"
    
    if tar -czf "$BACKUP_DIR/full-backups/$archive_name" \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.DS_Store' \
        --exclude='*.backup' \
        -C "$BACKUP_DIR" \
        memory-backup/ \
        skills-backup/ \
        backup-manifest-$DATE.json \
        2>/dev/null; then
        log "✅ 压缩包创建: $archive_name"
        local size=$(du -h "$BACKUP_DIR/full-backups/$archive_name" | cut -f1)
        log "   大小: $size"
        
        # 更新 latest 链接
        rm -f "$BACKUP_DIR/full-backups/latest"
        ln -s "$BACKUP_DIR/full-backups/$archive_name" "$BACKUP_DIR/full-backups/latest"
    else
        log "❌ 压缩包创建失败"
    fi
}

# 发送通知 (精简版)
send_notification() {
    local memory_count=$1
    local skills_count=$2
    
    # 获取压缩包大小
    local backup_size="未知"
    if [ -f "$BACKUP_DIR/full-backups/latest" ]; then
        backup_size=$(du -h "$BACKUP_DIR/full-backups/latest" 2>/dev/null | cut -f1)
    fi
    
    # 构建通知消息（极简版）
    local message="💾 备份完成 | $(date '+%m-%d %H:%M') | Memory:$memory_count | Skills:$skills_count | $backup_size"
    
    # 使用 broadcaster.py 直接发送到群聊
    python3 ~/.openclaw/workspace/agents/kilo/broadcaster.py \
        --task send \
        --message "$message" \
        --target group \
        2>/dev/null
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

log "========== 每日备份开始 (v2.2) =========="

# 检查磁盘
if [ ! -d "$BACKUP_DIR" ]; then
    log "FATAL: 备份目录未挂载: $BACKUP_DIR"
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
log "ALL BACKUPS COMPLETED SUCCESSFULLY"
