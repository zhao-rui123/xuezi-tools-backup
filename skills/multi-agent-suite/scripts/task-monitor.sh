#!/bin/bash
#
# 多Agent任务监控脚本
# 实时监控所有任务和Agent状态
#

echo "========================================"
echo "🤖 多Agent任务监控"
echo "========================================"

SUITE_DIR="$HOME/.openclaw/workspace/skills/multi-agent-suite"

cd "$SUITE_DIR"

echo ""
echo "👥 Agent团队状态:"
echo "----------------------------------------"
python3 core/orchestrator.py --list-agents

echo ""
echo "📋 当前任务:"
echo "----------------------------------------"
python3 core/orchestrator.py --list-tasks

echo ""
echo "========================================"
echo "监控完成"
echo "========================================"
echo ""
echo "常用命令:"
echo "  创建任务: python3 core/orchestrator.py --create-task '任务名' --description '描述' --requirements '需求1' '需求2'"
echo "  查看状态: python3 core/orchestrator.py --status task-xxx"
echo "  查看Agent: python3 core/orchestrator.py --list-agents"
