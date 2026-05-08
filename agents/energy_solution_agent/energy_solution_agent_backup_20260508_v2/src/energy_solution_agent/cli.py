from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .benchmark import run_benchmarks
from .engine import analyze_project
from .utils import read_json, write_json, write_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="energy-solution-agent")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze")
    analyze.add_argument("--input", required=True, help="Input JSON file")
    analyze.add_argument("--output", required=True, help="Output JSON file")
    analyze.add_argument("--report", help="Markdown report file")
    analyze.add_argument("--live-rules", action="store_true", help="Refresh province rules from configured official links")
    benchmark = sub.add_parser("benchmark")
    benchmark.add_argument("--examples", required=True, help="Example JSON directory")
    benchmark.add_argument("--output", help="Benchmark summary JSON file")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "analyze":
        try:
            payload = read_json(Path(args.input))
        except Exception as exc:
            print(f"Error reading input file {args.input}: {exc}", file=sys.stderr)
            return 1
        try:
            output, diagnostics, report = analyze_project(payload, enable_live_rules=args.live_rules)
        except Exception as exc:
            print(f"Error during analysis: {exc}", file=sys.stderr)
            return 1
        write_json(Path(args.output), output, pretty=True)
        if args.report:
            write_text(Path(args.report), report)
        else:
            print(report)
        if diagnostics.get("missing_fields", []):
            return 2
        return 0
    if args.command == "benchmark":
        rows = run_benchmarks(Path(args.examples))
        if args.output:
            write_json(Path(args.output), rows, pretty=True)
        else:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 3 if rows.get("summary", {}).get("has_errors") else 0
    return 1
