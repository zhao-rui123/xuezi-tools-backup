#!/bin/bash
# 安全安装技能包 - 一键使用system-guard保护机制安装

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_PATH="$1"

if [ -z "$SKILL_PATH" ]; then
    echo "用法: safe-install.sh <技能包路径>"
    echo "示例: safe-install.sh /path/to/new-skill"
    echo ""
    echo "此脚本会:"
    echo "  1. 创建系统快照备份"
    echo "  2. 运行安全检查"
    echo "  3. 沙箱测试"
    echo "  4. 安全安装"
    echo "  5. 如果失败可自动回滚"
    exit 1
fi

if [ ! -d "$SKILL_PATH" ]; then
    echo "❌ 错误: 技能包路径不存在: $SKILL_PATH"
    exit 1
fi

echo "🛡️ 开始安全安装流程..."
echo ""

# 运行安全安装
python3 "$SCRIPT_DIR/../system_guard.py" install "$SKILL_PATH"

echo ""
echo "✅ 安全安装流程完成"
