#!/usr/bin/env python3
"""
候选状态管理器

功能：
- list: 查看候选项（按 state/type 过滤）
- inbox: 查看待处理候选（state=new）
- mark-imported: 标记为已导入
- mark-ignored: 标记为忽略
- mark-batch-ignored: 按类型批量忽略
- stats: 统计候选状态
- cleanup-preview: 查看候选整理预览（不删原始数据）
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
CANDIDATE_DIR = WORKSPACE / "memory" / "auto-candidates"


def candidate_file(day: str) -> Path:
    return CANDIDATE_DIR / f"{day}.json"


def load(day: str) -> dict:
    path = candidate_file(day)
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def save(day: str, data: dict):
    path = candidate_file(day)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def cmd_list(args):
    data = load(args.day)
    items = data.get("items", [])
    if args.state:
        items = [x for x in items if x.get("state", "new") == args.state]
    if args.type:
        items = [x for x in items if x.get("type") == args.type]
    for item in items:
        print(f"[{item.get('id')}] {item.get('type')} | state={item.get('state', 'new')} | {item.get('content')}")


def cmd_inbox(args):
    data = load(args.day)
    items = [x for x in data.get("items", []) if x.get("state", "new") == "new"]
    if args.type:
        items = [x for x in items if x.get("type") == args.type]
    print(f"📥 待处理候选 ({args.day}) | 共 {len(items)} 条")
    for item in items:
        print(f"[{item.get('id')}] {item.get('type')} | {item.get('content')}")


def mark(day: str, dedupe_key: str, state: str, task_id: str = ""):
    data = load(day)
    updated = False
    for item in data.get("items", []):
        if item.get("dedupe_key") == dedupe_key:
            item["state"] = state
            item["handled_at"] = now_str()
            if task_id:
                item["task_id"] = task_id
            updated = True
            break
    save(day, data)
    return updated


def cmd_mark_imported(args):
    ok = mark(args.day, args.dedupe_key, "imported", task_id=args.task_id)
    print("✅ 已标记 imported" if ok else "❌ 未找到候选")


def cmd_mark_ignored(args):
    ok = mark(args.day, args.dedupe_key, "ignored")
    print("✅ 已标记 ignored" if ok else "❌ 未找到候选")


def cmd_mark_batch_ignored(args):
    data = load(args.day)
    count = 0
    for item in data.get("items", []):
        if item.get("state", "new") != "new":
            continue
        if args.type and item.get("type") != args.type:
            continue
        item["state"] = "ignored"
        item["handled_at"] = now_str()
        count += 1
    save(args.day, data)
    print(f"✅ 已批量忽略 {count} 条")


def cmd_stats(args):
    data = load(args.day)
    stats = {}
    by_type = {}
    for item in data.get("items", []):
        state = item.get("state", "new")
        stats[state] = stats.get(state, 0) + 1
        t = item.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    print(json.dumps({"by_state": stats, "by_type": by_type}, ensure_ascii=False, indent=2))


def cmd_cleanup_preview(args):
    data = load(args.day)
    items = data.get("items", [])
    new_items = [x for x in items if x.get("state", "new") == "new"]
    imported = [x for x in items if x.get("state", "new") == "imported"]
    ignored = [x for x in items if x.get("state", "new") == "ignored"]

    print(f"🧹 候选整理预览 ({args.day})")
    print(f"- new: {len(new_items)}")
    print(f"- imported: {len(imported)}")
    print(f"- ignored: {len(ignored)}")

    def show_group(title, group):
        if not group:
            return
        print(f"\n{title}")
        type_counter = {}
        for item in group:
            t = item.get('type', 'unknown')
            type_counter[t] = type_counter.get(t, 0) + 1
        for k, v in sorted(type_counter.items()):
            print(f"- {k}: {v}")

    show_group("📥 待处理分组", new_items)
    show_group("✅ 已导入分组", imported)
    show_group("🫥 已忽略分组", ignored)


def build_parser():
    parser = argparse.ArgumentParser(description="候选状态管理器")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list")
    p.add_argument("--day", required=True)
    p.add_argument("--state", default="")
    p.add_argument("--type", default="")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("inbox")
    p.add_argument("--day", required=True)
    p.add_argument("--type", default="")
    p.set_defaults(func=cmd_inbox)

    p = sub.add_parser("mark-imported")
    p.add_argument("--day", required=True)
    p.add_argument("--dedupe-key", required=True)
    p.add_argument("--task-id", default="")
    p.set_defaults(func=cmd_mark_imported)

    p = sub.add_parser("mark-ignored")
    p.add_argument("--day", required=True)
    p.add_argument("--dedupe-key", required=True)
    p.set_defaults(func=cmd_mark_ignored)

    p = sub.add_parser("mark-batch-ignored")
    p.add_argument("--day", required=True)
    p.add_argument("--type", default="")
    p.set_defaults(func=cmd_mark_batch_ignored)

    p = sub.add_parser("stats")
    p.add_argument("--day", required=True)
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("cleanup-preview")
    p.add_argument("--day", required=True)
    p.set_defaults(func=cmd_cleanup_preview)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
