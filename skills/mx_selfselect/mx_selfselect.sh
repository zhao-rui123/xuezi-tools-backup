#!/bin/bash
# 妙选自选股管理脚本

API_KEY="mkt_zdTwvCWmIr9g4mHoM8sOsaK8M_ffrhinQPP-GAkhTNs"

ACTION=$1
shift
STOCK=$*

if [ "$ACTION" = "query" ]; then
    echo "查询自选股列表..."
    curl -s -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/self-select/get' \
      -H 'Content-Type: application/json' \
      -H "apikey: $API_KEY" \
      --data '{"query": "查询我的自选股列表"}' | python3 -c "
import json,sys
d=json.load(sys.stdin)
data = d.get('data',{}).get('allResults',{}).get('result',{}).get('dataList',[])
print(f'共 {len(data)} 只自选股\n')
print('| 代码 | 名称 | 最新价 | 涨跌幅 |')
print('|---|---|---|---|')
for s in data:
    print(f\"{s.get('SECURITY_CODE','')} | {s.get('SECURITY_SHORT_NAME','')} | {s.get('NEWEST_PRICE','')} | {s.get('CHG','')}%\")
"
elif [ "$ACTION" = "add" ]; then
    echo "添加自选股: $STOCK"
    curl -s -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/self-select/manage' \
      -H 'Content-Type: application/json' \
      -H "apikey: $API_KEY" \
      --data "{\"query\": \"把${STOCK}添加到我的自选股列表\"}"
elif [ "$ACTION" = "remove" ]; then
    echo "删除自选股: $STOCK"
    curl -s -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/self-select/manage' \
      -H 'Content-Type: application/json' \
      -H "apikey: $API_KEY" \
      --data "{\"query\": \"把${STOCK}从我的自选股列表删除\"}"
else
    echo "用法: mx_selfselect [query|add|remove] [股票名称/代码]"
    echo "  query   - 查询自选股列表"
    echo "  add     - 添加股票到自选"
    echo "  remove  - 从自选删除股票"
fi
