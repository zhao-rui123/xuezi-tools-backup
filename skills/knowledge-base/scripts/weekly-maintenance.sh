#!/bin/bash
# Knowledge Base - 定期维护脚本
# 每周整理记忆到知识库，更新索引

set -e

WORKSPACE="$HOME/.openclaw/workspace"
KB_DIR="$WORKSPACE/knowledge-base"
MEMORY_DIR="$WORKSPACE/memory"
REPORT_FILE="/tmp/kb-maintenance-$(date '+%Y%m%d').log"

echo "========================================" > "$REPORT_FILE"
echo "  知识库维护报告" >> "$REPORT_FILE"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
echo "========================================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 1. 检查今日记忆
echo "📋 记忆文件检查" >> "$REPORT_FILE"
echo "----------------" >> "$REPORT_FILE"

TODAY=$(date '+%Y-%m-%d')
TODAY_FILE="$MEMORY_DIR/${TODAY}.md"
YESTERDAY_FILE="$MEMORY_DIR/$(date -v-1d '+%Y-%m-%d' 2>/dev/null || echo '').md"

if [[ -f "$TODAY_FILE" ]]; then
    LINES=$(wc -l < "$TODAY_FILE")
    echo "✅ 今日记忆: $LINES 行" >> "$REPORT_FILE"
else
    echo "⚠️  今日记忆文件不存在" >> "$REPORT_FILE"
fi

# 2. 统计知识库状态
echo "" >> "$REPORT_FILE"
echo "📚 知识库统计" >> "$REPORT_FILE"
echo "--------------" >> "$REPORT_FILE"

PROJECTS=$(find "$KB_DIR/projects" -name "README.md" 2>/dev/null | wc -l)
DECISIONS=$(find "$KB_DIR/decisions" -name "*.md" 2>/dev/null | grep -v "README.md" | wc -l)
PROBLEMS=$(find "$KB_DIR/problems" -name "*.md" 2>/dev/null | grep -v "README.md" | wc -l)
REFERENCES=$(find "$KB_DIR/references" -name "*.md" 2>/dev/null | wc -l)
OPERATIONS=$(find "$KB_DIR/operations" -name "*.md" 2>/dev/null | grep -v "README.md" | wc -l)

echo "项目文档:    $PROJECTS" >> "$REPORT_FILE"
echo "决策记录:    $DECISIONS" >> "$REPORT_FILE"
echo "问题方案:    $PROBLEMS" >> "$REPORT_FILE"
echo "参考资料:    $REFERENCES" >> "$REPORT_FILE"
echo "运维文档:    $OPERATIONS" >> "$REPORT_FILE"

# 3. 检查记忆归档（30天前的记忆）
echo "" >> "$REPORT_FILE"
echo "🗄️  记忆归档检查" >> "$REPORT_FILE"
echo "----------------" >> "$REPORT_FILE"

OLD_MEMORIES=$(find "$MEMORY_DIR" -name "*.md" -mtime +30 2>/dev/null | wc -l)
if [[ $OLD_MEMORIES -gt 0 ]]; then
    echo "⚠️  发现 $OLD_MEMORIES 个超过30天的记忆文件" >> "$REPORT_FILE"
    echo "建议: 手动审查后归档到 knowledge-base/archive/" >> "$REPORT_FILE"
else
    echo "✅ 所有记忆文件都在30天内" >> "$REPORT_FILE"
fi

# 4. 检查索引更新
echo "" >> "$REPORT_FILE"
echo "🔍 索引状态检查" >> "$REPORT_FILE"
echo "----------------" >> "$REPORT_FILE"

INDEX_FILE="$KB_DIR/INDEX.md"
if [[ -f "$INDEX_FILE" ]]; then
    INDEX_AGE=$(( ($(date +%s) - $(stat -f%m "$INDEX_FILE" 2>/dev/null || stat -c%Y "$INDEX_FILE" 2>/dev/null || echo 0)) / 86400 ))
    if [[ $INDEX_AGE -gt 7 ]]; then
        echo "⚠️  全局索引已 $INDEX_AGE 天未更新" >> "$REPORT_FILE"
        echo "建议: 检查是否有新项目/决策未纳入索引" >> "$REPORT_FILE"
    else
        echo "✅ 全局索引 $INDEX_AGE 天前更新" >> "$REPORT_FILE"
    fi
else
    echo "❌ 全局索引文件不存在" >> "$REPORT_FILE"
fi

# 5. 生成整理建议
echo "" >> "$REPORT_FILE"
echo "💡 本周整理建议" >> "$REPORT_FILE"
echo "----------------" >> "$REPORT_FILE"

# 检查今天的记忆是否有重要决策
if [[ -f "$TODAY_FILE" ]]; then
    if grep -q "DECISION\|决策" "$TODAY_FILE" 2>/dev/null; then
        echo "📌 今日记忆包含决策内容，建议整理到 decisions/" >> "$REPORT_FILE"
    fi
    
    if grep -q "TODO\|待办" "$TODAY_FILE" 2>/dev/null; then
        echo "📌 今日记忆包含待办事项，建议跟进完成状态" >> "$REPORT_FILE"
    fi
    
    if grep -q "问题解决\|修复\|bug" "$TODAY_FILE" 2>/dev/null; then
        echo "📌 今日记忆包含问题解决记录，建议整理到 problems/" >> "$REPORT_FILE"
    fi
fi

# 6. 完整性检查
echo "" >> "$REPORT_FILE"
echo "✅ 完整性检查" >> "$REPORT_FILE"
echo "--------------" >> "$REPORT_FILE"

REQUIRED_DIRS=("projects" "decisions" "problems" "references" "operations" "templates")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "$KB_DIR/$dir" ]]; then
        echo "✅ $dir/" >> "$REPORT_FILE"
    else
        echo "❌ $dir/ 缺失" >> "$REPORT_FILE"
    fi
done

echo "" >> "$REPORT_FILE"
echo "========================================" >> "$REPORT_FILE"
echo "报告完成: $REPORT_FILE" >> "$REPORT_FILE"

# 输出报告
cat "$REPORT_FILE"

# 发送飞书通知 - 使用广播专员
NOTIFICATION="📚 知识库维护报告 ($(date '+%Y-%m-%d %H:%M'))

📊 统计:
• 项目文档: $PROJECTS
• 决策记录: $DECISIONS
• 问题方案: $PROBLEMS
• 参考资料: $REFERENCES
• 运维文档: $OPERATIONS

$(grep -E "^(✅|⚠️|📌)" "$REPORT_FILE" | head -10)

---
🤖 广播专员 | $(date '+%H:%M')"

python3 /Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py \
    --task send \
    --message "$NOTIFICATION" \
    --target group \
    2>/dev/null

echo "✅ 维护通知已发送"

exit 0
