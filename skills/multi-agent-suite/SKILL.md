---
name: multi-agent-suite
description: |
  多Agent协作增强系统 v3.1 - 终极版
  11-Agent超级团队(新增Kilo通知Agent) + Web看板 + CI/CD + 完整开发流程
version: 3.1.0
---

# 多Agent协作系统 v3.1 - 终极版 🚀

**11-Agent超级团队(含通知Agent Kilo)**，企业级项目开发一站式解决方案！

## 🌟 核心特性

### 🤖 11-Agent超级团队
| Agent | 角色 | 专长 |
|-------|------|------|
| Alpha | Builder | 🎨 前端开发 |
| Bravo | Builder | ⚙️ 后端开发 |
| Charlie | Builder | 🔧 全栈整合 |
| Delta | Reviewer | 🔍 代码审查 |
| Echo | DevOps | 🚀 部署运维 |
| Foxtrot | Security Expert | 🔒 安全审计 |
| Golf | Performance Expert | ⚡ 性能优化 |
| Hotel | Documentation Expert | 📝 文档编写 |
| India | AI Expert | 🧠 AI算法 |
| Juliet | Data Expert | 📊 数据处理 |
| **Kilo** | **Notification Agent** | **📢 统一通知** |

### 🚀 5大增强功能
1. ✅ **Web管理界面** - 可视化任务看板
2. ✅ **Agent间通信** - 实时协作
3. ✅ **智能任务预估** - AI预测工期
4. ✅ **版本控制集成** - Git自动化
5. ✅ **CI/CD流水线** - 自动化部署

## 🆕 Kilo - 通知Agent (v3.1 新增)

**职责**: 统一发送所有定时任务通知和系统消息

**能力**:
- ✅ 发送每日备份通知
- ✅ 发送健康检查报告
- ✅ 发送系统告警
- ✅ 发送任务提醒
- ✅ 发送每日工作汇总

**使用方法**:
```bash
# 发送备份通知
python3 ~/.openclaw/workspace/skills/multi-agent-suite/agents/kilo_notification.py \
  --alert "备份完成！" --alert-type info

# 发送系统告警
python3 ~/.openclaw/workspace/skills/multi-agent-suite/agents/kilo_notification.py \
  --alert "磁盘空间不足" --alert-type warning

# 发送任务提醒
python3 ~/.openclaw/workspace/skills/multi-agent-suite/agents/kilo_notification.py \
  --reminder "检查备份" --due "22:00"

# 发送每日汇总
python3 ~/.openclaw/workspace/skills/multi-agent-suite/agents/kilo_notification.py \
  --daily-summary
```

**集成到定时任务**:
所有定时任务都可以通过 Kilo 统一发送通知，例如：
```bash
# 在备份脚本中调用
bash ~/.openclaw/workspace/scripts/kilo-notify.sh daily-backup success "备份62个文件"
```

## 📁 完整文件结构

```
multi-agent-suite/
├── SKILL.md                      # 本文档
├── core/
│   ├── orchestrator.py           # Agent调度器(v3.1支持11-Agent)
│   ├── workflow.py               # 开发流程管理
│   ├── agent_communication.py    # Agent通信模块
│   └── task_estimator.py         # 任务预估器
├── web-ui/                       # Web管理界面
│   ├── app.py
│   └── templates/
│       └── dashboard.html
├── agents/
│   ├── config.json               # 11-Agent配置
│   └── kilo_notification.py      # Kilo通知Agent ⭐NEW v3.1
└── scripts/                      # 工具脚本
    ├── git-integration.sh        # Git集成
    └── ci-cd.sh                  # CI/CD流水线
```

## 🚀 快速使用

### 查看11-Agent团队
```bash
cd ~/.openclaw/workspace/skills/multi-agent-suite/core
python3 orchestrator.py --list-agents
```

### 启动Web管理界面
```bash
cd ~/.openclaw/workspace/skills/multi-agent-suite/web-ui
python3 app.py
# 访问 http://localhost:8080
```

### 创建大型项目
```bash
cd ~/.openclaw/workspace/skills/multi-agent-suite/core
python3 workflow.py \
  --create "智能投资平台" \
  --description "AI驱动的投资分析平台" \
  --requirements "数据采集" "AI模型" "可视化" "用户系统"
```

### 使用Kilo发送通知
```bash
python3 ~/.openclaw/workspace/skills/multi-agent-suite/agents/kilo_notification.py \
  --alert "任务完成！" --alert-type info
```

## 🎯 适用场景

- ✅ 企业级Web应用
- ✅ AI驱动产品
- ✅ 大数据分析平台
- ✅ 复杂全栈系统
- ✅ 金融科技产品
- ✅ **定时任务统一通知** (Kilo新增)

---

**v3.1 终极版 - 11-Agent + 统一通知中心！** 🎉

*更新日志 v3.1:*
- 新增 Kilo (Notification Agent) - 统一通知中心
- 支持所有定时任务通过Kilo发送通知
- 优化Agent角色识别
