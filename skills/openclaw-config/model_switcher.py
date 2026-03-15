#!/usr/bin/env python3
"""
自然语言模型切换模块
智能识别用户切换意图，自动执行 /model 命令
"""

import re
from typing import Optional, Dict

class ModelSwitcher:
    """模型切换器"""
    
    # 模型别名映射
    MODEL_ALIASES = {
        # MiniMax
        'minimax': 'm25',
        'm25': 'm25',
        'm2.5': 'm25',
        'minimax-m2.5': 'm25',
        'minimax m2.5': 'm25',
        
        # Kimi Coding
        'k2p5': 'k2p5',
        'k2.5': 'k2p5',
        'coding': 'k2p5',
        'kimi coding': 'k2p5',
        'kimi-coding': 'k2p5',
        'kimi for coding': 'k2p5',
        
        # Kimi K2.5 (bailian)
        'kimi': 'kimi-k2.5',
        'kimi-k2.5': 'kimi-k2.5',
        'kimi k2.5': 'kimi-k2.5',
        
        # Qwen
        'qwen': 'qwen3.5-plus',
        'qwen3.5': 'qwen3.5-plus',
        '通义千问': 'qwen3.5-plus',
    }
    
    # 切换意图关键词
    SWITCH_PATTERNS = [
        r'切换到?\s*(.+)',
        r'切到?\s*(.+)',
        r'换到?\s*(.+)',
        r'换?成?\s*(.+)',
        r'用\s*(.+)',
        r'使用\s*(.+)',
        r'改成?\s*(.+)',
        r'改为?\s*(.+)',
        r'模型\s*(.+)',
    ]
    
    @classmethod
    def detect_switch_intent(cls, message: str) -> Optional[str]:
        """
        检测切换意图
        
        Args:
            message: 用户消息
            
        Returns:
            模型别名或None
        """
        message = message.lower().strip()
        
        # 直接匹配别名
        for alias, model in cls.MODEL_ALIASES.items():
            if message == alias or message == f'/{alias}':
                return model
        
        # 匹配切换意图
        for pattern in cls.SWITCH_PATTERNS:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                target = match.group(1).strip().lower()
                # 在别名中查找
                for alias, model in cls.MODEL_ALIASES.items():
                    if alias in target or target in alias:
                        return model
        
        return None
    
    @classmethod
    def get_model_info(cls, model: str) -> Dict:
        """获取模型信息"""
        model_info = {
            'k2p5': {
                'name': 'Kimi for Coding',
                'provider': 'kimi-coding',
                'desc': '适合编程，支持长上下文'
            },
            'm25': {
                'name': 'MiniMax M2.5',
                'provider': 'minimax-cn',
                'desc': '支持推理，有思考过程'
            },
            'kimi-k2.5': {
                'name': 'Kimi K2.5',
                'provider': 'bailian',
                'desc': '通用模型，支持图片'
            },
            'qwen3.5-plus': {
                'name': '通义千问3.5 Plus',
                'provider': 'bailian',
                'desc': '阿里模型，长上下文'
            }
        }
        return model_info.get(model, {'name': model, 'provider': 'unknown', 'desc': ''})


# 使用示例
if __name__ == "__main__":
    test_messages = [
        "切换到 k2p5",
        "用 MiniMax",
        "切到 coding",
        "换到 m25",
        "使用通义千问",
        "改成 kimi",
        "k2p5",  # 直接输入
        "m25",   # 直接输入
    ]
    
    for msg in test_messages:
        result = ModelSwitcher.detect_switch_intent(msg)
        if result:
            info = ModelSwitcher.get_model_info(result)
            print(f"'{msg}' → {result} ({info['name']})")
        else:
            print(f"'{msg}' → 未识别")
