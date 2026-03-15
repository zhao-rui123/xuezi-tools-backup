#!/usr/bin/env python3
"""
小龙虾之家 - 自动数据更新客户端
运行在本地Mac，定时向服务器上报数据
"""

import json
import time
import os
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error

# 配置
SERVER_URL = "http://106.54.25.161:5000/api/update"
DATA_FILE = Path.home() / ".openclaw" / "workspace" / "memory" / "snapshots" / "lobster_data.json"

# 房间映射
ROOM_MAPPING = {
    "studio": "studio",      # 工作室 - 写代码
    "livingroom": "livingroom",  # 客厅 - 休息
    "bedroom": "bedroom",    # 卧室 - 深夜工作
    "kitchen": "kitchen",    # 厨房
    "teahouse": "teahouse",  # 茶水室 - 思考
}

def load_session_data():
    """从Memory Suite读取会话数据"""
    try:
        # 读取今日记忆文件
        today = datetime.now().strftime("%Y-%m-%d")
        memory_file = Path.home() / ".openclaw" / "workspace" / "memory" / f"{today}.md"
        
        tasks = []
        tokens_used = 0
        work_time = 0
        
        if memory_file.exists():
            content = memory_file.read_text()
            # 统计任务数（根据自动保存次数估算）
            saves = content.count("**自动保存**")
            tasks = saves
            
            # 估算Token（每轮对话约5000-10000 token）
            tokens_used = saves * 8000
            
            # 估算工作时间（每次保存约10分钟）
            work_time = saves * 600  # 秒
        
        return {
            "tasks_completed": max(tasks, 1),
            "tokens_used": tokens_used,
            "work_time_seconds": work_time
        }
    except Exception as e:
        print(f"读取数据失败: {e}")
        return {
            "tasks_completed": 1,
            "tokens_used": 5000,
            "work_time_seconds": 600
        }

def determine_room_and_status():
    """根据当前时间判断位置和状态"""
    hour = datetime.now().hour
    
    if 0 <= hour < 8:
        return "bedroom", "sleeping"
    elif 8 <= hour < 9:
        return "kitchen", "breakfast"
    elif 9 <= hour < 12:
        return "studio", "working"
    elif 12 <= hour < 14:
        return "dining", "lunch"
    elif 14 <= hour < 18:
        return "studio", "working"
    elif 18 <= hour < 20:
        return "dining", "dinner"
    elif 20 <= hour < 23:
        return "studio", "working"
    else:
        return "bedroom", "resting"

def send_update(data):
    """发送数据到服务器"""
    try:
        headers = {
            "Content-Type": "application/json"
        }
        json_data = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(
            SERVER_URL,
            data=json_data,
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('success', False)
    except Exception as e:
        print(f"发送失败: {e}")
        return False

def main():
    """主函数 - 每10分钟更新一次"""
    print("🦞 小龙虾之家自动更新客户端启动")
    print(f"服务器: {SERVER_URL}")
    print("更新间隔: 10分钟")
    print("-" * 50)
    
    while True:
        try:
            # 加载数据
            session_data = load_session_data()
            room, status = determine_room_and_status()
            
            # 构建更新数据
            update_data = {
                "tasks_completed": session_data["tasks_completed"],
                "tokens_used": session_data["tokens_used"],
                "work_time_seconds": session_data["work_time_seconds"],
                "current_room": room,
                "current_status": status,
                "current_task": "自动同步任务",
                "task": f"更新于 {datetime.now().strftime('%H:%M')}"
            }
            
            # 发送更新
            success = send_update(update_data)
            
            if success:
                print(f"✅ {datetime.now().strftime('%H:%M:%S')} 数据已更新")
                print(f"   任务: {update_data['tasks_completed']} | Token: {update_data['tokens_used']:,} | 房间: {room}")
            else:
                print(f"❌ {datetime.now().strftime('%H:%M:%S')} 更新失败")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        # 等待10分钟
        time.sleep(600)

if __name__ == "__main__":
    main()
