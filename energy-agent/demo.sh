#!/bin/bash
# 储能电价循环优化Agent演示脚本
# 用法: python3 agent.py <电价Excel文件> --min-spread 100 --capacity 100

echo "储能电价循环优化Agent演示"
echo "用法: python3 agent.py <电价Excel文件> --min-spread 100 --capacity 100"
echo ""
echo "参数说明:"
echo "  <电价Excel文件>   - 国网电费清单Excel文件路径"
echo "  --min-spread      - 最小价差阈值(元/MWh)，默认100"
echo "  --capacity        - 储能容量(MWh)，默认100"
echo "  --format          - 输出格式: text/json/markdown/all"
echo "  --output/-o       - 输出文件路径(JSON/MD格式需要)"
echo ""
echo "示例:"
echo "  python3 agent.py data.xlsx --min-spread 100 --capacity 100"
echo "  python3 agent.py data.xlsx --min-spread 80 --capacity 200 --format json --output result.json"
echo "  python3 agent.py data.xlsx --format all --output result"
