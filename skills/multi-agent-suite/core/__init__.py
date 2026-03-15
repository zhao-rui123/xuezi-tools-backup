"""
Multi-Agent Suite Core Package
多Agent协作系统核心模块
"""

__version__ = "3.3.0"

from .orchestrator import MultiAgentOrchestrator
from .workflow import DevelopmentWorkflow
from .agent_communication import AgentCommunication
from .task_estimator import TaskEstimator
from .enhancements import (
    checkpoint_manager,
    load_balancer,
    retry_policy,
    performance_monitor,
    CheckpointManager,
    LoadBalancer,
    RetryPolicy,
    PerformanceMonitor
)
from .incremental_reviewer import IncrementalReviewer, CodeChange
from .context_manager import ContextWindowManager, ConversationContext, CompressionStrategy
from .templates import TemplateRegistry, WorkflowTemplate, TemplateType, template_registry
from .config_center import ConfigCenter, config_center
from .task_dag import TaskDAG, DAGTask, TaskState
from .nlp_parser import NaturalLanguageParser, ParsedTask, ProjectType, Complexity
from .task_queue import TaskQueue, TaskScheduler, task_queue, task_scheduler, TaskPriority, TaskStatus
from .audit_logger import AuditLogger, AuditLevel, AuditCategory, audit_logger
from .approval_system import ApprovalSystem, ApprovalRequest, ApprovalStatus, ApprovalType, approval_system

__all__ = [
    '__version__',
    'MultiAgentOrchestrator',
    'DevelopmentWorkflow',
    'AgentCommunication',
    'TaskEstimator',
    'CheckpointManager',
    'LoadBalancer',
    'RetryPolicy',
    'PerformanceMonitor',
    'IncrementalReviewer',
    'CodeChange',
    'ContextWindowManager',
    'ConversationContext',
    'CompressionStrategy',
    'TemplateRegistry',
    'WorkflowTemplate',
    'TemplateType',
    'template_registry',
    'ConfigCenter',
    'config_center',
    'TaskDAG',
    'DAGTask',
    'TaskState',
    'NaturalLanguageParser',
    'ParsedTask',
    'ProjectType',
    'Complexity',
    'TaskQueue',
    'TaskScheduler',
    'task_queue',
    'task_scheduler',
    'TaskPriority',
    'TaskStatus',
    'AuditLogger',
    'AuditLevel',
    'AuditCategory',
    'audit_logger',
    'ApprovalSystem',
    'ApprovalRequest',
    'ApprovalStatus',
    'ApprovalType',
    'approval_system',
    'checkpoint_manager',
    'load_balancer',
    'retry_policy',
    'performance_monitor',
]
