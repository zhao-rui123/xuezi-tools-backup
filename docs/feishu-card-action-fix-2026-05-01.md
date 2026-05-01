# Feishu 交互卡片修复记录（2026-05-01）

## 背景
工作台卡片按钮点击后，飞书侧有回调，但 OpenClaw gateway 日志持续报：
- `feishu[default]: ignoring malformed card action payload`

## 排查结论
不是按钮能力没开；`openclaw.json` 中已启用：
- `channels.feishu.capabilities.inlineButtons = "dm"`

真正根因是：
- OpenClaw 当前版本 Feishu 插件 `parseFeishuCardActionEventPayload()` 未兼容新版 card action 回调结构。
- 新版回调里 `context` 使用：
  - `open_chat_id`
  - `open_message_id`
- 旧解析逻辑强依赖：
  - `context.chat_id`
  - `context.open_id`
  - `context.user_id`

## 真实运行文件
实际运行中的 monitor 文件是：
- `/opt/homebrew/lib/node_modules/openclaw/dist/monitor-Bkbv5nYZ.js`

不是：
- `monitor-BDByGBM-.js`

## 最小兼容补丁
补丁位置：
- `function parseFeishuCardActionEventPayload(value)`

补丁思路：
- `context.open_id` 缺失时，回退到 `operator.open_id`
- `context.user_id` 缺失时，回退到 `operator.user_id`
- `context.chat_id` 缺失时，回退到 `context.open_chat_id`
- 保留 `open_message_id` 作为上下文字段

## 关键验证
已验证 structured quick action 能成功触发 `/help`：
- 卡片按钮 `value` 使用 structured object：
  - `oc: "ocf1"`
  - `k: "quick"`
  - `a: "feishu.quick_actions.help"`
  - `q: "/help"`
  - `c: { u, e, t }`
- 用户点击后，实际返回了帮助信息，证明 synthetic command 链路已打通。

## 备份文件
- `/opt/homebrew/lib/node_modules/openclaw/dist/monitor-Bkbv5nYZ.js.bak-20260501-1052`
- `/opt/homebrew/lib/node_modules/openclaw/dist/monitor-BDByGBM-.js.bak-20260501-1040`（误改备份，可忽略）

## 风险提示
- 这是对 dist 运行文件的热修，OpenClaw 升级后可能被覆盖。
- 升级后如交互卡片再次失效，应优先对照本文件重新检查 `parseFeishuCardActionEventPayload()` 是否已原生兼容 `open_chat_id`。

## 后续建议
1. 将补丁提交到 OpenClaw 正式源码（若后续要长期维护）
2. 工作台卡片按钮统一改成 structured quick action
3. 升级后做一次 `/help` 探针按钮回归测试
