#!/usr/bin/env python3
"""
多Agent协作系统 v2.0 - 核心调度器
功能：任务分配、状态跟踪、结果聚合、质量检查
"""

import os
import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# 配置
SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()
TASKS_DIR = SUITE_DIR / "tasks"
TASKS_DIR.mkdir(parents=True, exist_ok=True)

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEWING = "reviewing"

class AgentRole(Enum):
    BUILDER = "builder"           # 开发Agent
    REVIEWER = "reviewer"         # 审查Agent
    TESTER = "tester"             # 测试Agent
    DEVOPS = "devops"             # 部署Agent
    ORCHESTRATOR = "orchestrator" # 调度Agent
    SECURITY_EXPERT = "security_expert"       # 安全专家
    PERFORMANCE_EXPERT = "performance_expert" # 性能专家
    DOCUMENTATION_EXPERT = "documentation_expert" # 文档专家
    AI_EXPERT = "ai_expert"       # AI专家
    DATA_EXPERT = "data_expert"   # 数据专家
    NOTIFICATION_AGENT = "notification_agent"  # 通知Agent

@dataclass
class Agent:
    id: str
    name: str
    role: AgentRole
    status: str = "idle"
    current_task: Optional[str] = None
    capabilities: List[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []

@dataclass
class SubTask:
    id: str
    parent_task: str
    title: str
    description: str
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 3  # 1-5, 1最高
    dependencies: List[str] = None
    output_files: List[str] = None
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.output_files is None:
            self.output_files = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class MasterTask:
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    subtasks: List[str] = None
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        if self.subtasks is None:
            self.subtasks = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class MultiAgentOrchestrator:
    """多Agent协作调度器"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, MasterTask] = {}
        self.subtasks: Dict[str, SubTask] = {}
        self.load_state()
        self.initialize_agents()
    
    def initialize_agents(self):
        """初始化Agent团队 - 从配置文件加载"""
        config_file = SUITE_DIR / "agents" / "config.json"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for agent_data in config.get('agents', []):
                agent_id = agent_data['id']
                if agent_id not in self.agents:
                    # 从字符串转换回枚举
                    try:
                        role = AgentRole(agent_data['role'])
                    except ValueError:
                        # 如果role不存在，使用builder作为默认
                        role = AgentRole.BUILDER
                    
                    agent = Agent(
                        id=agent_id,
                        name=agent_data['name'],
                        role=role,
                        capabilities=agent_data.get('capabilities', [])
                    )
                    self.agents[agent_id] = agent
                    print(f"  ✅ 加载Agent: {agent.name} ({agent.role.value})")
        else:
            # 如果没有配置文件，使用默认agents
            default_agents = [
                Agent("alpha", "Alpha", AgentRole.BUILDER, capabilities=["html", "css", "ui"]),
                Agent("bravo", "Bravo", AgentRole.BUILDER, capabilities=["javascript", "algorithm", "backend"]),
                Agent("charlie", "Charlie", AgentRole.BUILDER, capabilities=["fullstack", "debug"]),
                Agent("delta", "Delta", AgentRole.REVIEWER, capabilities=["code_review", "testing"]),
                Agent("echo", "Echo", AgentRole.DEVOPS, capabilities=["deploy", "testing", "ops"]),
            ]
            
            for agent in default_agents:
                if agent.id not in self.agents:
                    self.agents[agent.id] = agent
        
        self.save_state()
    
    def load_state(self):
        """加载状态"""
        state_file = SUITE_DIR / "state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 恢复Agent
                for agent_id, agent_data in data.get('agents', {}).items():
                    self.agents[agent_id] = Agent(**agent_data)
                # 恢复任务
                for task_id, task_data in data.get('tasks', {}).items():
                    self.tasks[task_id] = MasterTask(**task_data)
                # 恢复子任务
                for subtask_id, subtask_data in data.get('subtasks', {}).items():
                    self.subtasks[subtask_id] = SubTask(**subtask_data)
    
    def save_state(self):
        """保存状态"""
        state_file = SUITE_DIR / "state.json"
        
        # 转换Agent数据为可序列化格式
        agents_data = {}
        for k, v in self.agents.items():
            agent_dict = asdict(v)
            agent_dict['role'] = v.role.value  # 转换枚举为字符串
            agents_data[k] = agent_dict
        
        data = {
            'updated_at': datetime.now().isoformat(),
            'agents': agents_data,
            'tasks': {
                k: {**asdict(v), 'status': v.status.value if hasattr(v.status, 'value') else v.status}
                for k, v in self.tasks.items()
            },
            'subtasks': {
                k: {**asdict(v), 'status': v.status.value if hasattr(v.status, 'value') else v.status}
                for k, v in self.subtasks.items()
            }
        }
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_task(self, title: str, description: str, requirements: List[str]) -> str:
        """创建主任务"""
        task_id = f"task-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        task = MasterTask(
            id=task_id,
            title=title,
            description=description
        )
        
        self.tasks[task_id] = task
        
        # 自动拆解子任务
        self.decompose_task(task_id, requirements)
        
        self.save_state()
        
        print(f"✅ 创建任务: {title} ({task_id})")
        return task_id
    
    def decompose_task(self, task_id: str, requirements: List[str]):
        """拆解任务为子任务"""
        task = self.tasks[task_id]
        
        # 根据需求自动拆解
        subtasks_config = []
        
        # 如果有UI需求
        if any('ui' in r.lower() or '界面' in r or 'html' in r.lower() for r in requirements):
            subtasks_config.append({
                'title': 'UI界面开发',
                'description': '开发用户界面和交互',
                'capabilities': ['html', 'css', 'ui'],
                'priority': 1
            })
        
        # 如果有算法/后端需求
        if any('algorithm' in r.lower() or 'backend' in r.lower() or '计算' in r for r in requirements):
            subtasks_config.append({
                'title': '后端逻辑开发',
                'description': '开发核心业务逻辑和算法',
                'capabilities': ['javascript', 'algorithm', 'backend'],
                'priority': 1
            })
        
        # 审查任务
        subtasks_config.append({
            'title': '代码审查',
            'description': '审查代码质量和功能完整性',
            'capabilities': ['code_review'],
            'priority': 2
        })
        
        # 测试任务
        subtasks_config.append({
            'title': '功能测试',
            'description': '测试所有功能是否正常工作',
            'capabilities': ['testing'],
            'priority': 3
        })
        
        # 部署任务
        subtasks_config.append({
            'title': '部署上线',
            'description': '部署到服务器并验证',
            'capabilities': ['deploy'],
            'priority': 4
        })
        
        # 创建子任务
        for i, config in enumerate(subtasks_config):
            subtask_id = f"{task_id}-sub{i+1}"
            subtask = SubTask(
                id=subtask_id,
                parent_task=task_id,
                title=config['title'],
                description=config['description'],
                priority=config['priority']
            )
            
            self.subtasks[subtask_id] = subtask
            task.subtasks.append(subtask_id)
            
            # 分配Agent
            self.assign_agent_to_subtask(subtask_id, config['capabilities'])
        
        print(f"  📋 拆解为 {len(subtasks_config)} 个子任务")
    
    def assign_agent_to_subtask(self, subtask_id: str, required_capabilities: List[str]):
        """分配Agent到子任务"""
        subtask = self.subtasks[subtask_id]
        
        # 找到最合适的Agent
        best_agent = None
        best_match = 0
        
        for agent in self.agents.values():
            if agent.status == "idle":
                # 计算匹配度
                match = len(set(agent.capabilities) & set(required_capabilities))
                if match > best_match:
                    best_match = match
                    best_agent = agent
        
        if best_agent:
            subtask.assigned_to = best_agent.id
            best_agent.status = "busy"
            best_agent.current_task = subtask_id
            print(f"  👤 分配 {best_agent.name} -> {subtask.title}")
        else:
            print(f"  ⚠️  暂无可用Agent: {subtask.title}")
        
        self.save_state()
    
    def execute_subtask(self, subtask_id: str) -> bool:
        """执行子任务（调用OpenClaw subagent）"""
        subtask = self.subtasks[subtask_id]
        agent = self.agents.get(subtask.assigned_to) if subtask.assigned_to else None
        
        if not agent:
            print(f"❌ 子任务未分配Agent: {subtask.title}")
            return False
        
        print(f"🚀 启动Agent {agent.name} 执行: {subtask.title}")
        
        subtask.status = TaskStatus.RUNNING
        subtask.started_at = datetime.now().isoformat()
        self.save_state()
        
        # 这里调用OpenClaw sessions_spawn
        try:
            # 构建任务指令
            task_prompt = f"""
你是 {agent.name} ({agent.role.value})，负责开发任务。

任务: {subtask.title}
描述: {subtask.description}

请在本地workspace目录创建文件完成任务。
完成后报告文件路径和简要说明。
"""
            
            # 实际调用会通过OpenClaw API
            # sessions_spawn(agent_id=agent.id, task=task_prompt)
            
            print(f"  ⏳ 任务执行中... (模拟)")
            
            # 模拟异步执行
            import time
            time.sleep(1)
            
            subtask.status = TaskStatus.COMPLETED
            subtask.completed_at = datetime.now().isoformat()
            subtask.result = f"由 {agent.name} 完成"
            
            agent.status = "idle"
            agent.current_task = None
            
            print(f"  ✅ 完成: {subtask.title}")
            
            self.save_state()
            return True
            
        except Exception as e:
            subtask.status = TaskStatus.FAILED
            subtask.result = str(e)
            
            agent.status = "idle"
            agent.current_task = None
            
            print(f"  ❌ 失败: {subtask.title} - {e}")
            
            self.save_state()
            return False
    
    def check_task_completion(self, task_id: str) -> bool:
        """检查任务完成状态"""
        task = self.tasks[task_id]
        
        completed = 0
        failed = 0
        total = len(task.subtasks)
        
        for subtask_id in task.subtasks:
            subtask = self.subtasks[subtask_id]
            if subtask.status == TaskStatus.COMPLETED:
                completed += 1
            elif subtask.status == TaskStatus.FAILED:
                failed += 1
        
        if completed == total:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            self.save_state()
            return True
        
        return False
    
    def get_task_status(self, task_id: str) -> Dict:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "任务不存在"}
        
        subtask_status = []
        for subtask_id in task.subtasks:
            subtask = self.subtasks[subtask_id]
            agent = self.agents.get(subtask.assigned_to) if subtask.assigned_to else None
            subtask_status.append({
                'id': subtask.id,
                'title': subtask.title,
                'status': subtask.status.value,
                'agent': agent.name if agent else '未分配',
                'priority': subtask.priority
            })
        
        return {
            'task_id': task_id,
            'title': task.title,
            'status': task.status.value,
            'subtasks': subtask_status,
            'progress': f"{sum(1 for s in subtask_status if s['status'] == 'completed')}/{len(subtask_status)}"
        }
    
    def list_agents(self):
        """列出所有Agent"""
        print("\n👥 Agent团队:")
        print("-" * 60)
        print(f"{'ID':<10} {'名称':<10} {'角色':<12} {'状态':<10} {'当前任务'}")
        print("-" * 60)
        for agent in self.agents.values():
            task = self.subtasks.get(agent.current_task) if agent.current_task else None
            print(f"{agent.id:<10} {agent.name:<10} {agent.role.value:<12} {agent.status:<10} {task.title if task else '-'}")
    
    def list_tasks(self):
        """列出所有任务"""
        print("\n📋 任务列表:")
        print("-" * 80)
        print(f"{'ID':<25} {'标题':<30} {'状态':<12} {'进度'}")
        print("-" * 80)
        for task in self.tasks.values():
            completed = sum(1 for st_id in task.subtasks 
                          if self.subtasks[st_id].status == TaskStatus.COMPLETED)
            total = len(task.subtasks)
            print(f"{task.id:<25} {task.title:<30} {task.status.value:<12} {completed}/{total}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='多Agent协作系统 v2.0')
    parser.add_argument('--create-task', type=str, help='创建任务')
    parser.add_argument('--description', type=str, help='任务描述')
    parser.add_argument('--requirements', type=str, nargs='+', help='需求列表')
    parser.add_argument('--status', type=str, help='查看任务状态')
    parser.add_argument('--list-agents', action='store_true', help='列出Agent')
    parser.add_argument('--list-tasks', action='store_true', help='列出任务')
    
    args = parser.parse_args()
    
    orchestrator = MultiAgentOrchestrator()
    
    if args.create_task:
        reqs = args.requirements or []
        orchestrator.create_task(args.create_task, args.description or "", reqs)
    elif args.status:
        status = orchestrator.get_task_status(args.status)
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.list_agents:
        orchestrator.list_agents()
    elif args.list_tasks:
        orchestrator.list_tasks()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
