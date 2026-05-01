# 工作台系统阶段性收口总结（2026-05-01）

## 一、本轮目标
围绕 OpenClaw 日常使用，逐步落地一套：
- 记忆提炼
- 候选状态管理
- 任务中心
- markdown 工作台
- Feishu 工作台卡片

目标不是一次做完完美系统，而是先形成 **可用闭环**。

---

## 二、已完成能力

### 1. 统一任务中心
脚本：`scripts/task_center.py`

已支持：
- 新增任务
- 列表查看
- 今日关注任务
- doing / blocked / done / reopen / archive
- 从候选层导入 `todo / blocked / progress / risk`
- 去重导入
- digest 整理视图
- 来源筛选（origin_type / tag 等）

数据文件：
- `projects/task-center/tasks.json`

---

### 2. 自动记忆提炼器（候选层）
脚本：`scripts/memory_candidate_extractor.py`

已支持提炼类型：
- `decision`
- `todo`
- `rule`
- `progress`
- `risk`
- `blocked`

输出目录：
- `memory/auto-candidates/`

当前策略：
- 先写候选层
- 不直接污染 `MEMORY.md`
- 做基础去重

---

### 3. 候选状态管理
脚本：`scripts/candidate_state_manager.py`

已支持状态：
- `new`
- `imported`
- `ignored`

已支持能力：
- list
- inbox
- stats
- cleanup-preview
- mark-imported
- mark-ignored
- mark-batch-ignored

核心原则：
- 不删除原始候选
- 只通过 state 管理生命周期

---

### 4. 自动化入口
脚本：`scripts/memory_task_flow.py`

已实现一步式链路：
1. 提炼候选
2. 保存候选
3. 导入任务中心
4. 输出 digest

---

### 5. Markdown 工作台摘要
脚本：`scripts/workspace_dashboard_md.py`

输出：
- `summary/dashboards/YYYY-MM-DD-dashboard.md`

内容包括：
- 候选状态统计
- 候选类型分布
- 待处理 inbox
- 当前阻塞
- 当前进行中
- 高优先级待办
- 今日自动导入任务

---

### 6. Feishu 工作台卡片
脚本：`scripts/workspace_dashboard_card.py`

当前正式形态：
- **主卡片：真 Feishu 卡片**
- **按钮：真交互按钮**
- **子结果：格式化文本回复**

这就是当前定版形态。

---

## 三、Feishu 交互卡片专项成果

### 已确认打通
- 主卡片发送 ✅
- 按钮点击回调 ✅
- structured quick action ✅
- synthetic command 执行 ✅
- `/help / digest / inbox / high / blocked` 等按钮命令可用 ✅

### 当前定版
- 主卡片是卡片
- 子结果是格式化文本
- 不强求二级子卡片渲染

### 原因
虽然已经尝试进一步把 `* card` 命令改成子卡片回复，但在当前 OpenClaw 运行时路径中，仍未完全收成稳定“二级真卡片”。

综合稳定性与收益，当前决定：
> **以“主卡片 + 格式化文本子结果”作为正式可用版收口。**

这不是缺陷，而是当前阶段的务实定版。

---

## 四、关键热修（非常重要）

### 修复点
为了让 Feishu 按钮交互真正生效，已对 OpenClaw 当前运行 dist 文件做最小兼容补丁：

真实运行文件：
- `/opt/homebrew/lib/node_modules/openclaw/dist/monitor-Bkbv5nYZ.js`

修复内容：
- 兼容新版 Feishu card action 回调结构中的：
  - `context.open_chat_id`
  - `context.open_message_id`
- 并用 `operator.open_id / user_id` 回填旧逻辑依赖的 context 字段

### 相关文档
- `docs/feishu-card-action-fix-2026-05-01.md`
- `docs/feishu-hotfix-recovery.md`
- `docs/feishu-card-workbench-fixed.md`

### 备份文件
- `/opt/homebrew/lib/node_modules/openclaw/dist/monitor-Bkbv5nYZ.js.bak-20260501-1052`

### 风险提醒
这是 **dist 热修**，OpenClaw 升级后可能被覆盖。

升级后如按钮再次失效：
1. 优先验证 `/help` 探针按钮
2. 若 снова报 `ignoring malformed card action payload`
3. 对照上述文档重新检查 `parseFeishuCardActionEventPayload()` 兼容层

---

## 五、当前正式定版（推荐记法）

### 工作台系统 V1 正式版
- 记忆提炼：已落地
- 候选状态：已落地
- 任务中心：已落地
- markdown 工作台：已落地
- Feishu 主卡片：已落地
- Feishu 按钮交互：已打通
- 子结果：格式化文本（正式定版）

---

## 六、后续可选增强（非必须）
1. 真正的二级子卡片回复
2. 候选处理按钮（导入/忽略）
3. 原卡片就地刷新而不是文本回复
4. 将 hotfix 提交到 OpenClaw 正式源码层，避免升级丢失

---

## 七、结论
这轮工作已经从“想法”变成了“可用系统”：

> **OpenClaw 工作台已经具备日常使用价值，可以正式投入使用。**

当前最重要的不是继续追求炫技，而是：
- 保持稳定
- 留好补丁说明
- 以后按需渐进增强
