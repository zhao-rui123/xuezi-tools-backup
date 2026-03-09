#!/bin/bash
# Session Memory Hook - 在 /new 时自动提取记忆
# 把这个脚本绑定到 /new 命令

# 设置环境变量
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export HOME="/Users/zhaoruicn"

# 运行记忆提取器
cd "$HOME/.openclaw/workspace/skills/enhanced-memory"
python3 session_distiller.py

echo "✅ 会话记忆已保存到 enhanced-memory"
