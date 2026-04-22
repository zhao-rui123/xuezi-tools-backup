"""
High-performance asynchronous event loop system with:
- Priority-based task scheduling
- Coroutine and callback support
- Timeout management and cancellation
- Multiplexing (select/epoll)
- Semaphore for concurrency control
- Performance monitoring
- DAG task dependency management
- Error handling and retry mechanism
"""

import asyncio
import heapq
import select
import signal
import time
import threading
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set, Tuple
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskType(Enum):
    COROUTINE = auto()
    CALLBACK = auto()


class TaskState(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    CANCELLED = auto()
    FAILED = auto()


@dataclass(order=True)
class PrioritizedTask:
    priority: int
    scheduled_time: float
    task_id: int = field(compare=False)
    task: 'BaseTask' = field(compare=False)


class BaseTask(ABC):
    _id_counter = 0
    _lock = threading.Lock()

    def __init__(
        self,
        priority: int = 0,
        timeout: Optional[float] = None,
        retries: int = 0,
        retry_delay: float = 1.0,
        max_retries: int = 3
    ):
        with BaseTask._lock:
            BaseTask._id_counter += 1
            self.id = BaseTask._id_counter

        self.priority = priority
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        self.max_retries = max_retries
        self.state = TaskState.PENDING
        self.result: Any = None
        self.error: Optional[Exception] = None
        self.created_at = time.time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self._cancelled = False
        self._dependencies: Set[int] = set()
        self._dependents: Set[int] = set()

    def cancel(self):
        self._cancelled = True
        self.state = TaskState.CANCELLED

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

    @abstractmethod
    def run(self) -> Any:
        pass

    @abstractmethod
    def get_task_type(self) -> TaskType:
        pass


class CallbackTask(BaseTask):
    def __init__(
        self,
        callback: Callable[[], Any],
        priority: int = 0,
        timeout: Optional[float] = None,
        retries: int = 0,
        retry_delay: float = 1.0,
        max_retries: int = 3
    ):
        super().__init__(priority, timeout, retries, retry_delay, max_retries)
        self.callback = callback

    def run(self) -> Any:
        return self.callback()

    def get_task_type(self) -> TaskType:
        return TaskType.CALLBACK


class CoroutineTask(BaseTask):
    def __init__(
        self,
        coroutine: Coroutine,
        priority: int = 0,
        timeout: Optional[float] = None,
        retries: int = 0,
        retry_delay: float = 1.0,
        max_retries: int = 3
    ):
        super().__init__(priority, timeout, retries, retry_delay, max_retries)
        self.coroutine = coroutine
        self._gen = None

    def run(self) -> Any:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            self.result = loop.run_until_complete(self.coroutine)
            return self.result
        finally:
            loop.close()

    def get_task_type(self) -> TaskType:
        return TaskType.COROUTINE


class Semaphore:
    def __init__(self, value: int):
        self._value = value
        self._lock = threading.Lock()
        self._waiters: deque = deque()
        self._internal_value = value

    def acquire(self, timeout: Optional[float] = None) -> bool:
        deadline = time.time() + timeout if timeout else None

        with self._lock:
            if self._internal_value > 0:
                self._internal_value -= 1
                return True

            if timeout == 0:
                return False

            event = threading.Event()
            self._waiters.append((event, deadline))
            self._value -= 1

        while True:
            if event.wait(timeout=max(0, deadline - time.time()) if deadline else None):
                with self._lock:
                    if self._internal_value > 0:
                        self._internal_value -= 1
                        if (event, deadline) in self._waiters:
                            self._waiters.remove((event, deadline))
                        return True
                return False
            else:
                with self._lock:
                    if (event, deadline) in self._waiters:
                        self._waiters.remove((event, deadline))
                        self._value += 1
                        return False

    def release(self):
        with self._lock:
            self._internal_value += 1
            self._value += 1
            if self._waiters:
                event, deadline = self._waiters.popleft()
                if deadline is None or time.time() < deadline:
                    event.set()


class DAGManager:
    def __init__(self):
        self._graph: Dict[int, Set[int]] = defaultdict(set)
        self._in_degree: Dict[int, int] = defaultdict(int)
        self._tasks: Dict[int, BaseTask] = {}

    def add_task(self, task_id: int, task: BaseTask):
        self._tasks[task_id] = task

    def add_dependency(self, task_id: int, depends_on: int):
        self._graph[depends_on].add(task_id)
        self._in_degree[task_id] += 1
        self._tasks[task_id]._dependencies.add(depends_on)
        self._tasks[depends_on]._dependents.add(task_id)

    def get_ready_tasks(self) -> List[int]:
        return [tid for tid, degree in self._in_degree.items() if degree == 0 and self._tasks[tid].state == TaskState.PENDING]

    def complete_task(self, task_id: int):
        for dependent_id in self._graph.get(task_id, []):
            self._in_degree[dependent_id] -= 1

    def has_cycle(self) -> bool:
        visited = set()
        rec_stack = set()

        def dfs(node: int) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self._graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node in self._tasks:
            if node not in visited:
                if dfs(node):
                    return True
        return False


class Monitor:
    def __init__(self):
        self._lock = threading.Lock()
        self._total_tasks: int = 0
        self._completed_tasks: int = 0
        self._failed_tasks: int = 0
        self._cancelled_tasks: int = 0
        self._total_latency: float = 0
        self._task_latencies: Dict[str, List[float]] = defaultdict(list)
        self._task_counts: Dict[str, int] = defaultdict(int)
        self._start_time = time.time()

    def record_task_start(self, task_type: str, task_id: int):
        with self._lock:
            self._total_tasks += 1
            self._task_counts[task_type] += 1

    def record_task_complete(self, task_type: str, latency: float, success: bool):
        with self._lock:
            if success:
                self._completed_tasks += 1
            else:
                self._failed_tasks += 1
            self._total_latency += latency
            self._task_latencies[task_type].append(latency)

    def record_task_cancelled(self):
        with self._lock:
            self._cancelled_tasks += 1

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            uptime = time.time() - self._start_time
            avg_latency = self._total_latency / self._completed_tasks if self._completed_tasks > 0 else 0

            task_stats = {}
            for task_type, latencies in self._task_latencies.items():
                if latencies:
                    task_stats[task_type] = {
                        "count": len(latencies),
                        "avg_latency": sum(latencies) / len(latencies),
                        "min_latency": min(latencies),
                        "max_latency": max(latencies)
                    }

            return {
                "uptime": uptime,
                "total_tasks": self._total_tasks,
                "completed_tasks": self._completed_tasks,
                "failed_tasks": self._failed_tasks,
                "cancelled_tasks": self._cancelled_tasks,
                "average_latency": avg_latency,
                "throughput": self._completed_tasks / uptime if uptime > 0 else 0,
                "task_stats": task_stats
            }

    def print_stats(self):
        stats = self.get_stats()
        print("\n" + "=" * 50)
        print("Event Loop Performance Monitor")
        print("=" * 50)
        print(f"Uptime:          {stats['uptime']:.2f}s")
        print(f"Total Tasks:     {stats['total_tasks']}")
        print(f"Completed:       {stats['completed_tasks']}")
        print(f"Failed:          {stats['failed_tasks']}")
        print(f"Cancelled:       {stats['cancelled_tasks']}")
        print(f"Avg Latency:     {stats['average_latency']*1000:.2f}ms")
        print(f"Throughput:      {stats['throughput']:.2f} tasks/s")
        print("\nPer-Task Stats:")
        for task_type, stat in stats['task_stats'].items():
            print(f"  {task_type}: count={stat['count']}, "
                  f"avg={stat['avg_latency']*1000:.2f}ms, "
                  f"min={stat['min_latency']*1000:.2f}ms, "
                  f"max={stat['max_latency']*1000:.2f}ms")
        print("=" * 50 + "\n")


class IOMultiplexer:
    def __init__(self):
        self._readers: Dict[int, Callable[[], None]] = {}
        self._writers: Dict[int, Callable[[], None]] = {}
        self._errors: Dict[int, Callable[[], None]] = {}
        self._timeout_tasks: List[Tuple[float, Callable[[], None]]] = []

    def register_reader(self, fd: int, callback: Callable[[], None]):
        self._readers[fd] = callback

    def register_writer(self, fd: int, callback: Callable[[], None]):
        self._writers[fd] = callback

    def register_error(self, fd: int, callback: Callable[[], None]):
        self._errors[fd] = callback

    def unregister(self, fd: int):
        self._readers.pop(fd, None)
        self._writers.pop(fd, None)
        self._errors.pop(fd, None)

    def register_timeout(self, deadline: float, callback: Callable[[], None]):
        heapq.heappush(self._timeout_tasks, (deadline, callback))

    def poll(self, timeout: Optional[float] = None) -> List[Tuple[str, int, Any]]:
        results = []

        r_list = list(self._readers.keys()) if self._readers else []
        w_list = list(self._writers.keys()) if self._writers else []
        e_list = list(self._errors.keys()) if self._errors else []

        if not r_list and not w_list and not e_list and not self._timeout_tasks:
            if timeout:
                time.sleep(timeout)
            return results

        ready, _, errors = select.select(r_list, w_list, e_list, timeout)

        for fd in ready:
            if fd in self._readers:
                results.append(("read", fd, self._readers[fd]))
        for fd in errors:
            if fd in self._errors:
                results.append(("error", fd, self._errors[fd]))
        for fd in ready:
            if fd in self._writers and fd not in results:
                results.append(("write", fd, self._writers[fd]))

        now = time.time()
        while self._timeout_tasks and self._timeout_tasks[0][0] <= now:
            _, callback = heapq.heappop(self._timeout_tasks)
            results.append(("timeout", 0, callback))

        return results


class EventLoop:
    def __init__(self, max_workers: Optional[int] = None):
        self._running = False
        self._lock = threading.Lock()
        self._task_queue: List[PrioritizedTask] = []
        self._tasks: Dict[int, BaseTask] = {}
        self._running_tasks: Set[int] = set()
        self._completed_tasks: Set[int] = set()

        self._multiplexer = IOMultiplexer()
        self._semaphore = Semaphore(max_workers or 100)
        self._dag = DAGManager()
        self._monitor = Monitor()

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def create_task(
        self,
        coro_or_callback: Any,
        priority: int = 0,
        timeout: Optional[float] = None,
        retries: int = 0,
        retry_delay: float = 1.0,
        max_retries: int = 3
    ) -> int:
        if asyncio.iscoroutine(coro_or_callback):
            task = CoroutineTask(coro_or_callback, priority, timeout, retries, retry_delay, max_retries)
        else:
            task = CallbackTask(coro_or_callback, priority, timeout, retries, retry_delay, max_retries)

        with self._lock:
            self._tasks[task.id] = task
            self._dag.add_task(task.id, task)
            self._schedule_task(task)

        return task.id

    def _schedule_task(self, task: BaseTask):
        scheduled_time = time.time()
        pt = PrioritizedTask(
            priority=task.priority,
            scheduled_time=scheduled_time,
            task_id=task.id,
            task=task
        )
        heapq.heappush(self._task_queue, pt)

    def add_dependency(self, task_id: int, depends_on: int):
        self._dag.add_dependency(task_id, depends_on)

    def get_ready_tasks(self) -> List[int]:
        return self._dag.get_ready_tasks()

    def _run_task(self, task: BaseTask) -> bool:
        task.started_at = time.time()
        task.state = TaskState.RUNNING
        self._monitor.record_task_start(task.get_task_type().name, task.id)

        try:
            deadline = time.time() + task.timeout if task.timeout else None

            try:
                result = task.run()
                task.result = result
                if deadline and time.time() > deadline:
                    raise TimeoutError(f"Task {task.id} timed out after {task.timeout}s")
            except Exception as inner_e:
                if deadline and time.time() > deadline:
                    raise TimeoutError(f"Task {task.id} timed out after {task.timeout}s") from inner_e
                raise

        except Exception as e:
            task.error = e
            logger.error(f"Task {task.id} exception: {e}, type={type(task)}, callback={getattr(task, 'callback', None)}, coroutine={getattr(task, 'coroutine', None)}")
            if task.retries < task.max_retries:
                task.retries += 1
                task.state = TaskState.PENDING
                logger.warning(f"Task {task.id} failed, retry {task.retries}/{task.max_retries}: {e}")
                time.sleep(task.retry_delay)
                self._schedule_task(task)
                return False
            else:
                task.state = TaskState.FAILED
                return False
        finally:
            task.completed_at = time.time()

        task.state = TaskState.COMPLETED
        self._dag.complete_task(task.id)
        return True

    def _process_ready_tasks(self):
        ready = self.get_ready_tasks()
        for task_id in ready:
            task = self._tasks[task_id]
            if task.is_cancelled:
                task.state = TaskState.CANCELLED
                self._monitor.record_task_cancelled()
                continue

            if self._semaphore.acquire(timeout=0):
                self._running_tasks.add(task_id)
                try:
                    success = self._run_task(task)
                    latency = task.completed_at - task.started_at if task.completed_at and task.started_at else 0
                    self._monitor.record_task_complete(task.get_task_type().name, latency, success)
                    if success:
                        self._completed_tasks.add(task_id)
                finally:
                    self._semaphore.release()
                    self._running_tasks.discard(task_id)

    def _process_queue(self):
        now = time.time()
        while self._task_queue:
            pt = self._task_queue[0]
            task = self._tasks.get(pt.task_id)

            if task is None or task.state in (TaskState.COMPLETED, TaskState.CANCELLED, TaskState.FAILED):
                heapq.heappop(self._task_queue)
                continue

            if self._semaphore.acquire(timeout=0.001):
                heapq.heappop(self._task_queue)
                self._running_tasks.add(pt.task_id)
                try:
                    success = self._run_task(task)
                    latency = task.completed_at - task.started_at if task.completed_at and task.started_at else 0
                    self._monitor.record_task_complete(task.get_task_type().name, latency, success)
                    if success:
                        self._completed_tasks.add(pt.task_id)
                finally:
                    self._semaphore.release()
                    self._running_tasks.discard(pt.task_id)
            else:
                break

    def run_loop(self):
        self._running = True
        while self._running or self._task_queue or self._running_tasks:
            self._process_ready_tasks()
            self._process_queue()

            io_events = self._multiplexer.poll(timeout=0.01)
            for event_type, fd, callback in io_events:
                try:
                    callback()
                except Exception as e:
                    logger.error(f"IO callback error: {e}")

            if self._stop_event.is_set():
                break

        self._running = False

    def _loop_thread(self):
        self.run_loop()

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._loop_thread, daemon=True)
            self._thread.start()

    def stop(self):
        self._running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

    def cancel_task(self, task_id: int):
        task = self._tasks.get(task_id)
        if task:
            task.cancel()

    def wait_task(self, task_id: int, timeout: Optional[float] = None) -> Any:
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        deadline = time.time() + timeout if timeout else None
        while task.state not in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED):
            if deadline and time.time() >= deadline:
                raise TimeoutError(f"Task {task_id} wait timeout")
            time.sleep(0.01)

        if task.state == TaskState.FAILED:
            if task.error:
                raise task.error
            raise RuntimeError(f"Task {task_id} failed with no error")
        return task.result

    def get_task_state(self, task_id: int) -> Optional[TaskState]:
        task = self._tasks.get(task_id)
        return task.state if task else None

    def register_io_reader(self, fd: int, callback: Callable[[], None]):
        self._multiplexer.register_reader(fd, callback)

    def register_io_writer(self, fd: int, callback: Callable[[], None]):
        self._multiplexer.register_writer(fd, callback)

    def get_monitor(self) -> Monitor:
        return self._monitor


class TaskGroup:
    def __init__(self, loop: EventLoop):
        self._loop = loop
        self._task_ids: List[int] = []

    def create_task(
        self,
        coro_or_callback: Any,
        priority: int = 0,
        timeout: Optional[float] = None
    ) -> int:
        task_id = self._loop.create_task(
            coro_or_callback,
            priority=priority,
            timeout=timeout
        )
        self._task_ids.append(task_id)
        return task_id

    def wait_all(self, timeout: Optional[float] = None) -> List[Any]:
        results = []
        for task_id in self._task_ids:
            try:
                result = self._loop.wait_task(task_id, timeout)
                results.append(result)
            except Exception as e:
                results.append(e)
        return results

    def cancel_all(self):
        for task_id in self._task_ids:
            self._loop.cancel_task(task_id)


@asynccontextmanager
async def async_timeout(loop: EventLoop, task_id: int, timeout: float):
    async def cancellable():
        try:
            yield
        except asyncio.CancelledError:
            loop.cancel_task(task_id)
            raise

    try:
        async def wait_with_timeout():
            try:
                return await asyncio.wait_for(cancellable(), timeout=timeout)
            except asyncio.TimeoutError:
                loop.cancel_task(task_id)
                raise
        yield wait_with_timeout()
    except asyncio.TimeoutError:
        loop.cancel_task(task_id)
        raise


async def demo_async_task(name: str, duration: float) -> str:
    await asyncio.sleep(duration)
    return f"{name} completed after {duration}s"


def demo_callback_task(name: str, duration: float) -> str:
    time.sleep(duration)
    return f"{name} completed after {duration}s"


if __name__ == "__main__":
    print("Starting Event Loop Demo...\n")

    loop = EventLoop(max_workers=10)

    task1_id = loop.create_task(
        demo_callback_task("Callback Task 1", 0.5),
        priority=2
    )

    task2_id = loop.create_task(
        demo_async_task("Async Task 1", 0.3),
        priority=1
    )

    task3_id = loop.create_task(
        demo_callback_task("Callback Task 2", 0.2),
        priority=3
    )

    loop.add_dependency(task3_id, task1_id)

    group = TaskGroup(loop)
    for i in range(5):
        group.create_task(
            demo_callback_task(f"Group Task {i}", 0.1),
            priority=i
        )

    loop.start()

    time.sleep(2)

    loop.get_monitor().print_stats()

    try:
        result = loop.wait_task(task1_id, timeout=2)
        print(f"Task 1 result: {result}")
    except Exception as e:
        print(f"Task 1 error: {e}")

    loop.stop()

    print("\nDemo completed!")
