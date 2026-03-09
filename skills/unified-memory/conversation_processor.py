#!/usr/bin/env python3
"""
统一记忆系统 - 智能对话处理器
在每次对话结束时自动调用，识别并存储重要信息
"""

import sys
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/skills/unified-memory')

from smart_memory import process_conversation, remember, recall, recognizer

def main():
    """主函数 - 处理对话输入"""
    if len(sys.argv) > 1:
        user_message = sys.argv[1]
        
        # 检查是否是明确的"记住"指令
        if user_message.startswith("记住") or user_message.startswith("请记住"):
            # 提取内容
            content = user_message.replace("记住", "").replace("请记住", "").strip(" :：，,。.")
            if content:
                result = remember(content, importance=0.85)
                if result:
                    print(f"✅ 已记住: {content[:50]}")
                else:
                    print("⚠️ 这条信息已经记录过了")
            return
        
        # 自动识别
        stored = process_conversation(user_message)
        if stored:
            print(f"\n💡 自动识别到 {len(stored)} 条重要信息并保存")

if __name__ == '__main__':
    main()
