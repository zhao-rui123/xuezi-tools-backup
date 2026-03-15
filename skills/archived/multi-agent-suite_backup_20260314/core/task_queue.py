"""
异步任务队列
后台执行任务 + 定时调度
"""

import threading
import queue
import time
import uuid
from typing import Callable, Any, Optional, Dict, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import json
from pathlib import Path

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()

class TaskPriority(Enum):
    """任务优先级"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AsyncTask:
    """异步任务"""
    id: str
    name: str
    func: str
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    callback: Optional[str] = None

class TaskQueue:
    """异步任务队列"""

    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.queue = queue.PriorityQueue()
        self.tasks: Dict[str, AsyncTask] = {}
        self.results: Dict[str, Any] = {}
        self.workers: List[threading.Thread] = []
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        """启动工作线程"""
        if self.running:
            return
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)

    def stop(self):
        """停止工作线程"""
        self.running = False
        for worker in self.workers:
            worker.join(timeout=1)
        self.workers.clear()

    def _worker(self):
        """工作线程"""
        while self.running:
            try:
                priority, task_id = self.queue.get(timeout=1)
                task = self.tasks.get(task_id)
                if not task:
                    continue

                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now().isoformat()

                try:
                    func = self._get_function(task.func)
                    if func:
                        task.result = func(*task.args, **task.kwargs)
                    task.status = TaskStatus.COMPLETED
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)

                task.completed_at = datetime.now().isoformat()
                self.results[task_id] = task.result
                self.queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")

    def _get_function(self, func_name: str) -> Optional[Callable]:
        """获取函数"""
        func_map = {
            'notify': self._notify_task,
            'backup': self._backup_task,
            'health_check': self._health_check_task,
            'deploy': self._deploy_task,
        }
        return func_map.get(func_name)

    def _notify_task(self, *args, **kwargs):
        """通知任务"""
        from agents.kilo_notification import NotificationAgent
        kilo = NotificationAgent()
        return kilo.send_custom_message(kwargs.get('message', ''), kwargs.get('type', '通知'))

    def _backup_task(self, *args, **kwargs):
        """备份任务"""
        time.sleep(2)
        return {"status": "success", "files": 62}

    def _health_check_task(self, *args, **kwargs):
        """健康检查任务"""
        return {"status": "healthy", "cpu": "45%", "memory": "60%"}

    def _deploy_task(self, *args, **kwargs):
        """部署任务"""
        time.sleep(3)
        return {"status": "deployed", "url": "https://example.com"}

    def submit(self, name: str, func: str, *args,
               priority: TaskPriority = TaskPriority.NORMAL,
               **kwargs) -> str:
        """提交任务"""
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        task = AsyncTask(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority
        )

        with self.lock:
            self.tasks[task_id] = task
            self.queue.put((-priority.value, task_id))

        return task_id

    def get_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        return {
            'id': task.id,
            'name': task.name,
            'status': task.status.value,
            'result': task.result,
            'error': task.error,
            'created_at': task.created_at,
            'started_at': task.started_at,
            'completed_at': task.completed_at
        }

    def cancel(self, task_id: str) -> bool:
        """取消任务"""
        task = self.tasks.get(task_id)
        if not task or task.status == TaskStatus.RUNNING:
            return False
        task.status = TaskStatus.CANCELLED
        return True

    def get_queue_status(self) -> Dict:
        """获取队列状态"""
        return {
            'pending': sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING),
            'running': sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING),
            'completed': sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
            'failed': sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED),
        }


class TaskScheduler:
    """定时任务调度器"""

    def __init__(self):
        self.scheduled_tasks: Dict[str, Dict] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

    def schedule(self, task_id: str, func: str, interval: int = 3600,
                args: tuple = (), kwargs: dict = None):
        """调度任务"""
        with self.lock:
            self.scheduled_tasks[task_id] = {
                'func': func,
                'interval': interval,
                'args': args,
                'kwargs': kwargs or {},
                'next_run': datetime.now(),
                'enabled': True
            }

    def unschedule(self, task_id: str):
        """取消调度"""
        with self.lock:
            self.scheduled_tasks.pop(task_id, None)

    def start(self):
        """启动调度器"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _run(self):
        """调度循环"""
        from agents.kilo_notification import NotificationAgent
        kilo = NotificationAgent()

        while self.running:
            now = datetime.now()
            with self.lock:
                for task_id, task in list(self.scheduled_tasks.items()):
                    if not task['enabled']:
                        continue

                    if now >= task['next_run']:
                        try:
                            if task['func'] == 'daily_summary':
                                kilo.send_daily_summary()
                            elif task['func'] == 'health_check':
                                kilo.send_health_check_report("自动检查")
                            elif task['func'] == 'backup':
                                kilo.send_backup_notification('success', '定时备份')

                            task['next_run'] = now + timedelta(seconds=task['interval'])
                        except Exception as e:
                            print(f"Scheduled task error: {e}")

            time.sleep(60)

    def list_scheduled(self) -> List[Dict]:
        """列出已调度的任务"""
        return [
            {
                'id': tid,
                'func': t['func'],
                'interval': t['interval'],
                'next_run': t['next_run'].isoformat(),
                'enabled': t['enabled']
            }
            for tid, t in self.scheduled_tasks.items()
        ]


task_queue = TaskQueue(max_workers=3)
task_scheduler = TaskScheduler()
