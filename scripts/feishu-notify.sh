#!/bin/bash
# OpenClaw Message 发送辅助脚本
# 用于 cron 等后台环境发送飞书消息

# 设置环境变量（cron 环境需要）
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

# 确保 openclaw 可执行
OPENCLAW_BIN="/opt/homebrew/bin/openclaw"
if [ ! -x "$OPENCLAW_BIN" ]; then
    # 尝试查找 openclaw
    OPENCLAW_BIN=$(which openclaw 2>/dev/null)
fi

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FEISHU_USER="ou_5a7b7ec0339ffe0c1d5bb6c5bc162579"

# 发送消息函数
send_message() {
    local message="$1"
    local channel="${2:-feishu}"
    
    if [ -z "$OPENCLAW_BIN" ]; then
        echo "错误: 找不到 openclaw 命令" >&2
        return 1
    fi
    
    # 使用 openclaw CLI 发送消息
    "$OPENCLAW_BIN" message send \
        --channel "$channel" \
        --target "$FEISHU_USER" \
        --message "$message" 2>&1
    
    return $?
}

# 发送文件函数
send_file() {
    local file_path="$1"
    local caption="${2:-}"
    local channel="${3:-feishu}"
    
    if [ ! -f "$file_path" ]; then
        echo "错误: 文件不存在: $file_path" >&2
        return 1
    fi
    
    if [ -z "$OPENCLAW_BIN" ]; then
        echo "错误: 找不到 openclaw 命令" >&2
        return 1
    fi
    
    # 使用 openclaw CLI 发送文件
    "$OPENCLAW_BIN" message send \
        --channel "$channel" \
        --target "$FEISHU_USER" \
        --media "$file_path" \
        --caption "$caption" 2>&1
    
    return $?
}

# 如果被直接调用（非source）
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    case "$1" in
        send)
            shift
            send_message "$@"
            ;;
        file)
            shift
            send_file "$@"
            ;;
        *)
            echo "用法: $0 send '消息内容' [channel]"
            echo "       $0 file /path/to/file '说明文字' [channel]"
            exit 1
            ;;
    esac
fi