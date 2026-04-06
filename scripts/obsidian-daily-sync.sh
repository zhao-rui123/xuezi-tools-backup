#!/bin/bash
# Obsidian每日工作日志同步脚本
# 每天22:00备份后执行

export HOME="/Users/zhaoruicn"
OBSSIDIAN_DIR="$HOME/.openclaw/workspace/obsidian-webdav"
MEMORY_SOURCE="/Users/zhaoruicn/.openclaw/workspace/memory"

TODAY=$(date +%Y.%m.%d)
TIMESTAMP=$(date +%Y-%m-%d)
MEMORY_FILE="$MEMORY_SOURCE/${TIMESTAMP}.md"
LOG_FILE="/tmp/obsidian_sync.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

sync_obsidian() {
    log "开始同步Obsidian..."
    
    # 检查今日memory文件是否存在
    if [ ! -f "$MEMORY_FILE" ]; then
        log "今日memory文件不存在: $MEMORY_FILE"
        return 1
    fi
    
    # 提取关键内容
    local content=$(cat "$MEMORY_FILE")
    
    # 生成日志文件名
    local filename="${TODAY}-AI工作日志.md"
    
    # 通过WebDAV上传
    curl -s -u "1034440765@qq.com:ai7eaer5mv2gixex" \
      -T <(cat <<EOF
---
tags: [#AI/日志] [#自动同步]
created: $TIMESTAMP
---

# $TODAY AI工作日志

## 今日内容摘要

$content

---
*本日志由系统自动生成*
EOF
) \
      "https://dav.jianguoyun.com/dav/BOSI/zhaorui/%e9%9b%aa%e5%ad%90%e5%8a%a9%e6%89%8b/AI%e5%8a%a9%e6%89%8b%e6%97%a5%e5%bf%97/${filename}"
    
    log "Obsidian同步完成: $filename"
}

sync_obsidian
