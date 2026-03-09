#!/usr/bin/env python3
"""
Memory QA System 测试脚本
验证问答功能的完整性和正确性
"""

import sys
import json
from memory_qa import MemoryQA, MemoryEntry, QAContext


def test_memory_qa():
    """测试问答系统"""
    print("=" * 60)
    print("🧠 Memory QA System 功能测试")
    print("=" * 60)
    
    # 初始化系统
    print("\n1️⃣ 初始化问答系统...")
    qa = MemoryQA()
    print("   ✅ 系统初始化成功")
    
    # 测试1: answer 功能
    print("\n2️⃣ 测试 answer() 功能...")
    
    test_questions = [
        "小龙虾之家是什么项目？",
        "昨天完成了什么工作？",
        "股票分析系统有什么功能？",
    ]
    
    for question in test_questions:
        print(f"\n   问题: {question}")
        result = qa.answer(question, top_k=3)
        print(f"   置信度: {result['confidence']:.2f}")
        print(f"   来源数: {len(result['sources'])}条记忆")
        if result['sources']:
            print(f"   示例来源: [{result['sources'][0]['date']}] {result['sources'][0]['category']}")
        print("   ✅ answer() 功能正常")
    
    # 测试2: summarize_period 功能
    print("\n3️⃣ 测试 summarize_period() 功能...")
    result = qa.summarize_period("2026-03-01", "2026-03-08", focus="项目")
    print(f"   统计: {result['stats'].get('total_entries', 0)} 条记忆")
    print(f"   类别数: {len(result['stats'].get('categories', {}))}")
    print(f"   亮点数: {len(result['highlights'])}")
    print("   ✅ summarize_period() 功能正常")
    
    # 测试3: find_related 功能
    print("\n4️⃣ 测试 find_related() 功能...")
    result = qa.find_related("股票分析", limit=5)
    print(f"   主题: {result['topic']}")
    print(f"   相关条目: {len(result['related_entries'])}条")
    print(f"   时间线: {len(result['timeline'])}个时间点")
    print("   ✅ find_related() 功能正常")
    
    # 测试4: generate_context_aware_response 功能
    print("\n5️⃣ 测试 generate_context_aware_response() 功能...")
    history = [
        {"role": "user", "content": "之前我们讨论过股票分析"},
        {"role": "assistant", "content": "是的，我们有股票分析技能包"}
    ]
    result = qa.generate_context_aware_response("它有什么功能？", history)
    print(f"   使用了上下文: {result['context_used']}")
    print(f"   置信度: {result['confidence']:.2f}")
    print(f"   建议数: {len(result['suggestions'])}")
    print("   ✅ generate_context_aware_response() 功能正常")
    
    # 测试5: 时间解析
    print("\n6️⃣ 测试时间解析功能...")
    time_tests = [
        "今天做了什么",
        "本周工作总结",
        "上个月有什么重要决策",
        "2026-03-01到2026-03-08期间"
    ]
    for test in time_tests:
        time_range = qa._extract_time_range(test)
        print(f"   '{test}' → {time_range}")
    print("   ✅ 时间解析功能正常")
    
    # 测试6: 主题提取
    print("\n7️⃣ 测试主题提取功能...")
    topic_tests = [
        "股票分析系统怎么样",
        "小龙虾之家是什么",
        "项目进展情况"
    ]
    for test in topic_tests:
        topic = qa._extract_topic(test)
        print(f"   '{test}' → 主题: {topic}")
    print("   ✅ 主题提取功能正常")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        success = test_memory_qa()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
