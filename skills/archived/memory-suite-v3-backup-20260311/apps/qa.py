#!/usr/bin/env python3
"""
Memory Suite v3.0 - 智能问答模块 (QA System)

功能：
1. 基于记忆回答问题
2. 语义搜索
3. 上下文关联

作者：Memory Suite Team
版本：3.0.0
日期：2026-03-11
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core import (
    setup_logger, expand_path, load_json, save_json,
    format_datetime, get_date_string, ConfigManager,
    truncate_text
)


class QASystem:
    """智能问答系统"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化问答系统"""
        self.logger = setup_logger("memory_suite.qa")
        self.logger.info("初始化问答系统...")
        
        if config is None:
            config_manager = ConfigManager()
            config = config_manager.load_config() or {}
        self.config = config
        
        self.workspace = expand_path(config.get('workspace', '~/.openclaw/workspace'))
        self.memory_dir = expand_path(config.get('memory_dir', '~/.openclaw/workspace/memory'))
        self.index_dir = self.memory_dir / 'index'
        
        self.logger.info("问答系统初始化完成")
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """搜索相关记忆"""
        self.logger.info(f"搜索：{query}")
        results = []
        
        memory_files = list(self.memory_dir.glob("2026-*.md"))
        memory_files.extend(self.memory_dir.glob("2025-*.md"))
        
        query_keywords = query.lower().split()
        
        for file_path in memory_files[:60]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                score = 0
                for keyword in query_keywords:
                    if keyword.lower() in content.lower():
                        score += 1
                
                if score > 0:
                    results.append({
                        'file': str(file_path),
                        'date': file_path.stem,
                        'content': truncate_text(content, 500),
                        'score': score
                    })
            except Exception as e:
                self.logger.warning(f"读取文件失败 {file_path}: {e}")
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def answer(self, question: str) -> Dict[str, Any]:
        """回答问题"""
        self.logger.info(f"回答问题：{question}")
        
        search_results = self.search(question, limit=5)
        
        return {
            'question': question,
            'timestamp': format_datetime(),
            'results': search_results,
            'answer': self._synthesize_answer(question, search_results)
        }
    
    def _synthesize_answer(self, question: str, results: List[Dict]) -> str:
        """合成答案"""
        if not results:
            return "未找到相关记忆记录。"
        
        answer_parts = []
        for i, result in enumerate(results[:3], 1):
            answer_parts.append(f"[{result['date']}] {truncate_text(result['content'], 200)}")
        
        return "\n\n".join(answer_parts)
    
    def run(self, question: str) -> Dict[str, Any]:
        """运行问答"""
        self.logger.info("=" * 60)
        self.logger.info("开始智能问答")
        self.logger.info("=" * 60)
        
        result = self.answer(question)
        
        print("\n" + "=" * 60)
        print(f"❓ 问题：{question}")
        print("=" * 60)
        print(f"\n{result['answer']}")
        print("\n" + "=" * 60)
        
        return result


def main():
    """CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Suite 智能问答')
    parser.add_argument('question', type=str, nargs='?', help='问题')
    parser.add_argument('--search', '-s', type=str, help='搜索关键词')
    parser.add_argument('--limit', '-l', type=int, default=5, help='结果数量')
    
    args = parser.parse_args()
    
    qa = QASystem()
    
    if args.search:
        results = qa.search(args.search, args.limit)
        for r in results:
            print(f"[{r['date']}] (score: {r['score']})")
            print(f"  {truncate_text(r['content'], 150)}\n")
    elif args.question:
        qa.run(args.question)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
