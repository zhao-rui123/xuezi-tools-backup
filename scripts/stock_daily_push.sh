#!/bin/bash
# 自选股每日推送脚本
# 工作日下午15:30自动执行

cd /Users/zhaoruicn/.openclaw/workspace

# 使用简化版 Python 脚本推送（避免 AkShare 超时问题）
python3 stock_feishu_push_simple.py >> /tmp/stock_push.log 2>&1

echo "[$(date)] 股票推送完成" >> ~/.openclaw/workspace/logs/stock_push.log
