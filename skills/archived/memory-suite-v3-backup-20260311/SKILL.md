# Memory Suite v3.0

统一记忆管理系统 - 整合实时保存、归档、分析、问答于一体。

## 功能特性

### 核心层
- **实时保存** - 每10分钟自动保存会话快照
- **归档系统** - 7天归档、30天永久记录、90天压缩、365天清理
- **语义索引** - 每小时更新索引，支持关键词搜索
- **分析引擎** - 月度分析、主题提取、关键词统计

### 应用层
- **智能问答** - 基于记忆内容回答问题
- **决策支持** - 从历史决策中提取建议
- **推荐系统** - 推荐相关记忆和任务
- **用户画像** - 分析用户偏好和习惯

### 集成层
- **知识库同步** - 同步记忆到 knowledge-base/
- **通知系统** - 飞书通知支持
- **备份协助** - 与备份系统协作

## 安装

```bash
# 添加到 skills 目录
ln -s ~/.openclaw/workspace/skills/memory-suite-v3 ~/.openclaw/skills/memory-suite

# 配置定时任务
crontab -e
# 添加: */10 * * * * python3 ~/.openclaw/workspace/skills/memory-suite-v3/scheduler.py run real-time
```

## CLI 使用

```bash
# 实时操作
python3 cli.py save              # 立即保存
python3 cli.py restore           # 恢复会话
python3 cli.py status            # 查看状态

# 搜索查询
python3 cli.py search "关键词"    # 语义搜索
python3 cli.py qa "问题"          # 智能问答

# 归档管理
python3 cli.py archive list      # 列出归档
python3 cli.py archive clean     # 清理旧归档

# 报告
python3 cli.py report daily      # 日报
python3 cli.py report weekly     # 周报
python3 cli.py report monthly    # 月报

# 系统
python3 cli.py doctor            # 诊断检查
python3 cli.py config show       # 显示配置
```

## 定时任务

```cron
# 实时层
*/10 * * * * python3 scheduler.py run real-time
0 * * * * python3 scheduler.py run index

# 归档层
30 0 * * * python3 scheduler.py run archive

# 分析层
0 1 * * * python3 scheduler.py run analyze-daily
0 2 1 * * python3 scheduler.py run analyze-monthly

# 集成层
0 6 * * * python3 scheduler.py run kb-sync
```

## 配置

编辑 `config/config.json`：

```json
{
  "modules": {
    "real_time": {"enabled": true, "interval_minutes": 10},
    "archiver": {"enabled": true, "archive_days": 7},
    "indexer": {"enabled": true, "interval_hours": 1},
    "analyzer": {"enabled": true}
  }
}
```

## 测试

```bash
python3 tests/test_suite.py
```

## 目录结构

```
memory-suite-v3/
├── core/           # 核心层
├── apps/           # 应用层
├── integration/    # 集成层
├── config/         # 配置
├── tests/          # 测试
├── cli.py          # CLI入口
├── scheduler.py    # 调度器
└── doctor.py       # 诊断工具
```

## 作者

AI Agent Team

## 版本

v3.0.0 - 2026-03-11
