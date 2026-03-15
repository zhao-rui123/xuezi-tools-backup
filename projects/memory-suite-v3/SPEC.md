# Memory Suite v3.0 - 完整重构规格文档

## 项目概述
整合 services/memory/ 和 skills/unified-memory/ 两个系统，创建统一的记忆管理技能包。

## 目标
- 统一CLI入口
- 统一配置管理
- 统一调度器
- 模块化架构
- 生产级稳定性

## 技术栈
- Python 3.11+
- 纯标准库（无外部依赖）
- JSON/YAML 配置

## 目录结构
```
skills/memory-suite-v3/
├── SKILL.md
├── config/
│   ├── config.json          # 主配置
│   └── modules.json         # 模块开关
├── core/                     # 核心层
│   ├── __init__.py
│   ├── real_time.py         # 实时保存
│   ├── archiver.py          # 归档系统
│   ├── indexer.py           # 语义索引
│   └── analyzer.py          # 分析引擎
├── apps/                     # 应用层
│   ├── __init__.py
│   ├── qa.py                # 智能问答
│   ├── advisor.py           # 决策支持
│   ├── recommender.py       # 推荐系统
│   └── profiler.py          # 用户画像
├── integration/              # 集成层
│   ├── __init__.py
│   ├── kb_sync.py           # 知识库同步
│   ├── notifier.py          # 通知系统
│   └── backup_helper.py     # 备份协助
├── cli.py                    # CLI入口
├── scheduler.py              # 调度器
├── doctor.py                 # 诊断工具
└── tests/
    └── test_suite.py
```

## 核心功能规格

### 1. Real-time (core/real_time.py)
- 每10分钟保存会话快照
- 保存到 memory/snapshots/current_session.json
- 保留最近50轮对话

### 2. Archiver (core/archiver.py)
- 7天后归档到 memory/archive/
- 30天后提取关键信息到 permanent/
- 90天后压缩
- 365天后删除

### 3. Indexer (core/indexer.py)
- 每小时更新语义索引
- 支持关键词搜索
- 索引存储在 memory/index/

### 4. Analyzer (core/analyzer.py)
- 月度记忆分析
- 主题提取
- 关键词统计

### 5. QA (apps/qa.py)
- 基于记忆回答问题
- 命令: memory-suite qa "问题"

### 6. Scheduler (scheduler.py)
- 统一调度所有定时任务
- 支持: scheduler run <task>
- 任务列表: real-time, archive, index, analyze, sync

### 7. CLI (cli.py)
- 统一命令入口
- 子命令: save, restore, search, qa, archive, report, config, doctor

### 8. Doctor (doctor.py)
- 系统健康检查
- 配置验证
- 问题诊断

## CLI 命令规格

```bash
# 实时操作
memory-suite save                    # 立即保存
memory-suite restore                 # 恢复会话
memory-suite status                  # 查看状态

# 搜索查询
memory-suite search <query>          # 语义搜索
memory-suite qa <question>           # 智能问答

# 归档管理
memory-suite archive list            # 列出归档
memory-suite archive restore <date>  # 恢复归档
memory-suite archive clean           # 清理旧归档

# 报告
memory-suite report daily            # 日报
memory-suite report weekly           # 周报
memory-suite report monthly          # 月报

# 配置
memory-suite config show             # 显示配置
memory-suite config set <key> <val>  # 设置配置
memory-suite config reset            # 重置配置

# 系统
memory-suite doctor                  # 诊断检查
memory-suite scheduler run <task>    # 运行定时任务
memory-suite scheduler list          # 列出任务
```

## 定时任务规格

```cron
# 实时层
*/10 * * * * memory-suite scheduler run real-time
0 * * * * memory-suite scheduler run index

# 归档层
30 0 * * * memory-suite scheduler run archive

# 分析层
0 1 * * * memory-suite scheduler run analyze-daily
0 2 1 * * memory-suite scheduler run analyze-monthly

# 集成层
0 6 * * * memory-suite scheduler run kb-sync
```

## 配置规格

```json
{
  "version": "3.0.0",
  "workspace": "~/.openclaw/workspace",
  "memory_dir": "~/.openclaw/workspace/memory",
  "modules": {
    "real_time": {"enabled": true, "interval_minutes": 10},
    "archiver": {"enabled": true, "archive_days": 7, "permanent_days": 30},
    "indexer": {"enabled": true, "interval_hours": 1},
    "analyzer": {"enabled": true},
    "qa": {"enabled": true},
    "kb_sync": {"enabled": true}
  },
  "notifications": {
    "enabled": true,
    "on_archive": true,
    "on_error": true
  }
}
```

## 验收标准

1. ✅ CLI所有命令可用
2. ✅ 定时任务正常运行
3. ✅ 数据不丢失
4. ✅ 配置可热更新
5. ✅ doctor检查通过
6. ✅ 测试用例通过

## 开发计划

### Phase 1: 核心层 (4个Agent)
- Agent 1: core/real_time.py + core/archiver.py
- Agent 2: core/indexer.py + core/analyzer.py
- Agent 3: cli.py + scheduler.py
- Agent 4: config/ + doctor.py

### Phase 2: 应用层 (2个Agent)
- Agent 5: apps/qa.py + apps/advisor.py
- Agent 6: apps/recommender.py + apps/profiler.py

### Phase 3: 集成层 (1个Agent)
- Agent 7: integration/ + tests/

### Phase 4: 整合测试 (Orchestrator)
- 整合所有模块
- 编写SKILL.md
- 配置定时任务
- 运行测试

## 依赖关系

```
cli.py -> scheduler.py -> core/*, apps/*, integration/*
doctor.py -> config/*
scheduler.py -> core/*, apps/*, integration/*
```

## 注意事项

1. 保持与现有数据格式兼容
2. 不要删除现有记忆文件
3. 支持从旧系统迁移
4. 所有错误都要捕获并记录
