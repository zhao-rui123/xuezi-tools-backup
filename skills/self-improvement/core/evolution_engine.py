#!/usr/bin/env python3
"""
自我进化系统核心引擎 (Self-Evolution Engine)
整合 unified-memory 和所有自我改进模块，实现真正的自我进化

核心功能：
1. 感知层 - 收集所有交互数据
2. 认知层 - 分析模式、发现问题、识别机会
3. 执行层 - 自动优化、生成建议、持续改进
4. 反馈层 - 验证效果、调整策略
"""

import json
import os
import sys
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict, Counter
import traceback

# 配置
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
SKILLS_DIR = WORKSPACE / "skills"
SELF_IMPROVE_DIR = SKILLS_DIR / "self-improvement"
UMS_DIR = SKILLS_DIR / "unified-memory"

# 确保目录存在
EVOLUTION_DATA_DIR = MEMORY_DIR / "evolution"
EVOLUTION_DATA_DIR.mkdir(parents=True, exist_ok=True)

# 数据文件
EVOLUTION_STATE_FILE = EVOLUTION_DATA_DIR / "evolution_state.json"
EVOLUTION_LOG_FILE = EVOLUTION_DATA_DIR / "evolution_log.json"
OPTIMIZATION_QUEUE_FILE = EVOLUTION_DATA_DIR / "optimization_queue.json"
LEARNING_PATTERNS_FILE = EVOLUTION_DATA_DIR / "learning_patterns.json"


@dataclass
class EvolutionState:
    """进化状态"""
    version: str = "1.0.0"
    last_update: str = field(default_factory=lambda: datetime.now().isoformat())
    total_interactions: int = 0
    total_improvements: int = 0
    active_optimizations: List[str] = field(default_factory=list)
    learned_patterns: int = 0
    performance_score: float = 100.0  # 0-100
    evolution_level: str = "initial"  # initial, learning, adapting, optimizing, self-aware


@dataclass
class InteractionRecord:
    """交互记录"""
    timestamp: str
    session_id: str
    query: str
    response_time_ms: int
    tokens_in: int
    tokens_out: int
    tools_used: List[str]
    success: bool
    error_type: Optional[str]
    topics: List[str]
    user_feedback: Optional[str] = None


@dataclass
class LearningPattern:
    """学习到的模式"""
    id: str
    pattern_type: str  # error, optimization, preference, behavior
    trigger: str
    condition: str
    action: str
    confidence: float  # 0-1
    occurrences: int
    first_seen: str
    last_seen: str
    examples: List[str]
    applied_count: int = 0


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    id: str
    category: str  # performance, accuracy, efficiency, user_experience
    title: str
    description: str
    impact_score: float  # 0-1
    effort_score: float  # 0-1
    priority: int  # 1-5
    auto_applicable: bool
    status: str = "pending"  # pending, approved, applied, rejected
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class SelfEvolutionEngine:
    """
    自我进化引擎
    整合所有模块，实现真正的自我进化
    """
    
    def __init__(self):
        self.state = self._load_state()
        self.ums_available = self._check_ums()
        self.recall = None
        self.analyzer = None
        self._init_ums()
        
    def _check_ums(self) -> bool:
        """检查 unified-memory 是否可用"""
        sys.path.insert(0, str(UMS_DIR))
        try:
            import unified_memory
            return True
        except ImportError:
            return False
    
    def _init_ums(self):
        """初始化 unified-memory 组件"""
        if self.ums_available:
            try:
                from unified_memory import EnhancedRecall, MemoryAnalyzer
                self.recall = EnhancedRecall()
                self.analyzer = MemoryAnalyzer()
                print("✅ Unified Memory System 已连接")
            except Exception as e:
                print(f"⚠️ UMS 初始化失败: {e}")
    
    def _load_state(self) -> EvolutionState:
        """加载进化状态"""
        if EVOLUTION_STATE_FILE.exists():
            try:
                with open(EVOLUTION_STATE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return EvolutionState(**data)
            except:
                pass
        return EvolutionState()
    
    def _save_state(self):
        """保存进化状态"""
        with open(EVOLUTION_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.state), f, ensure_ascii=False, indent=2)
    
    def record_interaction(self, query: str, response_time_ms: int,
                          tokens_in: int, tokens_out: int,
                          tools_used: List[str], success: bool = True,
                          error_type: Optional[str] = None) -> str:
        """
        记录一次交互，这是自我进化的基础数据源
        
        Args:
            query: 用户查询
            response_time_ms: 响应时间（毫秒）
            tokens_in: 输入token数
            tokens_out: 输出token数
            tools_used: 使用的工具列表
            success: 是否成功
            error_type: 错误类型（如果有）
            
        Returns:
            record_id: 记录ID
        """
        self.state.total_interactions += 1
        
        # 提取主题
        topics = self._extract_topics(query)
        
        # 创建记录
        record = InteractionRecord(
            timestamp=datetime.now().isoformat(),
            session_id=os.environ.get('OPENCLAW_SESSION', 'unknown'),
            query=query,
            response_time_ms=response_time_ms,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            tools_used=tools_used,
            success=success,
            error_type=error_type,
            topics=topics
        )
        
        # 保存到进化日志
        self._append_to_evolution_log(record)
        
        # 同步到 unified-memory
        if self.recall:
            memory_text = f"[交互记录] 查询: {query[:100]}...\n"
            memory_text += f"主题: {', '.join(topics)}\n"
            memory_text += f"耗时: {response_time_ms}ms, Token: {tokens_in}+{tokens_out}"
            
            importance = 0.6 if success else 0.9  # 失败记录更重要
            self.recall.store(memory_text, category="interaction", importance=importance)
        
        # 实时分析
        self._realtime_analysis(record)
        
        # 更新状态
        self._update_performance_score(record)
        self._save_state()
        
        return f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _extract_topics(self, text: str) -> List[str]:
        """从文本中提取主题"""
        topics = []
        
        # 技术主题
        tech_patterns = {
            "储能": ["储能", "电站", "锂电池", "PCS", "BMS", "光伏"],
            "股票": ["股票", "股市", "K线", "均线", "财报", "行情"],
            "开发": ["开发", "代码", "编程", "API", "技能包", "系统"],
            "记忆": ["记忆", "知识", "备份", "存储", "检索"],
            "部署": ["部署", "服务器", "上线", "网站", "nginx"],
            "数据分析": ["数据", "分析", "统计", "图表", "报表"]
        }
        
        for topic, keywords in tech_patterns.items():
            if any(kw in text for kw in keywords):
                topics.append(topic)
        
        return topics[:5]
    
    def _append_to_evolution_log(self, record: InteractionRecord):
        """追加到进化日志"""
        log_entry = asdict(record)
        
        logs = []
        if EVOLUTION_LOG_FILE.exists():
            try:
                with open(EVOLUTION_LOG_FILE, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                pass
        
        logs.append(log_entry)
        
        # 只保留最近 10000 条
        logs = logs[-10000:]
        
        with open(EVOLUTION_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    def _realtime_analysis(self, record: InteractionRecord):
        """实时分析交互记录，发现问题和机会"""
        # 检测慢响应
        if record.response_time_ms > 5000:
            self._create_optimization_suggestion(
                category="performance",
                title="响应时间优化",
                description=f"检测到响应时间 {record.response_time_ms}ms，建议优化工具调用",
                impact=0.7,
                effort=0.5
            )
        
        # 检测高token使用
        total_tokens = record.tokens_in + record.tokens_out
        if total_tokens > 5000:
            self._create_optimization_suggestion(
                category="efficiency",
                title="Token使用优化",
                description=f"单次交互使用 {total_tokens} tokens，建议精简上下文",
                impact=0.6,
                effort=0.4
            )
        
        # 检测错误
        if not record.success and record.error_type:
            self._learn_from_error(record)
    
    def _learn_from_error(self, record: InteractionRecord):
        """从错误中学习"""
        pattern_id = f"err_{hashlib.md5(record.error_type.encode()).hexdigest()[:8]}"
        
        # 加载现有模式
        patterns = self._load_learning_patterns()
        
        # 查找或创建模式
        if pattern_id in patterns:
            pattern = patterns[pattern_id]
            pattern.occurrences += 1
            pattern.last_seen = datetime.now().isoformat()
            pattern.examples.append(record.query[:100])
            pattern.examples = pattern.examples[-5:]  # 保留最近5个例子
            
            # 提高置信度
            pattern.confidence = min(0.95, pattern.confidence + 0.05)
        else:
            pattern = LearningPattern(
                id=pattern_id,
                pattern_type="error",
                trigger=record.query[:100],
                condition=f"遇到错误: {record.error_type}",
                action="记录并避免重复",
                confidence=0.5,
                occurrences=1,
                first_seen=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat(),
                examples=[record.query[:100]]
            )
            patterns[pattern_id] = pattern
            self.state.learned_patterns += 1
        
        self._save_learning_patterns(patterns)
        
        # 存储到 unified-memory
        if self.recall:
            memory_text = f"[错误学习] {record.error_type}\n"
            memory_text += f"触发: {record.query[:100]}\n"
            memory_text += f"模式ID: {pattern_id}"
            self.recall.store(memory_text, category="error_learning", importance=0.9)
    
    def _load_learning_patterns(self) -> Dict[str, LearningPattern]:
        """加载学习模式"""
        if LEARNING_PATTERNS_FILE.exists():
            try:
                with open(LEARNING_PATTERNS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {k: LearningPattern(**v) for k, v in data.items()}
            except:
                pass
        return {}
    
    def _save_learning_patterns(self, patterns: Dict[str, LearningPattern]):
        """保存学习模式"""
        data = {k: asdict(v) for k, v in patterns.items()}
        with open(LEARNING_PATTERNS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _create_optimization_suggestion(self, category: str, title: str,
                                        description: str, impact: float, effort: float):
        """创建优化建议"""
        suggestion_id = f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        suggestion = OptimizationSuggestion(
            id=suggestion_id,
            category=category,
            title=title,
            description=description,
            impact_score=impact,
            effort_score=effort,
            priority=int((impact * 0.7 + (1 - effort) * 0.3) * 5),
            auto_applicable=(effort < 0.3)  # 低工作量可以自动应用
        )
        
        # 加载队列
        queue = []
        if OPTIMIZATION_QUEUE_FILE.exists():
            try:
                with open(OPTIMIZATION_QUEUE_FILE, 'r', encoding='utf-8') as f:
                    queue = json.load(f)
            except:
                pass
        
        # 避免重复建议
        existing = [s for s in queue if s.get('title') == title and s.get('status') == 'pending']
        if not existing:
            queue.append(asdict(suggestion))
            
            with open(OPTIMIZATION_QUEUE_FILE, 'w', encoding='utf-8') as f:
                json.dump(queue, f, ensure_ascii=False, indent=2)
            
            self.state.active_optimizations.append(suggestion_id)
    
    def _update_performance_score(self, record: InteractionRecord):
        """更新性能评分"""
        # 基础分
        score = 100.0
        
        # 响应时间惩罚
        if record.response_time_ms > 3000:
            score -= (record.response_time_ms - 3000) / 100
        
        # Token效率惩罚
        token_efficiency = record.tokens_out / max(record.tokens_in, 1)
        if token_efficiency > 2:  # 输出token过多
            score -= (token_efficiency - 2) * 5
        
        # 失败惩罚
        if not record.success:
            score -= 20
        
        # 平滑更新
        self.state.performance_score = self.state.performance_score * 0.9 + max(0, score) * 0.1
    
    def get_relevant_learnings(self, query: str) -> List[LearningPattern]:
        """
        获取与当前查询相关的学习经验
        
        Args:
            query: 当前查询
            
        Returns:
            相关的学习模式列表
        """
        patterns = self._load_learning_patterns()
        
        # 按相关度排序
        relevant = []
        for pattern in patterns.values():
            # 简单文本匹配
            score = 0
            for example in pattern.examples:
                # 计算词汇重叠
                query_words = set(query.lower().split())
                example_words = set(example.lower().split())
                overlap = len(query_words & example_words)
                score = max(score, overlap / max(len(query_words), 1))
            
            if score > 0.3:  # 阈值
                relevant.append((pattern, score * pattern.confidence))
        
        # 按得分排序
        relevant.sort(key=lambda x: x[1], reverse=True)
        
        return [p for p, _ in relevant[:5]]
    
    def generate_evolution_report(self, period: str = "daily") -> str:
        """
        生成进化报告
        
        Args:
            period: 周期 (daily, weekly, monthly)
            
        Returns:
            报告文件路径
        """
        if period == "daily":
            days = 1
            title = "每日进化报告"
        elif period == "weekly":
            days = 7
            title = "每周进化报告"
        else:
            days = 30
            title = "每月进化报告"
        
        # 加载日志
        logs = []
        if EVOLUTION_LOG_FILE.exists():
            try:
                with open(EVOLUTION_LOG_FILE, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                pass
        
        # 筛选时间范围
        cutoff = datetime.now() - timedelta(days=days)
        recent_logs = [
            l for l in logs 
            if datetime.fromisoformat(l['timestamp']) > cutoff
        ]
        
        # 统计数据
        total = len(recent_logs)
        success_count = sum(1 for l in recent_logs if l['success'])
        failed_count = total - success_count
        avg_response_time = sum(l['response_time_ms'] for l in recent_logs) / total if total else 0
        total_tokens = sum(l['tokens_in'] + l['tokens_out'] for l in recent_logs)
        
        # 生成报告
        report = f"""# {title}

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 进化等级: {self.state.evolution_level}
> 性能评分: {self.state.performance_score:.1f}/100

## 📊 核心指标

| 指标 | 数值 | 变化 |
|------|------|------|
| 总交互数 | {total} | - |
| 成功率 | {success_count}/{total} ({success_count/total*100:.1f}%) | - |
| 平均响应 | {avg_response_time:.0f}ms | - |
| Token使用 | {total_tokens:,} | - |
| 学习模式 | {self.state.learned_patterns} | - |

## 🧠 学习成果

### 已识别模式
"""
        
        patterns = self._load_learning_patterns()
        for pattern in list(patterns.values())[-5:]:
            report += f"\n**{pattern.pattern_type.upper()}**: {pattern.condition}\n"
            report += f"- 置信度: {pattern.confidence:.0%}\n"
            report += f"- 发生次数: {pattern.occurrences}\n"
        
        # 优化建议
        report += "\n## 🔧 优化建议\n"
        
        queue = []
        if OPTIMIZATION_QUEUE_FILE.exists():
            try:
                with open(OPTIMIZATION_QUEUE_FILE, 'r', encoding='utf-8') as f:
                    queue = json.load(f)
            except:
                pass
        
        pending = [s for s in queue if s.get('status') == 'pending'][:5]
        if pending:
            for s in pending:
                report += f"\n**{s['title']}** (优先级: {s['priority']}/5)\n"
                report += f"- {s['description']}\n"
        else:
            report += "\n暂无待处理优化建议\n"
        
        # 热门主题
        report += "\n## 📈 热门主题\n"
        all_topics = []
        for l in recent_logs:
            all_topics.extend(l.get('topics', []))
        
        topic_counts = Counter(all_topics).most_common(5)
        for topic, count in topic_counts:
            report += f"- {topic}: {count} 次\n"
        
        # 保存报告
        report_file = EVOLUTION_DATA_DIR / f"report_{period}_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return str(report_file)
    
    def apply_pending_optimizations(self) -> List[str]:
        """
        自动应用待处理的优化建议
        
        Returns:
            已应用的优化ID列表
        """
        applied = []
        
        queue = []
        if OPTIMIZATION_QUEUE_FILE.exists():
            try:
                with open(OPTIMIZATION_QUEUE_FILE, 'r', encoding='utf-8') as f:
                    queue = json.load(f)
            except:
                pass
        
        for suggestion in queue:
            if suggestion.get('status') == 'pending' and suggestion.get('auto_applicable'):
                # 这里可以实现具体的自动优化逻辑
                # 比如：调整配置、更新缓存等
                
                suggestion['status'] = 'applied'
                suggestion['applied_at'] = datetime.now().isoformat()
                applied.append(suggestion['id'])
                self.state.total_improvements += 1
        
        with open(OPTIMIZATION_QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        
        self._save_state()
        
        return applied
    
    def evolve(self) -> Dict:
        """
        执行一次完整的自我进化循环
        
        Returns:
            进化结果
        """
        print("🧬 启动自我进化...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "actions": []
        }
        
        # 1. 生成报告
        report_file = self.generate_evolution_report("daily")
        results["actions"].append(f"生成报告: {report_file}")
        
        # 2. 应用自动优化
        applied = self.apply_pending_optimizations()
        if applied:
            results["actions"].append(f"应用优化: {len(applied)} 项")
        
        # 3. 更新进化等级
        self._update_evolution_level()
        
        # 4. 同步到 unified-memory
        if self.recall:
            summary = f"[自我进化] 完成 {len(results['actions'])} 项操作\n"
            summary += f"当前等级: {self.state.evolution_level}\n"
            summary += f"性能评分: {self.state.performance_score:.1f}"
            self.recall.store(summary, category="evolution", importance=0.8)
        
        self._save_state()
        
        print(f"✅ 自我进化完成，当前等级: {self.state.evolution_level}")
        
        return results
    
    def _update_evolution_level(self):
        """更新进化等级"""
        score = 0
        
        # 基于交互数
        if self.state.total_interactions > 1000:
            score += 2
        elif self.state.total_interactions > 100:
            score += 1
        
        # 基于学习模式数
        if self.state.learned_patterns > 20:
            score += 2
        elif self.state.learned_patterns > 5:
            score += 1
        
        # 基于性能评分
        if self.state.performance_score > 90:
            score += 2
        elif self.state.performance_score > 70:
            score += 1
        
        # 基于改进次数
        if self.state.total_improvements > 10:
            score += 1
        
        # 确定等级
        levels = ["initial", "learning", "adapting", "optimizing", "self-aware"]
        self.state.evolution_level = levels[min(score, 4)]


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自我进化系统")
    parser.add_argument("action", choices=[
        "evolve", "report", "status", "learn", "optimize"
    ])
    parser.add_argument("--period", default="daily", choices=["daily", "weekly", "monthly"])
    
    args = parser.parse_args()
    
    engine = SelfEvolutionEngine()
    
    if args.action == "evolve":
        results = engine.evolve()
        print(f"\n进化结果:")
        for action in results["actions"]:
            print(f"  ✓ {action}")
    
    elif args.action == "report":
        report_file = engine.generate_evolution_report(args.period)
        print(f"✅ 报告已生成: {report_file}")
    
    elif args.action == "status":
        print(f"🧬 自我进化状态")
        print(f"  版本: {engine.state.version}")
        print(f"  等级: {engine.state.evolution_level}")
        print(f"  交互数: {engine.state.total_interactions}")
        print(f"  学习模式: {engine.state.learned_patterns}")
        print(f"  性能评分: {engine.state.performance_score:.1f}/100")
        print(f"  改进次数: {engine.state.total_improvements}")
    
    elif args.action == "optimize":
        applied = engine.apply_pending_optimizations()
        print(f"✅ 已应用 {len(applied)} 项优化")


if __name__ == "__main__":
    main()
