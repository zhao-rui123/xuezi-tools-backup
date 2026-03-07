---
name: self-improvement
description: 自我进化系统 - 从错误中学习、性能监控、自动优化、技能包管理
metadata:
  openclaw:
    requires:
      bins: [python3, git]
---

# Self Improvement - 自我进化系统

## 🧠 核心理念

这是一个"元技能包"（Meta Skill）- 让AI助手能够自我学习、自我优化、自我管理的系统。

## 📦 包含模块

### 1. self_improvement.py - 学习系统

**功能：从错误和成功中学习，自动积累经验**

```bash
# 记录一次错误学习
python3 self_improvement.py learn-error "时区问题" "混淆了PST和北京时间" "始终使用数字时间，忽略时区标签"

# 应用学习到MEMORY.md
python3 self_improvement.py apply

# 生成自我提示
python3 self_improvement.py prompt
```

**学习流程：**
1. 记录错误场景 → 问题描述 → 解决方案
2. 存储到 `memory/self-improvement.json`
3. 定期汇总应用到 `MEMORY.md`
4. 生成自我提示词，避免重复犯错

---

### 2. performance_monitor.py - 性能监控

**功能：监控运行效率，发现优化点**

```bash
# 生成性能报告
python3 performance_monitor.py report

# 分析性能数据
python3 performance_monitor.py analyze

# 检测异常
python3 performance_monitor.py anomalies
```

**监控指标：**
- Token使用量（成本优化）
- 响应时间（用户体验）
- 工具调用次数（效率）
- 成功率（稳定性）
- 模型使用分布

---

### 3. skill_auto_updater.py - 技能包管理

**功能：自动维护、检查、更新技能包**

```bash
# 检查技能包更新
python3 skill_auto_updater.py check

# 自动维护所有技能包
python3 skill_auto_updater.py maintain

# 生成技能包索引
python3 skill_auto_updater.py index
```

**维护内容：**
- 检查Git状态
- 验证SKILL.md完整性
- 自动备份更改
- 生成技能包目录

---

## 🔄 进化循环

```
        ┌─────────────┐
        │   执行任务   │
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐
        │  记录性能   │ ← performance_monitor
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐
        │  遇到问题   │
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐
        │  记录学习   │ ← self_improvement
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐
        │  应用学习   │
        │  到MEMORY.md│
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐
        │  避免重复   │
        │   犯错     │
        └─────────────┘
```

---

## 📊 自动化集成

### 添加到定时任务

```bash
# 编辑 crontab
crontab -e

# 每天分析性能（早上8点）
0 8 * * * ~/.openclaw/workspace/skills/self-improvement/performance_monitor.py report >> /tmp/perf-report.log 2>&1

# 每周应用学习总结（周日晚上）
0 22 * * 0 ~/.openclaw/workspace/skills/self-improvement/self_improvement.py apply

# 每周维护技能包（周日凌晨）
0 3 * * 1 ~/.openclaw/workspace/skills/self-improvement/skill_auto_updater.py maintain
```

### 集成到心跳检查

在HEARTBEAT.md中添加：
```markdown
## 自我进化检查
- [ ] 性能是否正常？
- [ ] 是否有未应用的学习项？
- [ ] 技能包是否需要维护？
```

---

## 💡 使用场景

### 场景1: 错误学习

```
用户: "你又搞错时区了"
→ 执行: self_improvement.py learn-error "时区表述" "混淆PST和北京时间" "直接报数字，忽略时区标签"
→ 记录到 self-improvement.json
→ 下次遇到时间相关问题时自动提醒
```

### 场景2: 性能优化

```
发现响应时间超过5秒
→ performance_monitor.py 记录并标记为异常
→ 分析发现是工具调用过多
→ 优化为批量处理
→ 下次避免同样问题
```

### 场景3: 技能包自动维护

```
每周自动检查:
- 哪些技能包有未提交更改？
- 哪些SKILL.md需要更新？
- 生成最新技能包索引
```

---

## 🎯 进化目标

1. **减少重复错误** - 同样的错误不犯第二次
2. **提升响应效率** - 优化工具调用和上下文使用
3. **保持技能包健康** - 自动维护和更新
4. **持续学习改进** - 从每次交互中学习

---

## 🔒 隐私说明

- 性能数据只记录统计信息，不记录对话内容
- 学习项存储在本地，不上传
- 不包含任何个人敏感信息
