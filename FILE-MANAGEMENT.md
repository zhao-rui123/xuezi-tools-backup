# 文件管理规范

## 目录结构

```
~/.openclaw/workspace/
├── AGENTS.md              # 代理配置
├── BOOTSTRAP.md           # 首次启动指南
├── HEARTBEAT.md           # 心跳任务
├── IDENTITY.md            # 身份配置
├── MEMORY.md              # 长期记忆
├── SOUL.md                # 核心人格
├── TOOLS.md               # 工具配置
├── USER.md                # 用户信息
├── backup_memory.sh       # 备份脚本
├── daily_stock_report.sh  # 股票日报
├── stock_analyzer.py      # 股票分析
│
├── assets/                # 静态资源
│   ├── images/            # 图片文件
│   ├── icons/             # 图标文件
│   └── diagrams/          # 图表、示意图
│
├── knowledge-base/        # 知识库
│   ├── INDEX.md
│   ├── projects/
│   ├── decisions/
│   ├── problems/
│   └── references/
│
├── memory/                # 每日记忆
│   ├── YYYY-MM-DD.md
│   └── archive/
│
├── reports/               # 生成的报告
│   ├── daily/
│   ├── weekly/
│   └── project/
│
├── scripts/               # 脚本文件
│   ├── system-maintenance.sh
│   ├── daily-health-check.sh
│   ├── session-state.sh
│   └── startup-check.sh
│
├── skills/                # 技能包
│   ├── data-processor/
│   ├── report-generator/
│   └── ...
│
├── summary/               # 摘要汇总
│   └── daily/
│
└── tmp/                   # 临时文件
    ├── screenshots/       # 截图
    ├── downloads/         # 下载文件
    └── cache/             # 缓存文件
```

## 文件存放规则

| 文件类型 | 存放位置 | 清理策略 |
|---------|---------|---------|
| 截图 | `tmp/screenshots/` | 7天后自动删除 |
| 生成的报告 | `reports/` | 保留30天 |
| 图片资源 | `assets/images/` | 永久保留 |
| 下载文件 | `tmp/downloads/` | 7天后自动删除 |
| 缓存数据 | `tmp/cache/` | 随时可删除 |
| 日志 | `tmp/logs/` | 30天后自动删除 |

## 命名规范

### 截图文件
```
screenshot_YYYYMMDD_HHMMSS.png
chart_YYYYMMDD_description.png
```

### 报告文件
```
daily_health_YYYYMMDD.txt
stock_report_YYYYMMDD.md
project_report_YYYYMMDD_name.docx
```

### 临时文件
```
download_YYYYMMDD_filename.ext
cache_YYYYMMDD_hash.tmp
```

## 清理策略

### 自动清理（通过定时任务）
```bash
# 清理7天前的截图
find tmp/screenshots -name "*.png" -mtime +7 -delete

# 清理7天前的下载文件
find tmp/downloads -name "*" -mtime +7 -delete

# 清理30天前的报告
find reports -name "*" -mtime +30 -delete

# 清理30天前的日志
find tmp/logs -name "*.log" -mtime +30 -delete
```

### 手动清理
```bash
# 清理所有临时文件
rm -rf tmp/*/

# 清理旧报告
find reports -name "*" -mtime +7 -delete
```

## 重要文件保护

以下文件**禁止自动清理**：
- `memory/*.md` — 每日记忆
- `knowledge-base/**/*` — 知识库
- `skills/*/SKILL.md` — 技能包
- `assets/**/*` — 静态资源
- `scripts/*.sh` — 脚本文件

---
*创建于: 2026-03-04*
