#!/usr/bin/env bash
#===============================================================================
# backup-core.sh - 备份核心逻辑
#===============================================================================
# 基于 daily-backup-v2.sh 改造，集成到 ops 架构
#===============================================================================

set -euo pipefail

# 确保 OPS_DIR 可用
SCRIPT="${BASH_SOURCE[0]}"
while [ -L "$SCRIPT" ]; do
    SCRIPT="$(readlink "$SCRIPT")"
done
OPS_DIR="$(cd -P "$(dirname "$SCRIPT")/.." && pwd)"
export OPS_DIR

source "$OPS_DIR/lib/logger.sh"
source "$OPS_DIR/lib/lock.sh"
source "$OPS_DIR/config/backup.conf"

# 解析参数
TYPE="full"
TRACE_ID="$(date '+%Y%m%d_%H%M%S')-$(openssl rand -hex 3 2>/dev/null || echo "$$")"

while [ $# -gt 0 ]; do
    case "$1" in
        --type)  TYPE="$2"; shift 2 ;;
        --trace) TRACE_ID="$2"; shift 2 ;;
        *)       shift ;;
    esac
done

# 设置日志
LOG_FILE="$BACKUP_LOG_DIR/${TRACE_ID}.log"
BACKUP_STATUS_FILE="$BACKUP_STATUS_DIR/${TRACE_ID}.json"

# 路径
BACKUP_DIR="/Volumes/cu/ocu"
MEMORY_SOURCE="$WORKSPACE_DIR/memory"
SKILLS_SOURCE="$WORKSPACE_DIR/skills"
FULL_BACKUP_DIR="$BACKUP_DIR/full-backups"
ARCHIVE_NAME="openclaw-backup-${TRACE_ID}.tar.gz"
ARCHIVE_PATH="$FULL_BACKUP_DIR/$ARCHIVE_NAME"

# 统计
MEMORY_COUNT=0
SKILLS_COUNT=0

#===============================================================
# 日志前缀
#===============================================================
_log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [backup-core] $1"
}

#===============================================================
# 创建备份目录结构
#===============================================================
setup_backup_structure() {
    _log "创建备份目录结构..."
    mkdir -p "$BACKUP_DIR/memory-backup/daily"
    mkdir -p "$BACKUP_DIR/memory-backup/archive"
    mkdir -p "$BACKUP_DIR/memory-backup/snapshots"
    mkdir -p "$BACKUP_DIR/memory-backup/evolution"
    mkdir -p "$BACKUP_DIR/memory-backup/reports"
    mkdir -p "$BACKUP_DIR/memory-backup/knowledge"
    mkdir -p "$BACKUP_DIR/memory-backup/index"
    mkdir -p "$BACKUP_DIR/memory-backup/config"
    mkdir -p "$BACKUP_DIR/skills-backup/core"
    mkdir -p "$BACKUP_DIR/skills-backup/archived"
    mkdir -p "$BACKUP_DIR/skills-backup/suites"
    mkdir -p "$FULL_BACKUP_DIR"
    _log "✅ 目录结构创建完成"
}

#===============================================================
# 分类备份 Memory
#===============================================================
backup_memory_categorized() {
    _log "开始备份 Memory..."
    local count=0
    local memory_src="$MEMORY_SOURCE"
    local memory_dst="$BACKUP_DIR/memory-backup"

    # 每日记忆文件
    for file in "$memory_src"/2*.md; do
        [ -f "$file" ] || continue
        cp "$file" "$memory_dst/daily/" 2>/dev/null && count=$((count + 1))
    done

    # 归档文件
    if [ -d "$memory_src/archive" ]; then
        cp -r "$memory_src/archive"/* "$memory_dst/archive/" 2>/dev/null || true
        count=$((count + $(find "$memory_src/archive" -type f 2>/dev/null | wc -l)))
    fi

    # 会话快照
    if [ -d "$memory_src/session_states" ]; then
        cp -r "$memory_src/session_states"/* "$memory_dst/snapshots/" 2>/dev/null || true
    fi

    # 进化系统
    if [ -d "$memory_src/evolution" ]; then
        cp -r "$memory_src/evolution"/* "$memory_dst/evolution/" 2>/dev/null || true
    fi

    # 报告文件
    for file in "$memory_src"/*report*.json "$memory_src"/*report*.md; do
        [ -f "$file" ] || continue
        cp "$file" "$memory_dst/reports/" 2>/dev/null && count=$((count + 1))
    done

    # 知识图谱
    if [ -d "$memory_src/knowledge_graph" ]; then
        cp -r "$memory_src/knowledge_graph"/* "$memory_dst/knowledge/" 2>/dev/null || true
    fi

    # 搜索索引
    if [ -d "$memory_src/index" ]; then
        cp -r "$memory_src/index"/* "$memory_dst/index/" 2>/dev/null || true
    fi

    # 配置文件
    for file in "$memory_src"/*.json; do
        [ -f "$file" ] || continue
        cp "$file" "$memory_dst/config/" 2>/dev/null && count=$((count + 1))
    done

    MEMORY_COUNT=$count
    _log "✅ Memory 备份完成: $count 个文件"
}

#===============================================================
# 分类备份 Skills
#===============================================================
backup_skills_categorized() {
    _log "开始备份 Skills..."
    local count=0
    local skills_src="$SKILLS_SOURCE"
    local skills_dst="$BACKUP_DIR/skills-backup"

    # 核心技能
    if [ -d "$skills_src" ]; then
        for item in "$skills_src"/*; do
            [ -e "$item" ] || continue
            case "$(basename "$item")" in
                archived|suites|README.md) continue ;;
                *)
                    cp -r "$item" "$skills_dst/core/" 2>/dev/null || true
                    count=$((count + $(find "$item" -type f 2>/dev/null | wc -l)))
                    ;;
            esac
        done
    fi

    # 已归档技能
    if [ -d "$skills_src/archived" ]; then
        cp -r "$skills_src/archived"/* "$skills_dst/archived/" 2>/dev/null || true
        count=$((count + $(find "$skills_src/archived" -type f 2>/dev/null | wc -l)))
    fi

    # 技能包套件
    if [ -d "$skills_src/suites" ]; then
        cp -r "$skills_src/suites"/* "$skills_dst/suites/" 2>/dev/null || true
        count=$((count + $(find "$skills_src/suites" -type f 2>/dev/null | wc -l)))
    fi

    SKILLS_COUNT=$count
    _log "✅ Skills 备份完成: $count 个文件"
}

#===============================================================
# 生成备份清单
#===============================================================
generate_manifest() {
    _log "生成备份清单..."
    cat > "$BACKUP_DIR/backup-manifest-${TRACE_ID}.json" << EOF
{
  "trace_id": "$TRACE_ID",
  "backup_date": "$(date +%Y%m%d)",
  "backup_time": "$(date +%H:%M:%S)",
  "version": "3.0",
  "structure": {
    "memory": {
      "daily_notes": $(find "$BACKUP_DIR/memory-backup/daily" -type f 2>/dev/null | wc -l),
      "archive": $(find "$BACKUP_DIR/memory-backup/archive" -type f 2>/dev/null | wc -l),
      "snapshots": $(find "$BACKUP_DIR/memory-backup/snapshots" -type f 2>/dev/null | wc -l),
      "evolution": $(find "$BACKUP_DIR/memory-backup/evolution" -type f 2>/dev/null | wc -l),
      "reports": $(find "$BACKUP_DIR/memory-backup/reports" -type f 2>/dev/null | wc -l),
      "knowledge": $(find "$BACKUP_DIR/memory-backup/knowledge" -type f 2>/dev/null | wc -l),
      "index": $(find "$BACKUP_DIR/memory-backup/index" -type f 2>/dev/null | wc -l),
      "config": $(find "$BACKUP_DIR/memory-backup/config" -type f 2>/dev/null | wc -l)
    },
    "skills": {
      "core": $(find "$BACKUP_DIR/skills-backup/core" -type f 2>/dev/null | wc -l),
      "archived": $(find "$BACKUP_DIR/skills-backup/archived" -type f 2>/dev/null | wc -l),
      "suites": $(find "$BACKUP_DIR/skills-backup/suites" -type f 2>/dev/null | wc -l)
    }
  }
}
EOF
    _log "✅ 清单生成完成"
}

#===============================================================
# 创建压缩包
#===============================================================
create_archive() {
    _log "创建压缩包: $ARCHIVE_NAME..."
    cd "$BACKUP_DIR"

    # 排除不需要的目录
    local excludes=()
    for pattern in "${BACKUP_EXCLUDE_PATTERNS[@]}"; do
        excludes+=("--exclude=$pattern")
    done

    # 压缩（使用绝对路径备份workspace配置文件）
    if tar czf "$ARCHIVE_PATH" \
        --exclude="*.pyc" \
        --exclude="__pycache__" \
        --exclude="*.log" \
        --exclude=".git" \
        --exclude="node_modules" \
        --exclude="venv" \
        --exclude=".venv" \
        --exclude="*.tmp" \
        --exclude=".DS_Store" \
        memory-backup \
        skills-backup \
        "$WORKSPACE_DIR/AGENTS.md" \
        "$WORKSPACE_DIR/SOUL.md" \
        "$WORKSPACE_DIR/USER.md" \
        "$WORKSPACE_DIR/IDENTITY.md" \
        2>/dev/null; then

        # 创建 latest 符号链接
        ln -sf "$ARCHIVE_PATH" "$FULL_BACKUP_DIR/latest"

        local size
        size=$(du -h "$ARCHIVE_PATH" | cut -f1)
        _log "✅ 压缩包创建成功: $ARCHIVE_NAME ($size)"
        return 0
    else
        _log "❌ 压缩包创建失败"
        return 1
    fi
}

#===============================================================
# 清理旧备份（本地）
#===============================================================
cleanup_old_backups() {
    _log "清理旧备份（保留 ${BACKUP_LOCAL_RETENTION_DAYS} 天）..."
    local count
    count=$(ls -1t "$FULL_BACKUP_DIR"/openclaw-backup-*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -gt "$BACKUP_LOCAL_RETENTION_DAYS" ]; then
        ls -1t "$FULL_BACKUP_DIR"/openclaw-backup-*.tar.gz 2>/dev/null | \
            tail -n +$((BACKUP_LOCAL_RETENTION_DAYS + 1)) | \
            xargs -r rm -f
        _log "已清理旧备份，当前保留 $count 个"
    fi
}

#===============================================================
# 保存状态文件
#===============================================================
save_status() {
    local status="$1"
    local error="${2:-null}"

    cat > "$BACKUP_STATUS_FILE" << EOF
{
  "trace_id": "$TRACE_ID",
  "type": "$TYPE",
  "status": "$status",
  "error": "$error",
  "archive_name": "$ARCHIVE_NAME",
  "archive_path": "$ARCHIVE_PATH",
  "archive_size": "$(du -h "$ARCHIVE_PATH" 2>/dev/null | cut -f1 || echo "unknown")",
  "memory_count": $MEMORY_COUNT,
  "skills_count": $SKILLS_COUNT,
  "start_time": "$(cat "$BACKUP_LOG_DIR/${TRACE_ID}.log" 2>/dev/null | head -1 | grep -o '[0-9T:+-]\+' | head -1 || echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ')")",
  "end_time": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "local_backup_dir": "$FULL_BACKUP_DIR",
  "cloud_synced": false
}
EOF
}

#===============================================================
# 主程序
#===============================================================
main() {
    _log "========== 备份核心开始 | trace=$TRACE_ID | type=$TYPE =========="

    # 前置检查
    if [ ! -d "$BACKUP_DIR" ]; then
        _log "FATAL: 备份目录未挂载: $BACKUP_DIR"
        save_status "FAILED" "backup_dir_not_mounted"
        exit 1
    fi

    # 磁盘空间检查
    local available
    available=$(df -k "$BACKUP_DIR" | awk 'NR==2 {print $4}')
    if [ "$available" -lt 1048576 ]; then  # < 1GB
        _log "FATAL: 磁盘空间不足: ${available}KB"
        save_status "FAILED" "disk_space_insufficient"
        exit 1
    fi

    # 开始备份
    setup_backup_structure
    backup_memory_categorized
    backup_skills_categorized
    generate_manifest

    if ! create_archive; then
        save_status "FAILED" "archive_creation_failed"
        exit 1
    fi

    cleanup_old_backups
    save_status "SUCCESS"

    _log "========== 备份核心完成 | Memory:$MEMORY_COUNT | Skills:$SKILLS_COUNT =========="
}

main "$@"
