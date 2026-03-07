#!/bin/bash
# Stock Analysis Pro - 每日推送脚本
# 工作日16:30执行

cd /Users/zhaoruicn/.openclaw/workspace/skills/stock-analysis-pro

# 生成并发送日报
python3 -m stock_analysis_pro daily --send-feishu >> /tmp/stock_analysis_pro.log 2>&1

echo "[$(date)] 股票日报推送完成" >> ~/.openclaw/workspace/logs/stock_analysis_pro.log
