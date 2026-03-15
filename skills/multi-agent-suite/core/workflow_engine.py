#!/usr/bin/env python3
"""
多Agent软件开发工作流引擎 v4.1 - 专业级
遵循标准软件工程流程：需求 → 设计 → 开发 → 测试 → 部署 → 交付
使用专业级基础设施: 日志、单例、缓存、验证、异常处理
"""

import os
import json
import uuid
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict

from core.professional_base import (
    ProfessionalLogger,
    ConfigManager,
    SingletonMeta,
    BaseModel,
    ValidationError,
    NotFoundError,
    StateError,
    ThreadSafeCache,
    EventDispatcher,
    RetryPolicy,
    validate_required_fields,
    validate_field_type,
    MetricsCollector,
)

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()
PROJECTS_DIR = SUITE_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


class ProjectPhase(Enum):
    """项目阶段"""
    REQUIREMENT = "requirement"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    DELIVERY = "delivery"
    COMPLETED = "completed"


class PhaseStatus(Enum):
    """阶段状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    """任务优先级"""
    P0_CRITICAL = 0
    P1_HIGH = 1
    P2_MEDIUM = 2
    P3_LOW = 3


class ArtifactType(Enum):
    """产出物类型"""
    PRD = "prd"
    ARCHITECTURE = "architecture"
    ER_DIAGRAM = "er_diagram"
    API_DOC = "api_doc"
    SEQUENCE_DIAGRAM = "sequence"
    SOURCE_CODE = "source_code"
    TEST_REPORT = "test_report"
    DEPLOY_DOC = "deploy_doc"
    USER_MANUAL = "user_manual"
    SOURCE_BUNDLE = "source_bundle"


class ProjectPhaseConfig:
    """项目阶段配置"""
    
    def __init__(
        self,
        phase: ProjectPhase,
        name: str,
        description: str,
        primary_agent: str,
        participating_agents: List[str],
        required_artifacts: List[ArtifactType],
        activities: List[str],
        entry_criteria: List[str],
        exit_criteria: List[str],
    ):
        self.phase = phase
        self.name = name
        self.description = description
        self.primary_agent = primary_agent
        self.participating_agents = participating_agents
        self.required_artifacts = required_artifacts
        self.activities = activities
        self.entry_criteria = entry_criteria
        self.exit_criteria = exit_criteria


class Artifact(BaseModel):
    """产出物"""
    
    def __init__(
        self,
        id: str = None,
        name: str = "",
        type: ArtifactType = ArtifactType.SOURCE_CODE,
        path: str = "",
        description: str = "",
        created_by: str = "",
        created_at: datetime = None,
        version: str = "1.0.0",
        size: int = 0,
        checksum: str = "",
        metadata: Dict = None,
    ):
        self.id = id or str(uuid.uuid4())[:8]
        self.name = name
        self.type = type
        self.path = path
        self.description = description
        self.created_by = created_by
        self.created_at = created_at or datetime.now()
        self.version = version
        self.size = size
        self.checksum = checksum
        self.metadata = metadata or {}

    def validate(self) -> List[str]:
        """验证产出物数据"""
        errors = []
        if not self.name:
            errors.append("Artifact name is required")
        if not self.type:
            errors.append("Artifact type is required")
        return errors


class PhaseTask(BaseModel):
    """阶段任务"""
    
    def __init__(
        self,
        id: str = None,
        title: str = "",
        description: str = "",
        assigned_agent: str = "",
        status: PhaseStatus = PhaseStatus.PENDING,
        priority: TaskPriority = TaskPriority.P2_MEDIUM,
        dependencies: List[str] = None,
        artifacts: List[Artifact] = None,
        estimated_hours: float = 0.0,
        actual_hours: float = 0.0,
        notes: str = "",
        created_at: datetime = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        result: Optional[str] = None,
    ):
        self.id = id or str(uuid.uuid4())[:8]
        self.title = title
        self.description = description
        self.assigned_agent = assigned_agent
        self.status = status
        self.priority = priority
        self.dependencies = dependencies or []
        self.artifacts = artifacts or []
        self.estimated_hours = estimated_hours
        self.actual_hours = actual_hours
        self.notes = notes
        self.created_at = created_at or datetime.now()
        self.started_at = started_at
        self.completed_at = completed_at
        self.result = result

    def validate(self) -> List[str]:
        """验证任务数据"""
        errors = []
        if not self.title:
            errors.append("Task title is required")
        if not self.assigned_agent:
            errors.append("Task must be assigned to an agent")
        return errors


class Project(BaseModel):
    """项目"""
    
    def __init__(
        self,
        id: str = None,
        name: str = "",
        description: str = "",
        template: str = "web_app",
        phase: ProjectPhase = ProjectPhase.REQUIREMENT,
        status: PhaseStatus = PhaseStatus.PENDING,
        phases: Dict = None,
        tasks: List[PhaseTask] = None,
        artifacts: List[Artifact] = None,
        owner: str = "",
        deadline: Optional[str] = None,
        version: str = "1.0.0",
        created_at: datetime = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        metadata: Dict = None,
    ):
        self.id = id or f"proj-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.name = name
        self.description = description
        self.template = template
        self.phase = phase
        self.status = status
        self.phases = phases or {}
        self.tasks = tasks or []
        self.artifacts = artifacts or []
        self.owner = owner
        self.deadline = deadline
        self.version = version
        self.created_at = created_at or datetime.now()
        self.started_at = started_at
        self.completed_at = completed_at
        self.metadata = metadata or {}

    def validate(self) -> List[str]:
        """验证项目数据"""
        errors = []
        if not self.name:
            errors.append("Project name is required")
        if not self.template:
            errors.append("Project template is required")
        return errors


class WaterfallWorkflowEngine(metaclass=SingletonMeta):
    """瀑布模型工作流引擎 - 单例模式"""
    
    PHASE_CONFIGS: Dict[ProjectPhase, ProjectPhaseConfig] = {}
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._logger = ProfessionalLogger.get_logger("workflow_engine")
        self._config = ConfigManager()
        self._event_dispatcher = EventDispatcher()
        self._cache = ThreadSafeCache.get_cache("workflow", maxsize=256)
        
        self.projects: Dict[str, Project] = {}
        self._projects_lock = threading.RLock()
        
        self._initialize_phase_configs()
        self._load_projects()
        
        self._initialized = True
        self._logger.info("WorkflowEngine initialized successfully")
    
    def _initialize_phase_configs(self):
        """初始化阶段配置"""
        self.PHASE_CONFIGS = {
            ProjectPhase.REQUIREMENT: ProjectPhaseConfig(
                phase=ProjectPhase.REQUIREMENT,
                name="需求阶段",
                description="需求收集、分析、PRD编写",
                primary_agent="product",
                participating_agents=["product"],
                required_artifacts=[ArtifactType.PRD],
                activities=["需求收集", "需求分析", "PRD编写", "功能清单", "优先级排序", "用户故事"],
                entry_criteria=["用户原始需求"],
                exit_criteria=["PRD文档完成", "功能清单确认"]
            ),
            ProjectPhase.DESIGN: ProjectPhaseConfig(
                phase=ProjectPhase.DESIGN,
                name="设计阶段",
                description="系统架构设计、数据库设计、接口设计",
                primary_agent="architect",
                participating_agents=["architect", "bravo"],
                required_artifacts=[ArtifactType.ARCHITECTURE, ArtifactType.ER_DIAGRAM, ArtifactType.API_DOC],
                activities=["系统架构设计", "模块划分", "技术选型", "数据库设计", "接口设计", "数据字典"],
                entry_criteria=["PRD文档确认"],
                exit_criteria=["架构设计完成", "API文档完成"]
            ),
            ProjectPhase.DEVELOPMENT: ProjectPhaseConfig(
                phase=ProjectPhase.DEVELOPMENT,
                name="开发阶段",
                description="并行开发、代码规范、Git管理",
                primary_agent="orchestrator",
                participating_agents=["alpha", "bravo", "charlie", "delta"],
                required_artifacts=[ArtifactType.SOURCE_CODE],
                activities=["任务分配", "并行开发", "代码规范", "Git管理", "代码集成"],
                entry_criteria=["设计文档完成"],
                exit_criteria=["代码开发完成", "单元测试通过"]
            ),
            ProjectPhase.TESTING: ProjectPhaseConfig(
                phase=ProjectPhase.TESTING,
                name="测试阶段",
                description="单元测试、集成测试、Code Review",
                primary_agent="echo",
                participating_agents=["echo", "foxtrot", "golf"],
                required_artifacts=[ArtifactType.TEST_REPORT],
                activities=["单元测试", "集成测试", "Code Review", "缺陷报告", "回归测试", "安全审计"],
                entry_criteria=["代码开发完成"],
                exit_criteria=["测试通过", "Bug修复完成"]
            ),
            ProjectPhase.DEPLOYMENT: ProjectPhaseConfig(
                phase=ProjectPhase.DEPLOYMENT,
                name="部署阶段",
                description="部署上线、回滚方案、监控告警",
                primary_agent="kilo",
                participating_agents=["kilo", "orchestrator"],
                required_artifacts=[ArtifactType.DEPLOY_DOC],
                activities=["环境准备", "部署执行", "健康检查", "回滚方案", "监控配置"],
                entry_criteria=["测试通过"],
                exit_criteria=["部署成功", "健康检查通过"]
            ),
            ProjectPhase.DELIVERY: ProjectPhaseConfig(
                phase=ProjectPhase.DELIVERY,
                name="交付阶段",
                description="用户验收、使用文档、培训",
                primary_agent="product",
                participating_agents=["product", "hotel"],
                required_artifacts=[ArtifactType.USER_MANUAL],
                activities=["用户验收", "使用文档", "培训", "运维手册", "项目总结"],
                entry_criteria=["部署成功"],
                exit_criteria=["用户验收通过", "文档交付完成"]
            ),
        }
    
    def _load_projects(self):
        """加载项目"""
        projects_file = PROJECTS_DIR / "projects.json"
        if projects_file.exists():
            try:
                with open(projects_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for proj_id, proj_data in data.items():
                        proj_data = self._deserialize_project(proj_data)
                        self.projects[proj_id] = proj_data
                self._logger.info(f"Loaded {len(self.projects)} projects")
            except Exception as e:
                self._logger.error(f"Failed to load projects: {e}", exc_info=True)
    
    def _deserialize_project(self, data: Dict) -> Project:
        """反序列化项目"""
        data = data.copy()
        
        if 'phase' in data and isinstance(data['phase'], str):
            data['phase'] = ProjectPhase(data['phase'])
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = PhaseStatus(data['status'])
        
        if 'tasks' in data:
            data['tasks'] = [
                self._deserialize_task(t) if isinstance(t, dict) else t 
                for t in data['tasks']
            ]
        if 'artifacts' in data:
            data['artifacts'] = [
                self._deserialize_artifact(a) if isinstance(a, dict) else a 
                for a in data['artifacts']
            ]
        
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'started_at' in data and data['started_at'] and isinstance(data['started_at'], str):
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if 'completed_at' in data and data['completed_at'] and isinstance(data['completed_at'], str):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        
        return Project(**data)
    
    def _deserialize_task(self, data: Dict) -> PhaseTask:
        """反序列化任务"""
        data = data.copy()
        
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = PhaseStatus(data['status'])
        if 'priority' in data and isinstance(data['priority'], int):
            data['priority'] = TaskPriority(data['priority'])
        
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        return PhaseTask(**data)
    
    def _deserialize_artifact(self, data: Dict) -> Artifact:
        """反序列化产出物"""
        data = data.copy()
        
        if 'type' in data and isinstance(data['type'], str):
            data['type'] = ArtifactType(data['type'])
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        return Artifact(**data)
    
    def _save_projects(self):
        """保存项目"""
        projects_file = PROJECTS_DIR / "projects.json"
        data = {}
        
        with self._projects_lock:
            for proj_id, proj in self.projects.items():
                data[proj_id] = self._serialize_project(proj)
        
        try:
            with open(projects_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self._logger.debug(f"Saved {len(data)} projects")
        except Exception as e:
            self._logger.error(f"Failed to save projects: {e}", exc_info=True)
    
    def _serialize_project(self, project: Project) -> Dict:
        """序列化项目"""
        proj_dict = project.to_dict()
        
        if 'phase' in proj_dict and isinstance(proj_dict['phase'], ProjectPhase):
            proj_dict['phase'] = proj_dict['phase'].value
        if 'status' in proj_dict and isinstance(proj_dict['status'], PhaseStatus):
            proj_dict['status'] = proj_dict['status'].value
        
        for task in proj_dict.get('tasks', []):
            if 'status' in task and isinstance(task['status'], PhaseStatus):
                task['status'] = task['status'].value
            if 'priority' in task and isinstance(task['priority'], TaskPriority):
                task['priority'] = task['priority'].value
        
        for artifact in proj_dict.get('artifacts', []):
            if 'type' in artifact and isinstance(artifact['type'], ArtifactType):
                artifact['type'] = artifact['type'].value
        
        return proj_dict
    
    def add_listener(self, callback: Callable):
        """添加事件监听器"""
        self._event_dispatcher.subscribe("workflow", callback)
    
    def _notify(self, event: str, data: Dict):
        """触发事件"""
        MetricsCollector.record("workflow_events", 1)
        self._event_dispatcher.dispatch(f"workflow.{event}", data)
    
    @RetryPolicy.exponential_backoff(max_attempts=3, base_delay=1.0)
    def create_project(
        self,
        name: str,
        description: str = "",
        template: str = "web_app",
        requirements: List[str] = None,
        deadline: str = None,
    ) -> str:
        """创建项目"""
        start_time = time.time()
        
        validate_required_fields(
            {"name": name, "template": template},
            ["name", "template"]
        )
        
        project = Project(
            name=name,
            description=description,
            template=template,
            deadline=deadline,
            phases=self._init_phases(template)
        )
        
        errors = project.validate()
        if errors:
            raise ValidationError(f"Invalid project data: {errors}")
        
        with self._projects_lock:
            self.projects[project.id] = project
            self._create_phase_tasks(project, template)
            self._save_projects()
        
        MetricsCollector.record("projects_created", 1)
        
        elapsed = time.time() - start_time
        MetricsCollector.record("project_creation_time", elapsed)
        
        self._logger.info(
            f"Project created: {project.id} | name={name} | template={template} | "
            f"tasks={len(project.tasks)} | time={elapsed:.3f}s"
        )
        
        self._notify("project_created", {"project_id": project.id, "name": name})
        
        return project.id
    
    def _init_phases(self, template: str) -> Dict:
        """初始化阶段"""
        phases = {}
        for phase in ProjectPhase:
            if phase == ProjectPhase.COMPLETED:
                continue
            config = self.PHASE_CONFIGS.get(phase)
            if config:
                phases[phase.value] = {
                    "name": config.name,
                    "status": (
                        PhaseStatus.IN_PROGRESS.value 
                        if phase == ProjectPhase.REQUIREMENT 
                        else PhaseStatus.PENDING.value
                    ),
                    "primary_agent": config.primary_agent,
                    "required_artifacts": [a.value for a in config.required_artifacts],
                    "entry_criteria": config.entry_criteria,
                    "exit_criteria": config.exit_criteria
                }
        return phases
    
    def _create_phase_tasks(self, project: Project, template: str):
        """创建阶段任务"""
        phase_task_map = {
            ProjectPhase.REQUIREMENT: [
                ("收集用户需求", "product", TaskPriority.P0_CRITICAL),
                ("编写PRD文档", "product", TaskPriority.P0_CRITICAL),
                ("梳理功能清单", "product", TaskPriority.P1_HIGH),
                ("编写用户故事", "product", TaskPriority.P1_HIGH),
                ("功能优先级排序", "product", TaskPriority.P1_HIGH),
            ],
            ProjectPhase.DESIGN: [
                ("系统架构设计", "architect", TaskPriority.P0_CRITICAL),
                ("绘制ER图", "architect", TaskPriority.P0_CRITICAL),
                ("设计API接口", "architect", TaskPriority.P0_CRITICAL),
                ("技术选型", "architect", TaskPriority.P1_HIGH),
                ("绘制时序图", "architect", TaskPriority.P2_MEDIUM),
            ],
            ProjectPhase.DEVELOPMENT: [
                ("前端界面开发", "alpha", TaskPriority.P0_CRITICAL),
                ("后端API开发", "bravo", TaskPriority.P0_CRITICAL),
                ("数据库开发", "bravo", TaskPriority.P1_HIGH),
                ("功能整合联调", "charlie", TaskPriority.P0_CRITICAL),
                ("Bug修复优化", "delta", TaskPriority.P1_HIGH),
            ],
            ProjectPhase.TESTING: [
                ("制定测试计划", "echo", TaskPriority.P1_HIGH),
                ("编写单元测试", "echo", TaskPriority.P0_CRITICAL),
                ("执行集成测试", "echo", TaskPriority.P0_CRITICAL),
                ("Code Review", "echo", TaskPriority.P1_HIGH),
                ("安全审计", "foxtrot", TaskPriority.P1_HIGH),
                ("性能测试", "golf", TaskPriority.P2_MEDIUM),
            ],
            ProjectPhase.DEPLOYMENT: [
                ("环境配置", "kilo", TaskPriority.P0_CRITICAL),
                ("构建Docker镜像", "kilo", TaskPriority.P0_CRITICAL),
                ("执行部署", "kilo", TaskPriority.P0_CRITICAL),
                ("健康检查", "kilo", TaskPriority.P1_HIGH),
                ("配置监控告警", "kilo", TaskPriority.P2_MEDIUM),
            ],
            ProjectPhase.DELIVERY: [
                ("用户验收测试", "product", TaskPriority.P0_CRITICAL),
                ("编写用户手册", "hotel", TaskPriority.P1_HIGH),
                ("编写运维手册", "hotel", TaskPriority.P1_HIGH),
                ("项目总结", "product", TaskPriority.P2_MEDIUM),
            ]
        }
        
        for phase, tasks in phase_task_map.items():
            for title, agent, priority in tasks:
                task = PhaseTask(
                    title=title,
                    description=f"{title} - {phase.value}阶段",
                    assigned_agent=agent,
                    priority=priority,
                    status=(
                        PhaseStatus.IN_PROGRESS 
                        if phase == ProjectPhase.REQUIREMENT 
                        else PhaseStatus.PENDING
                    )
                )
                project.tasks.append(task)
        
        self._logger.debug(f"Created {len(project.tasks)} tasks for project {project.id}")
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """获取项目"""
        cache_key = f"project_{project_id}"
        
        cached = self._cache.get(cache_key)
        if cached:
            MetricsCollector.record("cache_hits", 1)
            return cached
        
        with self._projects_lock:
            project = self.projects.get(project_id)
        
        if project:
            self._cache.set(cache_key, project, ttl=300)
        
        return project
    
    def list_projects(self) -> List[Project]:
        """列出所有项目"""
        with self._projects_lock:
            return list(self.projects.values())
    
    def update_phase_status(
        self,
        project_id: str,
        phase: ProjectPhase,
        status: PhaseStatus
    ) -> bool:
        """更新阶段状态"""
        project = self.get_project(project_id)
        if not project:
            self._logger.warning(f"Project not found: {project_id}")
            return False
        
        phase_key = phase.value
        if phase_key not in project.phases:
            self._logger.warning(f"Phase not found: {phase_key}")
            return False
        
        with self._projects_lock:
            project.phases[phase_key]["status"] = status.value
            
            if status == PhaseStatus.COMPLETED:
                self._notify("phase_completed", {
                    "project_id": project_id,
                    "phase": phase.value
                })
                
                next_phase = self._get_next_phase(phase)
                if next_phase:
                    project.phase = next_phase
                    project.phases[next_phase.value]["status"] = PhaseStatus.IN_PROGRESS.value
            
            self._save_projects()
            self._cache.clear()
        
        self._logger.info(f"Phase updated: {project_id} | {phase_key} -> {status.value}")
        return True
    
    def _get_next_phase(self, current: ProjectPhase) -> Optional[ProjectPhase]:
        """获取下一阶段"""
        phases = list(ProjectPhase)
        try:
            idx = phases.index(current)
            if idx < len(phases) - 2:
                return phases[idx + 1]
        except (ValueError, IndexError):
            pass
        return None
    
    def start_task(self, project_id: str, task_id: str) -> bool:
        """开始任务"""
        project = self.get_project(project_id)
        if not project:
            return False
        
        with self._projects_lock:
            for task in project.tasks:
                if task.id == task_id and task.status == PhaseStatus.PENDING:
                    task.status = PhaseStatus.IN_PROGRESS
                    task.started_at = datetime.now()
                    self._save_projects()
                    self._cache.clear()
                    
                    self._logger.info(f"Task started: {task_id} in project {project_id}")
                    self._notify("task_started", {
                        "project_id": project_id,
                        "task_id": task_id
                    })
                    return True
        
        return False
    
    def complete_task(
        self,
        project_id: str,
        task_id: str,
        result: str = "",
        artifacts: List[Artifact] = None,
    ) -> bool:
        """完成任务"""
        project = self.get_project(project_id)
        if not project:
            return False
        
        with self._projects_lock:
            for task in project.tasks:
                if task.id == task_id and task.status == PhaseStatus.IN_PROGRESS:
                    task.status = PhaseStatus.COMPLETED
                    task.completed_at = datetime.now()
                    task.result = result
                    
                    if artifacts:
                        task.artifacts.extend(artifacts)
                        project.artifacts.extend(artifacts)
                    
                    if task.started_at:
                        task.actual_hours = (
                            datetime.now() - task.started_at
                        ).total_seconds() / 3600
                    
                    self._check_phase_completion(project)
                    self._save_projects()
                    self._cache.clear()
                    
                    self._logger.info(f"Task completed: {task_id} in project {project_id}")
                    self._notify("task_completed", {
                        "project_id": project_id,
                        "task_id": task_id
                    })
                    return True
        
        return False
    
    def _check_phase_completion(self, project: Project):
        """检查阶段完成"""
        if project.phase not in self.PHASE_CONFIGS:
            return
        
        config = self.PHASE_CONFIGS[project.phase]
        current_phase_tasks = [
            t for t in project.tasks
            if t.assigned_agent in config.participating_agents
        ]
        
        if current_phase_tasks and all(
            t.status == PhaseStatus.COMPLETED
            for t in current_phase_tasks
        ):
            self.update_phase_status(
                project.id,
                project.phase,
                PhaseStatus.COMPLETED
            )
    
    def add_artifact(self, project_id: str, artifact: Artifact) -> bool:
        """添加产出物"""
        project = self.get_project(project_id)
        if not project:
            return False
        
        with self._projects_lock:
            project.artifacts.append(artifact)
            self._save_projects()
            self._cache.clear()
        
        self._logger.info(f"Artifact added: {artifact.id} to project {project_id}")
        return True
    
    def get_project_status(self, project_id: str) -> Dict:
        """获取项目状态"""
        project = self.get_project(project_id)
        if not project:
            return {"error": "项目不存在", "code": "NOT_FOUND"}
        
        completed_tasks = sum(
            1 for t in project.tasks
            if t.status == PhaseStatus.COMPLETED
        )
        total_tasks = len(project.tasks)
        
        phase_info = project.phases.get(project.phase.value, {})
        
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "phase": project.phase.value,
            "phase_name": phase_info.get("name", ""),
            "status": project.status.value,
            "progress": f"{completed_tasks}/{total_tasks}",
            "progress_percent": round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "artifacts_count": len(project.artifacts),
            "created_at": project.created_at.isoformat(),
            "deadline": project.deadline
        }
    
    def get_phase_tasks(self, project_id: str, phase: ProjectPhase) -> List[PhaseTask]:
        """获取阶段任务"""
        project = self.get_project(project_id)
        if not project:
            return []
        
        config = self.PHASE_CONFIGS.get(phase)
        if not config:
            return []
        
        return [
            t for t in project.tasks
            if t.assigned_agent in config.participating_agents
        ]
    
    def generate_project_report(self, project_id: str) -> str:
        """生成项目报告"""
        project = self.get_project(project_id)
        if not project:
            return "项目不存在"
        
        lines = [
            "=" * 70,
            f"📊 项目报告: {project.name}",
            "=" * 70,
            f"项目ID: {project.id}",
            f"描述: {project.description}",
            f"模板: {project.template}",
            f"创建时间: {project.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"截止时间: {project.deadline or '未设置'}",
            "",
            "📋 阶段进度:",
            "-" * 70
        ]
        
        status_icons = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌"
        }
        
        for phase_key, phase_info in project.phases.items():
            icon = status_icons.get(phase_info.get("status", "pending"), "⚪")
            lines.append(
                f"  {icon} {phase_info.get('name', phase_key)} "
                f"[{phase_info.get('status', 'pending')}]"
            )
        
        lines.extend([
            "",
            "📝 任务列表:",
            "-" * 70
        ])
        
        task_status_icons = {
            PhaseStatus.PENDING: "⏳",
            PhaseStatus.IN_PROGRESS: "🔄",
            PhaseStatus.COMPLETED: "✅",
            PhaseStatus.FAILED: "❌"
        }
        
        for task in project.tasks:
            icon = task_status_icons.get(task.status, "⚪")
            lines.append(f"  {icon} [{task.priority.name}] {task.title} - {task.assigned_agent}")
        
        lines.extend([
            "",
            f"📦 产出物: {len(project.artifacts)} 个",
            "=" * 70
        ])
        
        return "\n".join(lines)
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        with self._projects_lock:
            if project_id not in self.projects:
                return False
            
            del self.projects[project_id]
            self._save_projects()
            self._cache.clear()
        
        self._logger.info(f"Project deleted: {project_id}")
        return True


import time

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='瀑布模型工作流引擎 v4.1 (Professional)')
    parser.add_argument('--create', type=str, help='创建项目')
    parser.add_argument('--description', type=str, help='项目描述')
    parser.add_argument('--template', type=str, default='web_app', help='项目模板')
    parser.add_argument('--requirements', type=str, nargs='+', help='需求列表')
    parser.add_argument('--deadline', type=str, help='截止日期')
    parser.add_argument('--list', action='store_true', help='列出项目')
    parser.add_argument('--status', type=str, help='查看项目状态')
    parser.add_argument('--report', type=str, help='生成项目报告')
    parser.add_argument('--phase', type=str, help='查看阶段任务')
    parser.add_argument('--delete', type=str, help='删除项目')
    
    args = parser.parse_args()
    
    engine = WaterfallWorkflowEngine()
    
    if args.create:
        project_id = engine.create_project(
            args.create,
            args.description or "",
            args.template,
            args.requirements,
            args.deadline
        )
        print(f"\n✅ 项目创建成功!")
        print(f"   ID: {project_id}")
        print(f"📌 查看项目状态: python -m core.cli project status {project_id}")
    
    elif args.list:
        projects = engine.list_projects()
        print("\n📋 项目列表:")
        print("-" * 80)
        for p in projects:
            status = engine.get_project_status(p.id)
            print(f"{p.id:<25} {p.name:<25} {status['phase_name']:<15} {status['progress']}")
        print("-" * 80)
    
    elif args.status:
        status = engine.get_project_status(args.status)
        if "error" in status:
            print(f"❌ {status['error']}")
        else:
            print("\n📊 项目状态:")
            print(f"  名称: {status['name']}")
            print(f"  当前阶段: {status['phase_name']} ({status['phase']})")
            print(f"  进度: {status['progress']} ({status['progress_percent']}%)")
            print(f"  任务: {status['completed_tasks']}/{status['total_tasks']}")
            print(f"  产出物: {status['artifacts_count']} 个")
    
    elif args.report:
        print(engine.generate_project_report(args.report))
    
    elif args.delete:
        if engine.delete_project(args.delete):
            print(f"✅ 项目已删除: {args.delete}")
        else:
            print(f"❌ 项目不存在: {args.delete}")
    
    elif args.phase:
        parts = args.phase.split(':')
        if len(parts) == 2:
            project_id, phase = parts
            try:
                phase_enum = ProjectPhase(phase)
                tasks = engine.get_phase_tasks(project_id, phase_enum)
                print(f"\n📋 {phase_enum.value} 阶段任务:")
                for t in tasks:
                    print(f"  [{t.status.value}] {t.title} - {t.assigned_agent}")
            except ValueError:
                print("无效的阶段")
        else:
            print("用法: --phase project_id:phase")
    
    else:
        parser.print_help()
        print("\n💡 快速使用:")
        print("   python -m core.cli project create '智能系统' --template web_app")
        print("   python -m core.cli project list")
        print("   python -m core.cli project status proj-xxx")


if __name__ == '__main__':
    main()
