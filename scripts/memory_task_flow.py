#!/usr/bin/env python3
"""
记忆提炼 → 任务中心 自动化入口 V1

一步完成：
1. 提炼候选
2. 保存候选
3. 导入任务中心
4. 输出 digest 摘要

目标：作为后续接入对话、日志、daily memory 的统一入口。
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from memory_candidate_extractor import MemoryCandidateExtractor
from task_center import TaskStore, Task, today_str, now_str, short_id, render_task
from candidate_state_manager import mark as mark_candidate_state

WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")


def import_candidates_from_items(items: List[dict], candidate_file: Path, project_override: str = "", policy: str = "default", high_priority_todo: bool = False) -> List[Task]:
    store = TaskStore()
    tasks = store.list_tasks()
    existing_dedupe = {t.dedupe_key for t in tasks if t.dedupe_key}
    imported: List[Task] = []

    for item in items:
        item_type = item.get("type")
        dedupe_key = item.get("dedupe_key", "")
        if dedupe_key and dedupe_key in existing_dedupe:
            continue

        if policy == "default":
            if item_type not in {"todo", "blocked", "progress"}:
                continue
        elif policy == "all-tasklike":
            if item_type not in {"todo", "blocked", "progress", "risk"}:
                continue
        else:
            raise ValueError(f"未知 policy: {policy}")

        status = "todo"
        blocked_reason = ""
        priority = "medium"
        title = item.get("content", "").strip()
        tags = list(item.get("tags", [])) + ["auto-import", "flow-v1"]

        if item_type == "blocked":
            status = "blocked"
            blocked_reason = title
            priority = "high"
        elif item_type == "progress":
            status = "doing"
            priority = "medium"
            title = f"跟进：{title}"
        elif item_type == "todo":
            status = "todo"
            priority = "high" if high_priority_todo else "medium"
        elif item_type == "risk":
            status = "blocked"
            blocked_reason = title
            priority = "high"
            title = f"风险关注：{title}"

        task = Task(
            id=short_id(),
            title=title,
            status=status,
            priority=priority,
            project=project_override or item.get("project", "default"),
            source=item.get("source", "flow"),
            origin_type=item_type,
            source_ref=str(candidate_file),
            dedupe_key=dedupe_key,
            notes=f"从自动化入口导入 | confidence={item.get('confidence', '')} | policy={policy}",
            due_date="",
            created_at=now_str(),
            updated_at=now_str(),
            completed_at="",
            blocked_reason=blocked_reason,
            tags=tags,
        )
        tasks.append(task)
        imported.append(task)
        if dedupe_key:
            existing_dedupe.add(dedupe_key)
            try:
                day = candidate_file.stem
                mark_candidate_state(day, dedupe_key, "imported", task_id=task.id)
            except Exception:
                pass

    store.save_tasks(tasks)
    return imported


def build_digest(day: str) -> str:
    store = TaskStore()
    tasks = store.list_tasks()
    today_tasks = [t for t in tasks if (t.created_at or "").startswith(day)]
    auto_tasks = [t for t in today_tasks if "auto-import" in (t.tags or [])]
    blocked = [t for t in tasks if t.status == "blocked" and t.status != "archived"]
    doing = [t for t in tasks if t.status == "doing" and t.status != "archived"]
    todo_high = [t for t in tasks if t.status == "todo" and t.priority == "high"]

    lines = [f"📦 任务中心整理视图 ({day})"]
    lines.append(f"- 今日新增任务: {len(today_tasks)}")
    lines.append(f"- 今日自动导入: {len(auto_tasks)}")
    lines.append(f"- 当前阻塞: {len(blocked)}")
    lines.append(f"- 当前进行中: {len(doing)}")
    lines.append(f"- 当前高优先级待办: {len(todo_high)}")

    if auto_tasks:
        lines.append("\n🤖 今日自动导入")
        for t in auto_tasks:
            lines.append(render_task(t))
    if blocked:
        lines.append("\n⛔ 当前阻塞")
        for t in blocked:
            lines.append(render_task(t))
    if doing:
        lines.append("\n🚧 当前进行中")
        for t in doing:
            lines.append(render_task(t))
    return "\n".join(lines)


def cmd_run(args):
    extractor = MemoryCandidateExtractor()
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
        source = args.file
    else:
        text = args.text
        source = args.source

    day = args.day or today_str()
    candidates = extractor.extract(text, source=source, project=args.project)
    candidate_file = extractor.save_candidates(candidates, day=day)
    imported = import_candidates_from_items(
        [asdict(c) for c in candidates],
        candidate_file=candidate_file,
        project_override=args.project,
        policy=args.policy,
        high_priority_todo=args.high_priority_todo,
    )

    print(f"✅ 候选文件: {candidate_file}")
    print(f"✅ 本次提炼候选: {len(candidates)} 条")
    print(f"✅ 本次导入任务: {len(imported)} 条")

    if imported:
        print("\n🧩 新导入任务")
        for t in imported:
            print(render_task(t))

    if args.show_candidates:
        print("\n📝 本次候选")
        print(json.dumps([asdict(c) for c in candidates], ensure_ascii=False, indent=2))

    print("\n" + build_digest(day))


def build_parser():
    parser = argparse.ArgumentParser(description="记忆提炼→任务中心 自动化入口 V1")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("run", help="运行完整链路")
    p.add_argument("text", nargs="?", default="")
    p.add_argument("--file", default="")
    p.add_argument("--source", default="manual")
    p.add_argument("--project", default="default")
    p.add_argument("--day", default="")
    p.add_argument("--policy", default="default", choices=["default", "all-tasklike"])
    p.add_argument("--high-priority-todo", action="store_true")
    p.add_argument("--show-candidates", action="store_true")
    p.set_defaults(func=cmd_run)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
