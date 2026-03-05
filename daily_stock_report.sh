#!/bin/bash
# 每日自选股报告 - 收盘后自动推送
# 运行时间: 工作日 15:30

WORKSPACE="/Users/zhaoruicn/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/stock_report.log"

# 创建日志目录
mkdir -p "$WORKSPACE/logs"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始生成报告..." >> "$LOG_FILE"

# 运行分析脚本并保存结果
REPORT=$(cd "$WORKSPACE" && python3 stock_analyzer.py 2>&1)

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 报告生成成功" >> "$LOG_FILE"
    
    # 保存报告到文件
    echo "$REPORT" > "$WORKSPACE/reports/daily_report_$(date +%Y%m%d).txt"
    
    # 发送飞书消息（通过 OpenClaw）
    # 这里会调用 message 工具发送
    echo "$REPORT"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 报告生成失败: $REPORT" >> "$LOG_FILE"
    exit 1
fi
