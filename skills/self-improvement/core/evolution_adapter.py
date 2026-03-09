#!/usr/bin/env python3
"""
自我进化系统整合适配器 (Evolution Integration Adapter)
连接 unified-memory、self-improvement 和所有相关模块
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# 路径配置
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
SKILLS_DIR = WORKSPACE / "skills"
UMS_DIR = SKILLS_DIR / "unified-memory"
SELF_IMPROVE_DIR = SKILLS_DIR / "self-improvement"

# 添加路径
sys.path.insert(0, str(UMS_DIR))
sys.path.insert(0, str(SELF_IMPROVE_DIR))
sys.path.insert(0, str(SELF_IMPROVE_DIR / 'core'))
sys.path.insert(0, str(SELF_IMPROVE_DIR / 'triggers'))


class EvolutionIntegrationAdapter:
    """
    自我进化系统整合适配器
    统一接口，连接所有模块
    """
    
    def __init__(self):
        self.ums_available = False
        self.recall = None
        self.analyzer = None
        self.knowledge_graph = None
        self.evolution_engine = None
        self.long_term_planner = None
        self.predictive_advisor = None
        
        self._init_modules()
    
    def _init_modules(self):
        """初始化所有模块"""
        # 1. Unified Memory System
        try:
            from unified_memory import EnhancedRecall, MemoryAnalyzer
            self.recall = EnhancedRecall()
            self.analyzer = MemoryAnalyzer()
            self.ums_available = True
            print("✅ Unified Memory System 已连接")
        except Exception as e:
            print(f"⚠️ UMS 未连接: {e}")
        
        # 2. Knowledge Graph
        try:
            from knowledge_graph import KnowledgeGraph
            self.knowledge_graph = KnowledgeGraph()
            print("✅ Knowledge Graph 已连接")
        except Exception as e:
            print(f"⚠️ Knowledge Graph 未连接: {e}")
        
        # 3. Evolution Engine
        try:
            from evolution_engine import SelfEvolutionEngine
            self.evolution_engine = SelfEvolutionEngine()
            print("✅ Evolution Engine 已连接")
        except Exception as e:
            print(f"⚠️ Evolution Engine 未连接: {e}")
        
        # 4. Long Term Planner
        try:
            from long_term_planner import LongTermPlanner
            self.long_term_planner = LongTermPlanner()
            print("✅ Long Term Planner 已连接")
        except Exception as e:
            print(f"⚠️ Long Term Planner 未连接: {e}")
        
        # 5. Predictive Advisor
        try:
            from predictive_advisor import PredictiveAdvisor
            self.predictive_advisor = PredictiveAdvisor()
            print("✅ Predictive Advisor 已连接")
        except Exception as e:
            print(f"⚠️ Predictive Advisor 未连接: {e}")
    
    # ==================== 感知层接口 ====================
    
    def record_interaction(self, query: str, response_time_ms: int,
                          tokens_in: int, tokens_out: int,
                          tools_used: List[str], success: bool = True,
                          error_type: Optional[str] = None):
        """
        记录交互，触发所有相关模块
        
        这是自我进化的入口点，每次对话后调用
        """
        # 1. 记录到进化引擎
        if self.evolution_engine:
            record_id = self.evolution_engine.record_interaction(
                query=query,
                response_time_ms=response_time_ms,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                tools_used=tools_used,
                success=success,
                error_type=error_type
            )
        
        # 2. 存储到 unified-memory
        if self.recall:
            memory_text = f"[对话] {query[:80]}...\n"
            memory_text += f"耗时: {response_time_ms}ms, Token: {tokens_in}+{tokens_out}"
            importance = 0.6 if success else 0.9
            self.recall.store(memory_text, category="conversation", importance=importance)
        
        # 3. 更新知识图谱
        if self.knowledge_graph:
            # 提取主题并添加到图谱
            topics = self._extract_topics(query)
            for topic in topics:
                self.knowledge_graph.add_entity(topic, "topic", {"source": "conversation"})
        
        # 4. 更新长期目标进度（如果相关）
        if self.long_term_planner:
            self._update_goal_progress(query)
        
        return record_id if self.evolution_engine else None
    
    def record_error(self, error_type: str, context: str, solution: str = None):
        """记录错误并学习"""
        # 1. 记录到 self_improvement
        try:
            from self_improvement import record_error
            record_error(context, error_type, solution or "待解决")
        except:
            pass
        
        # 2. 记录到进化引擎
        if self.evolution_engine:
            # 通过 record_interaction 记录为失败交互
            pass
        
        # 3. 存储到 unified-memory
        if self.recall:
            memory_text = f"[错误] {error_type}\n上下文: {context}\n解决方案: {solution or '待解决'}"
            self.recall.store(memory_text, category="error_learning", importance=0.95)
    
    def record_learning(self, category: str, trigger: str, 
                       lesson: str, solution: str):
        """记录学习经验"""
        # 存储到 unified-memory
        if self.recall:
            memory_text = f"[学习] {category}\n触发: {trigger}\n教训: {lesson}\n方案: {solution}"
            self.recall.store(memory_text, category="learning", importance=0.85)
    
    # ==================== 认知层接口 ====================
    
    def analyze_myself(self) -> Dict:
        """
        自我分析
        综合所有模块的数据，生成自我分析报告
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "modules": {}
        }
        
        # 1. 进化引擎状态
        if self.evolution_engine:
            report["modules"]["evolution"] = {
                "level": self.evolution_engine.state.evolution_level,
                "performance_score": self.evolution_engine.state.performance_score,
                "total_interactions": self.evolution_engine.state.total_interactions,
                "learned_patterns": self.evolution_engine.state.learned_patterns
            }
        
        # 2. 知识图谱统计
        if self.knowledge_graph:
            try:
                stats = self.knowledge_graph.get_stats()
                report["modules"]["knowledge_graph"] = stats
            except:
                pass
        
        # 3. 长期目标进度
        if self.long_term_planner:
            try:
                progress = self.long_term_planner.track_progress()
                report["modules"]["long_term_goals"] = progress
            except:
                pass
        
        # 4. 预测建议
        if self.predictive_advisor:
            try:
                predictions = self.predictive_advisor.predict_next_week_focus()
                report["modules"]["predictions"] = predictions
            except:
                pass
        
        return report
    
    def get_insights(self) -> List[str]:
        """
        获取洞察建议
        基于数据分析，生成改进建议
        """
        insights = []
        
        # 1. 性能洞察
        if self.evolution_engine:
            score = self.evolution_engine.state.performance_score
            if score < 70:
                insights.append(f"⚠️ 性能评分较低 ({score:.1f})，建议优化响应速度")
            elif score > 90:
                insights.append(f"✅ 性能优秀 ({score:.1f})，保持当前状态")
        
        # 2. 学习洞察
        if self.evolution_engine and self.evolution_engine.state.learned_patterns > 10:
            insights.append(f"🧠 已学习 {self.evolution_engine.state.learned_patterns} 个模式，建议定期回顾")
        
        # 3. 目标洞察
        if self.long_term_planner:
            try:
                active_goals = [g for g in self.long_term_planner.goals.values() if g.status == "active"]
                if len(active_goals) > 5:
                    insights.append(f"📋 活跃目标过多 ({len(active_goals)})，建议优先完成高优先级任务")
            except:
                pass
        
        return insights
    
    def get_relevant_context(self, query: str) -> str:
        """
        获取与查询相关的上下文
        整合记忆、学习模式、知识图谱
        """
        context_parts = []
        
        # 1. 从 unified-memory 检索
        if self.recall:
            try:
                results = self.recall.search(query, top_k=3)
                if results:
                    context_parts.append("## 相关记忆")
                    for r in results:
                        context_parts.append(f"- {r['memory']['text'][:100]}...")
            except:
                pass
        
        # 2. 从学习模式获取经验
        if self.evolution_engine:
            try:
                patterns = self.evolution_engine.get_relevant_learnings(query)
                if patterns:
                    context_parts.append("## 经验提示")
                    for p in patterns[:2]:
                        context_parts.append(f"- {p.action} (置信度: {p.confidence:.0%})")
            except:
                pass
        
        # 3. 从知识图谱获取关联
        if self.knowledge_graph:
            try:
                # 这里可以添加图谱查询逻辑
                pass
            except:
                pass
        
        return "\n\n".join(context_parts) if context_parts else ""
    
    # ==================== 执行层接口 ====================
    
    def evolve(self) -> Dict:
        """执行一次完整的自我进化"""
        results = {"actions": [], "timestamp": datetime.now().isoformat()}
        
        # 1. 进化引擎执行
        if self.evolution_engine:
            evo_results = self.evolution_engine.evolve()
            results["actions"].extend(evo_results.get("actions", []))
        
        # 2. 长期规划检查
        if self.long_term_planner:
            try:
                self.long_term_planner.track_progress()
                results["actions"].append("更新长期目标进度")
            except:
                pass
        
        # 3. 应用优化建议
        if self.evolution_engine:
            try:
                applied = self.evolution_engine.apply_pending_optimizations()
                if applied:
                    results["actions"].append(f"应用 {len(applied)} 项优化")
            except:
                pass
        
        return results
    
    def optimize_skill(self, skill_name: str) -> bool:
        """优化特定技能包"""
        # 这里可以实现技能包的自动优化逻辑
        # 比如：分析使用频率、识别瓶颈、生成改进建议
        return True
    
    # ==================== 辅助方法 ====================
    
    def _extract_topics(self, text: str) -> List[str]:
        """提取主题"""
        import re
        
        patterns = {
            "储能": ["储能", "电站", "锂电池", "PCS"],
            "股票": ["股票", "股市", "K线", "行情"],
            "开发": ["开发", "代码", "API", "技能包"],
            "记忆": ["记忆", "知识", "备份"],
            "部署": ["部署", "服务器", "nginx"]
        }
        
        topics = []
        for topic, keywords in patterns.items():
            if any(kw in text for kw in keywords):
                topics.append(topic)
        
        return topics
    
    def _update_goal_progress(self, query: str):
        """更新目标进度"""
        # 检查查询是否与某个目标相关
        try:
            for goal in self.long_term_planner.goals.values():
                if goal.status != "active":
                    continue
                
                # 简单的关键词匹配
                if any(kw in query for kw in goal.keywords):
                    # 更新进度
                    pass
        except:
            pass
    
    def generate_full_report(self) -> str:
        """生成完整的自我进化报告"""
        report_lines = ["# 自我进化系统完整报告\n"]
        report_lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 自我分析
        analysis = self.analyze_myself()
        report_lines.append("\n## 📊 模块状态\n")
        for module, data in analysis.get("modules", {}).items():
            report_lines.append(f"\n### {module}\n")
            for key, value in data.items():
                report_lines.append(f"- {key}: {value}\n")
        
        # 洞察建议
        insights = self.get_insights()
        report_lines.append("\n## 💡 洞察建议\n")
        for insight in insights:
            report_lines.append(f"- {insight}\n")
        
        return "".join(report_lines)


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自我进化系统整合适配器")
    parser.add_argument("action", choices=[
        "init", "status", "evolve", "report", "insights"
    ])
    
    args = parser.parse_args()
    
    adapter = EvolutionIntegrationAdapter()
    
    if args.action == "init":
        print("✅ 自我进化系统已初始化")
        print(f"   连接模块数: {sum([adapter.ums_available, adapter.evolution_engine is not None, adapter.long_term_planner is not None])}")
    
    elif args.action == "status":
        analysis = adapter.analyze_myself()
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
    
    elif args.action == "evolve":
        results = adapter.evolve()
        print(f"✅ 进化完成，执行 {len(results['actions'])} 项操作")
        for action in results['actions']:
            print(f"   - {action}")
    
    elif args.action == "report":
        report = adapter.generate_full_report()
        report_file = WORKSPACE / "memory" / "evolution" / f"full_report_{datetime.now().strftime('%Y%m%d')}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 报告已保存: {report_file}")
    
    elif args.action == "insights":
        insights = adapter.get_insights()
        print("💡 洞察建议:")
        for insight in insights:
            print(f"   - {insight}")


if __name__ == "__main__":
    main()
