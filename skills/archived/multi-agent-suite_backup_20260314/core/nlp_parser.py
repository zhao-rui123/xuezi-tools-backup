"""
自然语言任务解析器
自动理解用户需求并拆解任务
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

class ProjectType(Enum):
    """项目类型"""
    WEB_APP = "web_app"
    API_SERVICE = "api_service"
    DATA_ANALYSIS = "data_analysis"
    AI_PROJECT = "ai_project"
    MOBILE_APP = "mobile_app"
    SCRIPT = "script"
    UNKNOWN = "unknown"

class Complexity(Enum):
    """项目复杂度"""
    SIMPLE = 1
    MEDIUM = 2
    COMPLEX = 3
    VERY_COMPLEX = 4

@dataclass
class ParsedTask:
    """解析后的任务"""
    title: str
    project_type: ProjectType
    complexity: Complexity
    features: List[str]
    technologies: List[str]
    requirements: List[str]
    confidence: float

class NaturalLanguageParser:
    """自然语言任务解析器"""

    def __init__(self):
        self.patterns = self._init_patterns()

    def _init_patterns(self) -> Dict:
        """初始化模式匹配"""
        return {
            'project_type': {
                'web_app': [r'web', r'网站', r'前端', r'页面', r'网页', r'登录', r'注册', r'dashboard', r'管理系统'],
                'api_service': [r'api', r'接口', r'service', r'服务', r'rest', r'后端接口'],
                'data_analysis': [r'分析', r'数据', r'报表', r'dashboard', r'统计', r'可视化', r'图表'],
                'ai_project': [r'ai', r'人工智能', r'机器学习', r'深度学习', r'模型', r'神经网络', r'nlp', r'chatgpt'],
                'mobile_app': [r'手机', r'app', r'移动端', r'小程序', r'ios', r'android'],
                'script': [r'脚本', r'工具', r'自动化', r'小工具']
            },
            'feature': {
                '登录注册': [r'登录', r'注册', r'登陆', r'认证', r'auth', r'login', r'register'],
                '用户管理': [r'用户', r'管理', r'权限', r'角色', r'admin', r'user'],
                'CRUD': [r'增删改查', r'crud', r'列表', r'详情', r'编辑', r'删除'],
                '搜索': [r'搜索', r'search', r'查询', r'过滤'],
                '文件上传': [r'上传', r'文件', r'upload', r'附件'],
                '消息通知': [r'通知', r'消息', r'推送', r'notification', r'message'],
                '支付': [r'支付', r'钱', r'订单', r'支付', r'purchase', r'payment'],
                '图表': [r'图表', r'图', r'chart', r'graph', r'可视化'],
                '评论': [r'评论', r'反馈', r'评价', r'comment', r'review'],
                '分享': [r'分享', r'share']
            },
            'technology': {
                'python': [r'python', r'py', r'django', r'flask', r'fastapi'],
                'javascript': [r'javascript', r'js', r'node', r'nodejs'],
                'react': [r'react', r'reactjs', r'react.js'],
                'vue': [r'vue', r'vuejs', r'vue.js'],
                'typescript': [r'typescript', r'ts'],
                'database': [r'数据库', r'db', r'mysql', r'postgresql', r'mongodb', r'sqlite'],
                'api': [r'api', r'rest', r'graphql']
            },
            'complexity': {
                'simple': [r'简单', r'小', r'基础', r'simple', r'basic'],
                'medium': [r'中等', r'一般', r'normal', r'medium'],
                'complex': [r'复杂', r'大型', r'企业级', r'complex', r'enterprise'],
                'very_complex': [r'非常复杂', r'超级', r'very complex']
            }
        }

    def parse(self, user_input: str) -> ParsedTask:
        """解析用户输入"""
        user_input_lower = user_input.lower()

        project_type = self._detect_project_type(user_input_lower)
        features = self._detect_features(user_input_lower)
        technologies = self._detect_technologies(user_input_lower)
        complexity = self._detect_complexity(user_input_lower, features, technologies)

        title = self._generate_title(user_input, project_type)
        requirements = self._generate_requirements(features, technologies)
        confidence = self._calculate_confidence(features, technologies)

        return ParsedTask(
            title=title,
            project_type=project_type,
            complexity=complexity,
            features=features,
            technologies=technologies,
            requirements=requirements,
            confidence=confidence
        )

    def _detect_project_type(self, text: str) -> ProjectType:
        """检测项目类型"""
        scores = {}

        for ptype, patterns in self.patterns['project_type'].items():
            score = sum(1 for p in patterns if re.search(p, text))
            if score > 0:
                scores[ptype] = score

        if not scores:
            return ProjectType.UNKNOWN

        return ProjectType(max(scores, key=scores.get))

    def _detect_features(self, text: str) -> List[str]:
        """检测功能"""
        features = []

        for feature, patterns in self.patterns['feature'].items():
            if any(re.search(p, text) for p in patterns):
                features.append(feature)

        return features

    def _detect_technologies(self, text: str) -> List[str]:
        """检测技术栈"""
        technologies = []

        for tech, patterns in self.patterns['technology'].items():
            if any(re.search(p, text) for p in patterns):
                technologies.append(tech)

        return technologies

    def _detect_complexity(self, text: str, features: List[str], technologies: List[str]) -> Complexity:
        """检测复杂度"""
        base_score = len(features) + len(technologies)

        for pattern in self.patterns['complexity']['very_complex']:
            if re.search(pattern, text):
                return Complexity.VERY_COMPLEX

        for pattern in self.patterns['complexity']['complex']:
            if re.search(pattern, text):
                return Complexity.COMPLEX

        for pattern in self.patterns['complexity']['medium']:
            if re.search(pattern, text):
                return Complexity.MEDIUM

        if base_score <= 2:
            return Complexity.SIMPLE
        elif base_score <= 4:
            return Complexity.MEDIUM
        elif base_score <= 6:
            return Complexity.COMPLEX
        else:
            return Complexity.VERY_COMPLEX

    def _generate_title(self, user_input: str, project_type: ProjectType) -> str:
        """生成标题"""
        if len(user_input) < 30:
            return user_input.title()

        type_names = {
            ProjectType.WEB_APP: "Web应用",
            ProjectType.API_SERVICE: "API服务",
            ProjectType.DATA_ANALYSIS: "数据分析",
            ProjectType.AI_PROJECT: "AI项目",
            ProjectType.MOBILE_APP: "移动应用",
            ProjectType.SCRIPT: "工具脚本",
            ProjectType.UNKNOWN: "项目"
        }

        return f"{type_names.get(project_type, '项目')}-{datetime.now().strftime('%m%d')}"

    def _generate_requirements(self, features: List[str], technologies: List[str]) -> List[str]:
        """生成需求列表"""
        requirements = []

        for feature in features:
            requirement_map = {
                '登录注册': '用户登录注册功能',
                '用户管理': '用户管理功能',
                'CRUD': '数据增删改查',
                '搜索': '搜索功能',
                '文件上传': '文件上传下载',
                '消息通知': '消息通知',
                '支付': '支付功能',
                '图表': '数据可视化图表',
                '评论': '评论反馈',
                '分享': '分享功能'
            }
            if feature in requirement_map:
                requirements.append(requirement_map[feature])

        tech_requirements = {
            'python': 'Python后端开发',
            'javascript': 'JavaScript开发',
            'react': 'React前端',
            'vue': 'Vue前端',
            'database': '数据库设计'
        }

        for tech in technologies:
            if tech in tech_requirements:
                requirements.append(tech_requirements[tech])

        return requirements

    def _calculate_confidence(self, features: List[str], technologies: List[str]) -> float:
        """计算置信度"""
        total = len(features) + len(technologies)
        if total == 0:
            return 0.3
        elif total <= 2:
            return 0.6
        elif total <= 4:
            return 0.8
        else:
            return 0.9

    def explain_parsing(self, task: ParsedTask) -> str:
        """解释解析结果"""
        lines = [
            "📝 任务解析结果",
            "=" * 50,
            f"标题: {task.title}",
            f"项目类型: {task.project_type.value}",
            f"复杂度: {'★' * task.complexity.value}",
            f"置信度: {task.confidence:.0%}",
            ""
        ]

        if task.features:
            lines.append("检测到的功能:")
            for f in task.features:
                lines.append(f"  • {f}")
            lines.append("")

        if task.technologies:
            lines.append("技术栈:")
            for t in task.technologies:
                lines.append(f"  • {t}")
            lines.append("")

        if task.requirements:
            lines.append("需求清单:")
            for r in task.requirements:
                lines.append(f"  • {r}")

        return "\n".join(lines)

from datetime import datetime
