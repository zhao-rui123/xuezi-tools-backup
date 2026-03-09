# 备份结构说明 v2.1
## 重新整理的清晰备份目录

```
/Volumes/cu/ocu/
├── memory-backup/                 # 记忆备份 (62个文件)
│   ├── daily/                     # 8个 - 每日记忆文件
│   │   ├── 2026-03-01.md
│   │   ├── 2026-03-02.md
│   │   ├── 2026-03-03.md
│   │   ├── 2026-03-06.md
│   │   ├── 2026-03-07.md
│   │   ├── 2026-03-08.md
│   │   └── 2026-03-09.md
│   │
│   ├── archive/                   # 16个 - 历史归档
│   │   └── (归档的历史记忆文件)
│   │
│   ├── snapshots/                 # 1个 - 会话快照
│   │   └── (自动保存的会话状态)
│   │
│   ├── evolution/                 # 7个 - 自我进化系统
│   │   ├── learning_library.json
│   │   ├── evolution_score.json
│   │   └── (其他进化相关文件)
│   │
│   ├── reports/                   # 9个 - 系统报告
│   │   ├── system_test_report_2026-03-09.md
│   │   ├── importance_report.json
│   │   └── (其他报告)
│   │
│   ├── knowledge/                 # 4个 - 知识图谱
│   │   ├── graph.json
│   │   └── (知识图谱数据)
│   │
│   ├── index/                     # 3个 - 搜索索引
│   │   ├── keyword_index.json
│   │   └── (索引文件)
│   │
│   └── config/                    # 14个 - 配置文件
│       ├── memory_scores.json
│       ├── user_profile.json
│       ├── skill_memory.json
│       └── (其他配置)
│
├── skills-backup/                 # 技能备份 (236个文件)
│   ├── core/                      # 180个 - 核心技能包
│   │   ├── unified-memory/        # 38个文件 - 统一记忆系统
│   │   ├── stock-analysis-pro/    # 31个文件
│   │   ├── stock-screener/        # 22个文件
│   │   ├── self-improvement/      # 14个文件
│   │   ├── multi-agent-suite/     # 14个文件
│   │   ├── office-pro/            # 15个文件
│   │   └── (其他44个核心技能包)
│   │
│   ├── archived/                  # 42个 - 已归档技能
│   │   ├── yfinance-stock/
│   │   ├── memory-search/
│   │   ├── openclaw-memory-kit/
│   │   ├── nano-pdf/
│   │   └── report-generator/
│   │
│   └── suites/                    # 14个 - 技能套件
│       ├── stock-analysis-suite/
│       ├── system-ops-suite/
│       ├── document-suite/
│       └── file-transfer-suite/
│
├── full-backups/                  # 完整备份压缩包
│   ├── openclaw-backup-20260309_222543.tar.gz  # 2.2MB
│   └── latest -> (指向最新备份)
│
└── backup-manifest-20260309.json  # 备份清单
```

## 📊 备份统计

| 类别 | 文件数 | 说明 |
|------|--------|------|
| **Memory** | 62个 | 记忆文件，按类型分类 |
| **Skills** | 236个 | 技能包，按状态分类 |
| **总计** | 298个 | 完整备份 |
| **压缩包** | 2.2MB | tar.gz 格式 |

## 🎯 目录说明

### Memory 分类
- **daily/** - 每日工作记录，每天一个markdown文件
- **archive/** - 自动归档的历史记忆（7/30/90天）
- **snapshots/** - 会话快照，防止卡死的自动保存
- **evolution/** - 自我进化系统数据
- **reports/** - 系统生成的各种报告
- **knowledge/** - 知识图谱数据
- **index/** - 语义搜索索引
- **config/** - JSON配置文件

### Skills 分类
- **core/** - 核心技能包（44个正在使用的技能）
- **archived/** - 已归档的旧技能（5个不再使用的）
- **suites/** - 技能套件（4个套件入口）

## 🔍 如何查找文件

### 找今天的记忆
```
memory-backup/daily/2026-03-09.md
```

### 找系统测试报告
```
memory-backup/reports/system_test_report_2026-03-09.md
```

### 找股票分析技能
```
skills-backup/core/stock-analysis-pro/
```

### 找统一记忆系统
```
skills-backup/core/unified-memory/
```

### 查看最新备份清单
```
backup-manifest-20260309.json
```

## 📝 备份脚本

- **脚本位置**: `~/.openclaw/workspace/skills/system-backup/scripts/daily-backup-v2.sh`
- **定时任务**: 每天 22:00
- **日志位置**: `/tmp/backup_cron.log`

## ✅ 特点

1. **分类清晰** - 按功能分类存放，不再混乱
2. **清单管理** - 每次备份生成JSON清单，方便查看
3. **快速定位** - 知道文件类型就能快速找到
4. **自动清理** - 保留最近30天的压缩包

---

*备份结构版本: 2.1*
*更新时间: 2026-03-09*
