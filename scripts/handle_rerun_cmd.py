#!/usr/bin/env python3
"""
命令处理入口：收到 rerun execute <task> 时自动调用
"""
import subprocess, json, sys

TASK_ALLOWED = {'cc-min-test','cc-wrapper-test','codex-wrapper-test'}

cmd = sys.argv[1] if len(sys.argv) > 1 else ''
if cmd.startswith('rerun execute '):
    task = cmd.split('rerun execute ',1)[1].strip()
    if task not in TASK_ALLOWED:
        print(f'❌ 不允许重跑: {task}，仅限 {TASK_ALLOWED}')
        sys.exit(1)
    result = subprocess.run(
        ['bash', '/Users/zhaoruicn/.openclaw/workspace/scripts/rerun-test-task-result.sh', task],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    sys.exit(result.returncode)
else:
    print(f'未知命令: {cmd}')
    sys.exit(1)
