#!/bin/bash
# 轻量级安全增强 - 启用危险操作确认和审计日志

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 创建日志目录
mkdir -p ~/.openclaw/.logs

# 设置环境变量
export OPENCLAW_SAFETY_ENABLED=1
export OPENCLAW_AUDIT_ENABLED=1

echo "🛡️ 轻量级安全增强已启用"
echo ""
echo "功能:"
echo "  ✅ 危险操作确认 (rm -rf, chmod 777 等)"
echo "  ✅ 审计日志记录"
echo "  ✅ 关键文件自动备份"
echo ""
echo "日志位置: ~/.openclaw/.logs/audit.log"
echo "查看报告: python3 ~/.openclaw/workspace/skills/security-scanner/audit_logger.py report"
