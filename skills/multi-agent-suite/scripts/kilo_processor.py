#!/usr/bin/env python3
"""
Kilo通知处理器
读取通知队列并发送到飞书群聊
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

NOTIFICATION_DIR = Path("/tmp/kilo_notifications")

def process_notifications():
    """处理所有待发送的通知"""
    if not NOTIFICATION_DIR.exists():
        print("没有待处理的通知")
        return
    
    pending_files = list(NOTIFICATION_DIR.glob("*.json"))
    
    if not pending_files:
        print("没有待处理的通知")
        return
    
    print(f"发现 {len(pending_files)} 个待发送通知")
    
    for filepath in sorted(pending_files):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                notification = json.load(f)
            
            chat_id = notification.get('chat_id')
            message = notification.get('message')
            
            if chat_id and message:
                # 使用openclaw命令发送
                cmd = f'openclaw message send --channel feishu --target "{chat_id}" --message "{message[:500]}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ 已发送: {filepath.name}")
                    # 删除已发送的通知
                    filepath.unlink()
                else:
                    print(f"⚠️ 发送失败: {filepath.name} - {result.stderr}")
            else:
                print(f"⚠️ 无效通知: {filepath.name}")
                
        except Exception as e:
            print(f"❌ 处理失败: {filepath.name} - {e}")

if __name__ == '__main__':
    process_notifications()
