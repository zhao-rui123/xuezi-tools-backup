#!/usr/bin/env python3
"""
会话快照工具 - 增强版
从记忆文件提取当日任务，让快照内容不再为空
"""
import json
import re
import sys as _sys
from pathlib import Path
from datetime import datetime

SNAPSHOT_DIR = Path.home() / ".openclaw" / "workspace" / "memory"
SNAP_FILE = SNAPSHOT_DIR / "snapshots"

def extract_tasks_from_memory():
    """从今日记忆文件提取关键任务信息"""
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = SNAPSHOT_DIR / f"{today}.md"

    if not memory_file.exists():
        return {"date": today, "tasks": [], "summary": "无记忆文件"}

    with open(memory_file, "r", encoding="utf-8") as f:
        content = f.read()

    tasks = []

    # 提取所有 [UPDATE] 区块的内容作为任务
    update_blocks = re.findall(r'### \[UPDATE\][^\n]*\n+(.+?)(?=\n###|\n##|\Z)', content, re.DOTALL)
    for block in update_blocks[-3:]:  # 最近3个update
        lines = [l.strip().lstrip('-*') for l in block.strip().split('\n') if l.strip()]
        for line in lines[:3]:
            line = line.strip()
            if line and len(line) > 5:
                tasks.append(line[:120])
                break

    # 提取 [TODO] 完成项
    done_items = re.findall(r'- \[x\] (.+)', content)
    for item in done_items[-3:]:
        tasks.append("[完成] " + item[:100])

    # 提取 [PROJECT] 项目
    proj_items = re.findall(r'\*\*.*?\*\*.*?(?:\n|$)', content)
    for item in proj_items[-2:]:
        clean = re.sub(r'\*\*(.+?)\*\*', r'\1', item).strip()
        if clean and len(clean) > 5:
            tasks.append(clean[:120])

    summary = tasks[-1] if tasks else "无记录"
    return {
        "date": today,
        "summary": summary,
        "tasks": tasks[-5:],
        "task_count": len(tasks),
        "timestamp": datetime.now().isoformat(),
        "memory_file": str(memory_file)
    }


def save_snapshot(task=None):
    """保存当前任务状态"""
    today = datetime.now().strftime("%Y-%m-%d")
    snapshot_file = SNAPSHOT_DIR / f"{today}.json"

    info = extract_tasks_from_memory()
    manual = task if task and task != "未标注任务" else None

    data = {
        "date": today,
        "summary": manual if manual else info.get("summary", "无标注"),
        "manual_note": manual,
        "from_memory": info.get("tasks", []),
        "task_count": info.get("task_count", 0),
        "timestamp": datetime.now().isoformat()
    }
    data = {k: v for k, v in data.items() if v is not None and v != []}

    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    summary = data.get("summary", "")[:60]
    print(f"已保存: {summary}")
    return True


def load_snapshot():
    """加载最近的快照"""
    today = datetime.now().strftime("%Y-%m-%d")
    today_file = SNAPSHOT_DIR / f"{today}.json"

    if today_file.exists():
        with open(today_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"恢复今日 ({today}): {data.get('summary', '无描述')[:80]}")
        if data.get("from_memory"):
            print(f"  记忆文件任务数: {data.get('task_count', 0)}")
        return data

    # 找最近的其他快照
    files = sorted(SNAPSHOT_DIR.glob("????-??-??.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            print(f"恢复: {data.get('date', f.stem)} - {data.get('summary', '无描述')[:60]}")
            return data
        except Exception:
            continue

    print("无快照，尝试从记忆文件恢复...")
    info = extract_tasks_from_memory()
    if info.get("tasks"):
        print(f"从记忆文件恢复了 {len(info['tasks'])} 条任务")
        return info
    return None


def main():
    if len(_sys.argv) < 2:
        print("Usage: session-snapshot.py <save|load> [task]")
        _sys.exit(1)

    action = _sys.argv[1]

    if action == "save":
        task = _sys.argv[2] if len(_sys.argv) > 2 else "未标注任务"
        save_snapshot(task)
    elif action == "load":
        result = load_snapshot()
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Unknown action: {action}")


if __name__ == "__main__":
    main()
