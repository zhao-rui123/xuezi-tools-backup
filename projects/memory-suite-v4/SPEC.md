# Memory Suite v4.0 - 融合版规格文档

## 项目概述
将 Self-Improvement（自我进化）和 Knowledge-Base（知识库）功能融合到 Memory Suite v3.0，创建统一的记忆管理平台。

## 目标
- 整合三个系统的最佳功能
- 统一CLI、配置、调度器
- 模块化架构，易于扩展
- 保持向后兼容

## 目录结构

```
memory-suite-v4/
├── SKILL.md
├── config/
│   ├── config.json
│   └── modules.json
├── core/                       # 核心层（保留v3）
│   ├── __init__.py
│   ├── real_time.py           # 实时保存
│   ├── archiver.py            # 归档系统
│   ├── indexer.py             # 语义索引
│   └── analyzer.py            # 分析引擎
├── apps/                       # 应用层（扩展）
│   ├── __init__.py
│   ├── qa.py                  # 智能问答
│   ├── advisor.py             # 决策支持
│   ├── recommender.py         # 推荐系统
│   ├── profiler.py            # 用户画像
│   └── evolution/             # 新增：自我进化
│       ├── __init__.py
│       ├── daily_analyzer.py      # 每日分析
│       ├── long_term_planner.py   # 长期规划
│       ├── evolution_reporter.py  # 进化报告
│       └── skill_evaluator.py     # 技能评估
├── knowledge/                  # 新增：知识管理层
│   ├── __init__.py
│   ├── knowledge_manager.py       # 知识管理
│   ├── knowledge_graph.py         # 知识图谱
│   ├── knowledge_search.py        # 知识搜索
│   ├── knowledge_importer.py      # 知识导入
│   └── knowledge_sync.py          # 知识同步（替代原kb_sync）
├── integration/                # 集成层（保留）
│   ├── __init__.py
│   ├── notifier.py            # 通知系统
│   └── backup_helper.py       # 备份协助
├── scripts/                    # 维护脚本（保留）
│   ├── log_rotate.py
│   ├── error_notifier.py
│   └── cleanup.py
├── cli.py                      # CLI入口（扩展）
├── scheduler.py                # 调度器（扩展）
├── doctor.py                   # 诊断工具
└── tests/
    └── test_suite.py
```

## 新增功能规格

### 1. 自我进化模块 (apps/evolution/)

#### daily_analyzer.py
- 分析每日工作内容
- 统计任务完成情况
- 生成效率报告
- 定时：每天23:00

#### long_term_planner.py
- 基于历史数据生成长期规划
- 目标设定和追踪
- 月度/季度规划
- 定时：每月1号

#### evolution_reporter.py
- 生成自我进化报告
- 技能成长追踪
- 改进建议
- 定时：每月2号

#### skill_evaluator.py
- 评估技能包使用情况
- 使用频率统计
- 效果评估
- 定时：每周日

### 2. 知识管理模块 (knowledge/)

#### knowledge_manager.py
- 知识条目CRUD
- 知识分类管理
- 知识标签系统
- 知识版本控制

#### knowledge_graph.py
- 构建知识图谱
- 实体关系提取
- 图谱可视化（可选）
- 定时：每天01:00

#### knowledge_search.py
- 全文搜索
- 语义搜索
- 高级筛选
- 搜索结果排序

#### knowledge_importer.py
- 从记忆文件导入知识
- 自动提取关键信息
- 去重和合并
- 定时：每天06:00

#### knowledge_sync.py
- 同步到knowledge-base/
- 双向同步
- 冲突解决
- 替代原integration/kb_sync.py

## CLI扩展

```bash
# 自我进化命令
memory-suite evolution daily          # 每日分析
memory-suite evolution plan           # 长期规划
memory-suite evolution report         # 进化报告
memory-suite evolution skills         # 技能评估

# 知识管理命令
memory-suite knowledge list           # 列出知识
memory-suite knowledge search <query> # 搜索知识
memory-suite knowledge add <title>    # 添加知识
memory-suite knowledge graph          # 知识图谱
memory-suite knowledge sync           # 同步知识
```

## 定时任务配置

```cron
# 核心任务
*/10 * * * * scheduler run real-time
0 * * * * scheduler run index
30 0 * * * scheduler run archive
0 1 * * * scheduler run analyze-daily

# 自我进化任务
0 23 * * * scheduler run evolution-daily
0 2 1 * * scheduler run evolution-monthly
0 9 2 * * scheduler run evolution-report
0 22 * * 0 scheduler run skill-eval

# 知识管理任务
0 1 * * * scheduler run knowledge-graph
0 6 * * * scheduler run knowledge-sync

# 维护任务
0 3 * * * log_rotate.py
0 3 * * 1 cleanup.py
```

## 依赖关系

```
cli.py
  ↓
scheduler.py
  ↓
  ├── core/*
  ├── apps/*
  │   └── evolution/*
  ├── knowledge/*
  └── integration/*
```

## 配置扩展

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

## 验收标准

1. ✅ 所有v3功能正常
2. ✅ 自我进化功能可用
3. ✅ 知识管理功能可用
4. ✅ CLI命令完整
5. ✅ 定时任务正常
6. ✅ 测试通过
7. ✅ 文档完整

## 开发计划

### Phase 1: 自我进化模块（2个Agent）
- Agent 1: daily_analyzer.py + long_term_planner.py
- Agent 2: evolution_reporter.py + skill_evaluator.py

### Phase 2: 知识管理模块（2个Agent）
- Agent 3: knowledge_manager.py + knowledge_search.py
- Agent 4: knowledge_graph.py + knowledge_importer.py + knowledge_sync.py

### Phase 3: 整合层（1个Agent）
- Agent 5: CLI扩展 + scheduler扩展 + 配置更新

### Phase 4: 测试验证（Orchestrator）
- 整合测试
- 文档更新
- 部署验证
