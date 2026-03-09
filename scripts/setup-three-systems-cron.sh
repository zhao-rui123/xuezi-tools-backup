#!/bin/bash
#
# 三大系统自动化任务总配置脚本
# Unified Memory + Knowledge Base + Self-Evolution
#

set -e

echo "🎯 三大系统自动化任务总配置"
echo "=================================="
echo ""

WORKSPACE="$HOME/.openclaw/workspace"
UMS_DIR="$WORKSPACE/skills/unified-memory"
KB_DIR="$WORKSPACE/skills/knowledge-base"
SE_DIR="$WORKSPACE/skills/self-improvement"

echo "📋 将配置以下自动化任务："
echo ""

# 创建临时 cron 文件
TEMP_CRON=$(mktemp)

# 导出当前 crontab（保留现有任务）
crontab -l > "$TEMP_CRON" 2>/dev/null || echo "# 新建 crontab" > "$TEMP_CRON"

# 删除旧的三大系统任务（避免重复）
grep -v "# ===== Unified Memory" "$TEMP_CRON" > "$TEMP_CRON.tmp" 2>/dev/null || true
mv "$TEMP_CRON.tmp" "$TEMP_CRON" 2>/dev/null || true

grep -v "# ===== Self-Evolution" "$TEMP_CRON" > "$TEMP_CRON.tmp" 2>/dev/null || true
mv "$TEMP_CRON.tmp" "$TEMP_CRON" 2>/dev/null || true

grep -v "# ===== Knowledge-Memory" "$TEMP_CRON" > "$TEMP_CRON.tmp" 2>/dev/null || true
mv "$TEMP_CRON.tmp" "$TEMP_CRON" 2>/dev/null || true

grep -v "unified_memory.py daily" "$TEMP_CRON" > "$TEMP_CRON.tmp" 2>/dev/null || true
mv "$TEMP_CRON.tmp" "$TEMP_CRON" 2>/dev/null || true

grep -v "knowledge_graph.py build" "$TEMP_CRON" > "$TEMP_CRON.tmp" 2>/dev/null || true
mv "$TEMP_CRON.tmp" "$TEMP_CRON" 2>/dev/null || true

grep -v "evolution_triggers.py" "$TEMP_CRON" > "$TEMP_CRON.tmp" 2>/dev/null || true
mv "$TEMP_CRON.tmp" "$TEMP_CRON" 2>/dev/null || true

grep -v "knowledge_memory_integration.py" "$TEMP_CRON" > "$TEMP_CRON.tmp" 2>/dev/null || true
mv "$TEMP_CRON.tmp" "$TEMP_CRON" 2>/dev/null || true

grep -v "ums analyze monthly" "$TEMP_CRON" > "$TEMP_CRON.tmp" 2>/dev/null || true
mv "$TEMP_CRON.tmp" "$TEMP_CRON" 2>/dev/null || true

# 添加分隔线
echo "" >> "$TEMP_CRON"
echo "# ============================================" >> "$TEMP_CRON"
echo "# 三大系统自动化任务 (统一记忆 + 知识库 + 自我进化)" >> "$TEMP_CRON"
echo "# ============================================" >> "$TEMP_CRON"
echo "" >> "$TEMP_CRON"

# ============ 统一记忆系统 ============
echo "# ===== Unified Memory System Tasks =====" >> "$TEMP_CRON"
echo "# 每日记忆归档" >> "$TEMP_CRON"
echo "30 0 * * * /usr/bin/python3 $UMS_DIR/unified_memory.py daily >> /tmp/ums-daily.log 2>&1" >> "$TEMP_CRON"
echo "" >> "$TEMP_CRON"
echo "# 知识图谱自动更新" >> "$TEMP_CRON"
echo "0 1 * * * /usr/bin/python3 $UMS_DIR/knowledge_graph.py build --memory-dir $WORKSPACE/memory >> /tmp/ums-graph.log 2>&1" >> "$TEMP_CRON"
echo "" >> "$TEMP_CRON"
echo "# 月度记忆深度分析" >> "$TEMP_CRON"
echo "0 2 1 * * cd $UMS_DIR && /usr/bin/python3 unified_memory.py analyze >> /tmp/ums-monthly.log 2>&1" >> "$TEMP_CRON"
echo "" >> "$TEMP_CRON"

# ============ 知识库整合系统 ============
echo "# ===== Knowledge-Memory Integration Tasks =====" >> "$TEMP_CRON"
echo "# 每日知识同步 (记忆 → 知识库)" >> "$TEMP_CRON"
echo "0 1 * * * /usr/bin/python3 $KB_DIR/scripts/knowledge_memory_integration.py daily-sync >> /tmp/kb-integration.log 2>&1" >> "$TEMP_CRON"
echo "" >> "$TEMP_CRON"
echo "# 每周知识库维护" >> "$TEMP_CRON"
echo "0 5 * * 1 /bin/bash $KB_DIR/scripts/weekly-maintenance.sh >> /tmp/kb-maintenance.log 2>&1" >> "$TEMP_CRON"
echo "" >> "$TEMP_CRON"

# ============ 自我进化系统 ============
echo "# ===== Self-Evolution System Tasks =====" >> "$TEMP_CRON"
echo "# 每日自我进化" >> "$TEMP_CRON"
echo "0 23 * * * /usr/bin/python3 $SE_DIR/triggers/evolution_triggers.py daily >> /tmp/evolution-daily.log 2>&1" >> "$TEMP_CRON"
echo "" >> "$TEMP_CRON"
echo "# 每周进化回顾" >> "$TEMP_CRON"
echo "0 22 * * 0 /usr/bin/python3 $SE_DIR/triggers/evolution_triggers.py weekly >> /tmp/evolution-weekly.log 2>&1" >> "$TEMP_CRON"
echo "" >> "$TEMP_CRON"
echo "# 每月深度进化" >> "$TEMP_CRON"
echo "0 8 1 * * /usr/bin/python3 $SE_DIR/triggers/evolution_triggers.py monthly >> /tmp/evolution-monthly.log 2>&1" >> "$TEMP_CRON"
echo "" >> "$TEMP_CRON"

# 导入新的 crontab
crontab "$TEMP_CRON"

# 清理
rm "$TEMP_CRON"

echo "✅ 所有自动化任务已配置完成！"
echo ""
echo "📊 任务时间表："
echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│  时间        │  任务                                    │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│  00:30       │  统一记忆 - 每日记忆归档                 │"
echo "│  01:00       │  知识库   - 每日知识同步                 │"
echo "│  01:00       │  统一记忆 - 知识图谱更新                 │"
echo "│  05:00 周一  │  知识库   - 每周维护                     │"
echo "│  22:00 周日  │  自我进化 - 每周回顾                     │"
echo "│  23:00       │  自我进化 - 每日进化                     │"
echo "│  02:00 1号   │  统一记忆 - 月度分析                     │"
echo "│  08:00 1号   │  自我进化 - 月度进化                     │"
echo "└─────────────────────────────────────────────────────────┘"
echo ""
echo "📝 查看日志："
echo "   tail -f /tmp/ums-daily.log       # 统一记忆日志"
echo "   tail -f /tmp/kb-integration.log  # 知识库整合日志"
echo "   tail -f /tmp/evolution-daily.log # 自我进化日志"
echo ""
echo "🔧 管理命令："
echo "   crontab -l                       # 查看所有定时任务"
echo "   crontab -e                       # 编辑定时任务"
echo ""
