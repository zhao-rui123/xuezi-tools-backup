#!/bin/bash
# 安全扫描脚本 - 每周一执行
# 扫描 workspace/skills 目录的安全问题

WORKSPACE="$HOME/.openclaw/workspace"
LOG_FILE="/tmp/system-guard-scan.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') - 安全扫描开始" >> "$LOG_FILE"

cd "$WORKSPACE"
# 扫描主要技能包目录
python3 "$WORKSPACE/skills/security-scanner/security_scanner.py" "$WORKSPACE/skills" >> "$LOG_FILE" 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') - 安全扫描完成" >> "$LOG_FILE"
