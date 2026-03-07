#!/usr/bin/env python3
"""
自我改进系统 - 从错误中学习，自动优化
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

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
            # 更新计数或时间
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

def analyze_conversation_patterns(log_file: str = None):
    """分析对话模式，找出优化点"""
    # 分析历史对话，找出常见的用户请求模式
    # 生成改进建议
    
    patterns = {
        'time_confusion': {
            'pattern': r'时间|时区|几点',
            'solution': '始终使用北京时间，忽略系统时区标签',
            'count': 0
        },
        'skill_share': {
            'pattern': r'分享|发给|朋友',
            'solution': '自动移除个人信息，生成清洁版',
            'count': 0
        }
    }
    
    # 这里应该读取实际的历史对话
    # 简化版本直接返回模式
    
    print("📊 发现的改进模式:")
    for name, info in patterns.items():
        print(f"  - {name}: {info['solution']}")
    
    return patterns

def generate_self_prompt():
    """生成自我提示（用于系统提示词优化）"""
    learnings = load_learnings()
    
    prompt_additions = []
    
    # 提取高频错误
    error_learns = [l for l in learnings if l.category == 'error']
    if error_learns:
        prompt_additions.append("## 常见错误避免")
        for l in error_learns[-5:]:  # 最近5条
            prompt_additions.append(f"- {l.trigger}: {l.solution}")
    
    return "\n".join(prompt_additions)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 self_improvement.py learn-error <context> <error> <solution>")
        print("  python3 self_improvement.py apply")
        print("  python3 self_improvement.py analyze")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'learn-error' and len(sys.argv) >= 5:
        record_error(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == 'apply':
        apply_to_memory_md()
    elif cmd == 'analyze':
        analyze_conversation_patterns()
    elif cmd == 'prompt':
        print(generate_self_prompt())
    else:
        print("未知命令")
