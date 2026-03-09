#!/bin/bash
#
# 自我进化系统 - 一键安装脚本
# Self-Evolution System One-Click Setup
#

set -e

echo "🧬 自我进化系统安装器"
echo "======================"
echo ""

WORKSPACE="$HOME/.openclaw/workspace"
SKILLS_DIR="$WORKSPACE/skills"
EVOLUTION_DIR="$SKILLS_DIR/self-improvement"
MEMORY_DIR="$WORKSPACE/memory"

cd "$EVOLUTION_DIR"

# 检查 Python 环境
echo "📋 检查环境..."
python3 --version || { echo "❌ 需要 Python 3"; exit 1; }

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p "$MEMORY_DIR/evolution"
mkdir -p core triggers modules reports

# 检查 unified-memory 连接
echo "🔗 检查 unified-memory 连接..."
if [ -d "$SKILLS_DIR/unified-memory" ]; then
    echo "   ✅ unified-memory 已安装"
else
    echo "   ⚠️ unified-memory 未安装，部分功能将不可用"
fi

# 初始化进化状态
echo "📝 初始化进化状态..."
python3 -c "
import json
from pathlib import Path

state_file = Path('$MEMORY_DIR/evolution/evolution_state.json')
if not state_file.exists():
    state = {
        'version': '2.0.0',
        'last_update': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
        'total_interactions': 0,
        'total_improvements': 0,
        'active_optimizations': [],
        'learned_patterns': 0,
        'performance_score': 100.0,
        'evolution_level': 'initial'
    }
    state_file.write_text(json.dumps(state, indent=2))
    print('   ✅ 进化状态已初始化')
else:
    print('   ℹ️ 进化状态已存在')
"

# 测试核心模块
echo "🧪 测试核心模块..."
python3 core/evolution_engine.py status || echo "   ⚠️ 状态检查失败"

# 设置定时任务
echo ""
echo "⏰ 设置定时任务..."
echo "   建议添加以下 cron 任务："
echo ""
echo "   # 每日23:00执行自我进化"
echo "   0 23 * * * /usr/bin/python3 $EVOLUTION_DIR/triggers/evolution_triggers.py daily"
echo ""
echo "   # 每周日22:00生成周报"
echo "   0 22 * * 0 /usr/bin/python3 $EVOLUTION_DIR/triggers/evolution_triggers.py weekly"
echo ""
echo "   执行 'crontab -e' 添加以上任务"

# 添加到 HEARTBEAT.md
echo ""
echo "💓 心跳检查集成..."
HEARTBEAT_FILE="$WORKSPACE/HEARTBEAT.md"
if [ -f "$HEARTBEAT_FILE" ]; then
    if ! grep -q "自我进化检查" "$HEARTBEAT_FILE"; then
        echo "" >> "$HEARTBEAT_FILE"
        echo "## 自我进化检查" >> "$HEARTBEAT_FILE"
        echo "- [ ] 检查进化等级和性能评分" >> "$HEARTBEAT_FILE"
        echo "- [ ] 查看是否有新的优化建议" >> "$HEARTBEAT_FILE"
        echo "- [ ] 执行日常进化（如超过24小时未执行）" >> "$HEARTBEAT_FILE"
        echo "   ✅ 已添加到 HEARTBEAT.md"
    else
        echo "   ℹ️ 心跳检查已存在"
    fi
else
    echo "   ⚠️ HEARTBEAT.md 不存在，跳过"
fi

echo ""
echo "======================"
echo "✅ 安装完成！"
echo ""
echo "🚀 快速开始："
echo "   1. 查看状态: python3 core/evolution_engine.py status"
echo "   2. 执行进化: python3 core/evolution_engine.py evolve"
echo "   3. 生成报告: python3 core/evolution_engine.py report"
echo ""
echo "📚 更多信息请查看: SKILL.md"
echo ""
