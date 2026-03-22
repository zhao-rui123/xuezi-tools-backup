#!/bin/bash
# 知识图谱查询工具

KG_FILE="$HOME/.openclaw/workspace/memory/knowledge_graph/graph.json"

if [ ! -f "$KG_FILE" ]; then
    echo "知识图谱文件不存在"
    exit 1
fi

QUERY="$1"

if [ -z "$QUERY" ]; then
    echo "用法: kg_query <关键词>"
    echo "示例: kg_query 储能"
    exit 0
fi

echo "=== 知识图谱查询结果 ==="
echo "关键词: $QUERY"
echo ""

# 查找匹配的实体
python3 << PYEOF
import json

with open("$KG_FILE") as f:
    graph = json.load(f)

results = []
for id, e in graph.get('entities', {}).items():
    if "$QUERY" in e.get('name', '') or "$QUERY" in str(e.get('properties', {})):
        results.append(e)

if results:
    print(f"找到 {len(results)} 个实体:\n")
    for e in results[:10]:
        print(f"  - {e.get('name')} ({e.get('type')})")
        if e.get('properties'):
            print(f"    属性: {e.get('properties')}")
        if e.get('sources'):
            print(f"    来源: {', '.join(e.get('sources')[:3])}")
        print()
else:
    print("未找到匹配实体")
PYEOF
