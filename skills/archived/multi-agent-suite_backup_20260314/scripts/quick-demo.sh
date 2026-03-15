#!/bin/bash
#
# 多Agent协作系统 - 快速示例
# 演示如何创建一个任务并查看状态
#

echo "🚀 多Agent协作系统 - 快速示例"
echo "================================"

cd "$HOME/.openclaw/workspace/skills/multi-agent-suite"

echo ""
echo "步骤1: 查看Agent团队"
echo "--------------------"
python3 core/orchestrator.py --list-agents

echo ""
echo "步骤2: 创建示例任务"
echo "--------------------"
python3 core/orchestrator.py \
  --create-task "示例网站开发" \
  --description "开发一个简单的示例网站" \
  --requirements "首页界面" "关于页面" "联系表单"

echo ""
echo "步骤3: 查看所有任务"
echo "--------------------"
python3 core/orchestrator.py --list-tasks

echo ""
echo "================================"
echo "示例完成!"
echo "================================"
echo ""
echo "提示: 使用 --status [task-id] 查看任务详情"
