---
name: multi-agent-suite
description: |
  多Agent软件开发工作流系统 v4.1 - 专业级
  12-Agent团队 + 瀑布模型 + 文档生成 + 部署管理 + 质量保障
  专业级基础设施: 日志/单例/缓存/验证/异常处理
version: 4.1.0
---

# Multi-Agent 软件开发工作流系统 v4.1 🚀

**12-Agent超级团队**，企业级标准软件开发一站式解决方案！
完整遵循软件工程瀑布模型，从需求到交付全流程覆盖。

## 🌟 核心特性

### 🤖 12-Agent超级团队
| Agent | 角色 | 专长 | 阶段 |
|-------|------|------|------|
| Product | 产品经理 | 需求分析、PRD编写、优先级排序 | 需求/交付 |
| Architect | 架构师 | 系统架构设计、ER图、技术选型 | 设计 |
| Orchestrator | 项目经理 | 任务拆解、进度管理、资源协调 | 开发 |
| Alpha | 前端工程师 | HTML/CSS/JS/Vue/React界面开发 | 开发 |
| Bravo | 后端工程师 | Python/Java/算法/API开发 | 开发 |
| Charlie | 功能工程师 | 功能完善、业务逻辑、集成 | 开发 |
| Delta | 修复工程师 | Bug修复、性能优化 | 开发 |
| Echo | 测试工程师 | 单元测试、集成测试、Code Review | 测试 |
| Kilo | 运维工程师 | 部署监控、定时任务、CI/CD | 部署 |
| Foxtrot | 安全专家 | 安全审计、漏洞扫描 | 测试 |
| Golf | 性能专家 | 性能优化、负载测试 | 测试 |
| Hotel | 文档专家 | 技术文档、用户手册 | 交付 |

### 🏗️ 完整瀑布模型 (6大阶段)
1. **需求阶段** (Product) - 需求收集、PRD编写、功能清单
2. **设计阶段** (Architect) - 架构设计、ER图、API文档
3. **开发阶段** (Orchestrator调度) - 并行开发、代码规范
4. **测试阶段** (Echo) - 单元测试、集成测试、Code Review
5. **部署阶段** (Kilo) - 部署上线、回滚方案、监控告警
6. **交付阶段** (Product) - 用户验收、使用文档、培训

### 📦 核心模块
1. ✅ **专业基础模块** - 日志/单例/缓存/验证/异常 (v4.1新增)
2. ✅ **工作流引擎** - 完整的瀑布模型项目管理
3. ✅ **文档生成器** - PRD/架构/ER图/API/用户手册自动生成
4. ✅ **部署管理器** - Docker/K8s部署、健康检查、回滚
5. ✅ **质量保障** - 测试管理、缺陷跟踪、Code Review、安全扫描
6. ✅ **任务管理** - DAG依赖管理、智能分配
7. ✅ **Agent调度** - 负载均衡、熔断机制
8. ✅ **审计日志** - 完整操作记录
9. ✅ **审批系统** - 人工审批流程
10. ✅ **配置中心** - 统一配置管理
11. ✅ **状态持久化** - Checkpoint机制

## 📁 完整文件结构

```
multi-agent-suite/
├── SKILL.md                      # 本文档
├── core/
│   ├── __init__.py               # 包初始化
│   ├── cli.py                    # 统一CLI入口
│   ├── professional_base.py       # 专业级基础模块 v4.1 ⭐
│   ├── orchestrator.py           # Agent调度器
│   ├── workflow.py               # 旧版工作流 (兼容)
│   ├── workflow_engine.py         # 瀑布模型引擎 v4.1 ⭐
│   ├── document_generator.py     # 文档生成器 v2.0
│   ├── deployment_manager.py     # 部署管理器 v2.0
│   ├── quality_assurance.py      # 质量保障模块 v2.0
│   ├── task_dag.py               # 任务依赖DAG
│   ├── task_estimator.py         # 任务预估器
│   ├── agent_communication.py    # Agent通信
│   ├── incremental_reviewer.py   # 增量代码审查
│   ├── config_center.py          # 配置中心
│   ├── approval_system.py        # 审批系统
│   ├── audit_logger.py          # 审计日志
│   └── enhancements.py           # 增强模块
├── agents/
│   ├── __init__.py
│   ├── config.json               # 12-Agent完整配置
│   ├── kilo_notification.py      # Kilo通知Agent
│   └── ...
├── web-ui/                       # Web管理界面
│   ├── app.py
│   └── templates/dashboard.html
└── scripts/                      # 工具脚本
    ├── git-integration.sh
    └── ci-cd.sh
```

## 🚀 快速使用

### 统一CLI (推荐)
```bash
# 查看帮助
python -m core.cli help

# 版本信息
python -m core.cli version

# ============ 项目管理 ============
python -m core.cli project create "智能投资平台" --template web_app
python -m core.cli project list
python -m core.cli project status proj-xxx
python -m core.cli project report proj-xxx

# ============ Agent管理 ============
python -m core.cli agent list
python -m core.cli agent stats

# ============ 文档生成 ============
python -m core.cli doc prd "项目名"
python -m core.cli doc architecture "项目名"
python -m core.cli doc api "项目名"
python -m core.cli doc er "项目名"
python -m core.cli doc manual "项目名"
python -m core.cli doc deploy "项目名"

# ============ 部署管理 ============
python -m core.cli deploy list
python -m core.cli deploy servers

# ============ 质量保障 ============
python -m core.cli qa summary
python -m core.cli qa scan /path/to/project

# ============ 旧版功能 (兼容) ============
python -m core.cli task create "项目"
python -m core.cli web
python -m core.cli status
```

## 📋 专业级特性 (v4.1)

### 1. 日志系统
- 多级别日志 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- 文件轮转 (10MB/文件, 保留5个)
- 结构化日志格式
- 按模块隔离

### 2. 单例模式
- 线程安全的单例元类
- 所有核心管理器单例化
- 避免重复初始化

### 3. 缓存机制
- LRU缓存 (可配置大小)
- 线程安全
- TTL过期支持
- 自动清理过期项

### 4. 验证体系
- BaseModel基类
- validate()方法
- 必填字段验证
- 类型验证

### 5. 异常处理
- 自定义异常层次
- ValidationError - 验证错误
- NotFoundError - 资源不存在
- StateError - 状态错误
- ConfigurationError - 配置错误

### 6. 重试机制
- 指数退避算法
- 可配置重试次数
- 装饰器方式使用

### 7. 指标收集
- MetricsCollector
- 记录性能指标
- 统计分析

### 8. 事件分发
- EventDispatcher
- 发布/订阅模式
- 解耦组件通信

## 📋 瀑布模型流程

```
用户需求
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. 需求阶段 (Product)                                      │
│    • 需求收集    • 需求分析    • PRD文档编写                │
│    • 功能清单    • 优先级排序  • 用户故事                  │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 设计阶段 (Architect)                                    │
│    • 系统架构设计（架构图）                                 │
│    • 模块划分    • 技术选型                                 │
│    • 数据库设计（ER图）                                    │
│    • 接口设计（API文档）                                   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 开发阶段 (Orchestrator 调度)                             │
│    ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                   │
│    │Alpha │ │Bravo │ │Charlie│ │Delta │                   │
│    │前端  │ │后端  │ │功能  │ │修复  │                   │
│    └──────┘ └──────┘ └──────┘ └──────┘                   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 测试阶段 (Echo + Foxtrot + Golf)                        │
│    • 单元测试    • 集成测试    • Code Review               │
│    • 安全审计    • 性能测试    • 缺陷报告                  │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. 部署阶段 (Kilo)                                         │
│    • 部署到服务器    • 回滚方案                            │
│    • 监控告警        • 部署报告                            │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. 交付阶段 (Product + Hotel)                               │
│    • 用户验收        • 使用文档                            │
│    • 培训            • 运维手册                            │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 适用场景

- ✅ 标准Web应用开发
- ✅ API服务开发
- ✅ 企业级大型项目
- ✅ AI驱动产品
- ✅ 大数据分析平台
- ✅ 复杂全栈系统

---

**v4.1 专业版 - 12-Agent + 完整瀑布模型 + 专业级基础设施！** 🎉

*更新日志 v4.1:*
- 新增 professional_base.py 专业级基础模块
- 线程安全单例模式
- 专业日志系统 (轮转/分级)
- LRU缓存机制
- 完整的验证体系
- 自定义异常层次
- 指数退避重试
- 指标收集器
- 事件分发器

*更新日志 v4.0:*
- 新增 12-Agent 完整团队 (Product + Architect)
- 新增 完整瀑布模型工作流引擎
- 新增 文档自动生成器
- 新增 部署管理器
- 新增 质量保障模块
