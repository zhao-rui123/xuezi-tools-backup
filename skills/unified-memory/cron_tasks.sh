#!/bin/bash
#
# 统一记忆系统 - 定时任务脚本
# 第一阶段 + 第二阶段
#
# 添加到 crontab:
# 0 1 * * * /Users/zhaoruicn/.openclaw/workspace/skills/unified-memory/cron_tasks.sh >> /Users/zhaoruicn/.openclaw/workspace/memory/cron.log 2>&1
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_DIR="/Users/zhaoruicn/.openclaw/workspace/memory"
SKILLS_DIR="/Users/zhaoruicn/.openclaw/workspace/skills"
KNOWLEDGE_DIR="/Users/zhaoruicn/.openclaw/workspace/knowledge-base"
LOG_FILE="$MEMORY_DIR/cron.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "🕐 统一记忆系统 - 定时任务开始"
log "=========================================="

# ========== 第一阶段：基础优化 ==========
log "📦 第一阶段：基础优化"

# 1. 自动归档
log "  📦 执行自动归档..."
if python3 "$SCRIPT_DIR/auto_archive.py" >> "$LOG_FILE" 2>&1; then
    log "  ✅ 自动归档完成"
else
    log "  ❌ 自动归档失败"
fi

# 2. 重要性评估
log "  🎯 执行重要性评估..."
if python3 "$SCRIPT_DIR/importance_scorer.py" >> "$LOG_FILE" 2>&1; then
    log "  ✅ 重要性评估完成"
else
    log "  ❌ 重要性评估失败"
fi

# 3. 重建搜索索引
log "  🔍 重建搜索索引..."
if python3 "$SCRIPT_DIR/semantic_search.py" >> "$LOG_FILE" 2>&1; then
    log "  ✅ 索引重建完成"
else
    log "  ❌ 索引重建失败"
fi

# ========== 第二阶段：智能进化 ==========
log "🧠 第二阶段：智能进化"

# 4. 用户画像分析
log "  👤 更新用户画像..."
if python3 "$SCRIPT_DIR/user_profile.py" >> "$LOG_FILE" 2>&1; then
    log "  ✅ 用户画像更新完成"
else
    log "  ❌ 用户画像更新失败"
fi

# 5. 知识图谱构建
log "  🕸️  构建知识图谱..."
if python3 "$SCRIPT_DIR/knowledge_graph.py" >> "$LOG_FILE" 2>&1; then
    log "  ✅ 知识图谱构建完成"
else
    log "  ❌ 知识图谱构建失败"
fi

# 6. 生成智能推荐
log "  💡 生成智能推荐..."
if python3 "$SCRIPT_DIR/smart_recommendation.py" >> "$LOG_FILE" 2>&1; then
    log "  ✅ 智能推荐生成完成"
else
    log "  ❌ 智能推荐生成失败"
fi

# ========== 第三阶段：生态融合 ==========
log "🌐 第三阶段：生态融合"

# 7. 技能包记忆更新
log "  🛠️  更新技能包记忆..."
if python3 "$SCRIPT_DIR/skill_memory.py" >> "$LOG_FILE" 2>&1; then
    log "  ✅ 技能包记忆更新完成"
else
    log "  ❌ 技能包记忆更新失败"
fi

# 8. 知识库联动
log "  📚 同步知识库..."
if python3 "$SCRIPT_DIR/kb_integration.py" >> "$LOG_FILE" 2>&1; then
    log "  ✅ 知识库联动完成"
else
    log "  ❌ 知识库联动失败"
fi

# 9. 决策支持分析
log "  🎯 决策支持分析..."
if python3 "$SCRIPT_DIR/decision_support.py" >> "$LOG_FILE" 2>&1; then
    log "  ✅ 决策支持完成"
else
    log "  ❌ 决策支持失败"
fi

# ========== 第四阶段：自我进化 & 知识库管理 ==========
log "🧬 第四阶段：自我进化 & 知识库管理"

# 10. 自我进化系统
log "  🧬 运行自我进化系统..."
if python3 "$SKILLS_DIR/self-improvement/evolution_system_v2.py" >> "$LOG_FILE" 2>&1; then
    log "  ✅ 自我进化完成"
else
    log "  ❌ 自我进化失败"
fi

# 11. 知识库智能管理 ⭐NEW
log "  📚 知识库智能管理..."
if python3 "$KNOWLEDGE_DIR/kb_manager_v2.py" >> "$LOG_FILE" 2>&1; then
    log "  ✅ 知识库管理完成"
else
    log "  ❌ 知识库管理失败"
fi

log "=========================================="
log "✅ 定时任务完成 (全部11个任务)"
log "=========================================="
