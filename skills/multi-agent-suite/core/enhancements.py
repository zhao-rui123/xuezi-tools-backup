"""
Multi-Agent Suite 增强模块
包含：状态持久化、智能任务分配、错误重试与熔断、性能监控
"""

import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict
import threading

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MultiAgentSuite")


class CheckpointManager:
    """Checkpoint 状态持久化管理器"""

    def __init__(self, checkpoint_dir: Path = None):
        self.checkpoint_dir = checkpoint_dir or (SUITE_DIR / "checkpoints")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.current_checkpoint = None
        self.lock = threading.Lock()

    def save_checkpoint(self, data: Dict, name: str = None) -> Path:
        """保存检查点"""
        with self.lock:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            checkpoint_name = name or f"checkpoint_{timestamp}"
            checkpoint_file = self.checkpoint_dir / f"{checkpoint_name}.json"

            checkpoint_data = {
                'name': checkpoint_name,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }

            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)

            self.current_checkpoint = checkpoint_file
            logger.info(f"✅ 检查点已保存: {checkpoint_name}")

            self._cleanup_old_checkpoints(keep=10)
            return checkpoint_file

    def load_checkpoint(self, name: str = None) -> Optional[Dict]:
        """加载检查点"""
        with self.lock:
            if name:
                checkpoint_file = self.checkpoint_dir / f"{name}.json"
            else:
                checkpoints = sorted(self.checkpoint_dir.glob("checkpoint_*.json"))
                checkpoint_file = checkpoints[-1] if checkpoints else None

            if not checkpoint_file or not checkpoint_file.exists():
                logger.warning("⚠️ 未找到检查点")
                return None

            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"📂 检查点已加载: {checkpoint_file.name}")
                return data.get('data')
            except Exception as e:
                logger.error(f"❌ 加载检查点失败: {e}")
                return None

    def _cleanup_old_checkpoints(self, keep: int = 10):
        """清理旧检查点"""
        checkpoints = sorted(self.checkpoint_dir.glob("checkpoint_*.json"), key=lambda p: p.stat().st_mtime)
        for old in checkpoints[:-keep]:
            old.unlink()
            logger.info(f"🗑️ 已删除旧检查点: {old.name}")


class LoadBalancer:
    """智能任务分配器 - 负载监控 + 能力匹配"""

    def __init__(self):
        self.load_history = defaultdict(list)
        self.capabilities = self._load_capabilities()

    def _load_capabilities(self) -> Dict[str, List[str]]:
        """加载Agent能力配置"""
        config_file = SUITE_DIR / "agents" / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return {agent['id']: agent.get('capabilities', [])
                            for agent in config.get('agents', [])}
            except:
                pass
        return {}

    def get_agent_load(self, agent_id: str) -> float:
        """获取Agent当前负载 (0-1, 1为满载)"""
        if agent_id not in self.load_history:
            return 0.0

        recent = self.load_history[agent_id][-10:]
        if not recent:
            return 0.0

        active_count = sum(1 for load in recent if load > 0)
        return active_count / len(recent) if recent else 0.0

    def record_task_start(self, agent_id: str):
        """记录任务开始"""
        self.load_history[agent_id].append(1.0)

    def record_task_complete(self, agent_id: str):
        """记录任务完成"""
        self.load_history[agent_id].append(0.0)

    def find_best_agent(self, required_capabilities: List[str],
                       available_agents: Dict[str, Any]) -> Optional[str]:
        """查找最合适的Agent - 负载最低 + 能力匹配最好"""
        candidates = []

        for agent_id, agent in available_agents.items():
            if agent.status != "idle":
                continue

            agent_caps = self.capabilities.get(agent_id, [])
            matched = sum(1 for cap in required_capabilities if cap in agent_caps)
            if matched == 0:
                continue

            load = self.get_agent_load(agent_id)
            score = matched / (1 + load * 10)

            candidates.append((agent_id, score, load, matched))

        if not candidates:
            return None

        candidates.sort(key=lambda x: -x[1])
        best_agent_id = candidates[0][0]

        logger.info(f"🎯 智能分配: {best_agent_id} (匹配度: {candidates[0][3]}, 负载: {candidates[0][2]:.1%})")
        return best_agent_id

    def get_load_report(self, agents: Dict[str, Any]) -> Dict:
        """获取负载报告"""
        report = {}
        for agent_id, agent in agents.items():
            load = self.get_agent_load(agent_id)
            status = agent.status
            report[agent_id] = {
                'name': agent.name,
                'load': load,
                'status': status,
                'capabilities': self.capabilities.get(agent_id, [])
            }
        return report


class RetryPolicy:
    """错误重试与熔断机制"""

    def __init__(self):
        self.failure_count = defaultdict(int)
        self.success_count = defaultdict(int)
        self.circuit_breakers = defaultdict(lambda: {
            'state': 'closed',
            'failures': 0,
            'last_failure': None,
            'next_retry': None
        })

        self.max_retries = 3
        self.circuit_failure_threshold = 5
        self.circuit_recovery_time = 60

    def should_retry(self, agent_id: str, task_id: str) -> bool:
        """判断是否应该重试"""
        key = f"{agent_id}:{task_id}"
        breaker = self.circuit_breakers[key]

        if breaker['state'] == 'open':
            if time.time() < breaker['next_retry']:
                logger.warning(f"⛔ 熔断中: {agent_id}, 等待重试...")
                return False
            breaker['state'] = 'half-open'
            logger.info(f"🔄 熔断半开: {agent_id}, 尝试恢复...")

        return self.failure_count[key] < self.max_retries

    def record_success(self, agent_id: str, task_id: str):
        """记录成功"""
        key = f"{agent_id}:{task_id}"
        self.success_count[key] += 1
        self.failure_count[key] = 0

        breaker = self.circuit_breakers[key]
        if breaker['state'] == 'half-open':
            breaker['state'] = 'closed'
            breaker['failures'] = 0
            logger.info(f"✅ 熔断恢复: {agent_id}")

    def record_failure(self, agent_id: str, task_id: str):
        """记录失败"""
        key = f"{agent_id}:{task_id}"
        self.failure_count[key] += 1

        breaker = self.circuit_breakers[key]
        breaker['failures'] += 1
        breaker['last_failure'] = time.time()

        if breaker['failures'] >= self.circuit_failure_threshold:
            breaker['state'] = 'open'
            breaker['next_retry'] = time.time() + self.circuit_recovery_time
            logger.warning(f"🛡️ 熔断开启: {agent_id} (失败 {breaker['failures']} 次)")

    def get_backoff_delay(self, attempt: int) -> float:
        """指数退避延迟"""
        return min(2 ** attempt * 0.5, 30)

    def get_status(self) -> Dict:
        """获取熔断状态"""
        return {
            agent_id: {
                'state': info['state'],
                'failures': info['failures']
            }
            for agent_id, info in self.circuit_breakers.items()
            if info['failures'] > 0
        }


class PerformanceMonitor:
    """性能指标收集器"""

    def __init__(self):
        self.metrics = defaultdict(list)
        self.task_timings = {}
        self.lock = threading.Lock()

    def start_task(self, task_id: str, agent_id: str):
        """记录任务开始时间"""
        with self.lock:
            self.task_timings[task_id] = {
                'agent_id': agent_id,
                'start_time': time.time(),
                'start_datetime': datetime.now().isoformat()
            }

    def end_task(self, task_id: str, success: bool = True):
        """记录任务结束时间"""
        with self.lock:
            if task_id not in self.task_timings:
                return

            timing = self.task_timings.pop(task_id)
            duration = time.time() - timing['start_time']

            self.metrics[timing['agent_id']].append({
                'task_id': task_id,
                'duration': duration,
                'success': success,
                'timestamp': datetime.now().isoformat()
            })

            logger.info(f"⏱️ 任务 {task_id} 完成: {duration:.2f}秒, 状态: {'✅' if success else '❌'}")

    def get_agent_stats(self, agent_id: str = None) -> Dict:
        """获取Agent性能统计"""
        with self.lock:
            if agent_id:
                data = self.metrics.get(agent_id, [])
                return self._calculate_stats(data)

            stats = {}
            for aid, data in self.metrics.items():
                stats[aid] = self._calculate_stats(data)
            return stats

    def _calculate_stats(self, data: List[Dict]) -> Dict:
        """计算统计数据"""
        if not data:
            return {
                'total_tasks': 0,
                'avg_duration': 0,
                'success_rate': 0,
                'min_duration': 0,
                'max_duration': 0
            }

        durations = [d['duration'] for d in data]
        successes = sum(1 for d in data if d['success'])

        return {
            'total_tasks': len(data),
            'avg_duration': sum(durations) / len(durations),
            'success_rate': successes / len(data) * 100,
            'min_duration': min(durations),
            'max_duration': max(durations)
        }

    def generate_report(self) -> str:
        """生成性能报告"""
        stats = self.get_agent_stats()

        report_lines = [
            "📊 性能报告",
            "=" * 50,
            ""
        ]

        for agent_id, data in stats.items():
            if data['total_tasks'] == 0:
                continue

            report_lines.append(f"🤖 {agent_id}:")
            report_lines.append(f"   任务数: {data['total_tasks']}")
            report_lines.append(f"   平均耗时: {data['avg_duration']:.2f}秒")
            report_lines.append(f"   成功率: {data['success_rate']:.1f}%")
            report_lines.append(f"   最快: {data['min_duration']:.2f}秒 | 最慢: {data['max_duration']:.2f}秒")
            report_lines.append("")

        if not any(s['total_tasks'] > 0 for s in stats.values()):
            report_lines.append("(暂无数据)")

        return "\n".join(report_lines)


checkpoint_manager = CheckpointManager()
load_balancer = LoadBalancer()
retry_policy = RetryPolicy()
performance_monitor = PerformanceMonitor()
