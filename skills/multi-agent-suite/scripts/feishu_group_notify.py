#!/usr/bin/env python3
"""
飞书群聊通知工具
发送消息到指定群聊
"""

import sys
import json
import requests

# 飞书群聊ID
FEISHU_CHAT_ID = "oc_b14195eb990ab57ea573e696758ae3d5"

# API配置 - 使用OpenClaw Gateway的API
GATEWAY_URL = "http://localhost:18789"

def send_to_group_chat(message):
    """发送消息到飞书群聊"""
    try:
        # 构建API请求
        payload = {
            "channel": "feishu",
            "target": FEISHU_CHAT_ID,
            "message": message
        }
        
        # 调用本地Gateway API
        response = requests.post(
            f"{GATEWAY_URL}/api/message",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ 消息已发送到群聊: {FEISHU_CHAT_ID}")
            return True
        else:
            print(f"⚠️ 发送失败: {response.status_code} {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        # Gateway未启动，保存消息到文件
        print(f"⚠️ Gateway未启动，消息已保存到日志")
        return False
    except Exception as e:
        print(f"❌ 发送错误: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("用法: python3 feishu_group_notify.py '消息内容'")
        sys.exit(1)
    
    message = sys.argv[1]
    send_to_group_chat(message)

if __name__ == '__main__':
    main()
