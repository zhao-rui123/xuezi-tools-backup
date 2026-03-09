#!/usr/bin/env python3
"""
自我进化触发器 (Evolution Triggers)
自动触发自我进化的各种事件
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from evolution_engine import SelfEvolutionEngine

TRIGGER_LOG = Path("/Users/zhaoruicn/.openclaw/workspace/memory/evolution/trigger_log.json")
TRIGGER_STATE = Path("/Users/zhaoruicn/.openclaw/workspace/memory/evolution/trigger_state.json")


def log_trigger(trigger_type: str, details: dict):
    """记录触发事件"""
    logs = []
    if TRIGGER_LOG.exists():
        try:
            with open(TRIGGER_LOG, 'r') as f:
                logs = json.load(f)
        except:
            pass
    
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "type": trigger_type,
        "details": details
    })
    
    # 保留最近1000条
    logs = logs[-1000:]
    
    with open(TRIGGER_LOG, 'w') as f:
        json.dump(logs, f, indent=2)


def on_conversation_end(query: str, response_time_ms: int,
                        tokens_in: int, tokens_out: int,
                        tools_used: list, success: bool = True,
                        error_type: str = None):
    """
    对话结束时触发
    
    使用方式:
    from evolution_triggers import on_conversation_end
    on_conversation_end(
        query="用户查询",
        response_time_ms=2500,
        tokens_in=1500,
        tokens_out=800,
        tools_used=["read", "write"],
        success=True
    )
    """
    engine = SelfEvolutionEngine()
    
    record_id = engine.record_interaction(
        query=query,
        response_time_ms=response_time_ms,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        tools_used=tools_used,
        success=success,
        error_type=error_type
    )
    
    log_trigger("conversation_end", {
        "record_id": record_id,
        "response_time": response_time_ms,
        "success": success
    })
    
    return record_id


def on_error_occurred(error_type: str, context: str, solution: str = None):
    """
    错误发生时触发
    
    使用方式:
    from evolution_triggers import on_error_occurred
    on_error_occurred(
        error_type="API超时",
        context="调用股票API时超时",
        solution="添加重试机制"
    )
    """
    # 加载自我改进模块
    sys.path.insert(0, str(Path(__file__).parent.parent))
    try:
        from self_improvement import record_error
        record_error(context, error_type, solution or "待解决")
    except:
        pass
    
    log_trigger("error", {
        "error_type": error_type,
        "context": context[:100]
    })


def on_daily_evolution():
    """
    每日自我进化触发（由cron调用）
    
    crontab:
    0 23 * * * /usr/bin/python3 ~/.openclaw/workspace/skills/self-improvement/triggers/evolution_triggers.py daily
    """
    print("🧬 执行每日自我进化...")
    
    engine = SelfEvolutionEngine()
    results = engine.evolve()
    
    print(f"✅ 完成 {len(results['actions'])} 项进化操作")
    
    log_trigger("daily_evolution", {
        "actions_count": len(results['actions']),
        "evolution_level": engine.state.evolution_level
    })
    
    return results


def on_weekly_review():
    """
    每周回顾触发
    
    crontab:
    0 22 * * 0 /usr/bin/python3 ~/.openclaw/workspace/skills/self-improvement/triggers/evolution_triggers.py weekly
    """
    print("📊 执行每周进化回顾...")
    
    engine = SelfEvolutionEngine()
    report_file = engine.generate_evolution_report("weekly")
    
    print(f"✅ 周报已生成: {report_file}")
    
    # 同时生成长期规划报告
    sys.path.insert(0, str(Path(__file__).parent.parent))
    try:
        from long_term_planner import LongTermPlanner
        planner = LongTermPlanner()
        planner.generate_progress_report("weekly")
    except:
        pass
    
    log_trigger("weekly_review", {
        "report_file": report_file
    })
    
    return report_file


def on_monthly_analysis():
    """
    每月深度分析触发
    
    crontab:
    0 8 1 * * /usr/bin/python3 ~/.openclaw/workspace/skills/self-improvement/triggers/evolution_triggers.py monthly
    """
    print("🧠 执行每月深度分析...")
    
    engine = SelfEvolutionEngine()
    report_file = engine.generate_evolution_report("monthly")
    
    # 触发统一记忆的月度分析
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'unified-memory'))
    try:
        from unified_memory import MemoryAnalyzer
        analyzer = MemoryAnalyzer()
        analyzer.analyze_monthly()
    except:
        pass
    
    print(f"✅ 月报已生成: {report_file}")
    
    log_trigger("monthly_analysis", {
        "report_file": report_file
    })
    
    return report_file


def on_skill_usage(skill_name: str, duration_ms: int, success: bool):
    """
    技能包使用时触发
    
    用于追踪哪些技能最常用、哪些需要优化
    """
    log_trigger("skill_usage", {
        "skill": skill_name,
        "duration": duration_ms,
        "success": success
    })


def get_learning_advice(query: str) -> str:
    """
    获取学习建议（在回答用户前调用）
    
    使用方式:
    from evolution_triggers import get_learning_advice
    advice = get_learning_advice("用户查询")
    if advice:
        print(f"💡 根据经验: {advice}")
    """
    engine = SelfEvolutionEngine()
    patterns = engine.get_relevant_learnings(query)
    
    if not patterns:
        return None
    
    # 返回最相关的一条建议
    best = patterns[0]
    return f"根据之前的经验（{best.occurrences}次类似情况）: {best.action}"


def main():
    """命令行入口（供cron调用）"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自我进化触发器")
    parser.add_argument("trigger", choices=["daily", "weekly", "monthly", "status"])
    
    args = parser.parse_args()
    
    if args.trigger == "daily":
        on_daily_evolution()
    elif args.trigger == "weekly":
        on_weekly_review()
    elif args.trigger == "monthly":
        on_monthly_analysis()
    elif args.trigger == "status":
        engine = SelfEvolutionEngine()
        print(f"🧬 进化等级: {engine.state.evolution_level}")
        print(f"📊 性能评分: {engine.state.performance_score:.1f}")
        print(f"🧠 学习模式: {engine.state.learned_patterns}")


if __name__ == "__main__":
    main()
