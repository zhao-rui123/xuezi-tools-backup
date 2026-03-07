#!/usr/bin/env python3
"""
联网搜索技能包 - 基于Tavily API的AI搜索引擎
"""

import os
import json
import urllib.request
from typing import Dict, List, Optional
from dataclasses import dataclass

TAVILY_API_URL = "https://api.tavily.com/search"

def get_api_key() -> Optional[str]:
    """获取API Key"""
    return os.environ.get('TAVILY_API_KEY') or os.environ.get('TAVILY_KEY')

def search(query: str, max_results: int = 5, include_answer: bool = True) -> Dict:
    """
    使用Tavily进行AI搜索
    
    Args:
        query: 搜索查询
        max_results: 返回结果数量
        include_answer: 是否包含AI总结的答案
    """
    api_key = get_api_key()
    if not api_key:
        return {
            'error': '未设置TAVILY_API_KEY环境变量',
            'setup': '请设置: export TAVILY_API_KEY=your_key'
        }
    
    try:
        payload = {
            'api_key': api_key,
            'query': query,
            'max_results': max_results,
            'include_answer': include_answer,
            'search_depth': 'basic',  # basic 或 advanced
        }
        
        req = urllib.request.Request(
            TAVILY_API_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        response = urllib.request.urlopen(req, timeout=30)
        data = json.loads(response.read().decode('utf-8'))
        
        return data
        
    except Exception as e:
        return {'error': str(e)}

def format_search_result(result: Dict) -> str:
    """格式化搜索结果"""
    if 'error' in result:
        return f"❌ 搜索错误: {result['error']}"
    
    lines = [
        f"\n{'='*70}",
        f"🔍 搜索结果",
        f"{'='*70}",
        f"",
    ]
    
    # AI总结的答案
    if result.get('answer'):
        lines.append(f"📝 AI总结:")
        lines.append(f"{result['answer']}")
        lines.append(f"")
    
    # 搜索结果
    results = result.get('results', [])
    if results:
        lines.append(f"📄 相关网页 ({len(results)}个结果):")
        lines.append(f"")
        
        for i, r in enumerate(results, 1):
            title = r.get('title', '无标题')
            url = r.get('url', '')
            content = r.get('content', '')[:150] + '...' if len(r.get('content', '')) > 150 else r.get('content', '')
            
            lines.append(f"{i}. {title}")
            lines.append(f"   URL: {url}")
            lines.append(f"   {content}")
            lines.append(f"")
    
    lines.append(f"{'='*70}")
    return "\n".join(lines)

def quick_search(query: str) -> str:
    """快速搜索并返回格式化结果"""
    result = search(query)
    return format_search_result(result)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 web_search.py '搜索关键词'")
        print("  python3 web_search.py 'Python tutorial' --results 10")
        sys.exit(1)
    
    query = sys.argv[1]
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == '--results' else 5
    
    print(quick_search(query))
