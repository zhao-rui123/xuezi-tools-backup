"""
上下文窗口管理器
自动压缩长对话 + 分块处理
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class CompressionStrategy(Enum):
    """压缩策略"""
    KEEP_FIRST_LAST = "keep_first_last"
    SUMMARY_ONLY = "summary_only"
    IMPORTANCE_WEIGHTED = "importance_weighted"
    TOKEN_BUDGET = "token_budget"

@dataclass
class Message:
    """消息"""
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    token_count: int = 0
    importance: float = 1.0
    metadata: Dict = field(default_factory=dict)

@dataclass
class ConversationContext:
    """对话上下文"""
    messages: List[Message] = field(default_factory=list)
    summary: str = ""
    total_tokens: int = 0
    max_tokens: int = 8000

class ContextWindowManager:
    """上下文窗口管理器"""

    def __init__(self, max_tokens: int = 8000):
        self.max_tokens = max_tokens
        self.token_counts = {}
        self.compression_history = []

    def estimate_tokens(self, text: str) -> int:
        """估算Token数量 (中文字符约等于2个token)"""
        return len(text) // 2

    def add_message(self, role: str, content: str, importance: float = 1.0) -> Message:
        """添加消息"""
        token_count = self.estimate_tokens(content)
        message = Message(
            role=role,
            content=content,
            token_count=token_count,
            importance=importance
        )
        return message

    def compress_keep_first_last(self, messages: List[Message], keep_count: int = 5) -> List[Message]:
        """保留开头和结尾的消息"""
        if len(messages) <= keep_count * 2:
            return messages

        first = messages[:keep_count]
        last = messages[-keep_count:]
        middle_summary = self._create_summary(messages[keep_count:-keep_count])

        summary_message = Message(
            role="system",
            content=f"[{len(messages) - keep_count * 2} 条消息已压缩]\n{middle_summary}",
            importance=0.5
        )

        return first + [summary_message] + last

    def compress_by_importance(self, messages: List[Message]) -> List[Message]:
        """按重要性压缩"""
        if not messages:
            return []

        total_importance = sum(m.importance for m in messages)
        token_budget = self.max_tokens * 0.8

        result = []
        current_tokens = 0

        sorted_msgs = sorted(messages, key=lambda m: m.importance, reverse=True)

        for msg in sorted_msgs:
            if current_tokens + msg.token_count > token_budget:
                continue
            result.append(msg)
            current_tokens += msg.token_count

        return sorted(result, key=lambda m: m.timestamp)

    def _create_summary(self, messages: List[Message]) -> str:
        """创建摘要"""
        if not messages:
            return ""

        summary_parts = []
        roles = {}
        for msg in messages:
            roles[msg.role] = roles.get(msg.role, 0) + 1

        summary_parts.append(f"对话记录: {len(messages)} 条消息")
        summary_parts.append(f"角色分布: {', '.join(f'{k}:{v}' for k,v in roles.items())}")

        return "\n".join(summary_parts)

    def compress_context(self, context: ConversationContext,
                        strategy: CompressionStrategy = CompressionStrategy.KEEP_FIRST_LAST) -> ConversationContext:
        """压缩上下文"""
        if context.total_tokens <= self.max_tokens:
            return context

        original_tokens = context.total_tokens
        original_count = len(context.messages)

        if strategy == CompressionStrategy.KEEP_FIRST_LAST:
            compressed = self.compress_keep_first_last(context.messages)
        elif strategy == CompressionStrategy.IMPORTANCE_WEIGHTED:
            compressed = self.compress_by_importance(context.messages)
        else:
            compressed = context.messages[-10:]

        new_total = sum(m.token_count for m in compressed)

        context.messages = compressed
        context.total_tokens = new_total
        context.summary = f"[压缩: {original_count}→{len(compressed)} 消息, {original_tokens}→{new_total} tokens]"

        self.compression_history.append({
            'timestamp': datetime.now().isoformat(),
            'original': original_tokens,
            'compressed': new_total,
            'strategy': strategy.value
        })

        return context

    def split_long_task(self, task: str, max_length: int = 2000) -> List[str]:
        """拆分长任务"""
        if len(task) <= max_length:
            return [task]

        chunks = []
        sentences = task.replace('。', '。|').replace('\n', '|\n|').split('|')
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) <= max_length:
                current += sentence
            else:
                if current:
                    chunks.append(current.strip())
                current = sentence

        if current:
            chunks.append(current.strip())

        return chunks

    def get_context_stats(self, context: ConversationContext) -> Dict:
        """获取上下文统计"""
        return {
            'message_count': len(context.messages),
            'total_tokens': context.total_tokens,
            'max_tokens': self.max_tokens,
            'usage_percent': context.total_tokens / self.max_tokens * 100,
            'compression_count': len(self.compression_history)
        }
