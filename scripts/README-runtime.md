# scripts 运行时索引

*Last updated: 2026-04-27*

这份文件只记录 **当前真实运行入口**，不记录历史设计稿。

## 一、当前生产脚本

### A. crontab 入口
来源：`crontab -l`

| 时间 | 脚本 | 用途 | 日志 |
|---|---|---|---|
| `*/10 * * * *` | `scripts/session-snapshot.py save` | 会话自动保存 | `/tmp/session-snapshot.log` |
| `30 16 * * 1-5` | `scripts/stock_push_fast.py` | 股票日报（唯一现役入口） | `/tmp/stock_push.log` |
| `00 22 * * *` | `skills/system-backup/scripts/daily-backup-v2.sh` | 每日备份 | `/tmp/backup_cron.log` |
| `05 22 * * *` | `scripts/archive/backup-check.sh` | 备份检查 | `/tmp/backup_check.log` |
| `35 22 * * *` | `scripts/cloud-backup-sync.sh` | 云端备份同步 | `/tmp/cloud-backup.log` |
| `00 08 * * *` | `agents/kilo/broadcaster.py --task send` | 早安状态广播 | `/tmp/kilo_notify.log` |

### B. OpenClaw Cron 入口
来源：`openclaw cron list`

| 名称 | 调度 | 状态 | 说明 |
|---|---|---|---|
| `daily-backup` | 每天 22:00 | 运行中 | 与 crontab 形成双保险 |
| `weekly-cleanup` | 周日 03:00 | idle | 当前周清理入口 |

## 二、当前关键监控脚本

| 脚本 | 状态 | 说明 |
|---|---|---|
| `scripts/task_monitor.py` | 现役 | 已改成只反映当前真实任务 |
| `agents/kilo/broadcaster.py` | 现役 | 广播与通知发送入口 |

## 三、当前已归档的 crontab 快照

位置：`archived/cron-history/2026-04-27/`

- `new_crontab.txt`
- `optimized_crontab.txt`
- `crontab_active.txt`
- `crontab_restore_20260423.txt`

这些文件只做历史参考，**不能再当成当前配置真相来源**。

## 四、判断脚本是否现役的规则

优先级从高到低：
1. `crontab -l`
2. `openclaw cron list`
3. 运行日志是否近期更新
4. 本文件
5. 其他设计文档 / 历史快照

## 五、当前收口结论

- **股票日报**：只保留 crontab 入口
- **每日备份**：保留 crontab + OpenClaw cron 双保险
- **备份检查**：虽然在 `archive/`，但仍属于生产保留
- **周清理**：以 OpenClaw cron 为准
