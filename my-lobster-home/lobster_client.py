#!/usr/bin/env python3
"""
OpenClaw 集成客户端
在每次会话中调用 API 更新状态
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:5000/api"  # 本地测试
# API_BASE = "http://106.54.25.161:5000/api"  # 生产环境

class LobsterHomeClient:
    """小龙虾之家客户端"""
    
    def __init__(self, api_base=None):
        self.api_base = api_base or API_BASE
        self.current_task = None
    
    def start_task(self, task_name: str) -> dict:
        """开始任务"""
        try:
            response = requests.post(
                f"{self.api_base}/task/start",
                json={'task_name': task_name},
                timeout=5
            )
            data = response.json()
            print(f"🦞 [小龙虾] 开始任务: {task_name}")
            print(f"🦞 [小龙虾] 移动到: {data.get('room', 'workspace')}")
            return data
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            return None
    
    def complete_task(self, tokens_used: int = 0) -> dict:
        """完成任务"""
        try:
            response = requests.post(
                f"{self.api_base}/task/complete",
                json={'tokens_used': tokens_used},
                timeout=5
            )
            data = response.json()
            print(f"🦞 [小龙虾] 任务完成")
            print(f"🦞 [小龙虾] 移动到: {data.get('next_room', 'livingroom')}")
            return data
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            return None
    
    def update_status(self, room: str = None, status: str = None) -> dict:
        """更新状态"""
        try:
            data = {}
            if room:
                data['room'] = room
            if status:
                data['status'] = status
            
            response = requests.post(
                f"{self.api_base}/status",
                json=data,
                timeout=5
            )
            return response.json()
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            return None
    
    def get_status(self) -> dict:
        """获取当前状态"""
        try:
            response = requests.get(f"{self.api_base}/status", timeout=5)
            return response.json()
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            return None
    
    def get_summary(self) -> dict:
        """获取每日总结"""
        try:
            response = requests.get(f"{self.api_base}/summary", timeout=5)
            return response.json()
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            return None
    
    def slacking(self) -> dict:
        """记录摸鱼"""
        try:
            response = requests.post(f"{self.api_base}/slacking", timeout=5)
            data = response.json()
            print(f"🦞 [小龙虾] 去摸鱼: {data.get('room', 'bathroom')}")
            return data
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            return None


# 便捷函数
def get_client() -> LobsterHomeClient:
    return LobsterHomeClient()

def start_task(task_name: str):
    return get_client().start_task(task_name)

def complete_task(tokens_used: int = 0):
    return get_client().complete_task(tokens_used)

def update_status(room: str = None, status: str = None):
    return get_client().update_status(room, status)

def get_status():
    return get_client().get_status()


# 测试
if __name__ == '__main__':
    print("🦞 测试小龙虾之家客户端")
    
    client = get_client()
    
    # 测试开始任务
    print("\n1. 开始任务测试")
    client.start_task("测试任务")
    
    import time
    time.sleep(2)
    
    # 测试完成任务
    print("\n2. 完成任务测试")
    client.complete_task(tokens_used=500)
    
    # 测试获取状态
    print("\n3. 获取状态")
    status = client.get_status()
    print(f"当前房间: {status.get('current_room')}")
    print(f"今日任务: {status.get('today', {}).get('tasks_completed')}")
    
    print("\n✅ 测试完成")
