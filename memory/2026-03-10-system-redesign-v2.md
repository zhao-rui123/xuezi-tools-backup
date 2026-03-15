# 系统整体改造方案 v2.0 - 全面重构

## 问题清单（共8大类）

### 1. 记忆系统（核心）
- ❌ 实时保存刚修复，功能弱
- ❌ /new 后恢复不完整
- ❌ 错误学习有记录无触发
- ⚠️ 记忆搜索索引过时

### 2. 知识系统
- ⚠️ 知识提取机械，依赖人工
- ✅ 知识库有内容但更新慢

### 3. 进化系统
- ❌ 自我进化空洞无效

### 4. 技能包管理
- ⚠️ 57个技能包，可能冗余
- ❌ 很多无版本管理

### 5. 脚本管理
- ⚠️ 27个脚本，目录杂乱
- ❌ 无统一分类

### 6. 定时任务
- ⚠️ 20个任务，配置复杂
- ❌ 无统一监控

### 7. 日志管理
- ⚠️ 20个日志文件堆积
- ❌ 无自动清理

### 8. 备份系统
- ⚠️ 三重备份冗余
- ⚠️ 磁盘占用

---

## 新架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    核心服务层 (Core Services)               │
├─────────────────────────────────────────────────────────────┤
│  Memory Service          Knowledge Service    Action Service│
│  ───────────────         ────────────────     ─────────────│
│  • 实时保存               • 智能提取           • 任务生成   │
│  • 语义搜索               • 自动分类           • 进度跟踪   │
│  • 错误提醒               • 待确认机制         • 周报生成   │
│  • 上下文恢复             • 学习库触发         • 闭环反馈   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    支撑服务层 (Support Services)            │
├─────────────────────────────────────────────────────────────┤
│  Skill Service      Script Service    Monitor Service       │
│  ─────────────      ──────────────    ───────────────       │
│  • 版本管理          • 统一入口        • 任务看板           │
│  • 依赖检查          • 分类管理        • 日志聚合           │
│  • 自动审计          • 参数规范        • 告警通知           │
│  • 清理归档          • 文档生成        • 健康报告           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    基础设施层 (Infrastructure)              │
├─────────────────────────────────────────────────────────────┤
│  Backup Service      Git Service       Notify Service       │
│  ──────────────      ──────────        ─────────────        │
│  • 智能去重           • 语义提交        • 统一格式          │
│  • 增量备份           • 变更摘要        • 分级发送          │
│  • 自动清理           • 版本标签        • 批量合并          │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: 核心服务改造（今晚-明天）

### 1.1 Memory Service 重构

**文件结构：**
```
services/memory/
├── memory_service.py          # 主服务
├── real_time_saver.py         # 实时保存
├── context_recovery.py        # 上下文恢复
├── semantic_search.py         # 语义搜索
├── error_reminder.py          # 错误提醒
└── index/
    ├── semantic_index.json    # 语义索引
    ├── conversation_cache/    # 对话缓存
    └── summaries/             # 摘要文件
```

**核心功能：**

1. **实时保存（每10分钟）**
```python
class RealTimeSaver:
    def save(self):
        # 保存完整会话状态
        # 保存最后50轮对话
        # 生成语义摘要
        # 更新语义索引
```

2. **上下文恢复（on_session_start）**
```python
class ContextRecovery:
    def recover(self):
        # 1. 加载会话状态
        # 2. 读取相关学习项（场景匹配）
        # 3. 生成详细恢复提示：
        #    "你最后在做：系统改造方案
        #     已完成：实时记忆增强设计
        #     未解决：语义搜索如何实现
        #     ⚠️ 提醒：根据 error-001，不要主动搜索"
```

3. **语义搜索**
```python
class SemanticSearch:
    def search(self, query):
        # 1. 提取查询语义
        # 2. 匹配语义索引
        # 3. 返回相关记忆摘要（节省token）
        # 4. 按时间+相关度排序
```

4. **错误提醒**
```python
class ErrorReminder:
    def check(self, context):
        # 1. 分析当前场景
        # 2. 匹配 learnings/ 中的触发条件
        # 3. 如果匹配，返回提醒
```

### 1.2 Knowledge Service 重构

**文件结构：**
```
services/knowledge/
├── knowledge_service.py       # 主服务
├── smart_extractor.py         # 智能提取
├── draft_manager.py           # 草稿管理
└── learnings/
    ├── index.json             # 学习项索引+触发条件
    ├── error-001.md
    ├── workflow-001.md
    └── habit-001.md
```

**核心功能：**

1. **智能提取（每日01:00）**
```python
class SmartExtractor:
    def extract(self, memory_file):
        # 1. 读取昨日记忆
        # 2. AI分析识别：决策/问题/项目/学习
        # 3. 生成知识库草稿到 pending/
        # 4. 生成学习项到 learnings/
        # 5. 发送飞书："发现3个新知识项，请确认"
```

2. **草稿管理**
```python
class DraftManager:
    def confirm(self, draft_id):
        # 用户确认后，移动到正式目录
    def reject(self, draft_id):
        # 用户拒绝，删除或归档
```

### 1.3 Action Service 重构

**文件结构：**
```
services/action/
├── action_service.py          # 主服务
├── task_generator.py          # 任务生成
├── progress_tracker.py        # 进度跟踪
└── weekly_reporter.py         # 周报生成
```

**核心功能：**

1. **任务生成（每周日）**
```python
class TaskGenerator:
    def generate(self):
        # 1. 扫描知识库
        # 2. 识别：未完成决策/待解决问题/需更新项目
        # 3. 生成可执行任务列表
        # 4. 发送到飞书
```

2. **进度跟踪**
```python
class ProgressTracker:
    def track(self, task_id):
        # 跟踪任务完成情况
        # 更新任务状态
```

3. **周报生成**
```python
class WeeklyReporter:
    def report(self):
        # 1. 统计本周完成
        # 2. 列出下周任务
        # 3. 生成周报发送飞书
```

---

## Phase 2: 支撑服务改造（后天-周末）

### 2.1 Skill Service 技能包管理

**文件结构：**
```
services/skill/
├── skill_service.py           # 主服务
├── version_manager.py         # 版本管理
├── dependency_checker.py      # 依赖检查
└── audit_report.py            # 审计报告
```

**核心功能：**

1. **版本管理**
```python
class VersionManager:
    def bump_version(self, skill_name):
        # 自动更新版本号
        # 生成 changelog
    def check_update(self):
        # 检查技能包更新
```

2. **依赖检查**
```python
class DependencyChecker:
    def check(self):
        # 检查技能包依赖关系
        # 检测循环依赖
```

3. **自动审计（每月）**
```python
class SkillAuditor:
    def audit(self):
        # 1. 扫描所有技能包
        # 2. 检查：SKILL.md/版本/依赖/使用情况
        # 3. 生成审计报告
        # 4. 标记：活跃/闲置/废弃
```

### 2.2 Script Service 脚本管理

**文件结构：**
```
services/script/
├── script_service.py          # 主服务
├── unified_cli.py             # 统一入口
└── docs/
    └── api_reference.md       # API文档
```

**核心功能：**

1. **统一入口**
```bash
# 所有脚本统一入口
oc-cli memory save          # 保存记忆
oc-cli knowledge extract    # 提取知识
oc-cli action generate      # 生成任务
oc-cli skill audit          # 审计技能包
oc-cli backup run           # 执行备份
oc-cli status               # 系统状态
```

2. **分类管理**
```
scripts/
├── core/                     # 核心脚本（必须）
├── maintenance/              # 维护脚本
├── backup/                   # 备份脚本
└── deprecated/               # 废弃脚本
```

### 2.3 Monitor Service 监控服务

**文件结构：**
```
services/monitor/
├── monitor_service.py         # 主服务
├── task_dashboard.py          # 任务看板
├── log_aggregator.py          # 日志聚合
└── health_reporter.py         # 健康报告
```

**核心功能：**

1. **任务看板**
```python
class TaskDashboard:
    def show(self):
        # Web界面或飞书消息
        # 显示所有定时任务状态
        # 最近执行时间/结果
```

2. **日志聚合**
```python
class LogAggregator:
    def aggregate(self):
        # 收集所有日志
        # 按服务分类
        # 生成聚合报告
```

3. **健康报告（每日09:00）**
```python
class HealthReporter:
    def report(self):
        # 1. 检查所有服务状态
        # 2. 检查磁盘/内存
        # 3. 检查定时任务执行
        # 4. 生成健康报告
```

---

## Phase 3: 基础设施改造（下周）

### 3.1 Backup Service 备份服务

**核心功能：**

1. **智能去重**
```python
class DeduplicationBackup:
    def backup(self):
        # 1. 计算文件指纹
        # 2. 只备份变更文件
        # 3. 节省磁盘空间
```

2. **增量备份**
```python
class IncrementalBackup:
    def backup(self):
        # 只备份变更部分
        # 保留完整备份链
```

3. **自动清理**
```python
class BackupCleaner:
    def clean(self):
        # 保留：每日最近7天 + 每周最近4周 + 每月最近12月
        # 删除过期备份
```

### 3.2 Git Service 提交服务

**核心功能：**

1. **语义提交**
```python
class SemanticCommit:
    def commit(self):
        # 1. 分析变更内容
        # 2. 生成语义化提交信息
        # 例如："feat(memory): 添加实时保存功能"
```

2. **变更摘要**
```python
class ChangeSummary:
    def summarize(self):
        # 生成变更摘要
        # 包含：改了什么/为什么/影响范围
```

### 3.3 Notify Service 通知服务

**核心功能：**

1. **统一格式**
```python
class UnifiedNotifier:
    def send(self, level, message):
        # 统一通知格式
        # 分级：info/warning/error
        # 批量合并短时间内的通知
```

2. **分级发送**
```python
class PriorityNotifier:
    def send(self, priority):
        # 根据优先级选择发送方式
        # urgent: 立即发送
        # normal: 批量发送
        # low: 日报汇总
```

---

## 实施计划

### Week 1: 核心服务
- [ ] Day 1: Memory Service 重构
- [ ] Day 2: Knowledge Service 重构
- [ ] Day 3: Action Service 重构
- [ ] Day 4-5: 联调测试

### Week 2: 支撑服务
- [ ] Day 1-2: Skill Service
- [ ] Day 3-4: Script Service
- [ ] Day 5: Monitor Service

### Week 3: 基础设施
- [ ] Day 1-2: Backup Service
- [ ] Day 3-4: Git Service
- [ ] Day 5: Notify Service

### Week 4: 整合优化
- [ ] 全系统联调
- [ ] 性能优化
- [ ] 文档更新

---

## 预期效果

| 维度 | 改造前 | 改造后 |
|------|--------|--------|
| 记忆恢复 | ❌ 只有任务名 | ✅ 完整上下文+学习提醒 |
| 知识提取 | ⚠️ 机械复制 | ✅ AI分析+人工确认 |
| 任务闭环 | ❌ 空洞输出 | ✅ 可执行任务+跟踪 |
| 技能管理 | ⚠️ 57个无版本 | ✅ 自动审计+版本管理 |
| 脚本管理 | ⚠️ 27个杂乱 | ✅ 统一入口+分类 |
| 定时任务 | ⚠️ 20个复杂 | ✅ 看板监控+告警 |
| 日志管理 | ⚠️ 20个堆积 | ✅ 聚合+自动清理 |
| 备份管理 | ⚠️ 三重冗余 | ✅ 智能去重+增量 |
| Git提交 | ⚠️ 无意义信息 | ✅ 语义化提交 |
| 通知管理 | ⚠️ 碎片化 | ✅ 统一格式+分级 |

---

## 风险评估

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| 改造期间服务中断 | 中 | 高 | 分阶段实施，保留旧系统 |
| 数据迁移失败 | 低 | 高 | 完整备份，回滚方案 |
| 性能下降 | 低 | 中 | 监控指标，及时优化 |
| 学习成本 | 中 | 低 | 文档+培训 |

---

**建议：今晚开始 Phase 1.1（Memory Service），这是基础。**
