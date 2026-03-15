#!/usr/bin/env python3
"""
Memory Suite v3.0 - 错误通知脚本
任务失败时发送飞书通知
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置
NOTIFY_SCRIPT = Path("/path/to/workspace/scripts/feishu_notify.sh")

def send_notification(title, message, level="urgent"):
    """发送飞书通知"""
    if not NOTIFY_SCRIPT.exists():
        print(f"⚠️  通知脚本不存在: {NOTIFY_SCRIPT}")
        return False
    
    try:
        subprocess.run([
            str(NOTIFY_SCRIPT),
            title,
            message,
            level
        ], check=True, capture_output=True)
        print(f"✅ 通知已发送: {title}")
        return True
    except Exception as e:
        print(f"❌ 通知发送失败: {e}")
        return False

def notify_task_failure(task_name, error_message):
    """通知任务失败"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    title = f"❌ Memory Suite 任务失败"
    message = f"""
🤖 Memory Suite 告警

⏰ 时间: {timestamp}
📌 任务: {task_name}
❌ 错误: {error_message}

请检查系统状态！
"""
    
    return send_notification(title, message, level="urgent")

def notify_system_error(error_message):
    """通知系统错误"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    title = f"🚨 Memory Suite 系统错误"
    message = f"""
🤖 Memory Suite 紧急告警

⏰ 时间: {timestamp}
❌ 错误: {error_message}

请立即检查系统！
"""
    
    return send_notification(title, message, level="urgent")

def main():
    """主函数 - 测试通知"""
    if len(sys.argv) < 2:
        print("用法: python3 error_notifier.py <task_name> [error_message]")
        print("  或: python3 error_notifier.py --test")
        sys.exit(1)
    
    if sys.argv[1] == "--test":
        print("发送测试通知...")
        notify_task_failure("test_task", "这是一条测试消息")
    else:
        task_name = sys.argv[1]
        error_message = sys.argv[2] if len(sys.argv) > 2 else "未知错误"
        notify_task_failure(task_name, error_message)

if __name__ == "__main__":
    main()
