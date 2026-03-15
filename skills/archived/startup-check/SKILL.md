---
name: startup-check
description: Post-startup system verification. Use after OpenClaw Gateway starts or after switching models to verify all components are working correctly. Ensures system readiness before starting work.
---

# 启动检查技能

## 用途

在以下场景执行：
- Gateway 启动后
- 切换模型后
- 系统重启后

## 执行检查

```bash
bash ~/.openclaw/workspace/scripts/startup-check.sh
```

## 检查项目

| 序号 | 检查项 | 正常状态 |
|------|--------|---------|
| 1 | Gateway 启动 | 30秒内响应 |
| 2 | 技能包加载 | 显示数量 |
| 3 | 知识库 | INDEX.md 存在 |
| 4 | 备份系统 | 脚本存在 |
| 5 | 定时任务 | 显示数量 |

## 自动执行

添加到 shell 配置：

```bash
# ~/.zshrc
alias ocs='bash ~/.openclaw/workspace/scripts/startup-check.sh'
```

## 启动后工作流

```bash
# 1. 执行启动检查
bash ~/.openclaw/workspace/scripts/startup-check.sh

# 2. 读取系统状态
cat ~/.openclaw/workspace/MEMORY.md | head -50

# 3. 查看知识库索引
cat ~/.openclaw/workspace/knowledge-base/INDEX.md

# 4. 开始工作
```

## 故障处理

### Gateway 启动超时
```bash
# 强制重启
openclaw gateway stop
sleep 2
openclaw gateway start
```

### 技能包未加载
```bash
# 检查技能包目录
ls ~/.openclaw/workspace/skills/

# 重新扫描
openclaw skills scan
```

---
*创建于: 2026-03-04*
