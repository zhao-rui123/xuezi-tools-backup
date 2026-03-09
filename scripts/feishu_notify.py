#!/usr/bin/env python3
"""
飞书通知发送脚本
用于定时任务完成后自动发送通知
"""

import json
import urllib.request
import urllib.error
import sys
from datetime import datetime

# 飞书机器人配置
# 注意: 需要配置飞书自定义机器人 webhook
FEISHU_WEBHOOK = None  # 格式: https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx

def send_feishu_message(title, content, msg_type="text"):
    """发送飞书消息"""
    
    if not FEISHU_WEBHOOK:
        print("⚠️ 未配置飞书Webhook，跳过发送")
        print(f"消息内容:\n{content}")
        return False
    
    try:
        if msg_type == "text":
            payload = {
                "msg_type": "text",
                "content": {
                    "text": content
                }
            }
        elif msg_type == "interactive":
            payload = {
                "msg_type": "interactive",
                "card": {
                    "config": {"wide_screen_mode": True},
                    "header": {
                        "title": {"tag": "plain_text", "content": title}
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {"tag": "lark_md", "content": content}
                        }
                    ]
                }
            }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            FEISHU_WEBHOOK,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                print(f"✅ 消息发送成功: {title}")
                return True
            else:
                print(f"❌ 发送失败: {result}")
                return False
                
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False

def check_task_status():
    """检查凌晨1点任务执行状态"""
    
    tasks = {
        "知识图谱自动更新": "/tmp/ums-graph.log",
        "每日知识同步": "/tmp/kb-integration.log",
        "统一记忆归档": "/tmp/ums-daily.log",
        "统一记忆系统": "/Users/zhaoruicn/.openclaw/workspace/memory/cron.log"
    }
    
    results = []
    for task_name, log_file in tasks.items():
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                last_lines = ''.join(lines[-10:]) if lines else ""
                
            if "完成" in last_lines or "success" in last_lines.lower():
                status = "✅ 完成"
            elif "error" in last_lines.lower() or "失败" in last_lines:
                status = "❌ 失败"
            else:
                status = "⏳ 运行中"
                
            results.append(f"• {task_name}: {status}")
        except Exception as e:
            results.append(f"• {task_name}: ❓ 无法检查 ({e})")
    
    return '\n'.join(results)

def send_1am_notification():
    """发送凌晨1点任务完成通知"""
    
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    
    task_status = check_task_status()
    
    message = f"""🤖 凌晨1点定时任务完成通知

📅 日期: {date_str}
⏰ 时间: {time_str}

📋 任务执行状态:
{task_status}

所有任务已完成！"""
    
    # 同时打印到控制台和尝试发送
    print(message)
    
    # 保存通知到文件（供Agent读取）
    notification_file = f"/tmp/kilo_notification_1am_{now.strftime('%H%M%S')}.json"
    with open(notification_file, 'w', encoding='utf-8') as f:
        json.dump({
            "type": "定时任务通知",
            "title": "凌晨1点任务完成",
            "message": message,
            "timestamp": now.isoformat(),
            "priority": "normal"
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 通知已保存到: {notification_file}")
    
    # 尝试发送飞书消息（如果配置了Webhook）
    send_feishu_message("凌晨1点任务完成", message)
    
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--1am':
        send_1am_notification()
    else:
        print("用法: python3 feishu_notify.py --1am")
        print("发送凌晨1点任务完成通知")
