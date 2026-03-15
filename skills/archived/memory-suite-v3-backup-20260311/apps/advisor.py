#!/usr/bin/env python3
"""
Memory Suite v3 - 决策支持模块 (apps/advisor.py)

从历史决策中提取建议，识别决策模式，提供决策参考。

功能:
1. 从记忆中提取历史决策
2. 查找相似决策案例
3. 提供决策建议和参考
4. 风险评估
5. 决策模板推荐
6. 决策报告生成

作者: 雪子助手
版本: 3.0.0
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass, asdict, field


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('advisor')


@dataclass
class Decision:
    """决策记录数据结构"""
    id: str
    title: str
    context: str
    decision: str
    reasoning: str
    outcome: str  # success, partial, failure, unknown
    date: str
    tags: List[str] = field(default_factory=list)
    related_projects: List[str] = field(default_factory=list)
    lessons: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DecisionSuggestion:
    """决策建议数据结构"""
    type: str
    title: str
    content: str
    reasoning: str
    confidence: float
    action: str
    source_decision_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RiskAssessment:
    """风险评估结果"""
    risk_level: str  # low, medium, high
    risk_factors: List[Dict[str, str]]
    suggestions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DecisionAdvisor:
    """决策支持系统主类"""
    
    def __init__(self, memory_dir: str = None, config: Dict = None):
        """
        初始化决策支持系统
        
        Args:
            memory_dir: 记忆文件目录，默认为 ~/.openclaw/workspace/memory/
            config: 可选的配置字典
        """
        if memory_dir is None:
            memory_dir = os.path.expanduser("~/.openclaw/workspace/memory/")
        self.memory_dir = Path(memory_dir)
        self.config = config or {}
        self.decisions: List[Decision] = []
        self.decision_file = self.memory_dir / "decision_history.json"
        
        # 决策模式库
        self.decision_patterns = {
            "technical_selection": {
                "keywords": ["模型", "API", "技术", "框架", "库", "工具", "方案"],
                "template": "技术选型决策模板"
            },
            "project_management": {
                "keywords": ["项目", "开发", "计划", "排期", "里程碑", "交付"],
                "template": "项目管理决策模板"
            },
            "resource_allocation": {
                "keywords": ["资源", "预算", "成本", "投资", "采购", "设备"],
                "template": "资源分配决策模板"
            },
            "risk_management": {
                "keywords": ["风险", "安全", "备份", "回滚", "应急", "预案"],
                "template": "风险管理决策模板"
            }
        }
        
        logger.info(f"DecisionAdvisor initialized with memory_dir: {self.memory_dir}")
        self._load_decisions()
    
    def _load_decisions(self):
        """加载决策历史"""
        if self.decision_file.exists():
            try:
                with open(self.decision_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.decisions = [
                        Decision(**d) for d in data.get("decisions", [])
                    ]
                logger.info(f"Loaded {len(self.decisions)} decisions from history")
            except Exception as e:
                logger.error(f"Failed to load decision history: {e}")
                self.decisions = []
        else:
            logger.info("No decision history file found, starting fresh")
    
    def _save_decisions(self):
        """保存决策历史"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "decisions": [asdict(d) for d in self.decisions]
            }
            with open(self.decision_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.decisions)} decisions to history")
        except Exception as e:
            logger.error(f"Failed to save decision history: {e}")
    
    def extract_decisions_from_memory(self) -> int:
        """
        从记忆中提取决策
        
        Returns:
            新提取的决策数量
        """
        logger.info("Extracting decisions from memory files...")
        
        new_decisions = 0
        
        if not self.memory_dir.exists():
            logger.warning(f"Memory directory does not exist: {self.memory_dir}")
            return 0
        
        try:
            # 扫描记忆文件
            for file_path in sorted(self.memory_dir.glob("*.md")):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 查找 [DECISION] 区块
                    decision_blocks = re.findall(
                        r'\[DECISION\]\s*(.+?)(?=\n\[|\Z)',
                        content,
                        re.DOTALL
                    )
                    
                    for block in decision_blocks:
                        decision_text = block.strip()
                        if len(decision_text) < 10:
                            continue
                        
                        # 提取日期
                        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', file_path.name)
                        date = date_match.group(0) if date_match else datetime.now().strftime('%Y-%m-%d')
                        
                        # 生成 ID
                        decision_id = f"{date}-{hash(decision_text) % 10000:04d}"
                        
                        # 检查是否已存在
                        if any(d.id == decision_id for d in self.decisions):
                            continue
                        
                        # 解析决策
                        title = decision_text.split('\n')[0][:50]
                        reasoning = ""
                        context = ""
                        lessons = ""
                        
                        # 提取推理过程
                        reasoning_match = re.search(
                            r'(?:原因 | 理由 | 推理)[：:]\s*(.+?)(?=\n|$)',
                            decision_text
                        )
                        if reasoning_match:
                            reasoning = reasoning_match.group(1)
                        
                        # 提取上下文
                        context_match = re.search(
                            r'(?:背景 | 上下文 | 情况)[：:]\s*(.+?)(?=\n|$)',
                            decision_text
                        )
                        if context_match:
                            context = context_match.group(1)
                        
                        # 提取经验教训
                        lessons_match = re.search(
                            r'(?:教训 | 经验 | 反思)[：:]\s*(.+?)(?=\n|$)',
                            decision_text
                        )
                        if lessons_match:
                            lessons = lessons_match.group(1)
                        
                        # 提取标签
                        tags = []
                        tag_matches = re.findall(r'\[([^\]]+)\]', decision_text)
                        tags.extend(tag_matches)
                        
                        # 创建决策记录
                        decision = Decision(
                            id=decision_id,
                            title=title,
                            context=context,
                            decision=decision_text[:500],  # 限制长度
                            reasoning=reasoning,
                            outcome="unknown",  # 需要后续更新
                            date=date,
                            tags=tags,
                            related_projects=[],
                            lessons=lessons
                        )
                        
                        self.decisions.append(decision)
                        new_decisions += 1
                        logger.debug(f"Extracted decision: {decision_id}")
                        
                except Exception as e:
                    logger.error(f"Failed to process file {file_path.name}: {e}")
            
            if new_decisions > 0:
                self._save_decisions()
            
            logger.info(f"Extracted {new_decisions} new decisions")
            return new_decisions
            
        except Exception as e:
            logger.error(f"Error extracting decisions: {e}")
            return 0
    
    def find_similar_decisions(self, context: str, limit: int = 3) -> List[Decision]:
        """
        查找相似决策
        
        Args:
            context: 当前决策上下文描述
            limit: 返回数量限制
            
        Returns:
            相似决策列表
        """
        logger.info(f"Finding similar decisions for context: {context[:100]}...")
        
        if not self.decisions:
            logger.debug("No decisions in history")
            return []
        
        try:
            # 提取关键词
            keywords = self._extract_keywords(context)
            logger.debug(f"Extracted keywords: {keywords[:10]}")
            
            # 计算相似度
            scored = []
            for decision in self.decisions:
                score = 0
                decision_text = f"{decision.title} {decision.decision} {decision.reasoning} {decision.context}"
                
                for keyword in keywords:
                    if keyword.lower() in decision_text.lower():
                        score += 1
                
                # 标签匹配加分
                for tag in decision.tags:
                    if tag.lower() in context.lower():
                        score += 0.5
                
                if score > 0:
                    scored.append((decision, score))
            
            # 排序并返回
            scored.sort(key=lambda x: x[1], reverse=True)
            similar = [d for d, _ in scored[:limit]]
            
            logger.info(f"Found {len(similar)} similar decisions")
            return similar
            
        except Exception as e:
            logger.error(f"Error finding similar decisions: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        提取关键词
        
        Args:
            text: 文本内容
            
        Returns:
            关键词列表
        """
        keywords = []
        
        try:
            # 中文词汇 (2-4 字)
            chinese = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
            keywords.extend(chinese)
            
            # 英文词汇
            english = re.findall(r'[A-Za-z][A-Za-z0-9_]{2,}', text)
            keywords.extend([w.lower() for w in english])
            
            # 去重
            keywords = list(set(keywords))
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
        
        return keywords
    
    def get_decision_suggestions(self, context: str) -> List[DecisionSuggestion]:
        """
        获取决策建议
        
        Args:
            context: 决策上下文
            
        Returns:
            决策建议列表
        """
        logger.info(f"Getting decision suggestions for context: {context[:100]}...")
        
        suggestions = []
        
        try:
            # 1. 查找相似决策
            similar = self.find_similar_decisions(context)
            
            for decision in similar:
                # 根据结果给出建议
                if decision.outcome == "success":
                    suggestion = DecisionSuggestion(
                        type="similar_success",
                        title=f"参考成功决策：{decision.title[:40]}",
                        content=decision.decision[:100],
                        reasoning=decision.reasoning,
                        confidence=0.8,
                        action="该决策在过去取得了成功，可考虑类似方案",
                        source_decision_id=decision.id
                    )
                elif decision.outcome == "failure":
                    suggestion = DecisionSuggestion(
                        type="lesson_learned",
                        title=f"⚠️ 曾失败的类似决策：{decision.title[:40]}",
                        content=decision.decision[:100],
                        reasoning=decision.reasoning,
                        confidence=0.9,
                        action="该决策曾导致失败，建议避免或改进",
                        source_decision_id=decision.id
                    )
                else:
                    suggestion = DecisionSuggestion(
                        type="reference",
                        title=f"相关决策：{decision.title[:40]}",
                        content=decision.decision[:100],
                        reasoning=decision.reasoning,
                        confidence=0.6,
                        action="可参考该决策的思路",
                        source_decision_id=decision.id
                    )
                
                suggestions.append(suggestion)
            
            # 2. 基于常见模式给出建议
            for pattern_name, pattern_info in self.decision_patterns.items():
                if any(kw in context for kw in pattern_info["keywords"]):
                    if pattern_name == "technical_selection":
                        suggestions.append(DecisionSuggestion(
                            type="pattern",
                            title="🔧 技术选型建议",
                            content="根据历史记录，技术选型时应考虑：",
                            reasoning="",
                            confidence=0.7,
                            action="1. 优先使用已验证的方案\n2. 考虑长期维护成本\n3. 测试兼容性\n4. 评估社区支持和文档"
                        ))
                    elif pattern_name == "project_management":
                        suggestions.append(DecisionSuggestion(
                            type="pattern",
                            title="📋 项目管理建议",
                            content="项目启动前建议：",
                            reasoning="",
                            confidence=0.75,
                            action="1. 明确需求和目标\n2. 制定详细计划\n3. 预留缓冲时间\n4. 定期回顾进度\n5. 建立沟通机制"
                        ))
                    elif pattern_name == "resource_allocation":
                        suggestions.append(DecisionSuggestion(
                            type="pattern",
                            title="💰 资源分配建议",
                            content="资源分配时应考虑：",
                            reasoning="",
                            confidence=0.7,
                            action="1. 评估投入产出比\n2. 优先核心需求\n3. 考虑长期成本\n4. 预留应急预算"
                        ))
                    elif pattern_name == "risk_management":
                        suggestions.append(DecisionSuggestion(
                            type="pattern",
                            title="🛡️ 风险管理建议",
                            content="风险管理要点：",
                            reasoning="",
                            confidence=0.8,
                            action="1. 识别潜在风险\n2. 制定应急预案\n3. 建立监控机制\n4. 定期演练"
                        ))
            
        except Exception as e:
            logger.error(f"Error getting decision suggestions: {e}")
        
        return suggestions
    
    def assess_risk(self, decision_context: str) -> RiskAssessment:
        """
        风险评估
        
        Args:
            decision_context: 决策上下文
            
        Returns:
            风险评估结果
        """
        logger.info(f"Assessing risk for: {decision_context[:100]}...")
        
        risk_factors = []
        risk_level = "low"
        
        try:
            # 1. 检查是否有失败先例
            keywords = self._extract_keywords(decision_context)
            similar_failures = [
                d for d in self.decisions
                if d.outcome == "failure" and any(
                    kw.lower() in f"{d.title} {d.decision}".lower()
                    for kw in keywords
                )
            ]
            
            if similar_failures:
                risk_factors.append({
                    "factor": "历史失败先例",
                    "severity": "high",
                    "description": f"发现 {len(similar_failures)} 个类似失败决策"
                })
                risk_level = "high"
            
            # 2. 检查时间因素
            if any(word in decision_context for word in ["立即", "马上", "紧急", "今天必须"]):
                risk_factors.append({
                    "factor": "时间压力",
                    "severity": "medium",
                    "description": "决策时间紧迫，可能考虑不周"
                })
                if risk_level == "low":
                    risk_level = "medium"
            
            # 3. 检查复杂度
            complexity_indicators = ["系统", "架构", "重构", "迁移", "升级", "核心", "生产环境"]
            if any(indicator in decision_context for indicator in complexity_indicators):
                risk_factors.append({
                    "factor": "系统复杂性",
                    "severity": "medium",
                    "description": "涉及系统级变更，风险较高"
                })
                if risk_level == "low":
                    risk_level = "medium"
            
            # 4. 检查影响范围
            scope_indicators = ["全部", "所有", "全局", "整个", "用户", "线上"]
            if any(indicator in decision_context for indicator in scope_indicators):
                risk_factors.append({
                    "factor": "影响范围广",
                    "severity": "medium",
                    "description": "决策影响范围广泛，需谨慎"
                })
                if risk_level == "low":
                    risk_level = "medium"
            
            # 生成建议
            suggestions = []
            if risk_level in ["high", "medium"]:
                suggestions.append("建议制定回滚方案")
            if risk_level == "high":
                suggestions.append("建议小范围测试后再推广")
            if risk_factors:
                suggestions.append("建议咨询有相关经验的人员")
            if not suggestions:
                suggestions.append("风险可控，可执行")
            
        except Exception as e:
            logger.error(f"Error assessing risk: {e}")
            risk_factors.append({
                "factor": "评估错误",
                "severity": "medium",
                "description": str(e)
            })
            suggestions = ["请手动评估风险"]
        
        return RiskAssessment(
            risk_level=risk_level,
            risk_factors=risk_factors,
            suggestions=suggestions
        )
    
    def recommend_templates(self, decision_type: str = "") -> List[Dict]:
        """
        推荐决策模板
        
        Args:
            decision_type: 决策类型（可选）
            
        Returns:
            决策模板列表
        """
        logger.info(f"Recommending templates for type: {decision_type}")
        
        templates = [
            {
                "name": "技术选型决策",
                "template": """### 技术选型决策

**问题**: [描述需要解决的问题]

**方案 A**: [方案描述]
- 优点: 
- 缺点: 
- 风险: 
- 成本估算: 

**方案 B**: [方案描述]
- 优点: 
- 缺点: 
- 风险: 
- 成本估算: 

**决定**: [选择哪个方案]

**原因**: [详细说明决策理由]

**实施计划**: 
- 第一步: 
- 第二步: 
- 时间表: 

**回滚方案**: [如果失败如何回退]
""",
                "tags": ["技术", "选型", "架构"],
                "适用场景": "需要选择技术方案、框架、工具时"
            },
            {
                "name": "项目启动决策",
                "template": """### 项目启动决策

**项目名称**: 

**背景**: [为什么要做这个项目]

**目标**: [明确的项目目标，SMART 原则]

**范围**: [项目边界，包含/不包含什么]

**资源需求**: 
- 人力: 
- 时间: 
- 预算: 
- 设备/工具: 

**风险评估**: 
- 主要风险: 
- 应对措施: 

**成功标准**: [如何判断项目成功]

**决定**: [是否启动]

**下一步**: 
""",
                "tags": ["项目", "启动", "规划"],
                "适用场景": "启动新项目或重大功能前"
            },
            {
                "name": "快速决策",
                "template": """### 快速决策

**情况**: [简要描述当前情况]

**选项**: 
- A: 
- B: 

**决定**: [决策内容]

**原因**: [简要理由，1-2 句话]

**预期结果**: 

**后续跟进**: 
""",
                "tags": ["快速", "简单", "日常"],
                "适用场景": "日常小决策，不需要复杂分析"
            },
            {
                "name": "资源分配决策",
                "template": """### 资源分配决策

**背景**: [资源分配的背景]

**可用资源**: 
- 预算: 
- 人力: 
- 时间: 

**候选项目/需求**: 
1. [项目 1]: 预期收益，成本，优先级
2. [项目 2]: 预期收益，成本，优先级

**评估标准**: 
- ROI
- 战略匹配度
- 紧急程度

**决定**: [如何分配]

**理由**: 
""",
                "tags": ["资源", "预算", "优先级"],
                "适用场景": "需要在多个项目间分配有限资源时"
            },
            {
                "name": "风险评估决策",
                "template": """### 风险评估与决策

**决策内容**: 

**潜在风险**: 
1. [风险 1]: 概率，影响，应对措施
2. [风险 2]: 概率，影响，应对措施

**风险缓解计划**: 
- 预防措施: 
- 监控指标: 
- 应急预案: 

**收益评估**: 

**决定**: [是否执行，如何执行]

**审批**: [需要谁批准]
""",
                "tags": ["风险", "安全", "评估"],
                "适用场景": "高风险决策或需要正式风险评估时"
            }
        ]
        
        # 如果指定了类型，过滤相关模板
        if decision_type:
            filtered = [
                t for t in templates
                if decision_type.lower() in t["name"].lower() or
                   any(decision_type.lower() in tag.lower() for tag in t["tags"])
            ]
            if filtered:
                templates = filtered
        
        return templates
    
    def generate_decision_report(self) -> Dict[str, Any]:
        """
        生成决策报告
        
        Returns:
            决策报告字典
        """
        logger.info("Generating decision report...")
        
        try:
            if not self.decisions:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "summary": {
                        "total_decisions": 0,
                        "success": 0,
                        "failure": 0,
                        "unknown": 0,
                        "success_rate": 0
                    },
                    "message": "暂无决策记录"
                }
            
            # 统计
            total = len(self.decisions)
            success = sum(1 for d in self.decisions if d.outcome == "success")
            failure = sum(1 for d in self.decisions if d.outcome == "failure")
            partial = sum(1 for d in self.decisions if d.outcome == "partial")
            unknown = total - success - failure - partial
            
            # 按月份统计
            monthly = defaultdict(int)
            for d in self.decisions:
                month = d.date[:7] if len(d.date) >= 7 else d.date
                monthly[month] += 1
            
            # 按类别统计
            categories = defaultdict(int)
            for d in self.decisions:
                if d.tags:
                    categories[d.tags[0]] += 1
                else:
                    categories["未分类"] += 1
            
            # 最近决策
            recent = sorted(self.decisions, key=lambda x: x.date, reverse=True)[:10]
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_decisions": total,
                    "success": success,
                    "failure": failure,
                    "partial": partial,
                    "unknown": unknown,
                    "success_rate": round(success / total * 100, 1) if total > 0 else 0
                },
                "monthly_distribution": dict(monthly),
                "category_distribution": dict(categories),
                "recent_decisions": [
                    {
                        "id": d.id,
                        "title": d.title,
                        "date": d.date,
                        "outcome": d.outcome,
                        "tags": d.tags
                    }
                    for d in recent
                ],
                "patterns": self._analyze_patterns()
            }
            
            logger.info(f"Report generated: {total} decisions analyzed")
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "summary": {}
            }
    
    def _analyze_patterns(self) -> List[Dict]:
        """
        分析决策模式
        
        Returns:
            模式分析结果列表
        """
        patterns = []
        
        try:
            if not self.decisions:
                return patterns
            
            # 分析最常见的决策类型
            tag_counts = defaultdict(int)
            for d in self.decisions:
                for tag in d.tags:
                    tag_counts[tag] += 1
            
            if tag_counts:
                top_tags = sorted(tag_counts.items(), key=lambda x: -x[1])[:5]
                patterns.append({
                    "type": "common_topics",
                    "description": "最常见的决策主题",
                    "data": [{"tag": t, "count": c} for t, c in top_tags]
                })
            
            # 分析成功率
            outcome_counts = defaultdict(int)
            for d in self.decisions:
                outcome_counts[d.outcome] += 1
            
            if outcome_counts:
                patterns.append({
                    "type": "outcome_distribution",
                    "description": "决策结果分布",
                    "data": dict(outcome_counts)
                })
            
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
        
        return patterns
    
    def update_decision_outcome(self, decision_id: str, outcome: str, 
                                lessons: str = "") -> bool:
        """
        更新决策结果
        
        Args:
            decision_id: 决策 ID
            outcome: 结果 (success, partial, failure)
            lessons: 经验教训
            
        Returns:
            是否成功更新
        """
        logger.info(f"Updating decision {decision_id} outcome to {outcome}")
        
        try:
            for i, d in enumerate(self.decisions):
                if d.id == decision_id:
                    self.decisions[i].outcome = outcome
                    if lessons:
                        self.decisions[i].lessons = lessons
                    self._save_decisions()
                    logger.info(f"Decision {decision_id} updated successfully")
                    return True
            
            logger.warning(f"Decision {decision_id} not found")
            return False
            
        except Exception as e:
            logger.error(f"Error updating decision: {e}")
            return False
    
    def add_decision(self, title: str, decision: str, reasoning: str = "",
                    context: str = "", tags: List[str] = None) -> str:
        """
        添加新决策记录
        
        Args:
            title: 决策标题
            decision: 决策内容
            reasoning: 推理过程
            context: 背景上下文
            tags: 标签列表
            
        Returns:
            决策 ID
        """
        logger.info(f"Adding new decision: {title}")
        
        try:
            date = datetime.now().strftime('%Y-%m-%d')
            decision_id = f"{date}-{hash(title + decision) % 10000:04d}"
            
            new_decision = Decision(
                id=decision_id,
                title=title,
                context=context,
                decision=decision,
                reasoning=reasoning,
                outcome="unknown",
                date=date,
                tags=tags or [],
                related_projects=[],
                lessons=""
            )
            
            self.decisions.append(new_decision)
            self._save_decisions()
            
            logger.info(f"Decision {decision_id} added successfully")
            return decision_id
            
        except Exception as e:
            logger.error(f"Error adding decision: {e}")
            return ""
    
    def run(self) -> Dict[str, Any]:
        """
        运行决策支持系统（完整流程）
        
        Returns:
            运行结果报告
        """
        logger.info("=" * 60)
        logger.info("Running Decision Support System")
        logger.info("=" * 60)
        
        # 1. 提取历史决策
        new_count = self.extract_decisions_from_memory()
        
        # 2. 生成报告
        report = self.generate_decision_report()
        
        # 3. 打印摘要
        summary = report.get("summary", {})
        logger.info(f"\n决策统计摘要:")
        logger.info(f"  总决策数：{summary.get('total_decisions', 0)}")
        logger.info(f"  成功：{summary.get('success', 0)} 次")
        logger.info(f"  失败：{summary.get('failure', 0)} 次")
        logger.info(f"  成功率：{summary.get('success_rate', 0)}%")
        
        return report


# ============== 模块接口函数 ==============

def get_suggestions(context: str, memory_dir: str = None) -> List[Dict]:
    """
    获取决策建议的便捷函数
    
    Args:
        context: 决策上下文
        memory_dir: 记忆目录
        
    Returns:
        建议列表
    """
    advisor = DecisionAdvisor(memory_dir=memory_dir)
    suggestions = advisor.get_decision_suggestions(context)
    return [s.to_dict() for s in suggestions]


def assess_decision_risk(context: str, memory_dir: str = None) -> Dict:
    """
    评估决策风险的便捷函数
    
    Args:
        context: 决策上下文
        memory_dir: 记忆目录
        
    Returns:
        风险评估结果
    """
    advisor = DecisionAdvisor(memory_dir=memory_dir)
    risk = advisor.assess_risk(context)
    return risk.to_dict()


def find_similar(context: str, limit: int = 3, memory_dir: str = None) -> List[Dict]:
    """
    查找相似决策的便捷函数
    
    Args:
        context: 决策上下文
        limit: 结果数量
        memory_dir: 记忆目录
        
    Returns:
        相似决策列表
    """
    advisor = DecisionAdvisor(memory_dir=memory_dir)
    decisions = advisor.find_similar_decisions(context, limit)
    return [d.to_dict() for d in decisions]


def add_decision_record(title: str, decision: str, reasoning: str = "",
                       context: str = "", tags: List[str] = None,
                       memory_dir: str = None) -> str:
    """
    添加决策记录的便捷函数
    
    Args:
        title: 标题
        decision: 决策内容
        reasoning: 推理
        context: 上下文
        tags: 标签
        memory_dir: 记忆目录
        
    Returns:
        决策 ID
    """
    advisor = DecisionAdvisor(memory_dir=memory_dir)
    return advisor.add_decision(title, decision, reasoning, context, tags)


# ============== 命令行接口 ==============

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Memory Suite Advisor - 决策支持模块",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python advisor.py suggestions "要不要用新的 API 框架？"
  python advisor.py risk "重构核心系统"
  python advisor.py similar "技术选型"
  python advisor.py add --title "选择 API 框架" --decision "使用 FastAPI"
  python advisor.py report
        """
    )
    parser.add_argument("--memory-dir", help="记忆文件目录")
    parser.add_argument("--config", help="配置文件路径 (JSON)")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # suggestions 命令
    sug_parser = subparsers.add_parser("suggestions", help="获取决策建议")
    sug_parser.add_argument("context", help="决策上下文描述")
    sug_parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    
    # risk 命令
    risk_parser = subparsers.add_parser("risk", help="风险评估")
    risk_parser.add_argument("context", help="决策上下文描述")
    risk_parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    
    # similar 命令
    sim_parser = subparsers.add_parser("similar", help="查找相似决策")
    sim_parser.add_argument("context", help="搜索上下文")
    sim_parser.add_argument("-l", "--limit", type=int, default=3, help="结果数量")
    sim_parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    
    # add 命令
    add_parser = subparsers.add_parser("add", help="添加决策记录")
    add_parser.add_argument("--title", required=True, help="决策标题")
    add_parser.add_argument("--decision", required=True, help="决策内容")
    add_parser.add_argument("--reasoning", default="", help="推理过程")
    add_parser.add_argument("--context", default="", help="背景上下文")
    add_parser.add_argument("--tags", nargs="+", help="标签列表")
    
    # report 命令
    report_parser = subparsers.add_parser("report", help="生成决策报告")
    report_parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    
    # extract 命令
    extract_parser = subparsers.add_parser("extract", help="从记忆中提取决策")
    extract_parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 初始化系统
    advisor = DecisionAdvisor(memory_dir=args.memory_dir)
    
    try:
        if args.command == "suggestions":
            suggestions = advisor.get_decision_suggestions(args.context)
            if args.json:
                print(json.dumps([s.to_dict() for s in suggestions], 
                               ensure_ascii=False, indent=2))
            else:
                print(f"💡 决策建议 ({len(suggestions)}条):\n")
                for i, s in enumerate(suggestions, 1):
                    print(f"{i}. {s.title}")
                    print(f"   建议：{s.action}")
                    print(f"   置信度：{s.confidence:.0%}")
                    print()
        
        elif args.command == "risk":
            risk = advisor.assess_risk(args.context)
            if args.json:
                print(json.dumps(risk.to_dict(), ensure_ascii=False, indent=2))
            else:
                print(f"⚠️ 风险等级：{risk.risk_level.upper()}")
                if risk.risk_factors:
                    print("\n风险因素:")
                    for f in risk.risk_factors:
                        print(f"  • {f['factor']}: {f['description']}")
                print("\n建议:")
                for s in risk.suggestions:
                    print(f"  • {s}")
        
        elif args.command == "similar":
            decisions = advisor.find_similar_decisions(args.context, args.limit)
            if args.json:
                print(json.dumps([d.to_dict() for d in decisions], 
                               ensure_ascii=False, indent=2))
            else:
                print(f"📋 相似决策 ({len(decisions)}条):\n")
                for i, d in enumerate(decisions, 1):
                    print(f"{i}. [{d.date}] {d.title}")
                    print(f"   结果：{d.outcome}")
                    print(f"   决策：{d.decision[:100]}...")
                    print()
        
        elif args.command == "add":
            decision_id = advisor.add_decision(
                title=args.title,
                decision=args.decision,
                reasoning=args.reasoning,
                context=args.context,
                tags=args.tags
            )
            print(f"✅ 决策记录已添加: {decision_id}")
        
        elif args.command == "report":
            report = advisor.generate_decision_report()
            if args.json:
                print(json.dumps(report, ensure_ascii=False, indent=2))
            else:
                summary = report.get("summary", {})
                print("📊 决策报告")
                print(f"  总决策数：{summary.get('total_decisions', 0)}")
                print(f"  成功：{summary.get('success', 0)}")
                print(f"  失败：{summary.get('failure', 0)}")
                print(f"  成功率：{summary.get('success_rate', 0)}%")
                
                if report.get("recent_decisions"):
                    print("\n最近决策:")
                    for d in report["recent_decisions"][:5]:
                        outcome_emoji = {
                            "success": "✅", "failure": "❌", 
                            "partial": "⚠️", "unknown": "❓"
                        }.get(d['outcome'], "❓")
                        print(f"  {outcome_emoji} [{d['date']}] {d['title']}")
        
        elif args.command == "extract":
            count = advisor.extract_decisions_from_memory()
            if args.json:
                print(json.dumps({"extracted": count}, ensure_ascii=False))
            else:
                print(f"✅ 提取了 {count} 个新决策")
        
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
