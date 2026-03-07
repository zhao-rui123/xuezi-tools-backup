#!/usr/bin/env python3
"""
Enhanced Memory CLI - 命令行管理工具
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 直接导入当前目录的模块
import importlib.util
spec = importlib.util.spec_from_file_location("enhanced_memory", Path(__file__).parent / "__init__.py")
enhanced_memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(enhanced_memory)

get_memory = enhanced_memory.get_memory
EnhancedMemory = enhanced_memory.EnhancedMemory

def print_help():
    print("""
Enhanced Memory CLI

用法:
  python -m enhanced_memory list [--scope SCOPE] [--limit N]
  python -m enhanced_memory search QUERY [--scope SCOPE] [--top-k N]
  python -m enhanced_memory add TEXT [--category CAT] [--importance VAL] [--scope SCOPE]
  python -m enhanced_memory delete ID
  python -m enhanced_memory stats
  python -m enhanced_memory export [--output FILE]
  python -m enhanced_memory import FILE [--scope SCOPE]

示例:
  python -m enhanced_memory list --limit 10
  python -m enhanced_memory search "编程爱好" --top-k 5
  python -m enhanced_memory add "用户喜欢Python" --category preference --importance 0.8
  python -m enhanced_memory delete mem_00000001
  python -m enhanced_memory stats
""")

def cmd_list(args):
    """列出记忆"""
    mem = get_memory()
    scope = None
    limit = 20
    
    i = 0
    while i < len(args):
        if args[i] == "--scope" and i + 1 < len(args):
            scope = args[i + 1]
            i += 2
        elif args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        else:
            i += 1
    
    memories = mem.memories["memories"]
    filtered = []
    
    for mem_id, m in memories.items():
        if scope and m["scope"] != scope:
            continue
        filtered.append(m)
    
    # 按时间倒序
    filtered.sort(key=lambda x: x["timestamp"], reverse=True)
    filtered = filtered[:limit]
    
    print(f"\n共 {len(memories)} 条记忆" + (f" (作用域: {scope})" if scope else ""))
    print("-" * 80)
    
    for m in filtered:
        print(f"ID: {m['id']}")
        print(f"  内容: {m['text'][:60]}{'...' if len(m['text']) > 60 else ''}")
        print(f"  分类: {m['category']} | 重要性: {m['importance']:.1f} | 作用域: {m['scope']}")
        print()

def cmd_search(args):
    """搜索记忆"""
    if not args:
        print("错误: 请提供搜索关键词")
        return
    
    query = args[0]
    scope = None
    top_k = 5
    
    i = 1
    while i < len(args):
        if args[i] == "--scope" and i + 1 < len(args):
            scope = args[i + 1]
            i += 2
        elif args[i] == "--top-k" and i + 1 < len(args):
            top_k = int(args[i + 1])
            i += 2
        else:
            i += 1
    
    mem = get_memory()
    results = mem.recall(query, scope=scope, top_k=top_k)
    
    print(f"\n搜索: '{query}'" + (f" (作用域: {scope})" if scope else ""))
    print("-" * 80)
    
    if not results:
        print("未找到相关记忆")
        return
    
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r['score']:.3f}] {r['text'][:70]}")
        print(f"   ID: {r['id']} | 分类: {r['category']} | 作用域: {r['scope']}")
        print()

def cmd_add(args):
    """添加记忆"""
    if not args:
        print("错误: 请提供记忆内容")
        return
    
    text = args[0]
    category = "fact"
    importance = 0.5
    scope = "global"
    
    i = 1
    while i < len(args):
        if args[i] == "--category" and i + 1 < len(args):
            category = args[i + 1]
            i += 2
        elif args[i] == "--importance" and i + 1 < len(args):
            importance = float(args[i + 1])
            i += 2
        elif args[i] == "--scope" and i + 1 < len(args):
            scope = args[i + 1]
            i += 2
        else:
            i += 1
    
    mem = get_memory()
    mem_id = mem.store(text, category=category, importance=importance, scope=scope)
    
    if mem_id:
        print(f"✅ 记忆已保存: {mem_id}")
    else:
        print("❌ 记忆被过滤（可能是噪声内容）")

def cmd_delete(args):
    """删除记忆"""
    if not args:
        print("错误: 请提供记忆 ID")
        return
    
    mem_id = args[0]
    mem = get_memory()
    
    if mem.delete(mem_id):
        print(f"✅ 已删除: {mem_id}")
    else:
        print(f"❌ 未找到: {mem_id}")

def cmd_stats(args):
    """统计信息"""
    mem = get_memory()
    stats = mem.stats()
    
    print("\n📊 记忆统计")
    print("-" * 40)
    print(f"总记忆数: {stats['total']}")
    print(f"词索引大小: {stats['term_index_size']}")
    
    # 按分类统计
    by_category = {}
    by_scope = {}
    
    for m in mem.memories["memories"].values():
        cat = m["category"]
        sc = m["scope"]
        by_category[cat] = by_category.get(cat, 0) + 1
        by_scope[sc] = by_scope.get(sc, 0) + 1
    
    if by_category:
        print(f"\n按分类:")
        for cat, count in sorted(by_category.items()):
            print(f"  {cat}: {count}")
    
    if by_scope:
        print(f"\n按作用域:")
        for sc, count in sorted(by_scope.items()):
            print(f"  {sc}: {count}")

def cmd_export(args):
    """导出记忆"""
    output = "memories_export.json"
    
    if args and not args[0].startswith("--"):
        output = args[0]
    
    for i, arg in enumerate(args):
        if arg == "--output" and i + 1 < len(args):
            output = args[i + 1]
    
    mem = get_memory()
    data = {
        "export_time": str(datetime.now()),
        "memories": mem.memories["memories"]
    }
    
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已导出到: {output}")

def cmd_import(args):
    """导入记忆"""
    if not args:
        print("错误: 请提供文件路径")
        return
    
    filepath = args[0]
    scope = None
    
    for i, arg in enumerate(args):
        if arg == "--scope" and i + 1 < len(args):
            scope = args[i + 1]
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        mem = get_memory()
        imported = 0
        
        for mem_id, m in data.get("memories", {}).items():
            if scope:
                m["scope"] = scope
            mem.memories["memories"][mem_id] = m
            imported += 1
        
        mem._save_index()
        print(f"✅ 已导入 {imported} 条记忆")
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")

def main():
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        "list": cmd_list,
        "search": cmd_search,
        "add": cmd_add,
        "delete": cmd_delete,
        "stats": cmd_stats,
        "export": cmd_export,
        "import": cmd_import,
        "help": print_help,
    }
    
    if command in commands:
        commands[command](args)
    else:
        print(f"未知命令: {command}")
        print_help()

if __name__ == "__main__":
    from datetime import datetime
    main()
