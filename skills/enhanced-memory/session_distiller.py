#!/usr/bin/env python3
"""
会话记忆提取器 - 与 enhanced-memory 集成
当用户执行 /new 时，自动提取上一个会话的关键信息并存储
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 导入 enhanced_memory
import importlib.util
skill_path = Path(__file__).parent.parent / "enhanced-memory" / "__init__.py"
spec = importlib.util.spec_from_file_location("enhanced_memory", skill_path)
enhanced_memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(enhanced_memory)

# 会话快照路径
SNAPSHOT_DIR = Path("~/.openclaw/workspace/memory/snapshots").expanduser()

def load_latest_snapshot():
    """加载最新的会话快照"""
    if not SNAPSHOT_DIR.exists():
        return None
    
    snapshots = list(SNAPSHOT_DIR.glob("session_*.json"))
    if not snapshots:
        return None
    
    # 按修改时间排序
    latest = max(snapshots, key=lambda p: p.stat().st_mtime)
    
    try:
        with open(latest, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def extract_key_info(snapshot):
    """从快照中提取关键信息"""
    info = {
        "timestamp": snapshot.get("timestamp", ""),
        "current_task": snapshot.get("current_task", ""),
        "pending_items": snapshot.get("pending_items", []),
        "key_context": snapshot.get("key_context", {}),
    }
    return info

def distill_memories(info):
    """提炼记忆条目"""
    memories = []
    
    # 1. 任务记忆
    if info["current_task"]:
        memories.append({
            "text": f"上次会话任务: {info['current_task']}",
            "category": "fact",
            "importance": 0.7
        })
    
    # 2. 待办事项
    for item in info["pending_items"]:
        memories.append({
            "text": f"待办: {item}",
            "category": "decision",
            "importance": 0.8
        })
    
    # 3. 关键上下文
    for key, value in info["key_context"].items():
        memories.append({
            "text": f"{key}: {value}",
            "category": "fact",
            "importance": 0.6
        })
    
    return memories

def store_session_memories(memories, scope="global"):
    """存储会话记忆"""
    mem = enhanced_memory.get_memory()
    stored_ids = []
    
    for m in memories:
        mem_id = mem.store(
            text=m["text"],
            category=m["category"],
            importance=m["importance"],
            scope=scope,
            metadata={"source": "session_snapshot", "timestamp": datetime.now().isoformat()}
        )
        if mem_id:
            stored_ids.append(mem_id)
    
    return stored_ids

def main():
    """主函数 - 在 /new 时调用"""
    print("📸 正在提取上一个会话的记忆...")
    
    # 加载快照
    snapshot = load_latest_snapshot()
    if not snapshot:
        print("⚠️ 没有找到会话快照")
        return
    
    print(f"📄 加载快照: {snapshot.get('timestamp', '未知时间')}")
    
    # 提取信息
    info = extract_key_info(snapshot)
    
    # 提炼记忆
    memories = distill_memories(info)
    
    if not memories:
        print("ℹ️ 没有需要提取的关键信息")
        return
    
    # 存储记忆
    stored_ids = store_session_memories(memories)
    
    print(f"✅ 已提取并存储 {len(stored_ids)} 条记忆:")
    for mem_id in stored_ids:
        print(f"  - {mem_id}")

if __name__ == "__main__":
    main()
