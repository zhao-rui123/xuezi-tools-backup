# Memory and Operations Reference

这份文档收纳记忆流程、启动顺序、任务分流等操作参考，避免主规则文件继续膨胀。

## 启动顺序

1. Read `SOUL.md`
2. Read `USER.md`
3. `session-snapshot.py load`
4. 读取当天 `memory/YYYY-MM-DD.md`
5. 读取最近 sessions 历史
6. Read `MEMORY.md`
7. 报告恢复状态：上次做到什么、还剩什么、是否继续

## 记忆管理

### 三层架构
1. `memory/*.md` → 每日自动记录（source of truth）
2. `archive_summary.md` → 历史精华提炼
3. `claude.sqlite FTS` → 本地全文索引

### 写入时机
- 重要决策 → 更新 `MEMORY.md`
- 每日结束 → 归档到 `memory/`
- 对话超过30分钟 → 执行 session 压缩

### 每月整理
1. 读取过去30天每日 md
2. 提取精华更新到 `archive_summary.md`
3. 格式：项目 ~ 时间 ~ 具体内容
4. 归档已被合并的旧 md
5. `openclaw memory index --force`

## 任务节奏参考

### 汇报节点
- 任务启动：开始做什么、预计先查什么
- 关键里程碑：遇到问题或重大进展时同步
- 任务完成：改了什么、怎么验证、还有什么风险

### 任务大小判定
- 小型：单文件、简单功能、已知方案
- 中型：多模块、需调研
- 大型/复杂：架构设计、系统重构、多系统联动

### 任务分流
- 小型任务：前台快速处理，必要时再切 `screen`
- 中型任务：先前台收集证据，耗时步骤再放后台
- 复杂任务：Codex / OMC 规划执行，按阶段决定前后台

### 开发流程（简化）
1. 判断任务规模和证据需求
2. 前台拿证据 / 后台跑长任务
3. 验收结果，部署上线
4. 向用户汇报
