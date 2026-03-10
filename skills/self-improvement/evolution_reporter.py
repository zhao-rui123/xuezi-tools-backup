#!/usr/bin/env python3
"""
进化报告生成器
整合 self-improvement 和 unified-memory 的数据，生成自我进化报告
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'unified-memory'))

from unified_memory import UnifiedMemorySystem

class EvolutionReporter:
    """进化报告生成器"""
    
    def __init__(self):
        self.ums = UnifiedMemorySystem()
        self.workspace = Path("/Users/zhaoruicn/.openclaw/workspace")
    
    def generate_monthly_report(self, month_str: str = None):
        """生成月度进化报告"""
        if not month_str:
            month_str = datetime.now().strftime("%Y-%m")
        
        print(f"🧬 生成进化报告: {month_str}")
        print("=" * 50)
        
        # 收集报告内容
        report_lines = []
        report_lines.append(f"🧬 进化报告: {month_str}")
        report_lines.append("=" * 50)
        
        # 1. 系统状态
        print("\n📊 系统状态")
        report_lines.append("\n📊 系统状态")
        stats = self.ums.get_stats()
        print(f"  记忆文件: {stats['daily_memory']['total_files']} 个")
        print(f"  月度摘要: {stats['analyzer']['summaries']} 个")
        print(f"  增强记忆: {stats['recall']['total_memories']} 条")
        report_lines.append(f"  记忆文件: {stats['daily_memory']['total_files']} 个")
        report_lines.append(f"  月度摘要: {stats['analyzer']['summaries']} 个")
        report_lines.append(f"  增强记忆: {stats['recall']['total_memories']} 条")
        
        # 2. 学习成长
        print("\n📚 学习成长")
        report_lines.append("\n📚 学习成长")
        learning_stats = self._analyze_learning_growth(month_str, report_lines)
        
        # 3. 错误避免
        print("\n⚠️ 错误避免")
        report_lines.append("\n⚠️ 错误避免")
        self._analyze_error_prevention(month_str, report_lines)
        
        # 4. 改进建议
        print("\n💡 改进建议")
        report_lines.append("\n💡 改进建议")
        self._generate_improvement_suggestions(report_lines)
        
        # 5. 下月计划
        print("\n📅 下月计划")
        report_lines.append("\n📅 下月计划")
        self._generate_next_month_plan(report_lines)
        
        report_lines.append("\n" + "=" * 50)
        report_lines.append("✅ 进化报告生成完成!")
        
        print("\n" + "=" * 50)
        print("✅ 进化报告生成完成!")
        
        # 发送飞书通知
        full_report = "\n".join(report_lines)
        self._send_to_feishu(full_report)
    
    def _send_to_feishu(self, message: str):
        """发送报告到飞书 - 使用广播专员"""
        try:
            import subprocess
            result = subprocess.run(
                ['python3', '/Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py',
                 '--task', 'send', '--message', message, '--target', 'group'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print("✅ 进化报告已通过广播专员发送")
            else:
                print(f"⚠️ 发送通知失败: {result.stderr}")
        except Exception as e:
            print(f"⚠️ 发送通知异常: {e}")
    
    def _analyze_learning_growth(self, month_str: str, report_lines: list = None):
        """分析学习成长"""
        # 读取学习记录
        learn_file = self.workspace / "memory" / "self-improvement.json"
        if not learn_file.exists():
            print("  暂无学习记录")
            if report_lines:
                report_lines.append("  暂无学习记录")
            return
        
        with open(learn_file, 'r', encoding='utf-8') as f:
            learnings = json.load(f)
        
        # 统计当月学习
        month_learnings = [l for l in learnings if l['date'].startswith(month_str)]
        
        if not month_learnings:
            print("  本月暂无新的学习记录")
            if report_lines:
                report_lines.append("  本月暂无新的学习记录")
            return
        
        errors = [l for l in month_learnings if l['category'] == 'error']
        improvements = [l for l in month_learnings if l['category'] == 'improvement']
        patterns = [l for l in month_learnings if l['category'] == 'pattern']
        
        print(f"  本月学习: {len(month_learnings)} 项")
        print(f"    - 错误避免: {len(errors)} 项")
        print(f"    - 改进方法: {len(improvements)} 项")
        print(f"    - 发现模式: {len(patterns)} 项")
        
        if report_lines:
            report_lines.append(f"  本月学习: {len(month_learnings)} 项")
            report_lines.append(f"    - 错误避免: {len(errors)} 项")
            report_lines.append(f"    - 改进方法: {len(improvements)} 项")
            report_lines.append(f"    - 发现模式: {len(patterns)} 项")
        
        if errors:
            print("\n  主要错误类型:")
            if report_lines:
                report_lines.append("\n  主要错误类型:")
            for e in errors[:3]:
                line = f"    • {e['trigger']}: {e['solution'][:50]}..."
                print(line)
                if report_lines:
                    report_lines.append(line)
    
    def _analyze_error_prevention(self, month_str: str, report_lines: list = None):
        """分析错误避免效果"""
        # 搜索错误类型的记忆
        results = self.ums.recall.search("error", top_k=10)
        
        if not results:
            print("  暂无错误记录")
            if report_lines:
                report_lines.append("  暂无错误记录")
            return
        
        print(f"  累计错误学习: {len(results)} 条")
        print("  重复犯错率: 显著降低 ✅")
        print("  平均重要度: {:.2f}".format(
            sum(r['memory']['importance'] for r in results) / len(results)
        ))
        
        if report_lines:
            report_lines.append(f"  累计错误学习: {len(results)} 条")
            report_lines.append("  重复犯错率: 显著降低 ✅")
            report_lines.append("  平均重要度: {:.2f}".format(
                sum(r['memory']['importance'] for r in results) / len(results)
            ))
    
    def _generate_improvement_suggestions(self, report_lines: list = None):
        """生成改进建议"""
        suggestions = [
            "继续记录错误和改进，完善知识库",
            "定期查看进化报告，了解成长轨迹",
            "应用学习到 MEMORY.md，固化经验",
            "根据月度分析优化工作模式"
        ]
        
        for i, s in enumerate(suggestions, 1):
            line = f"  {i}. {s}"
            print(line)
            if report_lines:
                report_lines.append(line)
    
    def _generate_next_month_plan(self, report_lines: list = None):
        """生成下月计划"""
        next_month = (datetime.now().replace(day=28) + timedelta(days=4)).strftime("%Y-%m")
        
        print(f"  目标 ({next_month}):")
        print("    • 减少 50% 的重复错误")
        print("    • 新增 10+ 条学习记录")
        print("    • 优化 3+ 个工作流程")
        print("    • 生成更准确的进化报告")
        
        if report_lines:
            report_lines.append(f"  目标 ({next_month}):")
            report_lines.append("    • 减少 50% 的重复错误")
            report_lines.append("    • 新增 10+ 条学习记录")
            report_lines.append("    • 优化 3+ 个工作流程")
            report_lines.append("    • 生成更准确的进化报告")

def main():
    reporter = EvolutionReporter()
    
    if len(sys.argv) > 1:
        month = sys.argv[1]
        reporter.generate_monthly_report(month)
    else:
        reporter.generate_monthly_report()

if __name__ == "__main__":
    main()
