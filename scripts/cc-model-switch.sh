#!/bin/bash
# Claude Code 模型切换脚本
# 用法: cc-model-switch.sh [opus|minimax]

set -e

CLAUDE_SETTINGS="$HOME/.claude/settings.json"
BACKUP_DIR="$HOME/.claude/backups"

# 确保备份目录存在
mkdir -p "$BACKUP_DIR"

# 当前时间戳
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Opus 配置
OPUS_CONFIG='{
  "env": {
    "ANTHROPIC_BASE_URL": "https://timesniper.club",
    "ANTHROPIC_AUTH_TOKEN": "sk-OLqePftCUT0kOGggfgGtgeMOE3km0hPXwxUf6FTpFFL7mdsJ",
    "ANTHROPIC_MODEL": "claude-opus-4-6",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-6",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-opus-4-6",
    "ANTHROPIC_SMALL_FAST_MODEL": "claude-opus-4-6"
  },
  "includeCoAuthoredBy": false,
  "enabledPlugins": {
    "pyright-lsp@claude-plugins-official": true,
    "typescript-lsp@claude-plugins-official": true,
    "gopls-lsp@claude-plugins-official": true,
    "superpowers@claude-plugins-official": true
  }
}'

# MiniMax 配置
MINIMAX_CONFIG='{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.minimaxi.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "sk-cp-TaEn7XZHReif66-VaxR-UZJuHCoYYYqho4xu6pV22L3MtAL9oImB0iubia4dRjZDN-0avV5_rSS2ggBC6w2gHYz1tYN0semS3mps1PrA9lS-16qJhoh8l3Q",
    "ANTHROPIC_MODEL": "MiniMax-M2.7",
    "ANTHROPIC_SMALL_FAST_MODEL": "MiniMax-M2.7",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "MiniMax-M2.7",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "MiniMax-M2.7",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "MiniMax-M2.7",
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "includeCoAuthoredBy": false,
  "enabledPlugins": {
    "pyright-lsp@claude-plugins-official": true,
    "typescript-lsp@claude-plugins-official": true,
    "gopls-lsp@claude-plugins-official": true,
    "superpowers@claude-plugins-official": true
  }
}'

# 显示用法
show_usage() {
    echo "用法: cc-model-switch.sh [opus|minimax|status]"
    echo ""
    echo "选项:"
    echo "  opus     - 切换到 Opus 模型 (架构设计/验收)"
    echo "  minimax  - 切换到 MiniMax 模型 (执行开发)"
    echo "  status   - 查看当前模型配置"
    echo ""
    echo "示例:"
    echo "  cc-model-switch.sh opus      # 切换 Opus"
    echo "  cc-model-switch.sh minimax   # 切换 MiniMax"
}

# 备份当前配置
backup_current() {
    if [ -f "$CLAUDE_SETTINGS" ]; then
        cp "$CLAUDE_SETTINGS" "$BACKUP_DIR/settings-backup-$TIMESTAMP.json"
        echo "✓ 已备份当前配置到: $BACKUP_DIR/settings-backup-$TIMESTAMP.json"
    fi
}

# 切换到 Opus
switch_to_opus() {
    echo "🔄 切换到 Opus 模型..."
    backup_current
    echo "$OPUS_CONFIG" > "$CLAUDE_SETTINGS"
    echo "✅ 已切换到 Opus (claude-opus-4-6)"
    echo ""
    echo "适用场景:"
    echo "  - 架构设计"
    echo "  - 技术选型"
    echo "  - 代码评审"
    echo "  - 验收审查"
}

# 切换到 MiniMax
switch_to_minimax() {
    echo "🔄 切换到 MiniMax 模型..."
    backup_current
    echo "$MINIMAX_CONFIG" > "$CLAUDE_SETTINGS"
    echo "✅ 已切换到 MiniMax (MiniMax-M2.7)"
    echo ""
    echo "适用场景:"
    echo "  - 执行开发"
    echo "  - 代码编写"
    echo "  - 调试修复"
    echo "  - 日常任务"
}

# 查看当前状态
show_status() {
    if [ ! -f "$CLAUDE_SETTINGS" ]; then
        echo "❌ 未找到 Claude Code 配置文件"
        return 1
    fi
    
    echo "📊 当前 Claude Code 配置:"
    echo ""
    
    CURRENT_MODEL=$(cat "$CLAUDE_SETTINGS" | grep -o '"ANTHROPIC_MODEL": "[^"]*"' | cut -d'"' -f4 || echo "unknown")
    CURRENT_BASE_URL=$(cat "$CLAUDE_SETTINGS" | grep -o '"ANTHROPIC_BASE_URL": "[^"]*"' | cut -d'"' -f4 || echo "unknown")
    
    echo "  模型: $CURRENT_MODEL"
    echo "  API:  $CURRENT_BASE_URL"
    echo ""
    
    if echo "$CURRENT_MODEL" | grep -qi "opus"; then
        echo "✅ 当前是 Opus 模式 (架构设计/验收)"
    elif echo "$CURRENT_MODEL" | grep -qi "minimax"; then
        echo "✅ 当前是 MiniMax 模式 (执行开发)"
    else
        echo "⚠️  未知模型配置"
    fi
}

# 主逻辑
case "${1:-}" in
    opus)
        switch_to_opus
        ;;
    minimax)
        switch_to_minimax
        ;;
    status)
        show_status
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
