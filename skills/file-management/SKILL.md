---
name: file-management
description: Workspace file organization and cleanup. Use when organizing files, cleaning up temporary files, or managing workspace structure. Ensures consistent file placement and automatic cleanup.
---

# 文件管理技能

## 目录结构

```
workspace/
├── assets/          # 静态资源（图片、图标）
├── knowledge-base/  # 知识库
├── memory/          # 每日记忆
├── reports/         # 生成的报告
├── scripts/         # 脚本文件
├── skills/          # 技能包
├── summary/         # 摘要汇总
└── tmp/             # 临时文件
    ├── screenshots/ # 截图
    ├── downloads/   # 下载文件
    └── cache/       # 缓存
```

## 文件存放规则

| 文件类型 | 存放位置 | 保留时间 |
|---------|---------|---------|
| 截图 | `tmp/screenshots/` | 7天 |
| 下载文件 | `tmp/downloads/` | 7天 |
| 生成的报告 | `reports/` | 30天 |
| 图片资源 | `assets/images/` | 永久 |
| 缓存 | `tmp/cache/` | 随时可删 |

## 命名规范

### 截图
```
screenshot_YYYYMMDD_HHMMSS.png
```

### 报告
```
daily_health_YYYYMMDD.txt
stock_report_YYYYMMDD.md
```

## 清理脚本

**位置**: `scripts/file-cleanup.sh`

**执行**:
```bash
bash ~/.openclaw/workspace/scripts/file-cleanup.sh
```

**清理内容**:
- 7天前的截图
- 7天前的下载文件
- 30天前的报告
- 30天前的日志
- 空目录

## 定时清理

添加到 crontab（每周清理一次）:
```bash
0 3 * * 1 /Users/zhaoruicn/.openclaw/workspace/scripts/file-cleanup.sh
```

## 重要文件（禁止清理）

- `memory/*.md` — 每日记忆
- `knowledge-base/**/*` — 知识库
- `skills/*/SKILL.md` — 技能包
- `assets/**/*` — 静态资源
- `scripts/*.sh` — 脚本文件

## 手动整理命令

```bash
# 查看大文件
find ~/.openclaw/workspace -type f -size +1M

# 查看临时文件大小
du -sh tmp/*

# 清理所有临时文件
rm -rf tmp/*/

# 创建标准目录结构
mkdir -p tmp/{screenshots,downloads,cache}
mkdir -p reports/{daily,weekly,project}
```

---
*创建于: 2026-03-04*
