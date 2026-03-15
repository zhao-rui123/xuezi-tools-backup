#!/usr/bin/env python3
"""
Memory Suite v4.0 - 自我进化模块测试
验证 evolution_reporter 和 skill_evaluator 可被 scheduler 调用
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
WORKSPACE = Path("/home/user/workspace")
MEMORY_SUITE_V4 = WORKSPACE / "skills" / "memory-suite-v4"
sys.path.insert(0, str(MEMORY_SUITE_V4))

def test_evolution_reporter():
    """测试进化报告生成器"""
    print("=" * 60)
    print("测试 1: EvolutionReporter")
    print("=" * 60)
    
    try:
        from apps.evolution.evolution_reporter import EvolutionReporter
        
        reporter = EvolutionReporter()
        
        # 测试生成报告（不指定月份，使用默认上个月）
        print("\n📋 测试生成月度报告...")
        report_file = reporter.generate_monthly_report()
        
        if report_file:
            print(f"✅ 报告生成成功：{report_file}")
            return True
        else:
            print("❌ 报告生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_skill_evaluator():
    """测试技能评估器"""
    print("\n" + "=" * 60)
    print("测试 2: SkillEvaluator")
    print("=" * 60)
    
    try:
        from apps.evolution.skill_evaluator import SkillEvaluator
        
        evaluator = SkillEvaluator()
        
        # 测试记录技能使用
        print("\n📝 测试记录技能使用...")
        record_id = evaluator.record_usage(
            skill_name="test_skill",
            action="test_action",
            success=True,
            duration_ms=1500,
            tokens_used=2000
        )
        print(f"✅ 记录成功：{record_id}")
        
        # 测试获取统计
        print("\n📊 测试获取统计数据...")
        stats = evaluator.get_skill_statistics("test_skill")
        if stats:
            print(f"✅ 统计获取成功：{stats.skill_name}, 调用次数：{stats.total_calls}")
        else:
            print("❌ 统计获取失败")
            return False
        
        # 测试评估
        print("\n🔍 测试技能评估...")
        evaluations = evaluator.evaluate_skills(period_days=7)
        print(f"✅ 评估完成：{len(evaluations)} 个技能")
        
        # 测试生成周报告
        print("\n📄 测试生成周报告...")
        report_file = evaluator.generate_weekly_report()
        if report_file:
            print(f"✅ 报告生成成功：{report_file}")
        else:
            print("❌ 报告生成失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_scheduler_integration():
    """测试与 scheduler 的集成"""
    print("\n" + "=" * 60)
    print("测试 3: Scheduler 集成")
    print("=" * 60)
    
    try:
        # 模拟 scheduler 调用
        print("\n🔄 模拟 scheduler 调用 evolution_reporter...")
        from apps.evolution.evolution_reporter import EvolutionReporter
        reporter = EvolutionReporter()
        result = reporter.generate_monthly_report()
        print(f"✅ Scheduler 调用成功")
        
        print("\n🔄 模拟 scheduler 调用 skill_evaluator...")
        from apps.evolution.skill_evaluator import SkillEvaluator
        evaluator = SkillEvaluator()
        result = evaluator.evaluate_skills()
        print(f"✅ Scheduler 调用成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Memory Suite v4.0 - 自我进化模块测试")
    print("=" * 60)
    
    results = {
        "evolution_reporter": test_evolution_reporter(),
        "skill_evaluator": test_skill_evaluator(),
        "scheduler_integration": test_scheduler_integration()
    }
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过!")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
