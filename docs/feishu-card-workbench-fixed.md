# Feishu 工作台交互卡片固化说明

## 已固定内容
1. Feishu card action parse 兼容补丁已打入真实运行文件：
   - `/opt/homebrew/lib/node_modules/openclaw/dist/monitor-Bkbv5nYZ.js`
2. structured quick action 已验证可用（`/help` 按钮成功触发）
3. 工作台卡片生成器已升级为 V2 真交互版：
   - `scripts/workspace_dashboard_card.py`

## 工作台按钮协议
所有按钮统一使用 structured quick action object：
- `oc: "ocf1"`
- `k: "quick"`
- `a: "feishu.quick_actions.*"`
- `q: "命令"`
- `c: { u, e, t }`

## 当前按钮映射
- 查看 Inbox → `inbox`
- 查看阻塞 → `blocked`
- 查看高优先级 → `high`
- 查看摘要 → `digest`

## 注意
- 这是热修 + 固化方案，OpenClaw 升级后需要重新检查真实运行文件是否被覆盖。
- 如需长期稳定，建议后续把补丁提交到正式源码层。
