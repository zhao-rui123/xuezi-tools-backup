#!/usr/bin/env python3
"""
自我改进系统 - 从错误中学习，自动优化
与 unified-memory 联动，实现真正的自我进化
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

# 添加 unified-memory 路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'unified-memory'))

try:
    from unified_memory import EnhancedRecall
    UMS_AVAILABLE = True
except ImportError:
    UMS_AVAILABLE = False
    print("⚠️ unified-memory 不可用，使用本地存储")

@dataclass
class LearningItem:
    """学习项"""
    date: str
    category: str  # error/improvement/pattern
    trigger: str  # 触发场景
    lesson: str   # 学到的经验
    solution: str # 解决方案
    applied: bool = False

SELF_IMPROVE_LOG = os.path.expanduser("~/.openclaw/workspace/memory/self-improvement.json")

def get_ums_recall():
    """获取 unified-memory 的 recall 实例"""
    if UMS_AVAILABLE:
        return EnhancedRecall()
    return None

def save_to_unified_memory(context: str, lesson: str, solution: str, category: str = "improvement"):
    """保存到 unified-memory"""
    recall = get_ums_recall()
    if recall:
        # 构建记忆文本
        memory_text = f"[{category.upper()}] {context}\n问题: {lesson}\n解决方案: {solution}"
        
        # 重要性根据类别设置
        importance = 0.9 if category == "error" else 0.8
        
        # 存储到增强记忆
        recall.store(
            text=memory_text,
            category=category,
            importance=importance
        )
        print(f"💾 已同步到 unified-memory (重要度: {importance})")
        return True
    return False

def load_learnings() -> List[LearningItem]:
    """加载学习记录"""
    if not os.path.exists(SELF_IMPROVE_LOG):
        return []
    
    try:
        with open(SELF_IMPROVE_LOG, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [LearningItem(**item) for item in data]
    except:
        return []

def save_learnings(learnings: List[LearningItem]):
    """保存学习记录"""
    os.makedirs(os.path.dirname(SELF_IMPROVE_LOG), exist_ok=True)
    with open(SELF_IMPROVE_LOG, 'w', encoding='utf-8') as f:
        json.dump([{
            'date': l.date,
            'category': l.category,
            'trigger': l.trigger,
            'lesson': l.lesson,
            'solution': l.solution,
            'applied': l.applied
        } for l in learnings], f, ensure_ascii=False, indent=2)

def record_error(context: str, error_msg: str, solution: str):
    """记录错误并学习"""
    learnings = load_learnings()
    
    # 检查是否已记录过类似错误
    for l in learnings:
        if l.trigger in context and l.category == 'error':
            print(f"ℹ️ 类似错误已记录: {context}")
            return
    
    # 添加新学习项
    learnings.append(LearningItem(
        date=datetime.now().strftime('%Y-%m-%d'),
        category='error',
        trigger=context,
        lesson=error_msg,
        solution=solution,
        applied=False
    ))
    
    save_learnings(learnings)
    
    # 同步到 unified-memory
    save_to_unified_memory(context, error_msg, solution, category="error")
    
    print(f"✅ 已记录学习项: {context}")

def record_improvement(context: str, improvement: str, method: str):
    """记录改进方法"""
    learnings = load_learnings()
    
    learnings.append(LearningItem(
        date=datetime.now().strftime('%Y-%m-%d'),
        category='improvement',
        trigger=context,
        lesson=improvement,
        solution=method,
        applied=True
    ))
    
    save_learnings(learnings)
    
    # 同步到 unified-memory
    save_to_unified_memory(context, improvement, method, category="improvement")
    
    print(f"✅ 已记录改进: {context}")

def get_unapplied_learnings() -> List[LearningItem]:
    """获取未应用的学习项"""
    learnings = load_learnings()
    return [l for l in learnings if not l.applied]

def apply_to_memory_md():
    """将学习应用到 MEMORY.md"""
    learnings = load_learnings()
    unapplied = [l for l in learnings if not l.applied]
    
    if not unapplied:
        print("✅ 没有需要应用的新学习项")
        return
    
    memory_path = os.path.expanduser("~/.openclaw/workspace/MEMORY.md")
    
    # 读取现有内容
    if os.path.exists(memory_path):
        with open(memory_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "# MEMORY.md\n\n"
    
    # 添加新的学习总结
    new_section = f"\n\n## 自动学习总结 [{datetime.now().strftime('%Y-%m-%d')}]\n\n"
    
    errors = [l for l in unapplied if l.category == 'error']
    improvements = [l for l in unapplied if l.category == 'improvement']
    
    if errors:
        new_section += "### 错误避免\n\n"
        for l in errors:
            new_section += f"- **{l.trigger}**: {l.solution}\n"
    
    if improvements:
        new_section += "### 改进方法\n\n"
        for l in improvements:
            new_section += f"- **{l.trigger}**: {l.lesson}\n"
    
    # 追加到MEMORY.md
    with open(memory_path, 'a', encoding='utf-8') as f:
        f.write(new_section)
    
    # 标记为已应用
    for l in learnings:
        if not l.applied:
            l.applied = True
    save_learnings(learnings)
    
    print(f"✅ 已应用 {len(unapplied)} 条学习项到 MEMORY.md")

def check_before_action(context: str, action_type: str = "general") -> Optional[str]:
    """
    在执行操作前检查历史学习项，避免重复犯错
    
    Args:
        context: 当前上下文/关键词
        action_type: 操作类型
    
    Returns:
        如果有相关学习项，返回提醒信息；否则返回 None
    """
    recall = get_ums_recall()
    if not recall:
        # 回退到本地存储
        learnings = load_learnings()
        relevant = []
        for l in learnings:
            if any(keyword in l.trigger.lower() or keyword in l.lesson.lower() 
                   for keyword in context.lower().split()):
                relevant.append(l)
        
        if relevant:
            warning = "⚠️ 历史学习提醒:\n"
            for l in relevant[-3:]:  # 最近3条
                warning += f"  • [{l.category.upper()}] {l.trigger}\n"
                warning += f"    解决方案: {l.solution}\n"
            return warning
        return None
    
    # 使用 unified-memory 搜索
    results = recall.search(context, top_k=5)
    
    if results:
        error_results = [r for r in results if r['memory'].get('category') == 'error']
        
        if error_results:
            warning = "⚠️ 检测到可能的风险，历史错误提醒:\n"
            for r in error_results[:3]:
                mem = r['memory']
                warning += f"\n  • 重要度: {mem['importance']}\n"
                warning += f"    {mem['text'][:200]}..."
            return warning
    
    return None

def record_pattern(pattern_name: str, description: str, solution: str):
    """记录发现的模式"""
    learnings = load_learnings()
    
    learnings.append(LearningItem(
        date=datetime.now().strftime('%Y-%m-%d'),
        category='pattern',
        trigger=pattern_name,
        lesson=description,
        solution=solution,
        applied=True
    ))
    
    save_learnings(learnings)
    
    # 同步到 unified-memory
    save_to_unified_memory(pattern_name, description, solution, category="pattern")
    
    print(f"✅ 已记录模式: {pattern_name}")

def get_learning_stats():
    """获取学习统计"""
    learnings = load_learnings()
    
    stats = {
        'total': len(learnings),
        'errors': len([l for l in learnings if l.category == 'error']),
        'improvements': len([l for l in learnings if l.category == 'improvement']),
        'patterns': len([l for l in learnings if l.category == 'pattern']),
        'unapplied': len([l for l in learnings if not l.applied])
    }
    
    print("📊 学习统计:")
    print(f"  总数: {stats['total']}")
    print(f"  错误避免: {stats['errors']}")
    print(f"  改进方法: {stats['improvements']}")
    print(f"  发现模式: {stats['patterns']}")
    print(f"  待应用: {stats['unapplied']}")
    
    return stats

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 self_improvement.py learn-error <context> <error> <solution>")
        print("  python3 self_improvement.py improvement <context> <improvement> <method>")
        print("  python3 self_improvement.py check <context>")
        print("  python3 self_improvement.py apply")
        print("  python3 self_improvement.py stats")
        print("  python3 self_improvement.py analyze")
        print("  python3 self_improvement.py prompt")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'learn-error' and len(sys.argv) >= 5:
        record_error(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == 'improvement' and len(sys.argv) >= 5:
        record_improvement(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == 'check' and len(sys.argv) >= 3:
        result = check_before_action(sys.argv[2])
        if result:
            print(result)
        else:
            print("✅ 未检测到相关历史学习项")
    elif cmd == 'apply':
        apply_to_memory_md()
    elif cmd == 'stats':
        get_learning_stats()
    elif cmd == 'analyze':
        analyze_conversation_patterns()
    elif cmd == 'prompt':
        print(generate_self_prompt())
    else:
        print("未知命令")
