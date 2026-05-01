#!/usr/bin/env python3
"""
Markdown 工作台摘要生成器

输出一份可读的工作台摘要，作为后续飞书卡片层的数据基础。
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
TASK_FILE = WORKSPACE / "projects" / "task-center" / "tasks.json"
CANDIDATE_DIR = WORKSPACE / "memory" / "auto-candidates"
OUTPUT_DIR = WORKSPACE / "summary" / "dashboards"


def today_str() -> str:
    return date.today().strftime("%Y-%m-%d")


def load_tasks():
    if not TASK_FILE.exists():
        return []
    return json.loads(TASK_FILE.read_text(encoding="utf-8")).get("tasks", [])


def load_candidates(day: str):
    path = CANDIDATE_DIR / f"{day}.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    for item in items:
        item.setdefault("state", "new")
        item.setdefault("handled_at", "")
        item.setdefault("task_id", "")
    return items


def render_task_line(task: dict) -> str:
    extra = []
    if task.get("blocked_reason"):
        extra.append(f"阻塞={task['blocked_reason']}")
    if task.get("priority"):
        extra.append(f"优先级={task['priority']}")
    if task.get("origin_type"):
        extra.append(f"来源={task['origin_type']}")
    extra_text = " | ".join(extra)
    return f"- [{task.get('id')}] {task.get('title')}" + (f" ({extra_text})" if extra_text else "")


def render_candidate_line(item: dict) -> str:
    return f"- [{item.get('id')}] {item.get('type')} | {item.get('content')}"


def build_dashboard(day: str) -> str:
    tasks = load_tasks()
    candidates = load_candidates(day)

    by_state = Counter(x.get("state", "new") for x in candidates)
    by_type = Counter(x.get("type", "unknown") for x in candidates)

    inbox = [x for x in candidates if x.get("state", "new") == "new"]
    blocked = [t for t in tasks if t.get("status") == "blocked"]
    doing = [t for t in tasks if t.get("status") == "doing"]
    todo_high = [t for t in tasks if t.get("status") == "todo" and t.get("priority") == "high"]
    auto_today = [t for t in tasks if (t.get("created_at", "").startswith(day) and "auto-import" in (t.get("tags") or []))]

    lines = [f"# 工作台摘要 - {day}", ""]

    lines.append("## 1. 候选状态统计")
    lines.append(f"- new: {by_state.get('new', 0)}")
    lines.append(f"- imported: {by_state.get('imported', 0)}")
    lines.append(f"- ignored: {by_state.get('ignored', 0)}")
    lines.append("")

    lines.append("## 2. 候选类型分布")
    for k, v in sorted(by_type.items()):
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## 3. 待处理候选 inbox")
    if inbox:
        for item in inbox:
            lines.append(render_candidate_line(item))
    else:
        lines.append("- 无")
    lines.append("")

    lines.append("## 4. 当前阻塞任务")
    if blocked:
        for t in blocked:
            lines.append(render_task_line(t))
    else:
        lines.append("- 无")
    lines.append("")

    lines.append("## 5. 当前进行中任务")
    if doing:
        for t in doing:
            lines.append(render_task_line(t))
    else:
        lines.append("- 无")
    lines.append("")

    lines.append("## 6. 高优先级待办")
    if todo_high:
        for t in todo_high:
            lines.append(render_task_line(t))
    else:
        lines.append("- 无")
    lines.append("")

    lines.append("## 7. 今日自动导入任务")
    if auto_today:
        for t in auto_today:
            lines.append(render_task_line(t))
    else:
        lines.append("- 无")
    lines.append("")

    return "\n".join(lines)


def cmd_generate(args):
    day = args.day or today_str()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    content = build_dashboard(day)
    out = OUTPUT_DIR / f"{day}-dashboard.md"
    out.write_text(content, encoding="utf-8")
    print(f"✅ 已生成: {out}")
    if args.print:
        print("\n" + content)


def build_parser():
    parser = argparse.ArgumentParser(description="Markdown 工作台摘要生成器")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("generate")
    p.add_argument("--day", default="")
    p.add_argument("--print", action="store_true")
    p.set_defaults(func=cmd_generate)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
