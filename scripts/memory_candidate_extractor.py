#!/usr/bin/env python3
"""
自动记忆提炼器 V1（候选层）

目标：
- 从一段文本中提取结构化候选项
- 不直接写 MEMORY.md / daily memory 主文件
- 先写到 memory/auto-candidates/YYYY-MM-DD.json
- 做基础去重，供后续任务中心 / 记忆归档复用

提炼类型：
- decision 决策
- todo 待办
- rule 规则
- progress 进展
- risk 风险/坑点
- blocked 阻塞
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
CANDIDATE_DIR = MEMORY_DIR / "auto-candidates"


@dataclass
class Candidate:
    id: str
    type: str
    content: str
    confidence: float
    source: str
    project: str
    created_at: str
    tags: List[str]
    dedupe_key: str
    state: str = "new"
    handled_at: str = ""
    task_id: str = ""


class MemoryCandidateExtractor:
    def __init__(self, workspace: Path = WORKSPACE):
        self.workspace = workspace
        self.candidate_dir = workspace / "memory" / "auto-candidates"
        self.candidate_dir.mkdir(parents=True, exist_ok=True)

    def extract(self, text: str, source: str = "manual", project: str = "default") -> List[Candidate]:
        text = text.strip()
        if not text:
            return []

        candidates: List[Candidate] = []
        candidates.extend(self._extract_decisions(text, source, project))
        candidates.extend(self._extract_todos(text, source, project))
        candidates.extend(self._extract_rules(text, source, project))
        candidates.extend(self._extract_progress(text, source, project))
        candidates.extend(self._extract_risks(text, source, project))
        candidates.extend(self._extract_blocked(text, source, project))
        return self._dedupe(candidates)

    def save_candidates(self, candidates: List[Candidate], day: Optional[str] = None) -> Path:
        if not day:
            day = datetime.now().strftime("%Y-%m-%d")
        filepath = self.candidate_dir / f"{day}.json"

        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"date": day, "version": 1, "items": []}

        for item in data.get("items", []):
            item.setdefault("state", "new")
            item.setdefault("handled_at", "")
            item.setdefault("task_id", "")

        existing_keys = {item.get("dedupe_key") for item in data.get("items", [])}
        new_items = []
        for c in candidates:
            item = asdict(c)
            item.setdefault("state", "new")
            item.setdefault("handled_at", "")
            item.setdefault("task_id", "")
            if item["dedupe_key"] not in existing_keys:
                new_items.append(item)
                existing_keys.add(item["dedupe_key"])

        data["items"].extend(new_items)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath

    def _make_candidate(self, type_: str, content: str, confidence: float, source: str, project: str, tags: Optional[List[str]] = None) -> Candidate:
        content = self._clean(content)
        dedupe_key = self._hash(f"{type_}|{content}")
        return Candidate(
            id=self._hash(f"{datetime.now().isoformat()}|{type_}|{content}")[:10],
            type=type_,
            content=content,
            confidence=confidence,
            source=source,
            project=project,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            tags=tags or [],
            dedupe_key=dedupe_key,
        )

    def _extract_decisions(self, text: str, source: str, project: str) -> List[Candidate]:
        patterns = [
            r"(?:决定|确定|以后|后面)用(.{2,80}?)(?:。|\n|$)",
            r"采用(.{2,80}?)(?:。|\n|$)",
            r"就按(.{2,80}?)(?:来|做|执行)?(?:。|\n|$)",
            r"结论[：:](.{2,100}?)(?:\n|$)",
        ]
        return self._extract_by_patterns(text, patterns, "decision", 0.86, source, project, ["memory", "decision"])

    def _extract_todos(self, text: str, source: str, project: str) -> List[Candidate]:
        patterns = [
            r"待办[：:](.{2,100}?)(?:。|\n|$)",
            r"TODO[：: ](.{2,100}?)(?:。|\n|$)",
            r"(?:需要|还要|后面要|记得|下一步)(.{2,60}?)(?:。|\n|$)",
            r"先把(.{2,60}?)(?:做了|落实|补上)(?:。|\n|$)",
        ]
        return self._extract_by_patterns(text, patterns, "todo", 0.83, source, project, ["memory", "todo"])

    def _extract_rules(self, text: str, source: str, project: str) -> List[Candidate]:
        patterns = [
            r"(?:规则|准则|铁律|原则)[：:](.{2,120}?)(?:\n|$)",
            r"(先[^。\n]{2,40}?再[^。\n]{2,40}?)(?:。|\n|$)",
            r"(以后[^。\n]{2,60}?不要[^。\n]{1,40}?)(?:。|\n|$)",
            r"(以后[^。\n]{2,60}?必须[^。\n]{1,40}?)(?:。|\n|$)",
            r"(以后[^。\n]{2,60}?优先[^。\n]{1,40}?)(?:。|\n|$)",
            r"(以后[^。\n]{2,60}?默认[^。\n]{1,40}?)(?:。|\n|$)",
        ]
        items = self._extract_by_patterns(text, patterns, "rule", 0.88, source, project, ["memory", "rule"])
        normalized = []
        for c in items:
            c.content = c.content.replace("  ", " ").strip()
            normalized.append(c)
        return normalized

    def _extract_progress(self, text: str, source: str, project: str) -> List[Candidate]:
        patterns = [
            r"((?:已经|已|刚刚)[^。\n]{2,80}?(?:完成|做好|落地|搞定)(?:了)?)(?:。|\n|$)",
            r"([^。\n]{2,80}?(?:已经完成|已经接好|已经可用|已经打通))(?:。|\n|$)",
            r"(当前[^。\n]{2,100}?(?:正常|可用|在跑))(?:。|\n|$)",
        ]
        return self._extract_by_patterns(text, patterns, "progress", 0.79, source, project, ["memory", "progress"])

    def _extract_risks(self, text: str, source: str, project: str) -> List[Candidate]:
        patterns = [
            r"风险[：:](.{2,120}?)(?:\n|$)",
            r"注意(.{2,80}?)(?:。|\n|$)",
            r"(不要[^。\n]{2,80}?)(?:。|\n|$)",
            r"(可能会[^。\n]{2,80}?)(?:。|\n|$)",
            r"(容易[^。\n]{2,80}?)(?:。|\n|$)",
        ]
        return self._extract_by_patterns(text, patterns, "risk", 0.76, source, project, ["memory", "risk"])

    def _extract_blocked(self, text: str, source: str, project: str) -> List[Candidate]:
        patterns = [
            r"卡在(.{2,80}?)(?:。|\n|$)",
            r"等(.{2,80}?)(?:确认|回复|处理)(?:。|\n|$)",
            r"先暂停(.{0,60}?)(?:。|\n|$)",
            r"阻塞[：:](.{2,100}?)(?:\n|$)",
        ]
        return self._extract_by_patterns(text, patterns, "blocked", 0.82, source, project, ["memory", "blocked"])

    def _extract_by_patterns(self, text: str, patterns: List[str], type_: str, confidence: float, source: str, project: str, tags: List[str]) -> List[Candidate]:
        out: List[Candidate] = []
        for pattern in patterns:
            for match in re.findall(pattern, text, flags=re.IGNORECASE):
                if isinstance(match, tuple):
                    content = "".join(part for part in match if part).strip()
                else:
                    content = str(match).strip()
                content = self._clean(content)
                if len(content) < 2:
                    continue
                out.append(self._make_candidate(type_, content, confidence, source, project, tags))
        return out

    def _dedupe(self, candidates: List[Candidate]) -> List[Candidate]:
        seen = set()
        out = []
        for c in candidates:
            if c.dedupe_key in seen:
                continue
            seen.add(c.dedupe_key)
            out.append(c)
        return out

    def _clean(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        text = text.strip(" -—–:：。；;，,\n\t")
        return text.strip()

    def _hash(self, text: str) -> str:
        return hashlib.sha1(text.encode("utf-8")).hexdigest()


def cmd_extract(args):
    extractor = MemoryCandidateExtractor()
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
        source = args.file
    else:
        text = args.text
        source = args.source
    candidates = extractor.extract(text, source=source, project=args.project)
    if args.save:
        path = extractor.save_candidates(candidates, day=args.day)
        print(f"✅ 已写入候选文件: {path}")
    print(json.dumps([asdict(c) for c in candidates], ensure_ascii=False, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(description="自动记忆提炼器 V1（候选层）")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("extract", help="提取候选项")
    p.add_argument("text", nargs="?", default="")
    p.add_argument("--file", default="")
    p.add_argument("--source", default="manual")
    p.add_argument("--project", default="default")
    p.add_argument("--day", default="")
    p.add_argument("--save", action="store_true")
    p.set_defaults(func=cmd_extract)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
