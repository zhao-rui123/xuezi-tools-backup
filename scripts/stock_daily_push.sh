#!/bin/bash
# 自选股每日推送脚本 - 新浪财经+雪球融合版
# 工作日下午15:30自动执行

cd /Users/zhaoruicn/.openclaw/workspace

# 使用融合版 Python 脚本推送（新浪财经实时数据 + 雪球PE/PB指标）
python3 stock_feishu_push_fusion.py >> /tmp/stock_push.log 2>&1

echo "[$(date)] 股票推送完成" >> ~/.openclaw/workspace/logs/stock_push.log
