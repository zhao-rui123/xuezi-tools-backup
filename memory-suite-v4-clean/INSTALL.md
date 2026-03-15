# Memory Suite v4.0 - 统一记忆系统（清洁版）

## 说明
此版本已去除所有个人信息，可直接分享给朋友使用。

## 安装步骤

### 1. 复制到技能包目录
```bash
cp -r memory-suite-v4-clean ~/.openclaw/workspace/skills/memory-suite-v4
```

### 2. 修改配置文件
编辑 `~/.openclaw/workspace/skills/memory-suite-v4/config/config.json`：

```json
{
  "workspace": "/your/path/to/workspace",
  "memory_dir": "/your/path/to/workspace/memory",
  "knowledge_dir": "/your/path/to/workspace/knowledge-base"
}
```

### 3. 添加定时任务
```bash
crontab -e
```

添加：
```
# Memory Suite v4.0
0 0 * * * cd /your/path/to/workspace/skills/memory-suite-v4 && python3 scheduler.py run daily-init >> /tmp/memory-suite.log 2>&1
*/10 * * * * cd /your/path/to/workspace/skills/memory-suite-v4 && python3 scheduler.py run real-time >> /tmp/memory-suite.log 2>&1
0 * * * * cd /your/path/to/workspace/skills/memory-suite-v4 && python3 scheduler.py run index >> /tmp/memory-suite.log 2>&1
```

### 4. 测试
```bash
cd ~/.openclaw/workspace/skills/memory-suite-v4
python3 scheduler.py run daily-init
python3 cli.py status
```

## 核心功能
- 每日自动创建记忆文件
- 每10分钟实时保存会话
- 自动归档旧文件
- 生成每日分析报告

## 依赖
```bash
pip install pandas numpy
```

---
*清洁版 - 2026-03-13*
