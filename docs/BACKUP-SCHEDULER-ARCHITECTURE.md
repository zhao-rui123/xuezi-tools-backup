# 备份和定时任务系统架构设计

> 版本：v1.0 | 日期：2026-03-29 | 状态：设计稿，待雪子确认后实施

---

## 一、设计原则

### 1.1 核心原则

| 原则 | 说明 | 实现方式 |
|------|------|----------|
| **单一入口** | 所有备份只走一个入口脚本 | `backup-runner.sh` 统一调度 |
| **单一配置** | 所有任务配置集中管理 | `tasks.conf` YAML配置文件 |
| **三重验证** | 每个备份必须通过三级验证才视为成功 | 文件存在 → 大小有效 → 压缩完整 → 可恢复性测试 |
| **失败即告警** | 任何步骤失败立即告警，不静默 | 每步 `set -e` + exit code 检查 |
| **幂等设计** | 同一任务多次执行结果一致 | 锁文件机制 + 幂等函数 |
| **日志归一** | 所有日志写入统一目录+统一格式 | `logs/` 目录 + JSON结构日志 |
| **可追溯** | 每次执行都有唯一 trace_id | `trace_id = YYYYMMDD_HHMMSS_random` |

### 1.2 命名规范

```
# 备份命名
{type}-{category}-{YYYYMMDD_HHMMSS}.tar.gz
示例：backup-full-openclaw-20260329_220012.tar.gz

# 日志命名
{trace_id}.log
示例：20260329_220012_a3f.log

# 状态文件
{trace_id}.status.json
示例：20260329_220012_a3f.status.json
```

### 1.3 目录规范

```
~/.openclaw/
├── ops/                          # ★ 新建：运维操作根目录
│   ├── bin/                      # 核心脚本（唯一入口）
│   │   ├── backup-runner.sh      # 【新建】统一备份入口
│   │   ├── task-scheduler.sh     # 【新建】统一任务调度入口
│   │   └── health-monitor.sh     # 【新建】健康监控脚本
│   ├── config/
│   │   ├── backup.conf           # 【新建】备份配置（源路径、目标路径、保留策略）
│   │   ├── tasks.conf            # 【新建】任务配置（所有定时任务声明）
│   │   └── alerts.conf           # 【新建】告警配置（阈值、通知渠道）
│   ├── logs/                     # 统一日志目录
│   │   ├── backup/              # 备份日志（按月轮转）
│   │   ├── tasks/               # 任务日志（按月轮转）
│   │   └── health/              # 健康检查日志
│   ├── status/                   # 状态追踪目录
│   │   ├── backup/              # 备份状态文件（JSON）
│   │   └── tasks/               # 任务状态文件（JSON）
│   ├── lock/                     # 锁文件目录
│   └── reports/                  # 每日报告输出目录
├── workspace/
│   ├── scripts/                  # 【现有】业务脚本（改名为业务脚本目录）
│   ├── skills/                   # 【现有】技能包
│   └── memory/                   # 【现有】记忆文件
└── skills/system-backup/         # 【改造】备份技能包（核心逻辑移至此）
```

---

## 二、系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        cron（单一入口）                          │
│         /Users/zhaoruicn/.openclaw/ops/bin/task-scheduler.sh   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
           ┌────────────────────┼────────────────────┐
           │                    │                    │
           ▼                    ▼                    ▼
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │ 每日任务钩子  │     │ 每周任务钩子  │     │ 每月任务钩子  │
    │ daily_tasks │     │ weekly_tasks│     │ monthly_tasks│
    └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
           │                    │                    │
           └────────────────────┼────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │  task-scheduler.sh   │
                    │   统一任务调度中心    │
                    │   - 读取 tasks.conf  │
                    │   - 生成 trace_id    │
                    │   - 加载环境变量     │
                    │   - 执行任务函数     │
                    │   - 记录状态文件     │
                    │   - 发送通知        │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
 ┌─────────────┐      ┌─────────────┐       ┌─────────────┐
 │ backup-group│      │ memory-group│       │system-group │
 │ 备份任务组   │      │ 记忆任务组   │       │ 系统任务组   │
 └──────┬──────┘      └──────┬──────┘       └──────┬──────┘
        │                    │                      │
        ▼                    ▼                      ▼
 ┌─────────────────┐  ┌─────────────────┐   ┌─────────────────┐
 │ backup-runner   │  │ memory-suite    │   │ system-check    │
 │ 统一备份入口     │  │ scheduler.py    │   │ scripts         │
 │ (改造)          │  │ (现有，维持不变) │   │ (整理整合)       │
 └───────┬─────────┘  └─────────────────┘   └─────────────────┘
         │
  ┌──────┼──────┐
  │      │      │
  ▼      ▼      ▼
 ┌──── ┌──── ┌────┐
 │本地 │验证 │云端 │
 │备份 │检查 │同步 │
 └──── └──── └────┘
         │
         ▼
 ┌─────────────────┐
 │  四重验证机制    │
 │ 1.文件存在      │
 │ 2.大小有效>100KB│
 │ 3.tar完整性     │
 │ 4.可恢复性测试  │
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │  状态文件写入    │
 │ ops/status/     │
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │  飞书告警/通知   │
 └─────────────────┘
```

---

## 三、核心组件

### 3.1 备份组件

| 组件 | 类型 | 职责 | 状态 |
|------|------|------|------|
| `backup-runner.sh` | 统一入口 | 统一备份入口，协调所有备份子任务 | **新建** |
| `backup-core.sh` | 核心逻辑 | 执行本地备份（分类打包） | **改造**（基于daily-backup-v2.sh） |
| `backup-verify.sh` | 验证模块 | 四重验证：存在/大小/压缩/可恢复 | **新建** |
| `backup-cloud-sync.sh` | 同步模块 | 云端同步（腾讯云rsync） | **改造**（基于cloud-backup-sync.sh） |
| `backup-alert.sh` | 告警模块 | 失败告警+成功通知 | **新建** |

### 3.2 调度组件

| 组件 | 类型 | 职责 | 状态 |
|------|------|------|------|
| `task-scheduler.sh` | 调度中心 | cron统一入口，读取配置，执行任务，记录状态 | **新建** |
| `tasks.conf` | 配置文件 | 所有定时任务声明（YAML格式） | **新建** |
| `task-status-collector.sh` | 状态收集 | 汇总昨日任务执行情况，生成报告 | **改造**（基于daily-task-report.sh） |

### 3.3 监控组件

| 组件 | 类型 | 职责 | 状态 |
|------|------|------|------|
| `health-monitor.sh` | 健康监控 | 每日健康检查（磁盘/内存/进程/SSH） | **改造**（整合现有脚本） |
| `alert-manager.sh` | 告警管理 | 统一告警阈值和通知路由 | **新建** |

---

## 四、备份流程设计

### 4.1 统一备份流程（含四重验证）

```
backup-runner.sh 统一入口
        │
        ▼
┌───────────────────┐
│ 1. 前置检查        │
│   - 外部存储挂载检查 │
│   - 磁盘空间检查    │
│   - 锁文件检查（防重复）│
│   - 生成 trace_id  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 2. 执行本地备份     │
│   backup-core.sh  │
│   - 备份 memory/  │
│   - 备份 skills/  │
│   - 备份配置/报告   │
│   - 生成 manifest  │
│   - 创建压缩包     │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 3. 第一重验证      │
│   [验证-1]        │
│   检查文件存在      │
│   且大小 > 100KB  │
└────────┬──────────┘
         │ 失败 → 告警+退出
         ▼
┌───────────────────┐
│ 4. 第二重验证      │
│   [验证-2]        │
│   tar -tzf 完整性  │
└────────┬──────────┘
         │ 失败 → 告警+退出
         ▼
┌───────────────────┐
│ 5. 第三重验证      │
│   [验证-3]        │
│   可恢复性测试     │
│   解压到临时目录   │
│   检查关键文件     │
│   清理临时目录     │
└────────┬──────────┘
         │ 失败 → 告警+退出
         ▼
┌───────────────────┐
│ 6. 云端同步        │
│   backup-cloud    │
│   -sync.sh       │
│   - rsync 到腾讯云 │
│   - 验证远程文件   │
│   - 清理远程旧备份  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 7. 第四重验证      │
│   [验证-4]        │
│   云端文件存在     │
│   且大小匹配      │
└────────┬──────────┘
         │ 失败 → 告警+退出
         ▼
┌───────────────────┐
│ 8. 写入状态文件    │
│   ops/status/     │
│   backup/         │
│   {trace}.json   │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 9. 发送通知        │
│   - 成功：简要通知  │
│   - 失败：详细告警  │
│   到飞书群        │
└───────────────────┘
```

### 4.2 备份清单（manifest）结构

```json
{
  "trace_id": "20260329_220012_a3f",
  "backup_date": "20260329",
  "backup_time": "22:00:12",
  "status": "SUCCESS",
  "local": {
    "archive_path": "/Volumes/cu/ocu/full-backups/...",
    "archive_size": "45.2MB",
    "manifest_version": "2.0"
  },
  "cloud": {
    "remote_path": "/data/openclaw-backups/...",
    "synced": true,
    "verified": true
  },
  "verification": {
    "step1_file_exists": true,
    "step2_size_valid": true,
    "step3_tar_intact": true,
    "step4_recoverable": true,
    "step5_cloud_verified": true
  },
  "counts": {
    "memory_files": 127,
    "skills_files": 843,
    "config_files": 12
  },
  "duration_seconds": 47,
  "error": null
}
```

---

## 五、定时任务调度设计

### 5.1 统一任务配置（tasks.conf）

```yaml
# ============================================================
# 雪子助手 - 统一任务配置
# 路径：~/.openclaw/ops/config/tasks.conf
# 说明：所有定时任务在此声明，task-scheduler.sh 统一读取执行
# ============================================================

scheduler:
  timezone: "Asia/Shanghai"
  lock_dir: "~/.openclaw/ops/lock"
  log_dir: "~/.openclaw/ops/logs/tasks"
  status_dir: "~/.openclaw/ops/status/tasks"
  alert_on_failure: true
  alert_on_success: false  # 仅关键任务成功通知

# ============================================================
# 每日任务（每天执行）
# ============================================================
daily:
  - id: backup_full
    name: "每日完整备份"
    schedule: "00 22 * * *"
    group: backup
    script: "backup-runner.sh"
    args: ["--type", "full"]
    timeout: 3600        # 60分钟超时
    retry: 1             # 失败重试1次
    retry_delay: 1800   # 重试间隔30分钟
    notify: success     # success | failure | always | none
    depends: []

  - id: stock_push
    name: "股票自选股日报"
    schedule: "30 16 * * 1-5"
    group: report
    script: "python3"
    args: ["scripts/stock_push_fast.py"]
    timeout: 300
    retry: 0
    notify: failure
    depends: []
    cwd: "~/.openclaw/workspace"

  - id: memory_evolution
    name: "每日自我进化"
    schedule: "00 23 * * *"
    group: memory
    script: "scheduler.py"
    args: ["run", "evolution-daily"]
    timeout: 1800
    retry: 0
    notify: none
    depends: []
    interpreter: "python3"
    cwd: "~/.openclaw/workspace/skills/memory-suite-v4"

  - id: memory_archive
    name: "每日记忆归档"
    schedule: "30 00 * * *"
    group: memory
    script: "scheduler.py"
    args: ["run", "archive"]
    timeout: 600
    retry: 0
    notify: none
    depends: []

  - id: knowledge_graph
    name: "知识图谱更新"
    schedule: "00 01 * * *"
    group: memory
    script: "scheduler.py"
    args: ["run", "knowledge-graph"]
    timeout: 600
    retry: 0
    notify: none
    depends: []

  - id: log_rotate
    name: "日志轮转"
    schedule: "00 03 * * *"
    group: system
    script: "scripts/log_rotate.sh"
    timeout: 300
    retry: 0
    notify: none
    depends: []

  - id: feishu_sync
    name: "飞书知识同步"
    schedule: "00 06 * * *"
    group: data
    script: "scripts/feishu-bitable-sync.sh"
    timeout: 600
    retry: 1
    notify: failure
    depends: []

  - id: morning_greeting
    name: "早安问候"
    schedule: "00 08 * * *"
    group: report
    script: "kilo/broadcaster.py"
    args: ["--task", "send", "--message", "🔔 早安！系统状态正常", "--target", "group"]
    timeout: 60
    retry: 0
    notify: none
    depends: []

  - id: task_summary
    name: "每日任务汇总"
    schedule: "05 08 * * *"
    group: report
    script: "task-status-collector.sh"
    timeout: 120
    retry: 0
    notify: failure
    depends: ["morning_greeting"]

# ============================================================
# 每周任务（周日执行）
# ============================================================
weekly:
  sunday:
    - id: system_maintenance
      name: "系统维护"
      schedule: "00 02 * * 0"
      group: system
      script: "scripts/system-maintenance.sh"
      timeout: 600
      retry: 0
      notify: failure

    - id: ouc_cleanup
      name: "OUC清理"
      schedule: "00 03 * * 0"
      group: system
      script: "scripts/ouc-cleanup.sh"
      timeout: 600
      retry: 0
      notify: failure

  monday:
    - id: file_cleanup
      name: "文件清理"
      schedule: "00 03 * * 1"
      group: system
      script: "scripts/file-cleanup.sh"
      timeout: 600
      retry: 0
      notify: failure

    - id: security_scan
      name: "每周安全扫描"
      schedule: "00 04 * * 1"
      group: security
      script: "scripts/security-scan.sh"
      timeout: 600
      retry: 0
      notify: failure

    - id: health_check
      name: "健康检查"
      schedule: "30 06 * * 1"
      group: health
      script: "health-monitor.sh"
      timeout: 300
      retry: 0
      notify: failure

# ============================================================
# 每月任务（每月1号执行）
# ============================================================
monthly:
  - id: memory_deep_analyze
    name: "月度记忆深度分析"
    schedule: "00 02 1 * *"
    group: memory
    script: "scheduler.py"
    args: ["run", "analyze-daily"]
    timeout: 3600
    retry: 0
    notify: failure
    interpreter: "python3"
    cwd: "~/.openclaw/workspace/skills/memory-suite-v4"

  - id: backup_archive
    name: "月度归档备份"
    schedule: "00 04 1 * *"
    group: backup
    script: "backup-runner.sh"
    args: ["--type", "archive"]
    timeout: 3600
    retry: 1
    notify: success

  - id: evolution_monthly
    name: "每月深度进化"
    schedule: "00 10 1 * *"
    group: memory
    script: "scheduler.py"
    args: ["run", "evolution-monthly"]
    timeout: 3600
    retry: 0
    notify: failure

  - id: evolution_report
    name: "自我进化报告"
    schedule: "00 09 2 * *"
    group: report
    script: "scheduler.py"
    args: ["run", "evolution-report"]
    timeout: 600
    retry: 0
    notify: failure
```

### 5.2 任务调度流程

```
┌──────────────────────────────────────────────────┐
│            task-scheduler.sh 调度流程              │
└──────────────────────────────────────────────────┘

cron 触发
    │
    ▼
解析 tasks.conf（按当前时间匹配任务）
    │
    ▼
生成 trace_id，初始化状态文件
    │
    ├─── 并行执行无依赖任务
    │
    └─── 顺序执行有依赖任务
            │
            ▼
        执行任务脚本
            │
            ├─ 超时检查（timeout）
            ├─ 重试机制（retry × retry_delay）
            └─ 退出码判断
            │
            ▼
        更新状态文件（成功/失败/超时）
            │
            ▼
        依赖任务解锁（如有）
            │
            ▼
    所有任务完成
        │
        ▼
    汇总执行结果，发送汇总通知（如有失败则告警）
```

### 5.3 任务状态文件格式

```json
{
  "task_id": "backup_full",
  "task_name": "每日完整备份",
  "trace_id": "20260329_220012_a3f",
  "group": "backup",
  "schedule": "00 22 * * *",
  "start_time": "2026-03-29T22:00:12+08:00",
  "end_time": "2026-03-29T22:00:59+08:00",
  "duration_seconds": 47,
  "status": "SUCCESS",
  "exit_code": 0,
  "retry_count": 0,
  "max_retries": 1,
  "output_summary": "备份完成: memory=127, skills=843, size=45.2MB",
  "error": null,
  "notifications_sent": ["feishu_group"],
  "verified": true
}
```

---

## 六、监控和告警设计

### 6.1 告警分级

| 级别 | 触发条件 | 通知方式 | 响应要求 |
|------|----------|----------|----------|
| **P0 严重** | 备份完全失败/数据丢失 | 飞书@所有人 + 短信 | 立即处理 |
| **P1 警告** | 备份部分失败/验证不通过 | 飞书群消息 | 当日处理 |
| **P2 提醒** | 任务执行超时/重试成功 | 飞书群消息 | 次日处理 |
| **P3 通知** | 任务正常完成 | 无（静默） | 无需处理 |

### 6.2 每日健康检查项目

| 检查项 | 阈值 | P级别 | 操作 |
|--------|------|-------|------|
| 本地磁盘空间 | < 20% | P1 | 告警 |
| 备份盘空间 | < 30% | P1 | 告警 |
| 腾讯云磁盘空间 | < 20% | P1 | 告警 |
| 内存使用率 | > 80% | P2 | 提醒 |
| 备份任务连续失败 | ≥ 2次 | P0 | 严重告警 |
| cron服务状态 | 不可用 | P0 | 严重告警 |
| 昨日任务失败数 | ≥ 3个 | P1 | 告警 |

### 6.3 飞书通知模板

**备份成功通知（精简）：**
```
💾 备份完成 | 22:00 | Memory:127 | Skills:843 | 45.2MB | ☁️云端已同步
```

**备份失败告警（P0）：**
```
🚨【严重】备份失败 | 22:00
❌ 本地备份: 失败
❌ 验证: 未通过
原因: 外部存储未挂载
时间: 2026-03-29 22:00
请立即处理！
```

**每日任务汇总（P1汇总）：**
```
📊 定时任务日报 | 03-29

✅ 成功: 12 | ⚠️ 失败: 2 | 总计: 14

失败任务:
• backup_full (22:00) - 云端同步失败
• feishu_sync (06:00) - 连接超时

⚠️ 请检查以上失败任务
```

---

## 七、文件结构

### 7.1 新建目录树

```
~/.openclaw/ops/
├── bin/
│   ├── backup-runner.sh         # ★ 统一备份入口 [新建]
│   ├── backup-core.sh           # ★ 备份核心逻辑 [改造自daily-backup-v2.sh]
│   ├── backup-verify.sh         # ★ 四重验证模块 [新建]
│   ├── backup-cloud-sync.sh     # ★ 云端同步 [改造自cloud-backup-sync.sh]
│   ├── backup-alert.sh          # ★ 告警通知 [新建]
│   ├── task-scheduler.sh        # ★ 统一任务调度 [新建]
│   ├── task-status-collector.sh # ★ 任务状态汇总 [改造自daily-task-report.sh]
│   ├── health-monitor.sh        # ★ 健康监控 [新建，整合现有]
│   └── lib/
│       ├── logger.sh            # ★ 统一日志函数库 [新建]
│       ├── lock.sh              # ★ 锁文件管理 [新建]
│       └── notifier.sh          # ★ 通知函数库 [新建]
├── config/
│   ├── backup.conf              # ★ 备份配置 [新建]
│   ├── tasks.conf               # ★ 任务配置（YAML）[新建]
│   └── alerts.conf              # ★ 告警配置 [新建]
├── logs/
│   ├── backup/                  # 备份日志
│   ├── tasks/                   # 任务日志
│   └── health/                  # 健康检查日志
├── status/
│   ├── backup/                  # 备份状态JSON
│   └── tasks/                   # 任务状态JSON
├── lock/                        # 锁文件目录
└── reports/                     # 每日报告

# 现有需要整理的脚本（移入 ops/bin/）
scripts/
  # 需要保留的：backup-with-retry.sh（改名为 runner 别名）
  # 需要废弃的：backup-check.sh（功能合并到 backup-verify.sh）
  # 需要改造的：cloud-backup-sync.sh → ops/bin/backup-cloud-sync.sh
  # 需要改造的：daily-task-report.sh → ops/bin/task-status-collector.sh
```

### 7.2 crontab 精简为两条

```crontab
# ============================================================
# 雪子助手 - 精简版 crontab（仅2条核心入口）
# 所有任务由 task-scheduler.sh 统一调度
# ============================================================

# 每日任务调度（每天22:00触发）
00 22 * * * /Users/zhaoruicn/.openclaw/ops/bin/task-scheduler.sh run daily >> /tmp/ops_tasks.log 2>&1

# 每周任务调度（每周日02:00触发）
00 02 * * 0 /Users/zhaoruicn/.openclaw/ops/bin/task-scheduler.sh run weekly >> /tmp/ops_tasks.log 2>&1

# 每月任务调度（每月1号02:00触发）
00 02 1 * * /Users/zhaoruicn/.openclaw/ops/bin/task-scheduler.sh run monthly >> /tmp/ops_tasks.log 2>&1

# 股票推送（独立业务任务，直接执行）
30 16 * * 1-5 cd /Users/zhaoruicn/.openclaw/workspace && /opt/homebrew/bin/python3 scripts/stock_push_fast.py >> /tmp/stock_push.log 2>&1

# 早安问候（独立业务任务，直接执行）
00 08 * * * /Users/zhaoruicn/.openclaw/workspace/agents/kilo/broadcaster.py --task send --message '🔔 早安！系统状态正常' --target group >> /tmp/kilo_notify.log 2>&1
```

---

## 八、实施计划

### 阶段一：基础架构（第1-2天）

1. 创建 `ops/` 目录结构
2. 编写统一日志函数库 `lib/logger.sh`
3. 编写锁文件管理 `lib/lock.sh`
4. 编写通知函数库 `lib/notifier.sh`
5. 创建配置文件 `config/backup.conf` 和 `config/tasks.conf`

### 阶段二：备份系统重构（第3-4天）

1. 改造 `backup-core.sh`（基于现有 daily-backup-v2.sh）
2. 编写 `backup-verify.sh`（四重验证）
3. 改造 `backup-cloud-sync.sh`
4. 编写 `backup-runner.sh`（统一入口）
5. 编写 `backup-alert.sh`

### 阶段三：任务调度系统（第5-6天）

1. 编写 `task-scheduler.sh`（核心调度逻辑）
2. 改造 `task-status-collector.sh`
3. 整合现有健康检查脚本为 `health-monitor.sh`

### 阶段四：切换上线（第7天）

1. 备份当前 crontab 配置
2. 安装新 crontab
3. 执行一次完整备份测试
4. 验证所有任务正常
5. 确认飞书通知正常

### 阶段五：清理收尾（第8天）

1. 删除废弃脚本（backup-check.sh等）
2. 更新文档
3. 向雪子汇报完成状态

---

## 附录：关键脚本伪代码

### A. backup-runner.sh 核心逻辑

```bash
#!/usr/bin/env bash
#
# backup-runner.sh - 统一备份入口
# 用法: backup-runner.sh [--type full|archive] [--verify-only]
#

set -euo pipefail
export PATH="/opt/homebrew/bin:..."
export HOME="$(cd ~ && pwd)"

# ============================================================
# 初始化
# ============================================================
SOURCE="${BASH_SOURCE[0]}"
while [ -L "$SOURCE" ]; do
    DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
OPS_DIR="$(cd -P "$(dirname "$SOURCE")/.." && pwd)"

# 加载函数库
# shellcheck source=lib/logger.sh
source "$OPS_DIR/lib/logger.sh"
# shellcheck source=lib/lock.sh
source "$OPS_DIR/lib/lock.sh"
# shellcheck source=lib/notifier.sh
source "$OPS_DIR/lib/notifier.sh"

# 加载配置
# shellcheck source=../config/backup.conf
source "$OPS_DIR/config/backup.conf"

# 解析参数
TYPE="${TYPE:-full}"
VERIFY_ONLY="${VERIFY_ONLY:-false}"

# ============================================================
# 核心变量
# ============================================================
TRACE_ID="$(date '+%Y%m%d_%H%M%S')-$(openssl rand -hex 3)"
BACKUP_DIR="/Volumes/cu/ocu"
STATUS_DIR="$OPS_DIR/status/backup"
LOG_FILE="$OPS_DIR/logs/backup/${TRACE_ID}.log"
LOCK_FILE="$OPS_DIR/lock/backup.lock"
ARCHIVE_NAME="backup-${TYPE}-openclaw-${TRACE_ID}.tar.gz"

# ============================================================
# 主流程
# ============================================================
main() {
    log "=========================================="
    log "备份任务开始 | type=$TYPE | trace=$TRACE_ID"
    log "=========================================="

    # 前置检查
    preflight_check || { alert "P0" "前置检查失败"; exit 1; }

    # 加锁
    lock_acquire "$LOCK_FILE" || { alert "P0" "无法获取锁，备份已在运行"; exit 1; }
    trap "lock_release '$LOCK_FILE'" EXIT

    # 执行备份
    if [ "$VERIFY_ONLY" = "true" ]; then
        verify_existing
    else
        run_backup
    fi

    log "=========================================="
    log "备份任务完成 | status=SUCCESS"
    log "=========================================="
}

# ============================================================
# 前置检查
# ============================================================
preflight_check() {
    log "[检查] 外部存储挂载"
    [ -d "$BACKUP_DIR" ] || return 1

    log "[检查] 磁盘空间 (>10%)"
    local available
    available=$(df -k "$BACKUP_DIR" | awk 'NR==2 {print $4}')
    [ "$available" -gt 1048576 ] || return 1  # >1GB

    log "[检查] 上一任务是否完成"
    [ ! -f "$LOCK_FILE" ] || return 1

    return 0
}

# ============================================================
# 执行备份
# ============================================================
run_backup() {
    log "[步骤1] 执行本地备份..."
    bash "$OPS_DIR/bin/backup-core.sh" --type "$TYPE" --trace "$TRACE_ID" \
        >> "$LOG_FILE" 2>&1 || {
        log "[错误] backup-core.sh 执行失败"
        save_status "FAILED" "backup-core failed"
        return 1
    }

    log "[步骤2] 第一重验证（文件存在+大小）..."
    verify_step1 || {
        save_status "FAILED" "step1_verify_failed"
        return 1
    }

    log "[步骤3] 第二重验证（tar完整性）..."
    verify_step2 || {
        save_status "FAILED" "step2_verify_failed"
        return 1
    }

    log "[步骤4] 第三重验证（可恢复性测试）..."
    verify_step3 || {
        save_status "FAILED" "step3_verify_failed"
        return 1
    }

    log "[步骤5] 云端同步..."
    bash "$OPS_DIR/bin/backup-cloud-sync.sh" --trace "$TRACE_ID" \
        >> "$LOG_FILE" 2>&1 || {
        log "[警告] 云端同步失败，继续"
    }

    log "[步骤6] 第四重验证（云端文件）..."
    verify_cloud || {
        log "[警告] 云端验证失败，但本地备份有效"
    }

    save_status "SUCCESS"
}

# ============================================================
# 状态保存
# ============================================================
save_status() {
    local status="$1"
    local error="$2"

    cat > "$STATUS_DIR/${TRACE_ID}.json" << EOF
{
  "trace_id": "$TRACE_ID",
  "status": "$status",
  "error": "$error",
  "archive": "$ARCHIVE_NAME",
  "backup_dir": "$BACKUP_DIR",
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
}
EOF
}

main "$@"
```

### B. task-scheduler.sh 核心逻辑

```bash
#!/usr/bin/env bash
#
# task-scheduler.sh - 统一任务调度中心
# 用法: task-scheduler.sh run [daily|weekly|monthly]
#

set -euo pipefail

SOURCE="${BASH_SOURCE[0]}"
OPS_DIR="$(cd -P "$(dirname "$SOURCE")/.." && pwd)"
source "$OPS_DIR/lib/logger.sh"
source "$OPS_DIR/lib/lock.sh"
source "$OPS_DIR/lib/notifier.sh"

MODE="${1:-daily}"  # daily | weekly | monthly
TRACE_ID="$(date '+%Y%m%d_%H%M%S')"
LOG_DIR="$OPS_DIR/logs/tasks"
STATUS_DIR="$OPS_DIR/status/tasks"

log "=========================================="
log "任务调度开始 | mode=$MODE | trace=$TRACE_ID"
log "=========================================="

# 解析 tasks.conf，加载对应模式的任务
# ...

# 按依赖关系排序任务
# ...

# 执行任务（可并行无依赖任务）
# ...

# 汇总结果，发送通知
# ...
```

---

## 附录：废弃脚本清单

| 脚本名 | 现状 | 替代方案 |
|--------|------|----------|
| `backup-with-retry.sh` | 废弃 | `ops/bin/backup-runner.sh` |
| `backup-check.sh` | 废弃 | `ops/bin/backup-verify.sh` |
| `daily-backup-v2.sh` | 废弃 | `ops/bin/backup-core.sh` |
| `cloud-backup-sync.sh` | 废弃 | `ops/bin/backup-cloud-sync.sh` |
| `daily-task-report.sh` | 改造 | `ops/bin/task-status-collector.sh` |
| `setup-three-systems-cron.sh` | 废弃 | crontab精简 |

---

*本文档由 Claude 架构设计（基于现有系统分析）| 2026-03-29*
