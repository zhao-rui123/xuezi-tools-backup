#!/usr/bin/env python3
"""
小龙虾房子看板 v2.0 - 状态追踪器
与 OpenClaw 深度集成，自动记录任务和状态
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

class LobsterHouseTracker:
    """小龙虾房子状态追踪器"""
    
    # 房间映射
    ROOMS = {
        'study': '书房',
        'workspace': '工作室',
        'gameroom': '游戏室',
        'bedroom': '休息室',
        'bathroom': '卫生间',
        'kitchen': '厨房',
        'playground': '操场'
    }
    
    # 状态到房间的映射
    STATUS_TO_ROOM = {
        'working': 'workspace',
        'thinking': 'study',
        'gaming': 'gameroom',
        'resting': 'bedroom',
        'sleeping': 'bedroom',
        'slacking': 'bathroom',
        'eating': 'kitchen',
        'exercising': 'playground'
    }
    
    def __init__(self, data_dir: str = None):
        """初始化追踪器"""
        if data_dir is None:
            workspace = Path.home() / '.openclaw' / 'workspace'
            data_dir = workspace / 'agent-dashboard-v2' / 'data'
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats_file = self.data_dir / 'stats.json'
        self.history_dir = self.data_dir / 'history'
        self.history_dir.mkdir(exist_ok=True)
        
        # 当前状态
        self.current_room = 'bedroom'
        self.current_status = 'resting'
        self.last_activity = datetime.now()
        self.current_task = None
        self.task_start_time = None
        
        # 今日统计
        self.today_stats = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'tasks_completed': 0,
            'tokens_used': 0,
            'work_time_seconds': 0,
            'room_time': {room: 0 for room in self.ROOMS.keys()},
            'tasks': []
        }
        
        # 历史数据（30天）
        self.history = []
        
        # 计时器
        self.rest_timer = None
        self.gaming_timer = None
        self.slacking_timer = None
        
        # 加载数据
        self.load_data()
        
        # 启动后台线程
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def load_data(self):
        """加载历史数据"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 检查是否新的一天
                if data.get('today', {}).get('date') != today:
                    self._archive_old_data(data.get('today', {}))
                    self.today_stats['date'] = today
                else:
                    self.today_stats = data.get('today', self.today_stats)
                
                self.current_status = data.get('current_status', 'resting')
                self.current_room = data.get('current_room', 'bedroom')
                self.last_activity = datetime.fromisoformat(
                    data.get('last_activity', datetime.now().isoformat())
                )
                
                # 加载历史
                self._load_history()
                
            except Exception as e:
                print(f"加载数据失败: {e}")
    
    def save_data(self):
        """保存数据"""
        try:
            data = {
                'today': self.today_stats,
                'current_status': self.current_status,
                'current_room': self.current_room,
                'last_activity': self.last_activity.isoformat(),
                'current_task': self.current_task,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存数据失败: {e}")
    
    def _archive_old_data(self, old_data: dict):
        """归档旧数据"""
        if not old_data or old_data.get('date') == datetime.now().strftime('%Y-%m-%d'):
            return
        
        archive_file = self.history_dir / f"{old_data['date']}.json"
        try:
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(old_data, f, ensure_ascii=False, indent=2)
            print(f"📦 已归档 {old_data['date']} 的数据")
        except Exception as e:
            print(f"归档数据失败: {e}")
    
    def _load_history(self, days: int = 30):
        """加载历史数据"""
        self.history = []
        today = datetime.now()
        
        for i in range(1, days + 1):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            file_path = self.history_dir / f"{date}.json"
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.history.append({
                            'date': date,
                            'tasks': data.get('tasks_completed', 0),
                            'tokens': data.get('tokens_used', 0),
                            'work_time': data.get('work_time_seconds', 0)
                        })
                except Exception:
                    pass
    
    def switch_status(self, status: str):
        """切换状态并移动房间"""
        if status not in self.STATUS_TO_ROOM:
            print(f"无效状态: {status}")
            return
        
        old_status = self.current_status
        self.current_status = status
        self.current_room = self.STATUS_TO_ROOM[status]
        self.last_activity = datetime.now()
        
        # 特殊状态处理
        if status == 'working':
            self._cancel_timers()
        elif status == 'resting':
            self._start_rest_timer()
            self._start_gaming_timer()
        
        self.save_data()
        print(f"🦞 状态切换: {old_status} → {status} ({self.ROOMS[self.current_room]})")
        
        return self.current_room
    
    def start_task(self, task_name: str, estimated_tokens: int = 0):
        """开始任务"""
        self.current_task = task_name
        self.task_start_time = datetime.now()
        self.switch_status('working')
        
        print(f"🚀 开始任务: {task_name}")
        return self.current_room
    
    def complete_task(self, tokens_used: int = 0, success: bool = True):
        """完成任务"""
        if not self.current_task:
            return
        
        task_duration = 0
        if self.task_start_time:
            task_duration = (datetime.now() - self.task_start_time).total_seconds()
            self.today_stats['work_time_seconds'] += int(task_duration)
        
        # 记录任务
        task_record = {
            'name': self.current_task,
            'start_time': self.task_start_time.isoformat() if self.task_start_time else None,
            'end_time': datetime.now().isoformat(),
            'duration_seconds': int(task_duration),
            'tokens_used': tokens_used,
            'success': success
        }
        
        self.today_stats['tasks'].append(task_record)
        self.today_stats['tasks_completed'] += 1
        self.today_stats['tokens_used'] += tokens_used
        
        print(f"✅ 完成任务: {self.current_task}")
        print(f"   耗时: {int(task_duration)}秒")
        print(f"   Token: {tokens_used}")
        
        # 判断任务强度
        if task_duration > 1800:  # 超过30分钟
            self.switch_status('exercising')
            print(f"🦞 高强度工作！去操场运动一下")
        else:
            # 随机选择休息状态
            import random
            hour = datetime.now().hour
            
            if 11 <= hour <= 13 or 17 <= hour <= 19:
                self.switch_status('eating')
            else:
                rest_statuses = ['resting', 'thinking']
                new_status = random.choice(rest_statuses)
                self.switch_status(new_status)
        
        # 摸鱼检测
        self._check_slacking()
        
        self.current_task = None
        self.task_start_time = None
        self.save_data()
        
        return self.current_room
    
    def _check_slacking(self):
        """检查是否要摸鱼"""
        import random
        if random.random() < 0.15:  # 15%概率
            threading.Timer(3, self._go_slacking).start()
    
    def _go_slacking(self):
        """去摸鱼"""
        self.switch_status('slacking')
        print(f"🦞 去卫生间摸鱼...")
        
        # 3-5分钟后回来
        return_time = 180 + int((hash(self.current_task) % 120))
        threading.Timer(return_time, self._return_from_slacking).start()
    
    def _return_from_slacking(self):
        """摸鱼回来"""
        self.switch_status('resting')
        print(f"🦞 摸鱼结束，继续休息")
    
    def _start_rest_timer(self):
        """启动休息计时器（5分钟无工作自动休息）"""
        self._cancel_timers()
        self.rest_timer = threading.Timer(300, self._on_rest_timeout)
        self.rest_timer.start()
    
    def _start_gaming_timer(self):
        """启动游戏计时器（休息10分钟后去打游戏）"""
        self.gaming_timer = threading.Timer(600, self._on_gaming_timeout)
        self.gaming_timer.start()
    
    def _cancel_timers(self):
        """取消所有计时器"""
        if self.rest_timer:
            self.rest_timer.cancel()
            self.rest_timer = None
        if self.gaming_timer:
            self.gaming_timer.cancel()
            self.gaming_timer = None
    
    def _on_rest_timeout(self):
        """休息计时器超时"""
        if self.current_status == 'working':
            self.switch_status('resting')
            print(f"⏰ 5分钟无活动，自动休息")
    
    def _on_gaming_timeout(self):
        """游戏计时器超时"""
        if self.current_status == 'resting':
            self.switch_status('gaming')
            print(f"🎮 休息够了，开始打游戏！")
    
    def add_tokens(self, tokens: int):
        """添加token消耗"""
        self.today_stats['tokens_used'] += tokens
        self.save_data()
    
    def get_daily_summary(self) -> dict:
        """获取每日总结（用于飞书推送）"""
        # 找出最耗时的任务
        longest_task = None
        if self.today_stats['tasks']:
            longest_task = max(self.today_stats['tasks'], 
                             key=lambda x: x.get('duration_seconds', 0))
        
        # 房间停留时间排序
        room_times = sorted(
            self.today_stats['room_time'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'date': self.today_stats['date'],
            'tasks_completed': self.today_stats['tasks_completed'],
            'tokens_used': self.today_stats['tokens_used'],
            'work_time_seconds': self.today_stats['work_time_seconds'],
            'work_time_formatted': self._format_time(self.today_stats['work_time_seconds']),
            'longest_task': longest_task,
            'room_times': room_times[:3],  # Top 3房间
            'current_room': self.ROOMS.get(self.current_room, '未知'),
            'current_status': self.current_status
        }
    
    def _format_time(self, seconds: int) -> str:
        """格式化时间"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        return f"{minutes}分钟"
    
    def _update_loop(self):
        """后台更新循环"""
        while self.running:
            try:
                # 检查是否深夜
                hour = datetime.now().hour
                if (hour >= 23 or hour < 7) and self.current_status != 'sleeping':
                    self.switch_status('sleeping')
                
                # 记录房间时间
                if self.current_room:
                    self.today_stats['room_time'][self.current_room] = \
                        self.today_stats['room_time'].get(self.current_room, 0) + 60
                
                # 保存数据
                self.save_data()
                
                time.sleep(60)
                
            except Exception as e:
                print(f"更新循环出错: {e}")
                time.sleep(60)
    
    def stop(self):
        """停止追踪器"""
        self.running = False
        self._cancel_timers()
        self.save_data()
        print("🦞 小龙虾追踪器已停止")


# 全局实例
_tracker = None

def get_tracker() -> LobsterHouseTracker:
    """获取全局追踪器"""
    global _tracker
    if _tracker is None:
        _tracker = LobsterHouseTracker()
    return _tracker

# 便捷函数
def start_task(task_name: str, estimated_tokens: int = 0):
    return get_tracker().start_task(task_name, estimated_tokens)

def complete_task(tokens_used: int = 0, success: bool = True):
    return get_tracker().complete_task(tokens_used, success)

def switch_status(status: str):
    return get_tracker().switch_status(status)

def add_tokens(tokens: int):
    get_tracker().add_tokens(tokens)

def get_daily_summary() -> dict:
    return get_tracker().get_daily_summary()

def get_current_room() -> str:
    return get_tracker().current_room


if __name__ == '__main__':
    print("🦞 启动小龙虾房子追踪器 v2.0")
    tracker = get_tracker()
    
    try:
        print("\n当前状态:")
        print(f"  位置: {tracker.ROOMS[tracker.current_room]}")
        print(f"  状态: {tracker.current_status}")
        print(f"  今日任务: {tracker.today_stats['tasks_completed']}")
        print(f"  Token消耗: {tracker.today_stats['tokens_used']}")
        
        print("\n按 Ctrl+C 停止...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        tracker.stop()
