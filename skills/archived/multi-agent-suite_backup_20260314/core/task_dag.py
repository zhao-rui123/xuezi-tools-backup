"""
任务依赖DAG (有向无环图)
支持 A→B→C 依赖关系管理
"""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime

class TaskState(Enum):
    """任务状态"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class DAGTask:
    """DAG任务节点"""
    id: str
    name: str
    description: str = ""
    state: TaskState = TaskState.PENDING
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    result: Any = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class TaskDAG:
    """任务依赖DAG"""

    def __init__(self):
        self.tasks: Dict[str, DAGTask] = {}
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)

    def add_task(self, task_id: str, name: str, description: str = "",
                 dependencies: List[str] = None) -> DAGTask:
        """添加任务"""
        task = DAGTask(
            id=task_id,
            name=name,
            description=description,
            dependencies=dependencies or []
        )

        self.tasks[task_id] = task

        for dep_id in task.dependencies:
            self.graph[dep_id].add(task_id)
            self.reverse_graph[task_id].add(dep_id)

            if dep_id not in self.tasks:
                self.tasks[dep_id] = DAGTask(
                    id=dep_id,
                    name=dep_id,
                    description="隐式依赖任务"
                )

        self._update_task_states()
        return task

    def add_dependency(self, task_id: str, depends_on: str):
        """添加依赖关系"""
        if task_id not in self.tasks:
            raise ValueError(f"任务 {task_id} 不存在")

        if depends_on not in self.tasks:
            self.tasks[depends_on] = DAGTask(
                id=depends_on,
                name=depends_on,
                description="隐式依赖任务"
            )

        if depends_on not in self.tasks[task_id].dependencies:
            self.tasks[task_id].dependencies.append(depends_on)
            self.graph[depends_on].add(task_id)
            self.reverse_graph[task_id].add(depends_on)

        self._update_task_states()

    def remove_dependency(self, task_id: str, depends_on: str):
        """移除依赖关系"""
        if task_id in self.tasks and depends_on in self.tasks[task_id].dependencies:
            self.tasks[task_id].dependencies.remove(depends_on)
            self.graph[depends_on].discard(task_id)
            self.reverse_graph[task_id].discard(depends_on)

        self._update_task_states()

    def _update_task_states(self):
        """更新任务状态"""
        in_degree = defaultdict(int)

        for task_id in self.tasks:
            in_degree[task_id] = len(self.reverse_graph[task_id])

        ready_queue = deque()
        for task_id, degree in in_degree.items():
            task = self.tasks[task_id]
            if degree == 0 and task.state == TaskState.PENDING:
                task.state = TaskState.READY
                ready_queue.append(task_id)

        while ready_queue:
            task_id = ready_queue.popleft()
            task = self.tasks[task_id]

            if task.state == TaskState.READY:
                task.state = TaskState.PENDING
                for dependent_id in self.graph[task_id]:
                    dependent = self.tasks[dependent_id]
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0 and dependent.state == TaskState.PENDING:
                        dependent.state = TaskState.READY
                        ready_queue.append(dependent_id)

    def get_ready_tasks(self) -> List[DAGTask]:
        """获取就绪任务"""
        return [t for t in self.tasks.values() if t.state == TaskState.READY]

    def get_next_ready_task(self) -> Optional[DAGTask]:
        """获取下一个就绪任务"""
        ready = self.get_ready_tasks()
        return ready[0] if ready else None

    def start_task(self, task_id: str) -> bool:
        """开始任务"""
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task.state != TaskState.READY:
            return False

        task.state = TaskState.RUNNING
        task.started_at = datetime.now().isoformat()
        return True

    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """完成任务"""
        task = self.tasks.get(task_id)
        if not task or task.state != TaskState.RUNNING:
            return False

        task.state = TaskState.COMPLETED
        task.completed_at = datetime.now().isoformat()
        task.result = result

        for dependent_id in self.graph[task_id]:
            dependent = self.tasks[dependent_id]
            if all(self.tasks[dep_id].state == TaskState.COMPLETED
                   for dep_id in dependent.dependencies):
                dependent.state = TaskState.READY

        return True

    def fail_task(self, task_id: str, error: str):
        """任务失败"""
        task = self.tasks.get(task_id)
        if not task:
            return

        task.state = TaskState.FAILED
        task.error = error
        task.completed_at = datetime.now().isoformat()

        for dependent_id in self.graph[task_id]:
            dependent = self.tasks[dependent_id]
            dependent.state = TaskState.BLOCKED

    def get_execution_order(self) -> List[str]:
        """获取执行顺序 (拓扑排序)"""
        in_degree = {tid: len(t.dependencies) for tid, t in self.tasks.items()}
        queue = deque([tid for tid, deg in in_degree.items() if deg == 0])
        result = []

        while queue:
            task_id = queue.popleft()
            result.append(task_id)

            for dependent_id in self.graph[task_id]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)

        if len(result) != len(self.tasks):
            raise ValueError("检测到循环依赖!")

        return result

    def get_task_status(self) -> Dict:
        """获取任务状态"""
        status = {state: 0 for state in TaskState}
        for task in self.tasks.values():
            status[task.state] += 1

        return {
            'total': len(self.tasks),
            'pending': status[TaskState.PENDING],
            'ready': status[TaskState.READY],
            'running': status[TaskState.RUNNING],
            'completed': status[TaskState.COMPLETED],
            'failed': status[TaskState.FAILED],
            'blocked': status[TaskState.BLOCKED]
        }

    def visualize(self) -> str:
        """可视化DAG"""
        lines = ["📊 任务依赖图", "=" * 50, ""]

        for task_id, task in self.tasks.items():
            state_emoji = {
                TaskState.PENDING: "⏳",
                TaskState.READY: "✅",
                TaskState.RUNNING: "🔄",
                TaskState.COMPLETED: "✅✅",
                TaskState.FAILED: "❌",
                TaskState.BLOCKED: "🔒"
            }.get(task.state, "❓")

            deps = f" ← [{', '.join(task.dependencies)}]" if task.dependencies else ""
            lines.append(f"{state_emoji} {task_id}: {task.name}{deps}")

        lines.append("")
        status = self.get_task_status()
        lines.append(f"状态: {status['completed']}/{status['total']} 完成")

        return "\n".join(lines)
