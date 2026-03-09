#!/usr/bin/env python3
"""
像素风小龙虾任务看板 - 状态追踪器
实时追踪AI助手工作状态并记录统计数据
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

class AgentStatusTracker:
    """AI助手状态追踪器"""
    
    def __init__(self, data_dir: str = None):
        """初始化追踪器"""
        if data_dir is None:
            # 获取workspace路径
            workspace = Path.home() / '.openclaw' / 'workspace'
            data_dir = workspace / 'agent-dashboard' / 'data'
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats_file = self.data_dir / 'stats.json'
        self.status_file = self.data_dir / 'status.json'
        self.history_dir = self.data_dir / 'history'
        self.history_dir.mkdir(exist_ok=True)
        
        # 当前状态
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
            'tasks': []
        }
        
        # 休息计时器
        self.rest_timer = None
        self.rest_delay = 300  # 5分钟 = 300秒
        
        # 加载数据
        self.load_data()
        
        # 启动后台线程
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def load_data(self):
        """加载历史数据"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 检查是否需要新的一天
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 如果是新的一天，归档旧数据并重置
                if data.get('today', {}).get('date') != today:
                    self._archive_old_data(data.get('today', {}))
                    self.today_stats['date'] = today
                else:
                    self.today_stats = data.get('today', self.today_stats)
                    
                # 恢复当前状态
                self.current_status = data.get('current_status', 'resting')
                self.last_activity = datetime.fromisoformat(
                    data.get('last_activity', datetime.now().isoformat())
                )
                    
            except Exception as e:
                print(f"加载数据失败: {e}")
    
    def save_data(self):
        """保存数据到文件"""
        try:
            data = {
                'today': self.today_stats,
                'current_status': self.current_status,
                'last_activity': self.last_activity.isoformat(),
                'current_task': self.current_task,
                'updated_at': datetime.now().isoformat()
            }
            
            # 保存主统计文件
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 保存当前状态文件（供前端快速读取）
            status_data = {
                'status': self.current_status,
                'task': self.current_task,
                'last_activity': self.last_activity.isoformat(),
                'tasks_completed': self.today_stats['tasks_completed'],
                'tokens_used': self.today_stats['tokens_used'],
                'work_time': self._format_time(self.today_stats['work_time_seconds'])
            }
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, ensure_ascii=False, indent=2)
                
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
            print(f"已归档 {old_data['date']} 的数据")
        except Exception as e:
            print(f"归档数据失败: {e}")
    
    def start_task(self, task_name: str, estimated_tokens: int = 0):
        """开始新任务"""
        self.current_task = task_name
        self.task_start_time = datetime.now()
        self.last_activity = datetime.now()
        
        # 切换到工作状态
        self.switch_status('working')
        
        # 取消休息计时
        self._cancel_rest_timer()
        
        self.save_data()
        print(f"🦞 开始任务: {task_name}")
    
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
        
        print(f"✅ 完成任务: {self.current_task} (消耗 {tokens_used} tokens)")
        
        # 重置当前任务
        self.current_task = None
        self.task_start_time = None
        self.last_activity = datetime.now()
        
        # 切换到非工作状态
        self._switch_to_random_rest_status()
        
        # 启动休息计时器
        self._start_rest_timer()
        
        self.save_data()
    
    def switch_status(self, status: str):
        """切换状态"""
        valid_statuses = ['resting', 'working', 'thinking', 'exercising', 'eating', 'sleeping']
        
        if status not in valid_statuses:
            print(f"无效状态: {status}")
            return
            
        old_status = self.current_status
        self.current_status = status
        self.last_activity = datetime.now()
        
        # 如果进入工作状态，取消休息计时
        if status == 'working':
            self._cancel_rest_timer()
        elif old_status == 'working':
            # 从工作状态退出，启动休息计时
            self._start_rest_timer()
        
        self.save_data()
        print(f"🦞 状态切换: {old_status} → {status}")
    
    def _switch_to_random_rest_status(self):
        """随机切换到休息状态"""
        import random
        rest_statuses = ['resting', 'thinking', 'exercising', 'eating']
        
        # 根据时间偏好
        hour = datetime.now().hour
        if 11 <= hour <= 13 or 17 <= hour <= 19:
            # 饭点优先吃饭
            weights = [0.1, 0.1, 0.1, 0.7]
        elif 7 <= hour <= 9 or 18 <= hour <= 20:
            # 早晨和傍晚优先运动
            weights = [0.2, 0.2, 0.5, 0.1]
        else:
            # 其他时间平均
            weights = [0.3, 0.3, 0.2, 0.2]
        
        new_status = random.choices(rest_statuses, weights=weights)[0]
        self.switch_status(new_status)
    
    def _start_rest_timer(self):
        """启动休息计时器"""
        self._cancel_rest_timer()
        self.rest_timer = threading.Timer(self.rest_delay, self._on_rest_timeout)
        self.rest_timer.start()
    
    def _cancel_rest_timer(self):
        """取消休息计时器"""
        if self.rest_timer:
            self.rest_timer.cancel()
            self.rest_timer = None
    
    def _on_rest_timeout(self):
        """休息计时器超时回调"""
        if self.current_status == 'working':
            print("⏰ 5分钟无活动，自动切换到休息状态")
            self._switch_to_random_rest_status()
    
    def add_tokens(self, tokens: int):
        """添加token消耗统计"""
        self.today_stats['tokens_used'] += tokens
        self.save_data()
    
    def get_status(self) -> dict:
        """获取当前状态"""
        return {
            'status': self.current_status,
            'current_task': self.current_task,
            'last_activity': self.last_activity.isoformat(),
            'tasks_completed': self.today_stats['tasks_completed'],
            'tokens_used': self.today_stats['tokens_used'],
            'work_time_seconds': self.today_stats['work_time_seconds'],
            'work_time_formatted': self._format_time(self.today_stats['work_time_seconds'])
        }
    
    def get_today_stats(self) -> dict:
        """获取今日统计"""
        return self.today_stats.copy()
    
    def get_history(self, days: int = 7) -> list:
        """获取历史统计"""
        history = []
        today = datetime.now()
        
        for i in range(1, days + 1):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            file_path = self.history_dir / f"{date}.json"
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        history.append({
                            'date': date,
                            'tasks': data.get('tasks_completed', 0),
                            'tokens': data.get('tokens_used', 0),
                            'work_time': data.get('work_time_seconds', 0)
                        })
                except Exception:
                    pass
        
        return history
    
    def _update_loop(self):
        """后台更新循环"""
        while self.running:
            try:
                # 检查是否深夜
                hour = datetime.now().hour
                if (hour >= 23 or hour < 7) and self.current_status != 'sleeping':
                    self.switch_status('sleeping')
                
                # 每分钟保存一次数据
                self.save_data()
                
                time.sleep(60)
                
            except Exception as e:
                print(f"更新循环出错: {e}")
                time.sleep(60)
    
    def _format_time(self, seconds: int) -> str:
        """格式化时间"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    def stop(self):
        """停止追踪器"""
        self.running = False
        self._cancel_rest_timer()
        self.save_data()
        print("🦞 状态追踪器已停止")


# 全局追踪器实例
_tracker = None

def get_tracker() -> AgentStatusTracker:
    """获取全局追踪器实例"""
    global _tracker
    if _tracker is None:
        _tracker = AgentStatusTracker()
    return _tracker

def start_task(task_name: str, estimated_tokens: int = 0):
    """开始任务（便捷函数）"""
    tracker = get_tracker()
    tracker.start_task(task_name, estimated_tokens)

def complete_task(tokens_used: int = 0, success: bool = True):
    """完成任务（便捷函数）"""
    tracker = get_tracker()
    tracker.complete_task(tokens_used, success)

def switch_status(status: str):
    """切换状态（便捷函数）"""
    tracker = get_tracker()
    tracker.switch_status(status)

def add_tokens(tokens: int):
    """添加token消耗（便捷函数）"""
    tracker = get_tracker()
    tracker.add_tokens(tokens)

def get_status() -> dict:
    """获取当前状态（便捷函数）"""
    tracker = get_tracker()
    return tracker.get_status()


if __name__ == '__main__':
    # 测试代码
    print("🦞 启动小龙虾状态追踪器")
    tracker = get_tracker()
    
    try:
        # 模拟一些任务
        print("\n模拟任务流程:")
        
        start_task("测试任务1")
        time.sleep(2)
        complete_task(tokens_used=1000)
        
        time.sleep(1)
        
        start_task("测试任务2")
        time.sleep(2)
        complete_task(tokens_used=2000)
        
        print("\n当前状态:")
        print(json.dumps(get_status(), ensure_ascii=False, indent=2))
        
        print("\n今日统计:")
        print(json.dumps(tracker.get_today_stats(), ensure_ascii=False, indent=2))
        
        # 保持运行
        print("\n按 Ctrl+C 停止...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        tracker.stop()
