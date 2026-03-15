"""
工作流模板系统
预置 Web/API/数据分析/AI 项目模板
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class TemplateType(Enum):
    """模板类型"""
    WEB_APP = "web_app"
    API_SERVICE = "api_service"
    DATA_ANALYSIS = "data_analysis"
    AI_PROJECT = "ai_project"
    ENTERPRISE = "enterprise"
    MOBILE_APP = "mobile_app"

@dataclass
class WorkflowTemplate:
    """工作流模板"""
    id: str
    name: str
    description: str
    template_type: TemplateType
    stages: List[Dict[str, Any]]
    estimated_hours: float
    required_agents: List[str]
    required_capabilities: List[str]

class TemplateRegistry:
    """模板注册表"""

    def __init__(self):
        self.templates: Dict[str, WorkflowTemplate] = {}
        self._register_default_templates()

    def _register_default_templates(self):
        """注册默认模板"""

        self.templates[TemplateType.WEB_APP.value] = WorkflowTemplate(
            id=TemplateType.WEB_APP.value,
            name="Web应用开发",
            description="标准Web应用开发模板 - 前端 + 后端 + 部署",
            template_type=TemplateType.WEB_APP,
            stages=[
                {"name": "需求确认", "agent": "orchestrator", "capabilities": ["requirement"]},
                {"name": "UI设计", "agent": "alpha", "capabilities": ["html", "css", "ui"]},
                {"name": "前端开发", "agent": "alpha", "capabilities": ["html", "css", "javascript", "ui"]},
                {"name": "后端开发", "agent": "bravo", "capabilities": ["backend", "api", "database"]},
                {"name": "功能整合", "agent": "charlie", "capabilities": ["fullstack", "debug"]},
                {"name": "代码审查", "agent": "delta", "capabilities": ["code_review"]},
                {"name": "安全审计", "agent": "foxtrot", "capabilities": ["security"]},
                {"name": "性能优化", "agent": "golf", "capabilities": ["performance", "optimization"]},
                {"name": "测试验证", "agent": "echo", "capabilities": ["testing"]},
                {"name": "文档编写", "agent": "hotel", "capabilities": ["documentation"]},
                {"name": "部署上线", "agent": "echo", "capabilities": ["deploy", "ops"]},
            ],
            estimated_hours=24,
            required_agents=["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel"],
            required_capabilities=["html", "css", "javascript", "backend", "api", "fullstack", "code_review", "security", "performance", "testing", "documentation", "deploy"]
        )

        self.templates[TemplateType.API_SERVICE.value] = WorkflowTemplate(
            id=TemplateType.API_SERVICE.value,
            name="API服务开发",
            description="RESTful API 服务开发模板",
            template_type=TemplateType.API_SERVICE,
            stages=[
                {"name": "API设计", "agent": "bravo", "capabilities": ["backend", "api"]},
                {"name": "数据库设计", "agent": "juliet", "capabilities": ["sql", "database"]},
                {"name": "后端实现", "agent": "bravo", "capabilities": ["backend", "algorithm"]},
                {"name": "单元测试", "agent": "delta", "capabilities": ["testing"]},
                {"name": "性能优化", "agent": "golf", "capabilities": ["performance", "caching"]},
                {"name": "安全加固", "agent": "foxtrot", "capabilities": ["security", "encryption"]},
                {"name": "API文档", "agent": "hotel", "capabilities": ["api_docs"]},
                {"name": "部署配置", "agent": "echo", "capabilities": ["deploy", "ci_cd"]},
            ],
            estimated_hours=16,
            required_agents=["bravo", "juliet", "delta", "foxtrot", "golf", "hotel", "echo"],
            required_capabilities=["backend", "api", "sql", "database", "algorithm", "testing", "performance", "security", "documentation"]
        )

        self.templates[TemplateType.DATA_ANALYSIS.value] = WorkflowTemplate(
            id=TemplateType.DATA_ANALYSIS.value,
            name="数据分析项目",
            description="数据采集 + 分析 + 可视化模板",
            template_type=TemplateType.DATA_ANALYSIS,
            stages=[
                {"name": "数据采集", "agent": "juliet", "capabilities": ["sql", "etl", "data_viz"]},
                {"name": "数据清洗", "agent": "juliet", "capabilities": ["pandas", "data_viz"]},
                {"name": "数据分析", "agent": "juliet", "capabilities": ["analytics", "pandas"]},
                {"name": "可视化开发", "agent": "alpha", "capabilities": ["html", "css", "ui"]},
                {"name": "报告生成", "agent": "hotel", "capabilities": ["documentation"]},
                {"name": "性能优化", "agent": "golf", "capabilities": ["performance"]},
            ],
            estimated_hours=20,
            required_agents=["juliet", "alpha", "hotel", "golf"],
            required_capabilities=["sql", "etl", "pandas", "data_viz", "analytics", "html", "css", "documentation", "performance"]
        )

        self.templates[TemplateType.AI_PROJECT.value] = WorkflowTemplate(
            id=TemplateType.AI_PROJECT.value,
            name="AI项目开发",
            description="机器学习/深度学习项目开发模板",
            template_type=TemplateType.AI_PROJECT,
            stages=[
                {"name": "需求分析", "agent": "india", "capabilities": ["ai_expert"]},
                {"name": "数据准备", "agent": "juliet", "capabilities": ["sql", "etl", "pandas"]},
                {"name": "模型开发", "agent": "india", "capabilities": ["machine_learning", "deep_learning", "tensorflow"]},
                {"name": "模型训练", "agent": "india", "capabilities": ["model_training", "pytorch"]},
                {"name": "模型评估", "agent": "india", "capabilities": ["ai_api", "analytics"]},
                {"name": "API开发", "agent": "bravo", "capabilities": ["backend", "api", "ai_api"]},
                {"name": "前端集成", "agent": "alpha", "capabilities": ["html", "css", "ui"]},
                {"name": "性能优化", "agent": "golf", "capabilities": ["performance", "optimization"]},
                {"name": "安全审计", "agent": "foxtrot", "capabilities": ["security"]},
                {"name": "部署上线", "agent": "echo", "capabilities": ["deploy", "ops", "monitoring"]},
            ],
            estimated_hours=40,
            required_agents=["india", "juliet", "bravo", "alpha", "golf", "foxtrot", "echo"],
            required_capabilities=["machine_learning", "deep_learning", "tensorflow", "pytorch", "model_training", "sql", "etl", "pandas", "backend", "api", "ai_api", "html", "css", "performance", "security", "deploy"]
        )

        self.templates[TemplateType.ENTERPRISE.value] = WorkflowTemplate(
            id=TemplateType.ENTERPRISE.value,
            name="企业级项目",
            description="大型企业级应用开发模板",
            template_type=TemplateType.ENTERPRISE,
            stages=[
                {"name": "架构设计", "agent": "bravo", "capabilities": ["backend", "architecture"]},
                {"name": "数据库设计", "agent": "juliet", "capabilities": ["sql", "database"]},
                {"name": "微服务开发", "agent": "bravo", "capabilities": ["backend", "api"]},
                {"name": "前端开发", "agent": "alpha", "capabilities": ["html", "css", "ui", "responsive"]},
                {"name": "功能整合", "agent": "charlie", "capabilities": ["fullstack", "integration"]},
                {"name": "代码审查", "agent": "delta", "capabilities": ["code_review", "quality"]},
                {"name": "安全审计", "agent": "foxtrot", "capabilities": ["security", "audit"]},
                {"name": "性能优化", "agent": "golf", "capabilities": ["performance", "caching"]},
                {"name": "文档编写", "agent": "hotel", "capabilities": ["documentation", "api_docs"]},
                {"name": "自动化测试", "agent": "echo", "capabilities": ["testing", "ci_cd"]},
                {"name": "部署运维", "agent": "echo", "capabilities": ["deploy", "ops", "monitoring"]},
            ],
            estimated_hours=60,
            required_agents=["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "juliet"],
            required_capabilities=["backend", "api", "database", "sql", "html", "css", "ui", "fullstack", "code_review", "security", "performance", "documentation", "testing", "deploy", "ops"]
        )

    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """获取模板"""
        return self.templates.get(template_id)

    def list_templates(self) -> List[Dict]:
        """列出所有模板"""
        return [
            {
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'estimated_hours': t.estimated_hours,
                'stage_count': len(t.stages)
            }
            for t in self.templates.values()
        ]

    def get_template_stages(self, template_id: str) -> List[Dict]:
        """获取模板阶段"""
        template = self.get_template(template_id)
        return template.stages if template else []


template_registry = TemplateRegistry()
