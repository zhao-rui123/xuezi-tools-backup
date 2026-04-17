#!/bin/bash
#
# 重新整理的每日备份脚本 v2.4
# 清晰的目录结构 + 备份清单 + Kilo通知
# v2.3: 添加set -e确保错误时退出
# v2.4: 修复cp静默吞错误 + 备份workspace核心配置 + 只打包memory-suite-v4
# v2.5: 修复通配符bug(safe_cp_dir) + tar失败正确返回错误码
#

set -e  # 任何命令失败立即退出

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

# 确保 /Volumes/cu/ocu 挂载可用（cron可能没有自动挂载）
if [ ! -d "/Volumes/cu/ocu" ]; then
    # 尝试挂载
    mkdir -p /Volumes/cu 2>/dev/null || true
fi

BACKUP_DIR="/Volumes/cu/ocu"
LOG_FILE="/tmp/backup_memory.log"
DATE=$(date +%Y%m%d)
DATETIME=$(date +%Y%m%d_%H%M%S)

# 源目录
MEMORY_SOURCE="/Users/zhaoruicn/.openclaw/workspace/memory"
WORKSPACE_SKILLS_SOURCE="/Users/zhaoruicn/.openclaw/workspace/skills"

# 日志函数
log() {
    local msg="$(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

# 安全复制函数：替代 cp 2>/dev/null，记录错误但不中断
safe_cp() {
    local src="$1"
    local dst="$2"
    local opts="${3:-}"
    if [ -n "$opts" ]; then
        if ! cp $opts "$src" "$dst" 2>>"$LOG_FILE"; then
            log "⚠️ cp 失败: $src -> $dst"
            return 1
        fi
    else
        if ! cp "$src" "$dst" 2>>"$LOG_FILE"; then
            log "⚠️ cp 失败: $src -> $dst"
            return 1
        fi
    fi
    return 0
}

# 安全复制目录内容：避免通配符bug，正确处理空目录
# 用法: safe_cp_dir <源目录> <目标目录>
safe_cp_dir() {
    local src_dir="$1"
    local dst_dir="$2"
    if [ ! -d "$src_dir" ]; then
        return 0  # 源目录不存在，静默跳过
    fi
    local count
    count=$(find "$src_dir" -maxdepth 1 -mindepth 1 2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -eq 0 ]; then
        log "  ℹ️ 目录为空（跳过）: $src_dir"
        return 0
    fi
    if ! cp -r "$src_dir"/. "$dst_dir/" 2>>"$LOG_FILE"; then
        log "⚠️ cp 目录失败: $src_dir -> $dst_dir"
        return 1
    fi
    return 0
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
    local memory_src="$MEMORY_SOURCE"
    local memory_dst="$BACKUP_DIR/memory-backup"
    local file_count=0
    local cp_errors=0
    
    # 1. 每日记忆文件
    for file in "$memory_src"/2*.md; do
        if [ -f "$file" ]; then
            if safe_cp "$file" "$memory_dst/daily/"; then
                ((file_count++)) || true
            else
                ((cp_errors++)) || true
            fi
        fi
    done
    
    # 2. 归档文件
    if safe_cp_dir "$memory_src/archive" "$memory_dst/archive"; then
        local archive_count=$(find "$memory_src/archive" -type f 2>/dev/null | wc -l | tr -d ' ')
        file_count=$((file_count + archive_count))
    else
        ((cp_errors++)) || true
    fi
    
    # 3. 会话快照
    safe_cp_dir "$memory_src/session_states" "$memory_dst/snapshots" || ((cp_errors++)) || true
    
    # 4. 进化系统
    safe_cp_dir "$memory_src/evolution" "$memory_dst/evolution" || ((cp_errors++)) || true
    
    # 5. 报告文件
    for file in "$memory_src"/*report*.json "$memory_src"/*report*.md; do
        if [ -f "$file" ]; then
            if safe_cp "$file" "$memory_dst/reports/"; then
                ((file_count++)) || true
            else
                ((cp_errors++)) || true
            fi
        fi
    done
    
    # 6. 知识图谱
    safe_cp_dir "$memory_src/knowledge_graph" "$memory_dst/knowledge" || ((cp_errors++)) || true
    
    # 7. 搜索索引
    safe_cp_dir "$memory_src/index" "$memory_dst/index" || ((cp_errors++)) || true
    
    # 8. 配置文件
    for file in "$memory_src"/*.json; do
        if [ -f "$file" ]; then
            if safe_cp "$file" "$memory_dst/config/"; then
                ((file_count++)) || true
            else
                ((cp_errors++)) || true
            fi
        fi
    done
    
    if [ "$cp_errors" -gt 0 ]; then
        log "⚠️ Memory 备份完成但有 $cp_errors 个错误，请查看日志: $LOG_FILE"
    else
        log "✅ Memory 备份完成: $file_count 个文件"
    fi
    echo "$file_count"
}

# 备份 workspace 根目录核心配置文件
backup_workspace_configs() {
    local ws_root="/Users/zhaoruicn/.openclaw/workspace"
    local config_dst="$BACKUP_DIR/workspace-configs"
    mkdir -p "$config_dst"
    
    local config_count=0
    local config_errors=0
    local config_files=("MEMORY.md" "SOUL.md" "AGENTS.md" "USER.md" "TOOLS.md" "HEARTBEAT.md")
    
    for cfg in "${config_files[@]}"; do
        if [ -f "$ws_root/$cfg" ]; then
            if safe_cp "$ws_root/$cfg" "$config_dst/"; then
                ((config_count++)) || true
            else
                ((config_errors++)) || true
            fi
        else
            log "  ℹ️ 配置文件不存在（跳过）: $cfg"
        fi
    done
    
    if [ "$config_errors" -gt 0 ]; then
        log "⚠️ Workspace 配置备份有 $config_errors 个错误"
    else
        log "✅ Workspace 核心配置备份完成: $config_count 个文件"
    fi
    echo "$config_count"
}

# 只备份 memory-suite-v4（跳过大型skill目录）
backup_skills_categorized() {
    local skills_src="$WORKSPACE_SKILLS_SOURCE"
    local skills_dst="$BACKUP_DIR/skills-backup"
    local total_count=0
    local cp_errors=0
    
    # 只备份 memory-suite-v4（12M），跳过 glmv-stock-analyst(272M)、image-process(308M) 等大型目录
    local SKILLS_TO_BACKUP=("memory-suite-v4")
    
    for skill_name in "${SKILLS_TO_BACKUP[@]}"; do
        local skill_dir="$skills_src/$skill_name"
        if [ -d "$skill_dir" ]; then
            local file_count=$(find "$skill_dir" -type f 2>/dev/null | wc -l | tr -d ' ')
            local dir_size=$(du -sh "$skill_dir" 2>/dev/null | cut -f1)
            
            # 分类放入对应目录
            if [[ "$skill_name" == *"-suite"* ]]; then
                if cp -r "$skill_dir" "$skills_dst/suites/" 2>>"$LOG_FILE"; then
                    log "  📦 [套件] $skill_name: $file_count 个文件 ($dir_size)"
                else
                    log "  ❌ [套件] $skill_name: 复制失败！"
                    ((cp_errors++)) || true
                fi
            else
                if cp -r "$skill_dir" "$skills_dst/core/" 2>>"$LOG_FILE"; then
                    log "  🔧 [核心] $skill_name: $file_count 个文件 ($dir_size)"
                else
                    log "  ❌ [核心] $skill_name: 复制失败！"
                    ((cp_errors++)) || true
                fi
            fi
            
            total_count=$((total_count + file_count))
        else
            log "  ⚠️ Skill 目录不存在: $skill_name"
        fi
    done
    
    if [ "$cp_errors" -gt 0 ]; then
        log "⚠️ Skills 备份完成但有 $cp_errors 个错误"
    else
        log "✅ Skills 备份完成: $total_count 个文件（仅 memory-suite-v4）"
    fi
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
  "version": "2.4",
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
        --exclude='venv' \
        --exclude='node_modules' \
        --exclude='image-process/node_modules' \
        --exclude='electricity-v2' \
        --exclude='electricity-price-v2' \
        --exclude='projects' \
        --exclude='*.log' \
        --exclude='.git' \
        --exclude='.svn' \
        -C "$BACKUP_DIR" \
        memory-backup/ \
        skills-backup/ \
        workspace-configs/ \
        backup-manifest-$DATE.json \
        2>>"$LOG_FILE"; then
        log "✅ 压缩包创建: $archive_name"
        local size=$(du -h "$BACKUP_DIR/full-backups/$archive_name" | cut -f1)
        log "   大小: $size"
        
        # 更新 latest 链接
        rm -f "$BACKUP_DIR/full-backups/latest"
        ln -s "$BACKUP_DIR/full-backups/$archive_name" "$BACKUP_DIR/full-backups/latest"
    else
        log "❌ 压缩包创建失败，详见日志: $LOG_FILE"
        return 1
    fi
}

# 发送通知 (精简版)
send_notification() {
    local memory_count=$1
    local skills_count=$2
    local status="$3"  # "success" or "failure"
    
    # 验证备份有效性
    local backup_size="未知"
    local is_valid=false
    
    if [ -f "$BACKUP_DIR/full-backups/latest" ]; then
        local latest_file=$(readlink -f "$BACKUP_DIR/full-backups/latest" 2>/dev/null)
        if [ -f "$latest_file" ]; then
            backup_size=$(du -h "$latest_file" 2>/dev/null | cut -f1)
            local file_date=$(stat -f "%Sm" -t "%Y%m%d" "$latest_file" 2>/dev/null || stat -c "%y" "$latest_file" 2>/dev/null | cut -d' ' -f1 | tr -d '-')
            local today=$(date +%Y%m%d)
            
            # 检查是否是今天的备份且大小 > 100KB
            if [ "$file_date" = "$today" ] && [ -s "$latest_file" ]; then
                local size_bytes=$(stat -f "%z" "$latest_file" 2>/dev/null || stat -c "%s" "$latest_file" 2>/dev/null)
                if [ "$size_bytes" -gt 102400 ]; then
                    is_valid=true
                fi
            fi
        fi
    fi
    
    # 构建通知消息
    local message=""
    if [ "$status" = "failure" ] || [ "$is_valid" = false ]; then
        message="⚠️ 备份异常 | $(date '+%m-%d %H:%M') | Memory:$memory_count | Skills:$skills_count | $backup_size | 需检查"
        log "备份验证失败: size=$backup_size, is_valid=$is_valid"
    else
        message="💾 备份完成 | $(date '+%m-%d %H:%M') | Memory:$memory_count | Skills:$skills_count | $backup_size"
    fi
    
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

log "========== 每日备份开始 (v2.4) =========="

# 检查磁盘
if [ ! -d "$BACKUP_DIR" ]; then
    log "FATAL: 备份目录未挂载: $BACKUP_DIR"
    exit 1
fi

# 1. 创建目录结构
setup_backup_structure

# 2. 备份 Workspace 核心配置
config_count=$(backup_workspace_configs)

# 3. 备份 Memory
memory_count=$(backup_memory_categorized)

# 4. 备份 Skills（仅 memory-suite-v4）
skills_count=$(backup_skills_categorized)

# 5. 生成清单
generate_manifest

# 6. 创建压缩包
if ! create_archive; then
    log "压缩包创建失败，发送异常通知..."
    send_notification "$memory_count" "$skills_count" "failure"
    exit 1
fi

# 7. 清理旧备份
cleanup_old_backups

# 8. 发送通知 (通过Kilo)
send_notification "$memory_count" "$skills_count" "success"

log "========== 备份完成 =========="
