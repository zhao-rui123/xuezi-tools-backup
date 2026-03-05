#!/bin/bash

# 会话健康检查与优化建议
# 检查 token 使用、上下文大小，给出优化建议

echo "🔍 会话健康检查"
echo "================"

# 获取会话信息
SESSION_INFO=$(openclaw status 2>/dev/null | grep -A5 "Sessions")

# 解析 token 使用情况
# 示例: 78k/262k (30%) · 🗄️ 708% cached
TOKEN_INFO=$(echo "$SESSION_INFO" | grep "kimi-for-coding" | grep -oE '[0-9]+k/[0-9]+k \([0-9]+%\)')

if [ -n "$TOKEN_INFO" ]; then
    USED=$(echo "$TOKEN_INFO" | grep -oE '^[0-9]+k')
    TOTAL=$(echo "$TOKEN_INFO" | grep -oE '/[0-9]+k' | sed 's/\///')
    PERCENT=$(echo "$TOKEN_INFO" | grep -oE '\([0-9]+%\)' | sed 's/[()]//g')
    
    echo ""
    echo "📊 Token 使用情况"
    echo "  已使用: $USED / $TOTAL ($PERCENT)"
    
    # 计算百分比数字
    PERCENT_NUM=$(echo "$PERCENT" | sed 's/%//')
    
    if [ "$PERCENT_NUM" -lt 50 ]; then
        echo "  ✅ 状态: 健康"
    elif [ "$PERCENT_NUM" -lt 80 ]; then
        echo "  ⚠️ 状态: 偏高，建议关注"
    else
        echo "  🔴 状态: 过高，建议压缩或开新会话"
        echo ""
        echo "💡 建议操作:"
        echo "  1. 执行 /compact 压缩上下文"
        echo "  2. 或执行 /new 开启新会话"
    fi
else
    echo "  ℹ️ 无法获取 token 信息"
fi

# 检查会话数量
echo ""
echo "📁 会话文件"
SESSION_COUNT=$(ls ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | wc -l)
echo "  活跃会话: $SESSION_COUNT 个"

# 检查大文件
echo ""
echo "📦 大文件检查"
LARGE_FILES=$(find ~/.openclaw/agents/main/sessions -name "*.jsonl" -size +1M 2>/dev/null)
if [ -n "$LARGE_FILES" ]; then
    echo "  发现大会话文件:"
    echo "$LARGE_FILES" | while read f; do
        size=$(ls -lh "$f" | awk '{print $5}')
        name=$(basename "$f")
        echo "    - $name ($size)"
    done
    echo ""
    echo "💡 建议: 大文件可能影响性能，考虑清理旧会话"
else
    echo "  ✅ 无异常大文件"
fi

# 检查压缩次数
echo ""
echo "🗜️ 压缩统计"
COMPACT_COUNT=$(openclaw status 2>/dev/null | grep "compactionCount" | grep -oE '[0-9]+' || echo "0")
echo "  已执行压缩: $COMPACT_COUNT 次"

echo ""
echo "================"
echo "✅ 检查完成"
