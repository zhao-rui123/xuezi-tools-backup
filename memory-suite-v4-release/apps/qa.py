#!/usr/bin/env python3
"""
智能问答系统 - 基于记忆内容回答问题
"""

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from config import get_config

logger = logging.getLogger('memory-suite')


class QASystem:
    """智能问答系统"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._memory_dir = self._config.get_path('memory')

    def answer(self, question: str) -> str:
        """
        回答问题

        Args:
            question: 问题内容

        Returns:
            回答
        """
        if not question or not question.strip():
            return "请提供有效的问题。"

        logger.info(f"回答问题：{question}")

        try:
            memory_files = list(self._memory_dir.glob("*.md"))
            if not memory_files:
                return "抱歉，记忆中没有任何记录。"

            question_lower = question.lower().strip()
            results = []

            for memory_file in memory_files:
                try:
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    content_lower = content.lower()
                    if question_lower in content_lower:
                        score = content_lower.count(question_lower)
                        snippet = self._extract_snippet(content, question_lower)
                        results.append({
                            "file": memory_file.name,
                            "score": score,
                            "snippet": snippet
                        })
                except UnicodeDecodeError:
                    continue
                except PermissionError:
                    continue
                except Exception:
                    continue

            if not results:
                return self._generate_fallback_answer(question)

            results.sort(key=lambda x: x["score"], reverse=True)
            best_match = results[0]

            return f"在 {best_match['file']} 中找到相关内容：\n\n{best_match['snippet']}"

        except PermissionError as e:
            logger.error(f"问答失败 - 权限不足：{e}")
            return "抱歉，无法访问记忆文件。"
        except Exception as e:
            logger.error(f"问答失败：{e}")
            return "抱歉，处理问题时发生错误。"

    def _extract_snippet(self, content: str, query: str, max_length: int = 300) -> str:
        """提取相关内容片段"""
        content = content.replace("\n", " ").strip()
        idx = content.lower().find(query)

        if idx == -1:
            return content[:max_length] + "..." if len(content) > max_length else content

        start = max(0, idx - 80)
        end = min(len(content), idx + len(query) + 220)

        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def _generate_fallback_answer(self, question: str) -> str:
        """生成备用回答"""
        question_lower = question.lower()

        if "what" in question_lower or "什么" in question_lower:
            return "抱歉，未在记忆中找到相关信息。你可以尝试使用更具体的关键词进行搜索。"
        elif "how" in question_lower or "如何" in question_lower:
            return "记忆中没有找到相关的操作说明。你可以尝试其他问题。"
        elif "when" in question_lower or "什么时候" in question_lower:
            return "记忆中没有找到相关的时间信息。"
        elif "where" in question_lower or "哪里" in question_lower:
            return "记忆中没有找到相关的地点信息。"
        else:
            return "抱歉，未在记忆中找到相关信息。"

    def get_related_questions(self, context: str, limit: int = 5) -> List[str]:
        """获取相关问题建议"""
        try:
            memory_files = list(self._memory_dir.glob("*.md"))
            questions = []

            keywords = context.lower().split()[:3]

            for memory_file in memory_files:
                try:
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()

                    for keyword in keywords:
                        if keyword in content and len(keyword) > 2:
                            idx = content.find(keyword)
                            start = max(0, idx - 30)
                            end = min(len(content), idx + 30)
                            snippet = content[start:end]
                            if "?" not in snippet:
                                questions.append(f"关于 {keyword} 的内容")
                except Exception:
                    continue

            return list(set(questions))[:limit]

        except Exception:
            return []
