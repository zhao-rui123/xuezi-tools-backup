#!/bin/bash

# 会话状态保存与恢复脚本
# 在切换模型前保存当前状态，切换后恢复

SESSION_STATE_DIR="$HOME/.openclaw/workspace/.session-states"
DATE_STR=$(date '+%Y%m%d_%H%M%S')

mkdir -p "$SESSION_STATE_DIR"

save_session_state() {
    echo "💾 保存当前会话状态..."
    
    state_file="$SESSION_STATE_DIR/state_$DATE_STR.json"
    
    # 保存当前模型
    current_model=$(openclaw config get agents.defaults.model.primary 2>/dev/null | grep -v "No value" | head -1)
    
    # 保存当前工作目录
    current_dir=$(pwd)
    
    # 保存 Git 状态
    git_status=$(cd ~/.openclaw/workspace && git status --short 2>/dev/null)
    
    # 创建状态文件
    cat > "$state_file" << EOF
{
  "timestamp": "$DATE_STR",
  "model": "$current_model",
  "working_directory": "$current_dir",
  "git_status": $(echo "$git_status" | jq -R -s -c 'split("\n") | map(select(length > 0))'),
  "memory_files": $(ls ~/.openclaw/workspace/memory/*.md 2>/dev/null | wc -l | xargs echo)
}
EOF
    
    echo "  ✅ 状态已保存: $state_file"
    echo "  当前模型: $current_model"
}

restore_session_state() {
    echo "🔄 恢复会话状态..."
    
    # 找到最近的状态文件
    latest_state=$(ls -t "$SESSION_STATE_DIR"/state_*.json 2>/dev/null | head -1)
    
    if [ -z "$latest_state" ]; then
        echo "  ⚠️ 未找到保存的状态"
        return 1
    fi
    
    echo "  从 $latest_state 恢复"
    
    # 显示状态摘要
    echo ""
    echo "📋 上次会话状态:"
    cat "$latest_state" | jq -r '
      "  时间: \(.timestamp)",
      "  模型: \(.model)",
      "  工作目录: \(.working_directory)",
      "  Git变更: \(.git_status | length) 个文件",
      "  记忆文件: \(.memory_files) 个"
    '
}

cleanup_old_states() {
    echo "🧹 清理旧状态文件..."
    find "$SESSION_STATE_DIR" -name "state_*.json" -mtime +7 -delete
    echo "  ✅ 已清理7天前的状态文件"
}

case "${1:-save}" in
    save)
        save_session_state
        ;;
    restore)
        restore_session_state
        ;;
    cleanup)
        cleanup_old_states
        ;;
    *)
        echo "用法: $0 [save|restore|cleanup]"
        echo "  save    - 保存当前会话状态"
        echo "  restore - 恢复上次会话状态"
        echo "  cleanup - 清理旧状态文件"
        ;;
esac
