#!/usr/bin/env python3
"""
智能记忆搜索 - 自动判断中英文搜索策略
- 中文 → memory-suite-v4（整句匹配）
- 英文/数字 → OpenClaw FTS（精确匹配）
- 或者两者结合输出
"""

import subprocess
import sys
import re
import json

def is_chinese(text):
    """判断是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def search_memory_suite(query):
    """调用 memory-suite-v4 搜索"""
    cmd = [
        'python3', '-c',
        f'''
import sys
sys.argv = ['', 'search', "{query}"]
from cli import main
try: main()
except SystemExit: pass
'''
    ]
    try:
        result = subprocess.run(
            cmd,
            cwd='/Users/zhaoruicn/.openclaw/workspace/skills/memory-suite-v4',
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "memory-suite-v4 搜索超时\n"
    except Exception as e:
        return f"memory-suite-v4 搜索失败: {e}\n"

def search_openclaw_fts(query):
    """调用 OpenClaw FTS 搜索"""
    cmd = ['openclaw', 'memory', 'search', query]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        # 过滤掉插件加载信息
        lines = result.stdout.split('\n')
        filtered = [l for l in lines if not l.startswith('[plugins]')]
        return '\n'.join(filtered)
    except subprocess.TimeoutExpired:
        return "OpenClaw FTS 搜索超时\n"
    except Exception as e:
        return f"OpenClaw FTS 搜索失败: {e}\n"

def main():
    if len(sys.argv) < 2:
        print("用法: python3 smart-search.py <搜索词>")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    has_chinese = is_chinese(query)
    
    print(f"🔍 智能搜索: {query}")
    print("=" * 50)
    
    if has_chinese:
        # 混合查询：中文+英文，都跑
        print("📝 检测到中文，两个引擎都搜索")
        print("\n📖 memory-suite-v4 结果:")
        print("=" * 50)
        ms_result = search_memory_suite(query)
        print(ms_result)
        
        print("\n📊 OpenClaw FTS 结果:")
        print("=" * 50)
        fts_result = search_openclaw_fts(query)
        if "No matches" in fts_result:
            print("(无匹配)")
        else:
            print(fts_result)
    else:
        print("📊 英文/数字搜索，使用 OpenClaw FTS")
        print("=" * 50)
        fts_result = search_openclaw_fts(query)
        if "No matches" in fts_result:
            print("(无匹配，尝试 memory-suite-v4...)\n")
            print(search_memory_suite(query))
        else:
            print(fts_result)

if __name__ == '__main__':
    main()
