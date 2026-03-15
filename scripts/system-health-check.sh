#!/bin/bash
# 系统健康检查脚本

echo "=== OpenClaw 系统健康检查 ==="
echo "检查时间: $(date)"
echo ""

# 检查磁盘空间
echo "1. 磁盘空间:"
df -h /Users/zhaoruicn/.openclaw/workspace | tail -1

# 检查内存套件状态
echo ""
echo "2. Memory Suite v4 状态:"
cd /Users/zhaoruicn/.openclaw/workspace/skills/memory-suite-v4 && python3 cli.py status 2>&1 | head -20

# 检查定时任务
echo ""
echo "3. 定时任务数: $(crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$' | wc -l)"

# 检查技能包数量
echo ""
echo "4. 技能包统计:"
echo "   主要技能包: $(ls /Users/zhaoruicn/.openclaw/workspace/skills/ | grep -v archived | grep -v suites | wc -l)"
echo "   归档技能包: $(ls /Users/zhaoruicn/.openclaw/workspace/skills/archived/ 2>/dev/null | wc -l)"

echo ""
echo "=== 检查完成 ==="
