#!/usr/bin/env python3
"""
Memory Service - 上下文恢复模块 (增强版 v2.0)
Context Recovery Module - Enhanced with Learning Library Scene Matching

功能：
1. 加载会话状态（current_session.json）
2. 读取错误学习库（knowledge-base/learnings/）
3. 场景匹配：根据当前任务动态匹配相关学习项（增强版）
4. 模糊匹配和同义词支持
5. 生成 contextual 提醒（只显示相关内容）

Author: Bravo Agent (Builder) + Mike Agent (Enhancement)
Version: 2.0.0
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from difflib import SequenceMatcher
import hashlib


# ============ 配置常量 ============
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
KNOWLEDGE_BASE_DIR = WORKSPACE / "knowledge-base"
LEARNINGS_DIR = KNOWLEDGE_BASE_DIR / "learnings"

SESSION_SNAPSHOT_FILE = MEMORY_DIR / "snapshots" / "current_session.json"
SESSION_STATE_FILE = MEMORY_DIR / "session_states" / "current_session.json"

# 确保目录存在
LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)


# ============ 同义词和语义映射 ============

# 同义词映射表
SYNONYM_MAP = {
    # 开发相关
    "开发": ["编写", "编程", "coding", "programming", "dev", "development", "implement", "实现", "build", "构建"],
    "代码": ["程序", "脚本", "script", "code", "source", "源码", "program"],
    "修复": ["解决", "调试", "debug", "fix", "repair", "patch", "troubleshoot", "排查"],
    "错误": ["bug", "问题", "故障", "error", "issue", "exception", "fault", "defect", "崩溃", "crash"],
    "测试": ["验证", "test", "testing", "check", "verify", "validate", "检验"],
    "部署": ["发布", "上线", "deploy", "deployment", "release", "publish", "launch"],
    
    # 技术栈相关
    "python": ["py", "python3", "python2", "蟒蛇"],
    "javascript": ["js", "node", "nodejs", "node.js", "ecmascript"],
    "typescript": ["ts", "type script"],
    "数据库": ["db", "database", "sql", "mysql", "postgres", "mongodb", "数据存储"],
    "api": ["接口", "endpoint", "rest", "graphql", "web service", "服务接口"],
    "前端": ["frontend", "front-end", "ui", "界面", "页面", "web", "browser"],
    "后端": ["backend", "back-end", "server", "服务端", "服务器端"],
    
    # 文件相关
    "文件": ["文档", "file", "document", "档案", "资料"],
    "配置": ["设置", "config", "configuration", "setting", "preference", "选项"],
    "路径": ["目录", "文件夹", "path", "directory", "folder", "location"],
    
    # 系统相关
    "服务": ["service", "daemon", "后台", "server", "系统服务"],
    "进程": ["process", "task", "线程", "thread", "job"],
    "内存": ["memory", "ram", "存储", "缓存", "cache"],
    
    # 项目相关
    "项目": ["project", "工程", "应用", "application", "app", "产品", "product"],
    "任务": ["task", "工作", "work", "job", "todo", "待办", "事项"],
    "功能": ["feature", "特性", "能力", "capability", "function", "函数"],
    
    # Agent相关
    "agent": ["智能体", "代理", "助手", "assistant", "bot", "机器人", "ai"],
    "多agent": ["multi-agent", "multi agent", "多智能体", "agent团队", "agent team"],
    "工作流": ["workflow", "flow", "流程", "pipeline", "管道"],
    
    # 储能相关
    "储能": ["energy storage", "battery", "电池", "储能系统", "储能电站", "bess"],
    "测算": ["计算", "评估", "财务", "finance", "calculation", "modeling", "模型"],
    "电价": ["电价", "电费", "price", "tariff", "rate", "电价政策"],
    "光伏": ["solar", "太阳能", "pv", "photovoltaic", "发电"],
    
    # 股票相关
    "股票": ["stock", "share", "equity", "证券", "投资", "investment"],
    "行情": ["price", "market", "quote", "ticker", "走势", "价格"],
    "分析": ["analysis", "analyze", "研究", "research", "analytics", "统计"],
    "筛选": ["screener", "filter", "选股", "pick", "选择", "过滤"],
    
    # 飞书相关
    "飞书": ["feishu", "lark", "字节", "bytedance"],
    "文档": ["doc", "document", "docx", "wiki", "知识库"],
    "表格": ["sheet", "spreadsheet", "excel", "bitable", "多维表格"],
    
    # 通用动词
    "创建": ["新建", "生成", "create", "make", "generate", "build", "init", "初始化"],
    "更新": ["修改", "编辑", "update", "edit", "change", "modify", "revise"],
    "删除": ["移除", "清空", "delete", "remove", "clear", "drop", "erase"],
    "查看": ["读取", "显示", "read", "view", "show", "display", "get", "fetch"],
    "保存": ["存储", "写入", "save", "store", "write", "persist"],
    "发送": ["推送", "传输", "send", "push", "transmit", "deliver"],
    "获取": ["得到", "接收", "fetch", "get", "receive", "obtain", "acquire"],
}

# 场景关键词映射 - 用于快速场景识别
SCENE_KEYWORDS = {
    "memory_service": ["memory", "上下文", "context", "恢复", "recovery", "session", "会话", "学习库", "learning"],
    "file_operation": ["文件", "file", "上传", "下载", "读取", "保存", "路径", "folder", "directory"],
    "web_development": ["web", "网站", "html", "css", "javascript", "前端", "页面", "browser"],
    "api_development": ["api", "接口", "rest", "graphql", "endpoint", "backend", "后端"],
    "database": ["数据库", "db", "sql", "query", "表", "table", "存储"],
    "agent_development": ["agent", "智能体", "multi-agent", "工作流", "workflow"],
    "storage_calc": ["储能", "测算", "电价", "battery", "energy storage", "bess", "irr"],
    "stock_analysis": ["股票", "stock", "行情", "分析", "筛选", "screener"],
    "feishu_integration": ["飞书", "feishu", "lark", "文档", "多维表格", "bitable"],
    "server_ops": ["服务器", "server", "部署", "deploy", "nginx", "ssh", "运维"],
    "skill_dev": ["技能包", "skill", "工具包", "plugin", "extension"],
}

# 停用词扩展（中英文）
STOPWORDS = {
    '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '之', '与', '及', '等', '或', '但', '而', '如果', '因为', '所以', 'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or', 'because', 'until', 'while', 'this', 'that', 'these', 'those', 'am', 'it', 'its', 'what', 'which', 'who', 'whom', 'whose', 'whatever', 'whoever', 'whomever', 'whichever', '进行', '完成', '开始', '结束', '使用', '通过', '根据', '关于', '需要', '可以', '已经', '正在', '现在', '这里', '那里', '什么', '怎么', '为什么', '如何', '是否', '能够', '应该', '必须', '可能', '一定', '非常', '比较', '相对', '关于', '对于', '由于', '为了', '除了', '向着', '沿着', '随着', '趁着', '凭着', '按照', '依照', '根据', '通过', '经过', '随着', '除了', '向着', '沿着', '趁着', '凭着',
}


# ============ 数据类定义 ============

class LearningType(Enum):
    """学习项类型"""
    ERROR = "error"           # 错误修复
    PATTERN = "pattern"       # 模式/最佳实践
    DECISION = "decision"     # 重要决策
    WORKAROUND = "workaround" # 临时解决方案
    TIP = "tip"               # 小技巧


@dataclass
class LearningItem:
    """学习项数据结构"""
    id: str
    title: str
    content: str
    learning_type: LearningType
    tags: List[str] = field(default_factory=list)
    context: str = ""         # 适用场景描述
    solution: str = ""        # 解决方案
    created_at: str = ""
    updated_at: str = ""
    usage_count: int = 0      # 使用次数
    effectiveness: float = 0.0  # 有效性评分 (0-5)
    related_tasks: List[str] = field(default_factory=list)
    source: str = ""          # 来源文件
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "learning_type": self.learning_type.value,
            "tags": self.tags,
            "context": self.context,
            "solution": self.solution,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "usage_count": self.usage_count,
            "effectiveness": self.effectiveness,
            "related_tasks": self.related_tasks,
            "source": self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "LearningItem":
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            content=data.get("content", ""),
            learning_type=LearningType(data.get("learning_type", "tip")),
            tags=data.get("tags", []),
            context=data.get("context", ""),
            solution=data.get("solution", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            usage_count=data.get("usage_count", 0),
            effectiveness=data.get("effectiveness", 0.0),
            related_tasks=data.get("related_tasks", []),
            source=data.get("source", "")
        )


@dataclass
class SessionState:
    """会话状态数据结构"""
    timestamp: str
    session_key: str
    current_task: str
    pending_items: List[str] = field(default_factory=list)
    key_context: Dict = field(default_factory=dict)
    last_messages: List[str] = field(default_factory=list)
    recovery_phrase: str = ""
    auto_saved_at: str = ""
    project: str = ""
    agent_context: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SessionState":
        return cls(
            timestamp=data.get("timestamp", ""),
            session_key=data.get("session_key", ""),
            current_task=data.get("current_task", ""),
            pending_items=data.get("pending_items", []),
            key_context=data.get("key_context", {}),
            last_messages=data.get("last_messages", []),
            recovery_phrase=data.get("recovery_phrase", ""),
            auto_saved_at=data.get("auto_saved_at", ""),
            project=data.get("project", ""),
            agent_context=data.get("agent_context", {})
        )


@dataclass
class MatchResult:
    """匹配结果"""
    learning_item: LearningItem
    score: float
    match_reason: str
    match_type: str = ""  # 匹配类型：exact, synonym, fuzzy, semantic, scene


@dataclass
class RecoveryContext:
    """恢复上下文"""
    session_state: Optional[SessionState]
    matched_learnings: List[MatchResult]
    time_gap: timedelta
    recommendations: List[str]
    warnings: List[str]
    detected_scene: str = ""  # 检测到的场景


# ============ 核心类 ============

class ContextRecoveryService:
    """
    上下文恢复服务 (增强版)
    
    主要职责：
    1. 加载和管理会话状态
    2. 维护错误学习库
    3. 执行增强场景匹配（支持模糊匹配和同义词）
    4. 生成 contextual 恢复提示
    """
    
    def __init__(self):
        self.learnings: List[LearningItem] = []
        self.session_state: Optional[SessionState] = None
        self._load_all_learnings()
    
    # ========== 会话状态管理 ==========
    
    def load_session_state(self) -> Optional[SessionState]:
        """
        加载会话状态
        优先从 snapshots 加载，其次从 session_states 加载
        """
        # 尝试多个可能的位置
        possible_paths = [
            SESSION_SNAPSHOT_FILE,
            SESSION_STATE_FILE,
            MEMORY_DIR / "current_session.json",
        ]
        
        for path in possible_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.session_state = SessionState.from_dict(data)
                    return self.session_state
                except Exception as e:
                    print(f"⚠️ 读取会话状态失败 ({path}): {e}")
                    continue
        
        return None
    
    def save_session_state(self, state: SessionState) -> bool:
        """保存会话状态"""
        try:
            SESSION_SNAPSHOT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SESSION_SNAPSHOT_FILE, 'w', encoding='utf-8') as f:
                json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存会话状态失败: {e}")
            return False
    
    def calculate_time_gap(self, state: SessionState) -> timedelta:
        """计算距离上次会话的时间间隔"""
        try:
            last_time = datetime.fromisoformat(state.timestamp)
            return datetime.now() - last_time
        except:
            return timedelta(0)
    
    # ========== 错误学习库管理 ==========
    
    def _load_all_learnings(self):
        """加载所有学习项"""
        self.learnings = []
        
        if not LEARNINGS_DIR.exists():
            return
        
        # 加载所有 JSON 文件
        for json_file in LEARNINGS_DIR.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 支持单个对象或数组
                if isinstance(data, list):
                    for item_data in data:
                        item = LearningItem.from_dict(item_data)
                        item.source = str(json_file.name)
                        self.learnings.append(item)
                else:
                    item = LearningItem.from_dict(data)
                    item.source = str(json_file.name)
                    self.learnings.append(item)
                    
            except Exception as e:
                print(f"⚠️ 加载学习项失败 ({json_file}): {e}")
    
    def add_learning(self, item: LearningItem) -> bool:
        """添加新的学习项"""
        try:
            # 生成唯一ID
            if not item.id:
                item.id = self._generate_id(item.title)
            
            item.created_at = datetime.now().isoformat()
            item.updated_at = item.created_at
            
            # 保存到文件
            file_path = LEARNINGS_DIR / f"{item.id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(item.to_dict(), f, ensure_ascii=False, indent=2)
            
            self.learnings.append(item)
            return True
        except Exception as e:
            print(f"❌ 添加学习项失败: {e}")
            return False
    
    def update_learning_usage(self, item_id: str, effective: bool = True):
        """更新学习项使用统计"""
        for item in self.learnings:
            if item.id == item_id:
                item.usage_count += 1
                if effective:
                    # 更新有效性评分（简单移动平均）
                    item.effectiveness = (item.effectiveness * (item.usage_count - 1) + 5) / item.usage_count
                else:
                    item.effectiveness = (item.effectiveness * (item.usage_count - 1) + 1) / item.usage_count
                
                # 保存更新
                file_path = LEARNINGS_DIR / f"{item_id}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(item.to_dict(), f, ensure_ascii=False, indent=2)
                break
    
    def get_learnings_by_type(self, learning_type: LearningType) -> List[LearningItem]:
        """按类型获取学习项"""
        return [item for item in self.learnings if item.learning_type == learning_type]
    
    def get_learnings_by_tags(self, tags: List[str]) -> List[LearningItem]:
        """按标签获取学习项"""
        results = []
        for item in self.learnings:
            if any(tag in item.tags for tag in tags):
                results.append(item)
        return results
    
    # ========== 场景检测 ==========
    
    def detect_scene(self, task: str) -> str:
        """
        检测当前任务所属的场景
        
        Returns:
            场景名称或空字符串
        """
        if not task:
            return ""
        
        task_lower = task.lower()
        scene_scores = {}
        
        for scene, keywords in SCENE_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in task_lower:
                    score += 1
                    # 完整匹配加分
                    if keyword.lower() == task_lower or f" {keyword.lower()} " in f" {task_lower} ":
                        score += 2
            
            if score > 0:
                scene_scores[scene] = score
        
        if scene_scores:
            # 返回得分最高的场景
            return max(scene_scores, key=scene_scores.get)
        
        return ""
    
    # ========== 增强场景匹配 ==========
    
    def match_learnings(self, current_task: str, context: Dict = None, 
                        top_k: int = 5, min_score: float = 1.5) -> List[MatchResult]:
        """
        根据当前任务匹配相关学习项（增强版）
        
        匹配算法：
        1. 精确关键词匹配（任务描述 vs 学习项标题/内容/标签）
        2. 同义词扩展匹配
        3. 模糊匹配（编辑距离）
        4. 语义场景匹配
        5. 相关性评分和排序
        
        Args:
            current_task: 当前任务描述
            context: 额外上下文信息
            top_k: 返回的最大结果数
            min_score: 最小匹配分数阈值
        
        Returns:
            按相关性排序的匹配结果列表
        """
        if not self.learnings or not current_task:
            return []
        
        context = context or {}
        matches = []
        
        # 检测当前场景
        detected_scene = self.detect_scene(current_task)
        
        # 提取并扩展当前任务的关键词（包含同义词）
        task_keywords = self._extract_keywords(current_task)
        expanded_keywords = self._expand_synonyms(task_keywords)
        
        project_keywords = self._extract_keywords(context.get("project", ""))
        expanded_project_keywords = self._expand_synonyms(project_keywords)
        
        all_keywords = list(set(task_keywords + expanded_keywords + project_keywords + expanded_project_keywords))
        
        for item in self.learnings:
            score = 0.0
            reasons = []
            match_types = []
            
            # 1. 精确标题匹配（权重：4）
            title_score, title_reasons, title_types = self._match_text(
                item.title, all_keywords, base_weight=4.0
            )
            score += title_score
            reasons.extend(title_reasons)
            match_types.extend(title_types)
            
            # 2. 标签匹配（权重：3）
            tag_score, tag_reasons, tag_types = self._match_tags(
                item.tags, all_keywords, base_weight=3.0
            )
            score += tag_score
            reasons.extend(tag_reasons)
            match_types.extend(tag_types)
            
            # 3. 内容匹配（权重：2）
            content_score, content_reasons, content_types = self._match_text(
                item.content, all_keywords, base_weight=2.0
            )
            score += content_score
            reasons.extend(content_reasons)
            match_types.extend(content_types)
            
            # 4. 场景匹配（权重：2.5）
            if item.context:
                context_score, context_reasons, context_types = self._match_text(
                    item.context, all_keywords, base_weight=2.5
                )
                score += context_score
                reasons.extend(context_reasons)
                match_types.extend(context_types)
            
            # 5. 相关任务匹配（权重：3）
            if item.related_tasks:
                for related_task in item.related_tasks:
                    related_score, related_reasons, related_types = self._match_text(
                        related_task, all_keywords, base_weight=3.0
                    )
                    if related_score > 0:
                        score += related_score
                        reasons.extend(related_reasons)
                        match_types.extend(related_types)
                        break
            
            # 6. 模糊匹配 - 标题相似度（权重：1.5）
            fuzzy_score = self._fuzzy_match(current_task, item.title)
            if fuzzy_score > 0.6:  # 相似度阈值
                score += fuzzy_score * 1.5
                reasons.append(f"模糊匹配: 相似度 {fuzzy_score:.2f}")
                match_types.append("fuzzy")
            
            # 7. 场景一致性加分
            if detected_scene:
                item_scene = self.detect_scene(item.title + " " + item.context + " " + " ".join(item.tags))
                if item_scene == detected_scene:
                    score += 2.0
                    reasons.append(f"场景一致: {detected_scene}")
                    match_types.append("scene")
            
            # 8. 有效性加成（0-1分）
            score += item.effectiveness / 5
            
            # 9. 使用频率衰减（避免过度推荐）
            if item.usage_count > 0:
                score *= max(0.5, 1 - (item.usage_count * 0.03))
            
            # 10. 时效性加成（最近的学习项略微加分）
            if item.created_at:
                try:
                    created = datetime.fromisoformat(item.created_at)
                    days_old = (datetime.now() - created).days
                    if days_old < 7:  # 一周内
                        score *= 1.1
                except:
                    pass
            
            # 阈值过滤
            if score >= min_score:
                # 确定主要匹配类型
                primary_match_type = self._get_primary_match_type(match_types)
                
                matches.append(MatchResult(
                    learning_item=item,
                    score=score,
                    match_reason="; ".join(reasons[:3]),  # 只保留前3个原因
                    match_type=primary_match_type
                ))
        
        # 按分数排序
        matches.sort(key=lambda x: x.score, reverse=True)
        return matches[:top_k]
    
    def _match_text(self, text: str, keywords: List[str], base_weight: float = 1.0) -> Tuple[float, List[str], List[str]]:
        """
        匹配文本与关键词
        
        Returns:
            (分数, 原因列表, 匹配类型列表)
        """
        if not text or not keywords:
            return 0.0, [], []
        
        text_lower = text.lower()
        score = 0.0
        reasons = []
        match_types = []
        
        # 提取文本关键词
        text_keywords = self._extract_keywords(text)
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # 精确匹配
            if keyword_lower in text_lower:
                score += base_weight
                if keyword in text_keywords:
                    reasons.append(f"关键词 '{keyword}'")
                    match_types.append("exact")
                else:
                    reasons.append(f"同义词 '{keyword}'")
                    match_types.append("synonym")
            
            # 部分匹配（关键词的一部分）
            elif len(keyword) > 3:
                for text_kw in text_keywords:
                    if keyword_lower in text_kw.lower() or text_kw.lower() in keyword_lower:
                        score += base_weight * 0.5
                        reasons.append(f"部分匹配 '{keyword}'")
                        match_types.append("partial")
                        break
        
        return score, reasons, match_types
    
    def _match_tags(self, tags: List[str], keywords: List[str], base_weight: float = 1.0) -> Tuple[float, List[str], List[str]]:
        """
        匹配标签与关键词
        
        Returns:
            (分数, 原因列表, 匹配类型列表)
        """
        if not tags or not keywords:
            return 0.0, [], []
        
        score = 0.0
        reasons = []
        match_types = []
        matched_tags = []
        
        for tag in tags:
            tag_lower = tag.lower()
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                if keyword_lower == tag_lower:
                    score += base_weight
                    matched_tags.append(tag)
                    match_types.append("exact")
                elif keyword_lower in tag_lower or tag_lower in keyword_lower:
                    score += base_weight * 0.7
                    matched_tags.append(tag)
                    match_types.append("partial")
        
        if matched_tags:
            reasons.append(f"标签匹配: {', '.join(set(matched_tags))}")
        
        return score, reasons, match_types
    
    def _fuzzy_match(self, text1: str, text2: str) -> float:
        """
        计算两个文本的模糊匹配相似度
        
        Returns:
            相似度分数 (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        # 使用 SequenceMatcher 计算相似度
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _get_primary_match_type(self, match_types: List[str]) -> str:
        """确定主要匹配类型"""
        if not match_types:
            return "unknown"
        
        # 优先级顺序
        priority = ["exact", "scene", "synonym", "fuzzy", "partial"]
        for p in priority:
            if p in match_types:
                return p
        return match_types[0]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        提取关键词（增强版）
        
        支持中英文混合文本
        """
        if not text:
            return []
        
        # 转换为小写
        text = text.lower()
        
        # 移除标点符号，保留中文
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        
        # 分词 - 支持中英文
        # 中文：按字和常见词组提取
        # 英文：按空格分词
        words = []
        
        # 提取英文单词
        english_words = re.findall(r'[a-zA-Z]+', text)
        words.extend(english_words)
        
        # 提取中文字符和词组
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        words.extend(chinese_chars)
        
        # 提取中文词组（2-4字）
        chinese_text = ''.join(chinese_chars)
        for i in range(len(chinese_text) - 1):
            words.append(chinese_text[i:i+2])
            if i < len(chinese_text) - 2:
                words.append(chinese_text[i:i+3])
        
        # 过滤停用词和短词
        filtered_words = []
        for w in words:
            if len(w) > 1 or (len(w) == 1 and w in '储能股票飞书') :
                if w not in STOPWORDS and w not in {'http', 'https', 'www', 'com', 'org'}:
                    filtered_words.append(w)
        
        return list(set(filtered_words))
    
    def _expand_synonyms(self, keywords: List[str]) -> List[str]:
        """
        扩展关键词的同义词
        
        Args:
            keywords: 原始关键词列表
        
        Returns:
            扩展后的关键词列表（包含同义词）
        """
        expanded = set(keywords)
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # 查找同义词
            for main_word, synonyms in SYNONYM_MAP.items():
                if keyword_lower == main_word.lower() or keyword_lower in [s.lower() for s in synonyms]:
                    expanded.add(main_word)
                    expanded.update(synonyms)
        
        return list(expanded)
    
    def _generate_id(self, title: str) -> str:
        """生成唯一ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{title}_{timestamp}"
        hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"learning_{timestamp}_{hash_suffix}"
    
    # ========== 恢复提示生成 ==========
    
    def generate_recovery_prompt(self, recovery_context: RecoveryContext) -> str:
        """
        生成详细的恢复提示（Contextual 版本）
        
        只显示与当前任务相关的内容
        """
        lines = []
        
        # 头部信息
        lines.append("=" * 60)
        lines.append("🧠 上下文恢复报告")
        lines.append("=" * 60)
        
        # 会话状态
        if recovery_context.session_state:
            state = recovery_context.session_state
            lines.append(f"\n📌 上次会话状态")
            lines.append(f"   时间: {state.timestamp}")
            lines.append(f"   间隔: {self._format_time_gap(recovery_context.time_gap)}")
            lines.append(f"   任务: {state.current_task or '无'}")
            
            if state.project:
                lines.append(f"   项目: {state.project}")
            
            if state.pending_items:
                lines.append(f"\n   ⏳ 待办事项:")
                for i, item in enumerate(state.pending_items[:5], 1):
                    lines.append(f"      {i}. {item}")
        
        # 检测到的场景
        if recovery_context.detected_scene:
            lines.append(f"\n🎯 检测场景: {recovery_context.detected_scene}")
        
        # 匹配的学习项 - 只显示相关的
        if recovery_context.matched_learnings:
            lines.append(f"\n📚 相关经验提醒 (Top {len(recovery_context.matched_learnings)})")
            lines.append("-" * 60)
            
            # 按类型分组
            errors = [m for m in recovery_context.matched_learnings if m.learning_item.learning_type == LearningType.ERROR]
            patterns = [m for m in recovery_context.matched_learnings if m.learning_item.learning_type == LearningType.PATTERN]
            tips = [m for m in recovery_context.matched_learnings if m.learning_item.learning_type == LearningType.TIP]
            
            # 优先显示错误经验
            if errors:
                lines.append(f"\n   🐛 相关错误经验 ({len(errors)}条):")
                for i, match in enumerate(errors[:3], 1):
                    item = match.learning_item
                    lines.append(f"      [{i}] {item.title}")
                    lines.append(f"          内容: {item.content[:80]}...")
                    if item.solution:
                        lines.append(f"          方案: {item.solution[:60]}...")
            
            # 显示模式/最佳实践
            if patterns:
                lines.append(f"\n   📐 相关最佳实践 ({len(patterns)}条):")
                for i, match in enumerate(patterns[:2], 1):
                    item = match.learning_item
                    lines.append(f"      [{i}] {item.title}")
                    lines.append(f"          {item.content[:80]}...")
            
            # 显示小技巧
            if tips:
                lines.append(f"\n   💡 相关技巧 ({len(tips)}条):")
                for i, match in enumerate(tips[:2], 1):
                    item = match.learning_item
                    lines.append(f"      [{i}] {item.title}")
        
        # 推荐操作
        if recovery_context.recommendations:
            lines.append(f"\n💡 建议操作")
            lines.append("-" * 60)
            for rec in recovery_context.recommendations:
                lines.append(f"   • {rec}")
        
        # 警告信息
        if recovery_context.warnings:
            lines.append(f"\n⚠️ 注意事项")
            lines.append("-" * 60)
            for warning in recovery_context.warnings:
                lines.append(f"   • {warning}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    def generate_recovery_summary(self, recovery_context: RecoveryContext) -> str:
        """生成简洁的恢复摘要"""
        lines = []
        
        if recovery_context.session_state:
            state = recovery_context.session_state
            lines.append(f"⏰ 距离上次会话: {self._format_time_gap(recovery_context.time_gap)}")
            lines.append(f"📝 上次任务: {state.current_task or '无记录'}")
            
            if state.pending_items:
                lines.append(f"⏳ 待办: {len(state.pending_items)} 项")
        
        if recovery_context.detected_scene:
            lines.append(f"🎯 场景: {recovery_context.detected_scene}")
        
        if recovery_context.matched_learnings:
            # 统计各类型的数量
            errors = len([m for m in recovery_context.matched_learnings if m.learning_item.learning_type == LearningType.ERROR])
            patterns = len([m for m in recovery_context.matched_learnings if m.learning_item.learning_type == LearningType.PATTERN])
            
            if errors > 0:
                lines.append(f"🐛 相关错误经验: {errors} 条")
            if patterns > 0:
                lines.append(f"📐 相关最佳实践: {patterns} 条")
        
        return " | ".join(lines) if lines else "✅ 无历史上下文需要恢复"
    
    def _format_time_gap(self, gap: timedelta) -> str:
        """格式化时间间隔"""
        total_seconds = int(gap.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds}秒"
        elif total_seconds < 3600:
            return f"{total_seconds // 60}分钟"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}小时{minutes}分钟"
        else:
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            return f"{days}天{hours}小时"
    
    def _get_type_emoji(self, learning_type: LearningType) -> str:
        """获取类型对应的emoji"""
        emoji_map = {
            LearningType.ERROR: "🐛",
            LearningType.PATTERN: "📐",
            LearningType.DECISION: "🎯",
            LearningType.WORKAROUND: "🔧",
            LearningType.TIP: "💡"
        }
        return emoji_map.get(learning_type, "📄")
    
    # ========== 主流程 ==========
    
    def perform_recovery(self, current_task: str = "", context: Dict = None) -> RecoveryContext:
        """
        执行完整的上下文恢复流程（增强版）
        
        Args:
            current_task: 当前任务描述
            context: 额外上下文信息
        
        Returns:
            RecoveryContext: 恢复上下文对象
        """
        context = context or {}
        
        # 1. 加载会话状态
        session_state = self.load_session_state()
        
        # 2. 计算时间间隔
        time_gap = timedelta(0)
        if session_state:
            time_gap = self.calculate_time_gap(session_state)
        
        # 3. 如果没有提供当前任务，使用会话状态中的任务
        if not current_task and session_state:
            current_task = session_state.current_task
        
        # 4. 检测场景
        detected_scene = self.detect_scene(current_task)
        
        # 5. 匹配相关学习项（增强版）
        matched_learnings = []
        if current_task:
            matched_learnings = self.match_learnings(current_task, context, top_k=5, min_score=1.5)
        
        # 6. 生成推荐
        recommendations = self._generate_recommendations(session_state, matched_learnings, time_gap)
        
        # 7. 生成警告
        warnings = self._generate_warnings(session_state, time_gap)
        
        return RecoveryContext(
            session_state=session_state,
            matched_learnings=matched_learnings,
            time_gap=time_gap,
            recommendations=recommendations,
            warnings=warnings,
            detected_scene=detected_scene
        )
    
    def _generate_recommendations(self, state: Optional[SessionState], 
                                   matches: List[MatchResult], 
                                   gap: timedelta) -> List[str]:
        """生成操作建议"""
        recommendations = []
        
        if not state:
            recommendations.append("开始新的工作会话")
            return recommendations
        
        # 根据时间间隔推荐
        if gap < timedelta(minutes=30):
            recommendations.append("继续之前的工作")
        elif gap < timedelta(hours=2):
            recommendations.append("快速回顾之前的进展，然后继续")
        elif gap < timedelta(days=1):
            recommendations.append("建议先查看待办事项列表")
        else:
            recommendations.append("较长时间未操作，建议重新评估任务优先级")
        
        # 根据待办事项推荐
        if state and state.pending_items:
            recommendations.append(f"处理 {len(state.pending_items)} 个待办事项")
        
        # 根据匹配的学习项推荐
        if matches:
            error_learnings = [m for m in matches if m.learning_item.learning_type == LearningType.ERROR]
            if error_learnings:
                recommendations.append(f"⚠️ 注意 {len(error_learnings)} 个相关错误经验，避免重复踩坑")
            
            pattern_learnings = [m for m in matches if m.learning_item.learning_type == LearningType.PATTERN]
            if pattern_learnings:
                recommendations.append(f"📐 参考 {len(pattern_learnings)} 个相关最佳实践")
        
        return recommendations
    
    def _generate_warnings(self, state: Optional[SessionState], gap: timedelta) -> List[str]:
        """生成警告信息"""
        warnings = []
        
        if not state:
            return warnings
        
        # 长时间未操作警告
        if gap > timedelta(days=7):
            warnings.append("会话已过期超过一周，上下文可能不准确")
        
        # 待办事项警告
        if state and len(state.pending_items) > 5:
            warnings.append(f"待办事项堆积 ({len(state.pending_items)} 项)，建议优先处理")
        
        return warnings
    
    # ========== 学习库搜索和查询 ==========
    
    def search_learnings(self, query: str, search_fields: List[str] = None) -> List[MatchResult]:
        """
        搜索学习库
        
        Args:
            query: 搜索查询
            search_fields: 搜索字段列表 ['title', 'content', 'tags', 'context']
        
        Returns:
            匹配结果列表
        """
        if not query or not self.learnings:
            return []
        
        search_fields = search_fields or ['title', 'content', 'tags']
        matches = []
        
        query_keywords = self._extract_keywords(query)
        expanded_keywords = self._expand_synonyms(query_keywords)
        all_keywords = list(set(query_keywords + expanded_keywords))
        
        for item in self.learnings:
            score = 0.0
            reasons = []
            
            if 'title' in search_fields:
                title_score, title_reasons, _ = self._match_text(item.title, all_keywords, base_weight=3.0)
                score += title_score
                reasons.extend(title_reasons)
            
            if 'content' in search_fields:
                content_score, content_reasons, _ = self._match_text(item.content, all_keywords, base_weight=2.0)
                score += content_score
                reasons.extend(content_reasons)
            
            if 'tags' in search_fields:
                tag_score, tag_reasons, _ = self._match_tags(item.tags, all_keywords, base_weight=2.5)
                score += tag_score
                reasons.extend(tag_reasons)
            
            if 'context' in search_fields and item.context:
                context_score, context_reasons, _ = self._match_text(item.context, all_keywords, base_weight=2.0)
                score += context_score
                reasons.extend(context_reasons)
            
            if score >= 1.5:
                matches.append(MatchResult(
                    learning_item=item,
                    score=score,
                    match_reason="; ".join(reasons[:3])
                ))
        
        matches.sort(key=lambda x: x.score, reverse=True)
        return matches


# ============ 便捷函数 ============

def recover_context(current_task: str = "", context: Dict = None, 
                    verbose: bool = True) -> Optional[str]:
    """
    便捷的上下文恢复函数（增强版）
    
    Args:
        current_task: 当前任务描述
        context: 额外上下文
        verbose: 是否生成详细报告
    
    Returns:
        恢复提示字符串，如果没有可恢复内容则返回 None
    """
    service = ContextRecoveryService()
    recovery_context = service.perform_recovery(current_task, context)
    
    # 检查是否有可恢复的内容
    has_content = (
        recovery_context.session_state is not None or 
        len(recovery_context.matched_learnings) > 0
    )
    
    if not has_content:
        return None
    
    if verbose:
        return service.generate_recovery_prompt(recovery_context)
    else:
        return service.generate_recovery_summary(recovery_context)


def quick_recover() -> str:
    """快速恢复，返回简洁摘要"""
    result = recover_context(verbose=False)
    return result or "✅ 无历史上下文需要恢复"


def add_error_learning(title: str, content: str, solution: str = "", 
                       tags: List[str] = None, context: str = "") -> bool:
    """
    便捷函数：添加错误学习项
    
    Args:
        title: 标题
        content: 错误描述
        solution: 解决方案
        tags: 标签列表
        context: 适用场景
    
    Returns:
        是否成功添加
    """
    service = ContextRecoveryService()
    
    item = LearningItem(
        id="",
        title=title,
        content=content,
        learning_type=LearningType.ERROR,
        tags=tags or [],
        context=context,
        solution=solution
    )
    
    return service.add_learning(item)


def add_learning(title: str, content: str, learning_type: str = "tip",
                 solution: str = "", tags: List[str] = None, 
                 context: str = "", related_tasks: List[str] = None) -> bool:
    """
    便捷函数：添加学习项（通用版）
    
    Args:
        title: 标题
        content: 内容
        learning_type: 类型 (error, pattern, decision, workaround, tip)
        solution: 解决方案
        tags: 标签列表
        context: 适用场景
        related_tasks: 相关任务列表
    
    Returns:
        是否成功添加
    """
    service = ContextRecoveryService()
    
    item = LearningItem(
        id="",
        title=title,
        content=content,
        learning_type=LearningType(learning_type),
        tags=tags or [],
        context=context,
        solution=solution,
        related_tasks=related_tasks or []
    )
    
    return service.add_learning(item)


def search_learnings(query: str) -> List[Dict]:
    """
    搜索学习库
    
    Args:
        query: 搜索查询
    
    Returns:
        匹配的学习项字典列表
    """
    service = ContextRecoveryService()
    matches = service.search_learnings(query)
    
    return [
        {
            "id": m.learning_item.id,
            "title": m.learning_item.title,
            "type": m.learning_item.learning_type.value,
            "score": m.score,
            "reason": m.match_reason
        }
        for m in matches
    ]


# ============ 命令行接口 ============

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="上下文恢复服务 v2.0")
    parser.add_argument("action", choices=[
        "recover", "quick", "add-learning", "list-learnings", "match", "search", "detect-scene"
    ], help="执行的操作")
    parser.add_argument("--task", "-t", help="当前任务描述")
    parser.add_argument("--title", help="学习项标题")
    parser.add_argument("--content", "-c", help="学习项内容")
    parser.add_argument("--solution", "-s", help="解决方案")
    parser.add_argument("--tags", help="标签（逗号分隔）")
    parser.add_argument("--type", choices=["error", "pattern", "decision", "workaround", "tip"],
                        default="tip", help="学习项类型")
    parser.add_argument("--context", help="适用场景")
    parser.add_argument("--query", "-q", help="搜索查询")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--top-k", type=int, default=5, help="返回结果数量")
    
    args = parser.parse_args()
    
    service = ContextRecoveryService()
    
    if args.action == "recover":
        result = recover_context(args.task or "", verbose=args.verbose)
        if result:
            print(result)
        else:
            print("✅ 无历史上下文需要恢复")
    
    elif args.action == "quick":
        print(quick_recover())
    
    elif args.action == "add-learning":
        if not args.title or not args.content:
            print("❌ 需要提供 --title 和 --content")
            exit(1)
        
        item = LearningItem(
            id="",
            title=args.title,
            content=args.content,
            learning_type=LearningType(args.type),
            tags=args.tags.split(",") if args.tags else [],
            context=args.context or "",
            solution=args.solution or ""
        )
        
        if service.add_learning(item):
            print(f"✅ 学习项已添加: {item.id}")
        else:
            print("❌ 添加失败")
    
    elif args.action == "list-learnings":
        learnings = service.learnings
        print(f"📚 共 {len(learnings)} 条学习记录")
        for item in learnings:
            print(f"  [{service._get_type_emoji(item.learning_type)}] {item.title} ({item.learning_type.value})")
    
    elif args.action == "match":
        if not args.task:
            print("❌ 需要提供 --task")
            exit(1)
        
        matches = service.match_learnings(args.task, top_k=args.top_k)
        print(f"🔍 找到 {len(matches)} 条相关学习项")
        for match in matches:
            print(f"  • {match.learning_item.title} (评分: {match.score:.1f}, 类型: {match.match_type})")
            print(f"    原因: {match.match_reason}")
    
    elif args.action == "search":
        if not args.query:
            print("❌ 需要提供 --query")
            exit(1)
        
        matches = service.search_learnings(args.query)
        print(f"🔍 搜索 '{args.query}' 找到 {len(matches)} 条结果")
        for match in matches:
            print(f"  • {match.learning_item.title} (评分: {match.score:.1f})")
    
    elif args.action == "detect-scene":
        if not args.task:
            print("❌ 需要提供 --task")
            exit(1)
        
        scene = service.detect_scene(args.task)
        if scene:
            print(f"🎯 检测场景: {scene}")
        else:
            print("🤷 未识别到特定场景")
