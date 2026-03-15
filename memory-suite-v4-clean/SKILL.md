# Memory Suite v4.0

统一记忆管理系统 - 融合实时保存、归档、分析、问答、自我进化与知识管理于一体。

## 功能特性

### 核心层 (core/)
- **实时保存** - 每 10 分钟自动保存会话快照
- **归档系统** - 7 天归档、30 天永久记录、90 天压缩、365 天清理
- **语义索引** - 每小时更新索引，支持关键词搜索
- **分析引擎** - 每日/周/月分析、主题提取、关键词统计

### 应用层 (apps/)
- **智能问答** - 基于记忆内容回答问题
- **决策支持** - 从历史决策中提取建议
- **推荐系统** - 推荐相关记忆和任务
- **用户画像** - 分析用户偏好和习惯

### 自我进化模块 (apps/evolution/)
- **每日分析** - 分析每日工作内容，统计任务完成情况，生成效率报告
- **长期规划** - 基于历史数据生成月度/季度规划，目标设定和追踪
- **进化报告** - 生成自我进化报告，技能成长追踪，改进建议
- **技能评估** - 评估技能包使用情况，使用频率统计，效果评估

### 知识管理模块 (knowledge/)
- **知识管理** - 知识条目 CRUD、分类管理、标签系统、版本控制
- **知识图谱** - 构建知识图谱，实体关系提取，图谱可视化
- **知识搜索** - 全文搜索、语义搜索、高级筛选、搜索结果排序
- **知识导入** - 从记忆文件导入知识，自动提取关键信息，去重合并
- **知识同步** - 同步到 knowledge-base/，双向同步，冲突解决

### 集成层 (integration/)
- **知识库同步** - 同步记忆到 knowledge-base/
- **通知系统** - 飞书通知支持
- **备份协助** - 与备份系统协作

## 安装

```bash
# 添加到 skills 目录
ln -s ~/.openclaw/workspace/skills/memory-suite-v4 ~/.openclaw/skills/memory-suite

# 配置定时任务
crontab -e
```

## CLI 使用

### 实时操作
```bash
python3 cli.py save              # 立即保存
python3 cli.py restore           # 恢复会话
python3 cli.py status            # 查看状态
```

### 搜索查询
```bash
python3 cli.py search "关键词"    # 语义搜索
python3 cli.py qa "问题"          # 智能问答
```

### 归档管理
```bash
python3 cli.py archive list      # 列出归档
python3 cli.py archive clean     # 清理旧归档
```

### 报告生成
```bash
python3 cli.py report daily      # 日报
python3 cli.py report weekly     # 周报
python3 cli.py report monthly    # 月报
```

### 自我进化 (新增)
```bash
python3 cli.py evolution daily         # 每日分析
python3 cli.py evolution plan          # 长期规划
python3 cli.py evolution report        # 进化报告
python3 cli.py evolution skills        # 技能评估
python3 cli.py evolution status        # 进化状态
```

### 知识管理 (新增)
```bash
python3 cli.py knowledge list          # 列出知识条目
python3 cli.py knowledge search "query" # 搜索知识
python3 cli.py knowledge add "标题"    # 添加知识
python3 cli.py knowledge graph         # 构建知识图谱
python3 cli.py knowledge sync          # 同步知识库
python3 cli.py knowledge show <id>     # 显示知识详情
```

### 系统管理
```bash
python3 cli.py doctor            # 诊断检查
python3 cli.py config show       # 显示配置
python3 cli.py scheduler list    # 列出定时任务
python3 cli.py scheduler run <task>  # 运行任务
```

## 定时任务

```cron
# 核心层 - 实时层
*/10 * * * * python3 scheduler.py run real-time
0 * * * * python3 scheduler.py run index

# 核心层 - 归档层
30 0 * * * python3 scheduler.py run archive

# 核心层 - 分析层
0 1 * * * python3 scheduler.py run analyze-daily

# 自我进化层
0 23 * * * python3 scheduler.py run evolution-daily        # 每日分析
0 2 1 * * python3 scheduler.py run evolution-monthly       # 月度规划
0 9 2 * * python3 scheduler.py run evolution-report        # 进化报告
0 22 * * 0 python3 scheduler.py run skill-eval             # 技能评估 (每周日)

# 知识管理层
0 1 * * * python3 scheduler.py run knowledge-graph         # 知识图谱
0 6 * * * python3 scheduler.py run knowledge-sync          # 知识同步
0 6 * * * python3 scheduler.py run knowledge-import        # 知识导入

# 维护任务
0 3 * * * python3 scripts/log_rotate.py
0 3 * * 1 python3 scripts/cleanup.py
```

## 配置

编辑 `config/config.json`：

```json
{
  "modules": {
    "real_time": {"enabled": true, "interval_minutes": 10},
    "archiver": {"enabled": true, "archive_days": 7},
    "indexer": {"enabled": true, "interval_hours": 1},
    "analyzer": {"enabled": true},
    "evolution": {
      "enabled": true,
      "daily_analysis": true,
      "long_term_planning": true,
      "monthly_report": true,
      "skill_evaluation": true
    },
    "knowledge": {
      "enabled": true,
      "graph_building": true,
      "auto_import": true,
      "sync_enabled": true
    }
  }
}
```

## 目录结构

```
memory-suite-v4/
├── SKILL.md                    # 技能文档
├── cli.py                      # CLI 入口
├── scheduler.py                # 调度器
├── doctor.py                   # 诊断工具
├── config/
│   ├── config.json             # 主配置
│   └── modules.json            # 模块配置
├── core/                       # 核心层
│   ├── __init__.py
│   ├── real_time.py           # 实时保存
│   ├── archiver.py            # 归档系统
│   ├── indexer.py             # 语义索引
│   └── analyzer.py            # 分析引擎
├── apps/                       # 应用层
│   ├── __init__.py
│   ├── qa.py                  # 智能问答
│   ├── advisor.py             # 决策支持
│   ├── recommender.py         # 推荐系统
│   ├── profiler.py            # 用户画像
│   └── evolution/             # 自我进化
│       ├── __init__.py
│       ├── daily_analyzer.py      # 每日分析
│       ├── long_term_planner.py   # 长期规划
│       ├── evolution_reporter.py  # 进化报告
│       └── skill_evaluator.py     # 技能评估
├── knowledge/                  # 知识管理
│   ├── __init__.py
│   ├── knowledge_manager.py       # 知识管理
│   ├── knowledge_graph.py         # 知识图谱
│   ├── knowledge_search.py        # 知识搜索
│   ├── knowledge_importer.py      # 知识导入
│   └── knowledge_sync.py          # 知识同步
├── integration/                # 集成层
│   ├── __init__.py
│   ├── notifier.py            # 通知系统
│   └── backup_helper.py       # 备份协助
├── scripts/                    # 维护脚本
│   ├── log_rotate.py
│   ├── error_notifier.py
│   └── cleanup.py
└── tests/
    └── test_suite.py
```

## 模块依赖

```
cli.py
  ↓
scheduler.py
  ↓
  ├── core/*                    # 核心功能
  ├── apps/*                    # 应用功能
  │   └── evolution/*           # 自我进化
  ├── knowledge/*               # 知识管理
  └── integration/*             # 集成功能
```

## 错误处理

所有模块均包含完善的错误处理：
- 模块未实现时自动降级
- 错误自动通知（通过 scripts/error_notifier.py）
- 详细的日志记录
- 优雅的错误恢复机制

## 测试

```bash
python3 tests/test_suite.py
```

## 版本历史

### v4.0.0 (2026-03-11)
- ✅ 融合 Self-Improvement 和 Knowledge-Base 功能
- ✅ 统一 CLI 接口
- ✅ 统一调度器
- ✅ 新增自我进化命令：evolution daily/plan/report/skills
- ✅ 新增知识管理命令：knowledge list/search/add/graph/sync
- ✅ 新增定时任务：evolution-daily/monthly/report, skill-eval, knowledge-graph/sync/import
- ✅ 完善错误通知集成
- ✅ 与 v3.0 风格保持一致

### v3.0.0
- 初始统一版本

## 作者

AI Agent Team

## 许可证

MIT
