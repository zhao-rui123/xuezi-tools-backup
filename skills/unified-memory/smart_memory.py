#!/usr/bin/env python3
"""
智能记忆识别系统
自动分析对话内容，识别重要信息并存储到增强记忆
"""

import json
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / ".memory" / "enhanced"
MEMORY_FILE = MEMORY_DIR / "memories.json"

# 确保目录存在
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# 重要信息模式识别
IMPORTANT_PATTERNS = {
    "preference": {
        "patterns": [
            r"我喜欢(.+)",
            r"我偏好(.+)",
            r"我喜欢用(.+)",
            r"我习惯(.+)",
            r"我倾向于(.+)",
            r"我更(.+)",
            r"我喜欢看(.+)",
            r"我喜欢买(.+)",
            r"我喜欢做(.+)",
            r"我喜欢听(.+)",
        ],
        "importance": 0.7,
        "category": "preference"
    },
    "decision": {
        "patterns": [
            r"决定(.+)",
            r"确定(.+)",
            r"选定(.+)",
            r"采用(.+)",
            r"确定使用(.+)",
            r"确定选(.+)",
            r"最终决定(.+)",
            r"[重要决策]",
            r"【重要决策】",
        ],
        "importance": 0.9,
        "category": "decision"
    },
    "identity": {
        "patterns": [
            r"我的名字是(.+)",
            r"我叫(.+)",
            r"我是(.+)",
            r"我的职业是(.+)",
            r"我的工作(.+)",
            r"我的公司(.+)",
            r"我的邮箱(.+)",
            r"我的电话(.+)",
            r"我的地址(.+)",
        ],
        "importance": 0.85,
        "category": "identity"
    },
    "finance": {
        "patterns": [
            r"我的股票(.+)",
            r"我买了(.+)股",
            r"我持有(.+)",
            r"我的基金(.+)",
            r"我的投资(.+)",
            r"我的账户(.+)",
            r"股票代码(.+)",
            r"持仓(.+)",
        ],
        "importance": 0.85,
        "category": "finance"
    },
    "schedule": {
        "patterns": [
            r"我明天要(.+)",
            r"我下周要(.+)",
            r"我计划(.+)",
            r"我打算(.+)",
            r"记得提醒我(.+)",
            r"别忘了(.+)",
            r"\[TODO\]",
            r"【TODO】",
        ],
        "importance": 0.75,
        "category": "schedule"
    },
    "project": {
        "patterns": [
            r"项目名称(.+)",
            r"项目叫(.+)",
            r"网站地址(.+)",
            r"GitHub(.+)",
            r"服务器IP(.+)",
            r"项目目标(.+)",
            r"项目里程碑(.+)",
        ],
        "importance": 0.8,
        "category": "project"
    },
    "constraint": {
        "patterns": [
            r"必须(.+)",
            r"一定要(.+)",
            r"不能(.+)",
            r"不要(.+)",
            r"禁止(.+)",
            r"绝不要(.+)",
            r"千万不要(.+)",
        ],
        "importance": 0.75,
        "category": "constraint"
    },
    "improvement": {
        "patterns": [
            r"我犯错了(.+)",
            r"注意(.+)",
            r"记住不要(.+)",
            r"以后(.+)",
            r"避免(.+)",
            r"改进(.+)",
            r"优化(.+)",
            r"教训(.+)",
            r"错误(.+)",
        ],
        "importance": 0.9,
        "category": "improvement"
    }
}

# 关键词权重（用于计算重要性）
KEYWORD_WEIGHTS = {
    "重要": 0.1,
    "关键": 0.1,
    "必须": 0.15,
    "一定": 0.1,
    "永远": 0.1,
    "绝对": 0.1,
    "特别": 0.05,
    "非常": 0.05,
    "核心": 0.1,
    "主要": 0.05,
    "记住": 0.15,
    "别忘了": 0.1,
}


class SmartMemoryRecognizer:
    """智能记忆识别器"""
    
    def __init__(self):
        self.memories = self._load_memories()
    
    def _load_memories(self):
        """加载已有记忆"""
        if MEMORY_FILE.exists():
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_memories(self):
        """保存记忆"""
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)
    
    def _calculate_importance(self, text: str, base_importance: float) -> float:
        """计算重要性分数"""
        importance = base_importance
        
        # 根据关键词增加重要性
        for keyword, weight in KEYWORD_WEIGHTS.items():
            if keyword in text:
                importance += weight
        
        # 根据文本长度调整（太短或太长都降低重要性）
        length = len(text)
        if length < 5:
            importance -= 0.2
        elif length > 200:
            importance -= 0.1
        
        # 限制在0-1范围内
        return max(0.1, min(1.0, importance))
    
    def _is_duplicate(self, text: str) -> bool:
        """检查是否重复"""
        text_normalized = text.strip().lower()
        for mem in self.memories[-50:]:  # 只检查最近50条
            if text_normalized in mem['text'].lower() or mem['text'].lower() in text_normalized:
                return True
        return False
    
    def recognize(self, user_message: str, ai_response: str = None) -> list:
        """
        识别对话中的重要信息
        
        Args:
            user_message: 用户消息
            ai_response: AI回复（可选）
        
        Returns:
            识别出的记忆列表
        """
        recognized_memories = []
        
        # 分析用户消息
        for mem_type, config in IMPORTANT_PATTERNS.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, user_message, re.IGNORECASE)
                for match in matches:
                    # 提取内容
                    if match.groups():
                        content = match.group(1).strip()
                    else:
                        content = user_message.strip()
                    
                    # 清理内容
                    content = re.sub(r'[,，.。!！?？]$', '', content)
                    
                    if len(content) < 3:  # 太短的跳过
                        continue
                    
                    # 检查重复
                    if self._is_duplicate(content):
                        continue
                    
                    # 计算重要性
                    importance = self._calculate_importance(content, config['importance'])
                    
                    recognized_memories.append({
                        'text': content,
                        'category': config['category'],
                        'importance': round(importance, 2),
                        'source': 'auto_recognized',
                        'matched_pattern': pattern,
                        'context': user_message[:100]  # 保存上下文
                    })
        
        return recognized_memories
    
    def store(self, text: str, category: str = "general", importance: float = 0.5, 
              source: str = "user_explicit") -> dict:
        """
        存储记忆
        
        Args:
            text: 记忆内容
            category: 类别
            importance: 重要性 0-1
            source: 来源（user_explicit 或 auto_recognized）
        """
        # 检查重复
        if self._is_duplicate(text):
            return None
        
        memory = {
            'id': len(self.memories) + 1,
            'text': text,
            'category': category,
            'importance': importance,
            'source': source,
            'created': datetime.now().isoformat(),
            'access_count': 0
        }
        
        self.memories.append(memory)
        self._save_memories()
        
        return memory
    
    def auto_store_from_conversation(self, user_message: str, ai_response: str = None) -> list:
        """
        从对话中自动识别并存储记忆
        
        Returns:
            存储成功的记忆列表
        """
        recognized = self.recognize(user_message, ai_response)
        stored = []
        
        for mem in recognized:
            # 只存储高重要性的（避免噪音）
            if mem['importance'] >= 0.7:
                result = self.store(
                    text=mem['text'],
                    category=mem['category'],
                    importance=mem['importance'],
                    source='auto_recognized'
                )
                if result:
                    stored.append(result)
        
        return stored
    
    def search(self, query: str, top_k: int = 5) -> list:
        """搜索记忆"""
        results = []
        query_lower = query.lower()
        
        for mem in self.memories:
            score = 0
            
            # 文本匹配
            if query_lower in mem['text'].lower():
                score += 1.0
            
            # 类别匹配
            if query_lower == mem.get('category', '').lower():
                score += 0.5
            
            if score > 0:
                # 时间衰减
                created = datetime.fromisoformat(mem['created'])
                age_days = (datetime.now() - created).days
                time_decay = 0.5 + 0.5 * (2.71828 ** (-age_days / 60))
                
                # 重要性加权
                importance_weight = 0.7 + 0.3 * mem['importance']
                
                final_score = score * time_decay * importance_weight
                
                results.append({
                    'memory': mem,
                    'score': final_score,
                    'time_decay': time_decay
                })
        
        # 排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            'total_memories': len(self.memories),
            'by_category': {},
            'by_source': {}
        }


# 全局实例
recognizer = SmartMemoryRecognizer()


def process_conversation(user_message: str, ai_response: str = None) -> list:
    """
    处理对话，自动识别并存储重要信息
    
    在每次对话结束时调用
    """
    stored = recognizer.auto_store_from_conversation(user_message, ai_response)
    
    if stored:
        print(f"💾 自动识别并存储了 {len(stored)} 条记忆:")
        for mem in stored:
            print(f"   [{mem['category']}] {mem['text'][:50]}... (重要度: {mem['importance']})")
    
    return stored


def remember(text: str, importance: float = 0.8) -> dict:
    """
    用户主动要求记住
    """
    return recognizer.store(text, importance=importance, source='user_explicit')


def recall(query: str, top_k: int = 5) -> list:
    """
    搜索记忆
    """
    return recognizer.search(query, top_k)


if __name__ == '__main__':
    # 测试
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            # 测试自动识别
            test_messages = [
                "我喜欢用 Python 编程",
                "我决定使用 React 作为前端框架",
                "记住我的股票代码是 002460",
                "我叫雪子，做储能项目的",
                "千万不要把 API key 上传到 GitHub",
            ]
            
            print("🧪 测试智能记忆识别:")
            for msg in test_messages:
                print(f"\n用户: {msg}")
                stored = process_conversation(msg)
                if not stored:
                    print("   (未识别出需要自动存储的信息)")
        
        elif sys.argv[1] == 'store' and len(sys.argv) > 2:
            # 手动存储
            text = ' '.join(sys.argv[2:])
            result = remember(text)
            if result:
                print(f"✅ 已存储: {text}")
            else:
                print("⚠️ 重复或未存储")
        
        elif sys.argv[1] == 'search' and len(sys.argv) > 2:
            # 搜索
            query = ' '.join(sys.argv[2:])
            results = recall(query)
            print(f"🔍 搜索 '{query}':")
            for r in results:
                mem = r['memory']
                print(f"   [{mem['category']}] {mem['text']} (重要度: {mem['importance']}, 得分: {r['score']:.3f})")
        
        elif sys.argv[1] == 'stats':
            # 统计
            stats = recognizer.get_stats()
            print(f"📊 记忆统计:")
            print(f"   总数: {stats['total_memories']}")
    else:
        print("用法:")
        print("  python smart_memory.py test          测试自动识别")
        print("  python smart_memory.py store <内容>   手动存储")
        print("  python smart_memory.py search <关键词> 搜索")
        print("  python smart_memory.py stats         查看统计")
