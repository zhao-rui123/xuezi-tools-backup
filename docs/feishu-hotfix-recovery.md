# OpenClaw Feishu 热修恢复说明

## 本次热修目标
修复 Feishu 交互卡片 action 回调在当前 OpenClaw 版本中的解析兼容问题。

## 实际修改文件
- `/opt/homebrew/lib/node_modules/openclaw/dist/monitor-Bkbv5nYZ.js`

## 修改点
在 `parseFeishuCardActionEventPayload(value)` 中兼容：
- `context.open_chat_id -> context.chat_id`
- `context.open_id/user_id` 缺失时回退到 `operator.open_id/user_id`
- 保留 `open_message_id`

## 备份文件
- `/opt/homebrew/lib/node_modules/openclaw/dist/monitor-Bkbv5nYZ.js.bak-20260501-1052`

## 升级/丢失后恢复建议
1. 升级 OpenClaw 后先验证交互卡片 `/help` 探针按钮
2. 若 снова报 `ignoring malformed card action payload`：
   - 重新定位真实运行的 monitor chunk
   - 对照 `docs/feishu-card-action-fix-2026-05-01.md` 重新补 parse 兼容
3. 不建议直接恢复旧 hash 文件覆盖新版本，优先按新版本实际文件重新打最小补丁

## 验证标准
- 按钮点击后不再出现 malformed
- 能看到 structured action 被解析
- `/help` / `digest` / `inbox` / `high` 可正常返回结果
