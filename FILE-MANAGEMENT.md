# 文件管理规范

## 目录结构

```
~/.openclaw/workspace/
├── AGENTS.md              # 代理配置
├── BOOTSTRAP.md           # 首次启动指南
├── FILE-MANAGEMENT.md     # 本文件
├── HEARTBEAT.md           # 心跳任务
├── IDENTITY.md            # 身份配置
├── MEMORY.md              # 长期记忆
├── SOUL.md                # 核心人格
├── TOOLS.md               # 工具配置
├── USER.md                # 用户信息
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
│   ├── backup_memory.sh
│   ├── daily_stock_report.sh
│   ├── daily-health-check.sh
│   ├── file-cleanup.sh
│   ├── session-state.sh
│   ├── startup-check.sh
│   └── system-maintenance.sh
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
    ├── cache/             # 缓存文件
    ├── downloads/         # 下载文件
    ├── logs/              # 日志文件
    └── screenshots/       # 截图
```

## 文件存放规则

| 文件类型 | 存放位置 | 保留时间 | 说明 |
|---------|---------|---------|------|
| 截图 | `tmp/screenshots/` | 14天 | 临时截图 |
| 下载文件 | `tmp/downloads/` | 14天 | 下载的临时文件 |
| 生成的报告 | `reports/` | 60天 | 日报、周报、项目报告 |
| 日志文件 | `tmp/logs/` | 60天 | 应用日志 |
| 缓存数据 | `tmp/cache/` | 随时可删 | 临时缓存 |
| 图片资源 | `assets/images/` | 永久 | 项目图片、图标 |
| 技能包 | `skills/` | 永久 | SKILL.md 文件 |
| 知识库 | `knowledge-base/` | 永久 | 结构化知识 |
| 记忆文件 | `memory/` | 永久 | 每日记忆 |
| 脚本文件 | `scripts/` | 永久 | 自动化脚本 |

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

### 自动清理（每周一凌晨3点执行）
```bash
# 清理14天前的截图
find tmp/screenshots -name "*.png" -mtime +14 -delete

# 清理14天前的下载文件
find tmp/downloads -type f -mtime +14 -delete

# 清理60天前的报告
find reports -type f -mtime +60 -delete

# 清理60天前的日志
find tmp/logs -name "*.log" -mtime +60 -delete
```

### 手动清理
```bash
# 查看临时文件大小
du -sh tmp/*

# 清理所有临时文件（谨慎）
rm -rf tmp/*/

# 清理特定类型文件
find tmp/screenshots -name "*.png" -mtime +7 -delete
```

## 重要文件保护

以下文件**禁止自动清理**：
- `memory/*.md` — 每日记忆
- `knowledge-base/**/*` — 知识库
- `skills/*/SKILL.md` — 技能包
- `assets/**/*` — 静态资源
- `scripts/*.sh` — 脚本文件
- `.git/` — Git 仓库

## 存储空间管理

当前配置：
- **总空间**: 350G
- **清理策略**: 保守（14天/60天）
- **监控**: 每日健康检查报告包含磁盘使用情况

---
*创建于: 2026-03-04*  
*更新: 2026-03-04（延长保留时间至14天/60天）*
