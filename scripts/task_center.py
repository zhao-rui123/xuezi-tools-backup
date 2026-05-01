#!/usr/bin/env python3
"""
统一任务中心（最小可用版）

功能：
- add: 新增任务
- list: 列出任务
- today: 查看今日未完成任务
- block: 标记阻塞
- doing: 标记进行中
- done: 标记完成
- reopen: 重新打开
- archive: 归档
- show: 查看单个任务

存储：workspace/projects/task-center/tasks.json
原则：先做最小可用，不接数据库，不改现有主链路。
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional

WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
DATA_DIR = WORKSPACE / "projects" / "task-center"
DATA_FILE = DATA_DIR / "tasks.json"

VALID_STATUS = {
    "todo",
    "doing",
    "blocked",
    "done",
    "archived",
}


@dataclass
class Task:
    id: str
    title: str
    status: str = "todo"
    priority: str = "medium"
    project: str = "default"
    source: str = "manual"
    notes: str = ""
    due_date: str = ""     # YYYY-MM-DD
    created_at: str = ""
    updated_at: str = ""
    completed_at: str = ""
    blocked_reason: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TaskStore:
    def __init__(self, path: Path = DATA_FILE):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save({"version": 1, "tasks": []})

    def _load(self) -> Dict[str, Any]:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: Dict[str, Any]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def list_tasks(self) -> List[Task]:
        data = self._load()
        return [Task(**item) for item in data.get("tasks", [])]

    def save_tasks(self, tasks: List[Task]) -> None:
        data = {"version": 1, "tasks": [asdict(t) for t in tasks]}
        self._save(data)

    def get(self, task_id: str) -> Optional[Task]:
        for task in self.list_tasks():
            if task.id == task_id:
                return task
        return None


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str() -> str:
    return date.today().strftime("%Y-%m-%d")


def short_id() -> str:
    return uuid.uuid4().hex[:8]


def render_task(task: Task) -> str:
    bits = [
        f"[{task.id}] {task.title}",
        f"状态={task.status}",
        f"优先级={task.priority}",
        f"项目={task.project}",
    ]
    if task.due_date:
        bits.append(f"截止={task.due_date}")
    if task.blocked_reason:
        bits.append(f"阻塞={task.blocked_reason}")
    if task.tags:
        bits.append(f"标签={','.join(task.tags)}")
    return " | ".join(bits)


def cmd_add(args):
    store = TaskStore()
    tasks = store.list_tasks()
    task = Task(
        id=short_id(),
        title=args.title.strip(),
        status="todo",
        priority=args.priority,
        project=args.project,
        source=args.source,
        notes=args.notes.strip(),
        due_date=args.due_date.strip(),
        created_at=now_str(),
        updated_at=now_str(),
        tags=[t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else [],
    )
    tasks.append(task)
    store.save_tasks(tasks)
    print(f"✅ 已添加任务: {render_task(task)}")


def cmd_list(args):
    store = TaskStore()
    tasks = store.list_tasks()

    if args.status:
        tasks = [t for t in tasks if t.status == args.status]
    if args.project:
        tasks = [t for t in tasks if t.project == args.project]
    if not args.all:
        tasks = [t for t in tasks if t.status != "archived"]

    tasks.sort(key=lambda t: (t.status, t.priority, t.created_at), reverse=False)

    if not tasks:
        print("暂无任务")
        return

    for t in tasks:
        print(render_task(t))


def cmd_today(args):
    store = TaskStore()
    tasks = store.list_tasks()
    today = today_str()

    picked = []
    for t in tasks:
        if t.status in {"done", "archived"}:
            continue
        if t.due_date == today or t.priority == "high" or t.status in {"doing", "blocked"}:
            picked.append(t)

    if not picked:
        print("今天没有高优先级/到期/进行中的未完成任务 ✅")
        return

    print("📋 今日关注任务")
    for t in picked:
        print(render_task(t))


def update_status(task_id: str, status: str, note: str = "", blocked_reason: str = ""):
    if status not in VALID_STATUS:
        raise ValueError(f"invalid status: {status}")

    store = TaskStore()
    tasks = store.list_tasks()
    found = None
    for t in tasks:
        if t.id == task_id:
            t.status = status
            t.updated_at = now_str()
            if note:
                t.notes = (t.notes + "\n" if t.notes else "") + f"[{t.updated_at}] {note}"
            if blocked_reason:
                t.blocked_reason = blocked_reason
            if status == "done":
                t.completed_at = t.updated_at
                t.blocked_reason = ""
            if status in {"todo", "doing", "reopened"}:
                t.completed_at = ""
            found = t
            break
    if not found:
        print(f"❌ 未找到任务: {task_id}")
        sys.exit(1)
    store.save_tasks(tasks)
    print(f"✅ 已更新: {render_task(found)}")


def cmd_doing(args):
    update_status(args.id, "doing", note=args.note)


def cmd_done(args):
    update_status(args.id, "done", note=args.note)


def cmd_reopen(args):
    update_status(args.id, "todo", note=args.note)


def cmd_archive(args):
    update_status(args.id, "archived", note=args.note)


def cmd_block(args):
    update_status(args.id, "blocked", note=args.note, blocked_reason=args.reason.strip())


def cmd_show(args):
    store = TaskStore()
    task = store.get(args.id)
    if not task:
        print(f"❌ 未找到任务: {args.id}")
        sys.exit(1)
    print(json.dumps(asdict(task), ensure_ascii=False, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(description="统一任务中心")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add", help="新增任务")
    p.add_argument("title")
    p.add_argument("--priority", default="medium", choices=["low", "medium", "high"])
    p.add_argument("--project", default="default")
    p.add_argument("--source", default="manual")
    p.add_argument("--notes", default="")
    p.add_argument("--due-date", default="")
    p.add_argument("--tags", default="")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("list", help="列出任务")
    p.add_argument("--status", choices=sorted(VALID_STATUS))
    p.add_argument("--project", default="")
    p.add_argument("--all", action="store_true")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("today", help="查看今日关注任务")
    p.set_defaults(func=cmd_today)

    for name, func in [
        ("doing", cmd_doing),
        ("done", cmd_done),
        ("reopen", cmd_reopen),
        ("archive", cmd_archive),
    ]:
        p = sub.add_parser(name, help=f"标记{name}")
        p.add_argument("id")
        p.add_argument("--note", default="")
        p.set_defaults(func=func)

    p = sub.add_parser("block", help="标记阻塞")
    p.add_argument("id")
    p.add_argument("reason")
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_block)

    p = sub.add_parser("show", help="查看任务详情")
    p.add_argument("id")
    p.set_defaults(func=cmd_show)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
