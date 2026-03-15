# Memory Suite v4.0 - 统一记忆系统

## 清洁版说明

此版本已去除所有个人信息，可安全分享给朋友。

## 安装步骤

### 1. 解压到技能包目录
```bash
cp -r memory-suite-v4-clean ~/.openclaw/workspace/skills/
```

### 2. 配置路径
编辑 `config/config.json`，修改以下路径为你的实际路径：

```json
{
  "workspace": "/path/to/your/workspace",
  "memory_dir": "/path/to/your/workspace/memory",
  "knowledge_dir": "/path/to/your/workspace/knowledge-base"
}
```

### 3. 配置定时任务
```bash
crontab -e
```

添加以下内容：
```
# Memory Suite v4.0 核心任务
0 0 * * * cd /path/to/your/workspace/skills/memory-suite-v4 && python3 scheduler.py run daily-init
*/10 * * * * cd /path/to/your/workspace/skills/memory-suite-v4 && python3 scheduler.py run real-time
0 * * * * cd /path/to/your/workspace/skills/memory-suite-v4 && python3 scheduler.py run index
30 0 * * * cd /path/to/your/workspace/skills/memory-suite-v4 && python3 scheduler.py run archive
0 1 * * * cd /path/to/your/workspace/skills/memory-suite-v4 && python3 scheduler.py run analyze-daily
```

### 4. 测试运行
```bash
cd ~/.openclaw/workspace/skills/memory-suite-v4
python3 scheduler.py run daily-init
python3 scheduler.py run real-time
```

### 5. 查看状态
```bash
python3 cli.py status
```

## 功能特性

- ✅ 每日自动创建记忆文件 (00:00)
- ✅ 每10分钟实时保存会话内容
- ✅ 每小时更新语义索引
- ✅ 每天归档旧记忆文件 (00:30)
- ✅ 每天生成分析报告 (01:00)

## 目录结构

```
memory-suite-v4/
├── config/          # 配置文件
├── core/            # 核心模块
│   ├── real_time.py         # 实时保存
│   ├── session_capture.py   # 会话捕获
│   ├── archiver.py          # 归档管理
│   ├── analyzer.py          # 分析引擎
│   └── indexer.py           # 索引管理
├── cli.py           # 命令行工具
├── scheduler.py     # 定时任务调度器
└── SKILL.md         # 使用文档
```

## 使用方法

### 手动保存
```bash
python3 cli.py save
```

### 查看状态
```bash
python3 cli.py status
```

### 系统诊断
```bash
python3 cli.py doctor
```

## 依赖安装

```bash
pip install pandas numpy
```

## 注意事项

1. 首次使用请修改 `config/config.json` 中的路径
2. 确保工作目录有读写权限
3. 定时任务需要使用绝对路径
4. 日志文件保存在 `/tmp/memory-suite.log`

## 文档

详见 `SKILL.md` 文件。

---
*清洁版 - 2026-03-13*
