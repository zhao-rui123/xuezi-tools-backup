# 总驾驶台互动卡片 V1

## 目标
做一张统一首页卡片，把已做好的：
- OpenClaw 会话模型切换
- Claude Code 模型切换
- 工作台/任务跟踪
- 全面检查/健康检查

收进同一个入口里。

## 脚本
- `scripts/cockpit_card.py`

## 输出
- `summary/cards/cockpit-card.json`

## 当前按钮布局

### 🧠 模型区
- OpenClaw 模型 → `openclaw model card`
- Claude Code 模型 → `cc model card`
- 会话 Status → `/status`

### 📋 任务区
- 工作台总览 → `workspace card`
- Inbox → `inbox card`
- Blocked → `blocked card`
- High → `high card`
- Digest → `digest card`

### 🩺 系统区
- 全面检查 → `healthcheck summary`
- 备份状态 → `backup status`
- 帮助 → `/help`

## 设计原则
1. 总卡片只做导航，不把所有细节塞爆
2. 已有成熟卡片优先复用，不重复造轮子
3. 健康检查在总卡片中只显示摘要，详细结果通过按钮获取
4. 先做稳定入口，再逐步补二级交互

## 备注
- 当前 `openclaw model card` / `cc model card` / `workspace card` / `healthcheck summary` 需要在 quick action 分支中识别并返回对应内容。
- 如果后续要做“原卡片就地刷新”，再单独升级，不影响 V1 使用。
