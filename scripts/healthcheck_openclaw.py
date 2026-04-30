#!/usr/bin/env python3
"""
OpenClaw 统一健康检查 v1
只读检查，不做系统修改。

检查项：
1. OpenClaw gateway / channel / tasks 摘要
2. Tailscale 在线状态
3. 关键定时任务最近执行情况
4. Claude / Codex 本地入口可用性
5. 磁盘 / 内存资源
6. Git 工作区状态
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
NOW = datetime.now()
REMOTE_HOST = "root@43.108.18.71"
REMOTE_SSH_KEY = str(Path.home() / ".ssh/id_ed25519")

LOG_TASKS = [
    ("股票推送", Path("/tmp/stock_push.log"), "16:30", 48),
    ("每日备份", Path("/tmp/backup_cron.log"), "22:00", 24),
    ("云端同步", Path("/tmp/cloud-backup.log"), "22:35", 24),
    ("会话快照", Path("/tmp/session-snapshot.log"), "每10分钟", 1),
]


@dataclass
class CheckItem:
    name: str
    status: str  # ok warn fail info
    summary: str
    detail: Optional[str] = None


def run(cmd: List[str], timeout: int = 20, cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd) if cwd else None,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def run_shell(command: str, timeout: int = 20) -> Tuple[int, str, str]:
    try:
        proc = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def emoji(status: str) -> str:
    return {
        "ok": "✅",
        "warn": "⚠️",
        "fail": "❌",
        "info": "ℹ️",
    }.get(status, "•")


def parse_openclaw_status() -> List[CheckItem]:
    code, out, err = run(["openclaw", "status"], timeout=30, cwd=WORKSPACE)
    if code != 0:
        return [CheckItem("OpenClaw 状态", "fail", "openclaw status 执行失败", err or out)]

    items: List[CheckItem] = []
    text = out

    gateway_line = next((line for line in text.splitlines() if "│ Gateway service" in line), "")
    tailscale_line = next((line for line in text.splitlines() if "│ Tailscale" in line), "")
    update_line = next((line for line in text.splitlines() if "│ Update" in line), "")
    tasks_line = next((line for line in text.splitlines() if "│ Tasks" in line), "")
    channels_line = next((line for line in text.splitlines() if "│ Feishu" in line), "")

    if "running" in gateway_line.lower() or "active" in gateway_line.lower():
        items.append(CheckItem("Gateway", "ok", "LaunchAgent 已加载且运行中", gateway_line.strip()))
    else:
        items.append(CheckItem("Gateway", "fail", "Gateway 看起来不在正常运行", gateway_line.strip() or text[:400]))

    if tailscale_line:
        tail_text = tailscale_line.split("│")[-2].strip() if tailscale_line.count("│") >= 2 else tailscale_line
        if tail_text.lower() == "off":
            items.append(CheckItem("OpenClaw 视角 Tailscale", "warn", "openclaw status 里显示 Tailscale=off", tailscale_line.strip()))
        else:
            items.append(CheckItem("OpenClaw 视角 Tailscale", "ok", tail_text, tailscale_line.strip()))

    if channels_line:
        if "OK" in channels_line:
            items.append(CheckItem("Feishu 通道", "ok", "Feishu 通道正常", channels_line.strip()))
        else:
            items.append(CheckItem("Feishu 通道", "warn", "Feishu 通道需要关注", channels_line.strip()))

    if tasks_line:
        m = re.search(r"(\d+) active .*? (\d+) running .*? (\d+) error .*? (\d+) warn", tasks_line)
        if m:
            active, running, errors, warns = map(int, m.groups())
            status = "ok" if errors == 0 else "warn"
            items.append(CheckItem("任务系统", status, f"{active} active / {running} running / {errors} error / {warns} warn", tasks_line.strip()))
        else:
            items.append(CheckItem("任务系统", "info", tasks_line.strip(), None))

    if update_line and "available" in update_line.lower():
        items.append(CheckItem("版本更新", "warn", "发现 OpenClaw 可更新版本", update_line.strip()))
    elif update_line:
        items.append(CheckItem("版本更新", "ok", "当前无明显更新提示", update_line.strip()))

    return items


def check_tailscale_runtime() -> CheckItem:
    code, out, err = run(["tailscale", "status"], timeout=20)
    if code != 0:
        return CheckItem("Tailscale 运行态", "fail", "tailscale status 执行失败", err or out)

    lines = [line for line in out.splitlines() if line.strip()]
    online = any("cnmac-mini" in line for line in lines)
    offline_count = sum(1 for line in lines if "offline" in line.lower())
    summary = "本机在线" if online else "未看到本机在线记录"
    detail = f"设备数 {len(lines)}，离线 {offline_count}"
    status = "ok" if online else "warn"
    return CheckItem("Tailscale 运行态", status, summary, detail)


def check_log_task(name: str, path: Path, schedule: str, freshness_hours: int) -> CheckItem:
    if not path.exists():
        return CheckItem(name, "fail", f"日志不存在：{path}")

    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    age_hours = (NOW - mtime).total_seconds() / 3600
    tail = ""
    try:
        tail = "\n".join(path.read_text(errors="ignore").splitlines()[-3:])
    except Exception:
        pass

    if age_hours <= freshness_hours:
        status = "ok"
        summary = f"最近更新 {mtime.strftime('%m-%d %H:%M')}（计划 {schedule}）"
    else:
        status = "warn"
        summary = f"最后更新较久：{mtime.strftime('%m-%d %H:%M')}（计划 {schedule}）"

    if "失败" in tail or "❌" in tail.lower() or "error" in tail.lower():
        status = "warn"
    return CheckItem(name, status, summary, tail or str(path))


def check_exec_entry(name: str, command: str) -> CheckItem:
    code, out, err = run_shell(f"command -v {command}")
    if code == 0 and out:
        return CheckItem(name, "ok", f"已发现命令：{out.splitlines()[0]}")
    return CheckItem(name, "warn", f"未找到命令：{command}", err or out)


def check_disk() -> CheckItem:
    total, used, free = shutil.disk_usage(WORKSPACE)
    used_pct = round(used / total * 100, 1)
    status = "ok" if used_pct < 75 else "warn" if used_pct < 85 else "fail"
    summary = f"工作区所在磁盘已用 {used_pct}%"
    detail = f"free={free // (1024**3)}GB total={total // (1024**3)}GB"
    return CheckItem("磁盘空间", status, summary, detail)


def check_memory() -> CheckItem:
    code, out, err = run(["vm_stat"], timeout=10)
    if code != 0:
        return CheckItem("内存状态", "warn", "vm_stat 执行失败", err or out)

    page_size = 4096
    m = re.search(r"page size of (\d+) bytes", out)
    if m:
        page_size = int(m.group(1))

    values = {}
    for line in out.splitlines():
        m = re.match(r"([^:]+):\s+([\d\.]+)", line)
        if m:
            key = m.group(1).strip()
            val = int(float(m.group(2).replace('.', '')))
            values[key] = val

    free_pages = values.get("Pages free", 0) + values.get("Pages speculative", 0)
    active_pages = values.get("Pages active", 0) + values.get("Pages wired down", 0) + values.get("Pages occupied by compressor", 0)
    total_pages = free_pages + active_pages + values.get("Pages inactive", 0)
    free_gb = free_pages * page_size / (1024**3)
    used_pct = round((active_pages / total_pages) * 100, 1) if total_pages else 0
    status = "ok" if free_gb > 2 else "warn"
    summary = f"估算活跃内存占比 {used_pct}%"
    detail = f"free≈{free_gb:.1f}GB"
    return CheckItem("内存状态", status, summary, detail)


def check_git_status() -> CheckItem:
    code, out, err = run(["git", "status", "--short"], cwd=WORKSPACE)
    if code != 0:
        return CheckItem("Git 工作区", "warn", "git status 执行失败", err or out)
    lines = [line for line in out.splitlines() if line.strip()]
    if not lines:
        return CheckItem("Git 工作区", "ok", "工作区干净")
    return CheckItem("Git 工作区", "info", f"存在 {len(lines)} 个未提交改动", "\n".join(lines[:10]))


def ssh_base_cmd() -> List[str]:
    return [
        "ssh",
        "-i", REMOTE_SSH_KEY,
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=6",
        REMOTE_HOST,
    ]


def check_remote_ssh() -> CheckItem:
    code, out, err = run(ssh_base_cmd() + ["echo ok"], timeout=12)
    if code == 0 and out.strip() == "ok":
        return CheckItem("云服务器 SSH", "ok", "SSH 连通正常")
    return CheckItem("云服务器 SSH", "fail", "SSH 连通失败", err or out)


def check_remote_memory() -> CheckItem:
    code, out, err = run(ssh_base_cmd() + ["free -m | sed -n '2p'"], timeout=12)
    if code != 0 or not out.strip():
        return CheckItem("云服务器内存", "warn", "无法获取内存信息", err or out)

    parts = out.split()
    if len(parts) < 7:
        return CheckItem("云服务器内存", "warn", "内存输出格式异常", out)

    total = int(parts[1])
    used = int(parts[2])
    available = int(parts[6])
    used_pct = round(used / total * 100, 1) if total else 0
    status = "ok" if used_pct < 75 else "warn"
    return CheckItem("云服务器内存", status, f"已用 {used_pct}% ({used}MB/{total}MB)", f"available={available}MB")


def check_remote_v2ray() -> CheckItem:
    remote_cmd = "systemctl is-active v2ray; echo '---'; systemctl show v2ray -p NRestarts -p ActiveEnterTimestamp --no-pager 2>/dev/null || true; echo '---'; journalctl -u v2ray -n 8 --no-pager 2>/dev/null | tail -n 8"
    code, out, err = run(ssh_base_cmd() + [remote_cmd], timeout=15)
    if code != 0:
        return CheckItem("云服务器 V2Ray", "warn", "无法获取 V2Ray 状态", err or out)

    parts = out.split("---")
    active = parts[0].strip() if parts else ""
    meta = parts[1].strip() if len(parts) > 1 else ""
    logs = parts[2].strip() if len(parts) > 2 else ""

    restarts_match = re.search(r"NRestarts=(\d+)", meta)
    restarts = int(restarts_match.group(1)) if restarts_match else None

    status = "ok"
    summary = "V2Ray 运行正常"

    if active != "active":
        status = "fail"
        summary = f"V2Ray 非 active（当前：{active or 'unknown'}）"
    elif restarts is not None and restarts > 3:
        status = "warn"
        summary = f"V2Ray 有重启记录（{restarts} 次）"

    detail_lines = []
    if meta:
        detail_lines.append(meta)
    if logs:
        detail_lines.append(logs)
    return CheckItem("云服务器 V2Ray", status, summary, "\n".join(detail_lines) if detail_lines else None)


def build_report(items: List[CheckItem]) -> str:
    ok_count = sum(1 for i in items if i.status == "ok")
    warn_count = sum(1 for i in items if i.status == "warn")
    fail_count = sum(1 for i in items if i.status == "fail")

    lines = []
    lines.append(f"🔍 OpenClaw 健康检查 v1 | {NOW.strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append(f"总览：✅{ok_count} / ⚠️{warn_count} / ❌{fail_count}")
    lines.append("")

    for item in items:
        lines.append(f"{emoji(item.status)} {item.name}: {item.summary}")
        if item.detail:
            detail = item.detail.strip()
            if detail:
                lines.append(f"   {detail.replace(chr(10), chr(10) + '   ')}")
    
    risks = []
    for item in items:
        if item.status in {"warn", "fail"}:
            risks.append(f"- {item.name}: {item.summary}")

    lines.append("")
    lines.append("风险提示：")
    if risks:
        lines.extend(risks[:8])
    else:
        lines.append("- 暂无明显风险项")

    suggestions = []
    for item in items:
        if item.name == "Gateway" and item.status == "fail":
            suggestions.append("- Gateway 异常时先试：openclaw gateway restart")
        if item.name == "版本更新" and item.status == "warn":
            suggestions.append("- 可择机执行：openclaw update")
        if item.name == "磁盘空间" and item.status in {"warn", "fail"}:
            suggestions.append("- 关注 logs / tmp / 历史备份占用")
        if item.name == "股票推送" and item.status == "warn":
            suggestions.append("- 检查 /tmp/stock_push.log 和 crontab 16:30 入口")
        if item.name == "云端同步" and item.status == "warn":
            suggestions.append("- 检查 /tmp/cloud-backup.log 和 22:35 同步脚本")

    lines.append("")
    lines.append("建议动作：")
    if suggestions:
        lines.extend(dict.fromkeys(suggestions))
    else:
        lines.append("- 暂不需要处理")

    return "\n".join(lines)


def main() -> None:
    items: List[CheckItem] = []
    items.extend(parse_openclaw_status())
    items.append(check_tailscale_runtime())

    for name, path, schedule, freshness in LOG_TASKS:
        items.append(check_log_task(name, path, schedule, freshness))

    items.append(check_exec_entry("Claude Code 入口", "claude"))
    items.append(check_exec_entry("Codex 入口", "codex"))
    items.append(check_disk())
    items.append(check_memory())
    items.append(check_remote_ssh())
    items.append(check_remote_memory())
    items.append(check_remote_v2ray())
    items.append(check_git_status())

    print(build_report(items))


if __name__ == "__main__":
    main()
