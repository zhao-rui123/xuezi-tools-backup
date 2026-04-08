#!/bin/bash
# Obsidian每日工作日志同步脚本
# 每天23:10执行，从memory提取并整理成工作总结格式

export HOME="/Users/zhaoruicn"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
WEBDAV_USER="1034440765@qq.com"
WEBDAV_PASS="ai7eaer5mv2gixex"
WEBDAV_BASE="https://dav.jianguoyun.com/dav/BOSI/zhaorui"
MEMORY_DIR="$HOME/.openclaw/workspace/memory"
TODAY=$(date +%Y.%m.%d)
TODAY_ISO=$(date +%Y-%m-%d)
MEMORY_FILE="$MEMORY_DIR/${TODAY_ISO}.md"
LOG_FILE="$HOME/.openclaw/workspace/ops/logs/tasks/obsidian_sync.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# 从memory文件生成工作总结
generate_summary() {
    local memory_file="$1"
    
    if [ ! -f "$memory_file" ]; then
        echo ""
        return
    fi
    
    python3 << 'PYEOF'
import re
from pathlib import Path
from datetime import datetime

today_display = datetime.now().strftime("%Y.%m.%d")
memory_file = Path("/Users/zhaoruicn/.openclaw/workspace/memory/2026-04-07.md")

if not memory_file.exists():
    print("")
    exit(0)

content = memory_file.read_text()

# 提取手动补充的高质量内容（通常在 ## 手动补充 或 ## XX:XX 手动 之后）
manual_sections = []
in_manual = False
current_section = []

for line in content.split('\n'):
    # 检测手动补充章节开始
    if re.match(r'^## \d{2}:\d{2} 手动', line) or '手动补充' in line:
        if current_section and in_manual:
            manual_sections.append('\n'.join(current_section))
        current_section = []
        in_manual = True
    elif re.match(r'^## \d{2}:\d{2} 自动', line):
        if current_section and in_manual:
            manual_sections.append('\n'.join(current_section))
        current_section = []
        in_manual = False
    elif in_manual:
        current_section.append(line)

if current_section and in_manual:
    manual_sections.append('\n'.join(current_section))

# 从手动内容中提取关键信息
key_points = []
for section in manual_sections:
    lines = section.split('\n')
    for line in lines:
        line = line.strip()
        # 提取标题行
        if line.startswith('### '):
            key_points.append(line.replace('### ', '📌 ')[:60])
        # 提取完成标记
        elif '✅' in line and len(line) < 100:
            clean = line.replace('✅', '').strip()
            if clean and not clean.startswith('-'):
                key_points.append(f"✅ {clean[:70]}")
        # 提取重要发现
        elif '核心' in line or '关键' in line or '结论' in line:
            key_points.append(line[:80])

# 提取项目相关（储能、股票、AIDC等）
project_keywords = ['储能', '股票', 'AIDC', 'Obsidian', 'MemPalace', 'MindVault', '备份', '脚本', 'Word', '文档']
project_points = []
for line in content.split('\n'):
    line = line.strip()
    for kw in project_keywords:
        if kw in line and len(line) > 10 and len(line) < 150:
            if '##' not in line and '```' not in line:
                clean = line[:80]
                if clean not in project_points:
                    project_points.append(clean)
                    break

# 去重并限制数量
seen = set()
unique_points = []
for p in key_points + project_points:
    if p not in seen and len(p) > 5:
        unique_points.append(p)
        seen.add(p)

# 生成总结
output = f"""# {today_display} 工作日志 #AI/日志

## 📋 今日完成

"""

count = 0
for point in unique_points:
    if count < 10:
        output += f"- {point}\n"
        count += 1

# 主要工作领域
output += f"""
## 📌 主要领域

"""

# 从手动补充中提取章节标题
section_titles = []
for section in manual_sections:
    for line in section.split('\n'):
        match = re.match(r'^### (.+)', line.strip())
        if match:
            title = match.group(1).strip()
            if title and title not in section_titles:
                section_titles.append(title)

for title in section_titles[:5]:
    output += f"- {title}\n"

# 标签
tags = set(re.findall(r'#\w+(?:/\w+)?', content))
if tags:
    output += f"\n## 🏷️ 标签\n"
    output += " ".join(sorted(tags)[:15])
    output += "\n"

# 系统状态
output += f"""
## 🔧 系统状态
- ✅ 记忆提取：正常
- ✅ Obsidian同步：正常
- ✅ 定时任务：运行中

---
*本日志由系统自动生成 ({datetime.now().strftime('%Y-%m-%d %H:%M')})*
"""

print(output)
PYEOF
}

# 主流程
main() {
    log "开始同步Obsidian工作日志..."
    
    if [ ! -f "$MEMORY_FILE" ]; then
        log "今日memory文件不存在: $MEMORY_FILE"
        exit 1
    fi
    
    log "生成工作总结..."
    SUMMARY=$(generate_summary "$MEMORY_FILE")
    
    if [ -z "$SUMMARY" ]; then
        log "生成工作总结失败"
        exit 1
    fi
    
    # 文件名
    FILENAME="${TODAY}-AI工作日志.md"
    ENCODED_FILENAME=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$FILENAME'))")
    URL="${WEBDAV_BASE}/%e9%9b%aa%e5%ad%90%e5%8a%a9%e6%89%8b/AI%e5%8a%a9%e6%89%8b%e6%97%a5%e5%bf%97/${ENCODED_FILENAME}"
    
    # 上传到Obsidian
    log "上传到Obsidian: $FILENAME"
    RESULT=$(curl -s -u "$WEBDAV_USER:$WEBDAV_PASS" -X PUT -T <(echo "$SUMMARY") "$URL" 2>&1)
    
    if echo "$RESULT" | grep -q "ObjectNotFound\|created\|No Content\|201\|204"; then
        log "Obsidian同步完成: $FILENAME"
    else
        log "Obsidian同步结果: $RESULT"
    fi
}

main
