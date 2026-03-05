#!/bin/bash

# OpenClaw 系统启动检查
# 在 Gateway 启动后执行，确保所有组件正常

echo "🔍 OpenClaw 系统启动检查"
echo "=========================="

# 1. 检查 Gateway
max_wait=30
waited=0
echo -n "[1/5] 等待 Gateway 启动..."

while ! curl -s http://127.0.0.1:18789/health >/dev/null 2>&1; do
    if [ $waited -ge $max_wait ]; then
        echo " ❌ 超时"
        exit 1
    fi
    sleep 1
    waited=$((waited + 1))
    echo -n "."
done
echo " ✅ ($waited 秒)"

# 2. 检查技能包加载
echo -n "[2/5] 检查技能包..."
skills_count=$(ls ~/.openclaw/workspace/skills/*/SKILL.md 2>/dev/null | wc -l)
if [ "$skills_count" -gt 0 ]; then
    echo " ✅ ($skills_count 个技能包)"
else
    echo " ⚠️ (未找到技能包)"
fi

# 3. 检查知识库
echo -n "[3/5] 检查知识库..."
if [ -f ~/.openclaw/workspace/knowledge-base/INDEX.md ]; then
    echo " ✅"
else
    echo " ⚠️"
fi

# 4. 检查备份系统
echo -n "[4/5] 检查备份系统..."
if [ -f ~/.openclaw/workspace/backup_memory.sh ]; then
    echo " ✅"
else
    echo " ⚠️"
fi

# 5. 检查定时任务
echo -n "[5/5] 检查定时任务..."
cron_count=$(crontab -l 2>/dev/null | grep -v "^#" | grep -c "openclaw\|backup\|health" || echo 0)
if [ "$cron_count" -gt 0 ]; then
    echo " ✅ ($cron_count 个任务)"
else
    echo " ⚠️"
fi

echo "=========================="
echo "✅ 系统启动检查完成"
echo ""
echo "💡 提示:"
echo "  - 读取 MEMORY.md 获取最新上下文"
echo "  - 查看知识库 INDEX.md 了解项目状态"
echo "  - 使用技能包快速开始工作"
