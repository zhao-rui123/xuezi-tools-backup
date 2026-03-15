"""
对话结束自动记录模块
检测对话结束信号，自动保存摘要到记忆文件
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

MEMORY_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/memory")

# 对话结束关键词
END_KEYWORDS = [
    "再见", "拜拜", "晚安", "好了", "就这样", 
    "先这样", "先去", "忙吧", "结束",
    "goodbye", "bye", "see you", "gotta go"
]

def detect_end_signal(message: str) -> bool:
    """检测是否是对话结束信号"""
    if not message:
        return False
    message_lower = message.lower().strip()
    for keyword in END_KEYWORDS:
        if keyword.lower() in message_lower:
            return True
    return False

def save_conversation_summary(
    current_model: str = None,
    topics: List[str] = None,
    actions: List[str] = None
):
    """
    保存对话摘要到记忆文件
    
    Args:
        current_model: 当前使用的模型
        topics: 对话主题列表
        actions: 完成的任务列表
    """
    memory_file = MEMORY_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    
    topics_text = "\n".join([f"- {t}" for t in (topics or [])])
    actions_text = "\n".join([f"- {a}" for a in (actions or [])])
    
    entry = f"""
## [{datetime.now().strftime('%H:%M')}] 对话结束 - 自动记录

**类型**: auto_summary
**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 对话信息
- 模型: {current_model or '未知'}

### 讨论主题
{topics_text if topics_text else "-（无）"}

### 完成的任务
{actions_text if actions_text else "-（无）"}

---
"""
    
    try:
        with open(memory_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        print(f"✅ 对话摘要已保存")
        return True
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False


def check_and_auto_save(last_message: str, context: Dict = None) -> bool:
    """
    检查是否需要自动保存
    
    Args:
        last_message: 最后一条用户消息
        context: 上下文信息
        
    Returns:
        是否已保存
    """
    if detect_end_signal(last_message):
        # 自动保存摘要
        save_conversation_summary(
            current_model=context.get("model") if context else None,
            topics=context.get("topics", []) if context else [],
            actions=context.get("actions", []) if context else []
        )
        return True
    return False


if __name__ == "__main__":
    # 测试
    test_messages = [
        "好了就这样吧",
        "再见",
        "拜拜",
        "今天先到这里",
        "我去吃饭了"
    ]
    
    print("=== 对话结束信号检测测试 ===")
    for msg in test_messages:
        result = detect_end_signal(msg)
        print(f"'{msg}' → {'✅ 结束' if result else '❌ 继续'}")
