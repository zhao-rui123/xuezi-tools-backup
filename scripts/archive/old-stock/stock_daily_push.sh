#!/bin/bash
# 自选股每日推送脚本 - V3完整版（新浪+雪球+技术分析）
# 工作日下午16:30自动执行

# 设置环境变量
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

cd /Users/zhaoruicn/.openclaw/workspace

# 使用V3完整版Python脚本
python3 stock_daily_push_v3.py >> /tmp/stock_push.log 2>&1

echo "[$(date)] 股票推送完成" >> ~/.openclaw/workspace/logs/stock_push.log
