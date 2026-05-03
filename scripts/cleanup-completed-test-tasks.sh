#!/usr/bin/env bash
set -euo pipefail
cd /Users/zhaoruicn/.openclaw/workspace
ARCHIVE_DIR="logs/agent-screen/archived/2026-05-03-cleanup"
mkdir -p "$ARCHIVE_DIR"
for task in cc-min-test cc-wrapper-test codex-wrapper-test; do
  bash scripts/agent-screen-clean.sh "$task" || true
done
mv logs/agent-screen/cc-min-test*.meta "$ARCHIVE_DIR"/ 2>/dev/null || true
mv logs/agent-screen/cc-min-test*.prompt.txt "$ARCHIVE_DIR"/ 2>/dev/null || true
mv logs/agent-screen/cc-wrapper-test*.meta "$ARCHIVE_DIR"/ 2>/dev/null || true
mv logs/agent-screen/cc-wrapper-test*.prompt.txt "$ARCHIVE_DIR"/ 2>/dev/null || true
mv logs/agent-screen/codex-wrapper-test*.meta "$ARCHIVE_DIR"/ 2>/dev/null || true
mv logs/agent-screen/codex-wrapper-test*.prompt.txt "$ARCHIVE_DIR"/ 2>/dev/null || true
python3 scripts/clean_test_result_card.py --task cc-min-test --save >/dev/null
python3 scripts/clean_test_result_card.py --task cc-wrapper-test --save >/dev/null
python3 scripts/clean_test_result_card.py --task codex-wrapper-test --save >/dev/null
python3 scripts/clean_test_tasks_panel_card.py >/dev/null
python3 scripts/screen_detail_panel_card.py >/dev/null
printf 'archive=%s\n' "$ARCHIVE_DIR"
ls -1 "$ARCHIVE_DIR" | wc -l
