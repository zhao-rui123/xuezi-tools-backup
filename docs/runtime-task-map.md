# Runtime Task Map

*Last updated: 2026-04-27*

## 当前真实运行入口

### 1. 系统 crontab（当前生效）
来源：`crontab -l`

| 时间 | 任务 | 脚本 | 状态 | 备注 |
|---|---|---|---|---|
| `*/10 * * * *` | 会话自动保存 | `scripts/session-snapshot.py save` | ✅ 运行中 | 唯一的会话快照入口 |
| `30 16 * * 1-5` | 股票日报 | `scripts/stock_push_fast.py` | ✅ 运行中 | 当前唯一股票日报入口 |
| `00 22 * * *` | 每日备份 | `skills/system-backup/scripts/daily-backup-v2.sh` | ✅ 运行中 | 与 OpenClaw cron 双保险，可接受 |
| `05 22 * * *` | 备份检查 | `scripts/archive/backup-check.sh` | ⚠️ 历史脚本 | 建议评估是否并入备份主脚本 |
| `35 22 * * *` | 云端同步 | `scripts/cloud-backup-sync.sh` | ✅ 运行中 | 独立于主备份 |
| `00 08 * * *` | 早安状态 ping | `agents/kilo/broadcaster.py` | ✅ 运行中 | 轻通知 |

### 2. OpenClaw Cron（当前生效）
来源：`openclaw cron list`

| 名称 | 调度 | 状态 | 备注 |
|---|---|---|---|
| `daily-backup` | `0 22 * * *` | ✅ ok | 与 crontab 双保险，符合 MEMORY/HEARTBEAT 说明 |
| `weekly-cleanup` | `0 3 * * 0` | 😴 idle | 当前周清理入口 |

## 当前判断

> 注：本文件在 2026-04-27 第二轮收口后，`stock-daily` 已从 OpenClaw cron 删除。


### 保留
- `session-snapshot.py`
- `stock_push_fast.py`
- `daily-backup-v2.sh`
- `cloud-backup-sync.sh`
- `weekly-cleanup`（OpenClaw cron）
- `broadcaster.py --task send` 早安通知

### 当前仍待收口
- **每日备份**：crontab 与 OpenClaw cron 双保险（可保留）
- **备份检查**：`scripts/archive/backup-check.sh` 仍在 crontab，但已经属于历史目录

### 历史文档 / 快照（不应再视为运行入口）
- `scripts/new_crontab.txt`
- `scripts/optimized_crontab.txt`
- `scripts/crontab_active.txt`
- `scripts/crontab_restore_20260423.txt`
- `docs/BACKUP-SCHEDULER-ARCHITECTURE.md`（设计稿，不是现状）
- `ops_archive/**`（历史方案）

## 推荐的下一步收口

### P1（建议尽快）
1. 更新 `HEARTBEAT.md` / 相关说明，使其只反映真实运行入口（已完成）
2. 后续评估是否保留 22:00 每日备份的双保险策略
3. 视情况再处理 `openclaw tasks maintenance --apply` 的历史残留

### P2（可后做）
1. 给 `scripts/` 建立 `runtime/ manual/ archive/` 三层结构
2. 把当前真正在跑的脚本做一个极简索引 README
3. 清理 `openclaw tasks maintenance --apply` 提示的 task-flow 残留
