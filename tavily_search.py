#!/usr/bin/env python3
"""
Tavily搜索工具 - 直接使用API
绕过OpenClaw内置工具限制
"""

import os
import json
import requests
from typing import List, Dict, Optional

class TavilySearch:
    """Tavily搜索客户端"""
    
    API_URL = "https://api.tavily.com/search"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('TAVILY_API_KEY')
        if not self.api_key:
            raise ValueError("需要提供Tavily API Key")
    
    def search(self, 
               query: str, 
               search_depth: str = "basic",
               max_results: int = 5,
               include_answer: bool = True,
               include_images: bool = False,
               include_raw_content: bool = False) -> Dict:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            search_depth: 搜索深度 (basic/advanced)
            max_results: 最大结果数
            include_answer: 是否包含AI总结答案
            include_images: 是否包含图片
            include_raw_content: 是否包含原始内容
        """
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": include_answer,
            "include_images": include_images,
            "include_raw_content": include_raw_content,
        }
        
        try:
            response = requests.post(self.API_URL, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def format_results(self, results: Dict) -> str:
        """格式化搜索结果"""
        if "error" in results:
            return f"搜索失败: {results['error']}"
        
        output = []
        
        # AI答案
        if results.get("answer"):
            output.append("=" * 60)
            output.append("📋 AI总结")
            output.append("=" * 60)
            output.append(results["answer"])
            output.append("")
        
        # 搜索结果
        output.append("=" * 60)
        output.append("🔍 搜索结果")
        output.append("=" * 60)
        
        for i, result in enumerate(results.get("results", []), 1):
            output.append(f"\n[{i}] {result.get('title', '无标题')}")
            output.append(f"    URL: {result.get('url', 'N/A')}")
            output.append(f"    内容: {result.get('content', '无内容')[:200]}...")
        
        return "\n".join(output)

# 便捷函数
def search_news(query: str, days: int = 7, max_results: int = 10) -> str:
    """
    搜索新闻
    
    Args:
        query: 搜索关键词
        days: 最近几天的新闻
        max_results: 最大结果数
    """
    api_key = os.environ.get('TAVILY_API_KEY')
    if not api_key:
        return "错误: 未设置TAVILY_API_KEY环境变量"
    
    client = TavilySearch(api_key)
    
    # 添加时间限制
    time_query = f"{query} 最近{days}天"
    
    results = client.search(
        query=time_query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=True,
        include_raw_content=True
    )
    
    return client.format_results(results)

def search_companies(industry: str, topic: str = "新品发布") -> str:
    """
    搜索企业信息
    
    Args:
        industry: 行业名称
        topic: 主题
    """
    query = f"{industry}企业 {topic} 2026"
    return search_news(query, days=30, max_results=10)

# 主函数
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 tavily_search.py '搜索关键词'")
        print("或: python3 tavily_search.py --news '关键词' --days 7")
        sys.exit(1)
    
    if sys.argv[1] == "--news":
        query = sys.argv[2] if len(sys.argv) > 2 else "储能新品"
        days = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == "--days" else 7
        print(search_news(query, days))
    else:
        query = sys.argv[1]
        api_key = os.environ.get('TAVILY_API_KEY')
        if not api_key:
            print("错误: 请设置TAVILY_API_KEY环境变量")
            sys.exit(1)
        
        client = TavilySearch(api_key)
        results = client.search(query, max_results=5)
        print(client.format_results(results))
