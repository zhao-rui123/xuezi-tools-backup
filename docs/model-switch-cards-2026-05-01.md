# 模型切换卡片记录（2026-05-01）

## 结论
已在 Feishu 中打通两类模型切换卡片：

1. `🎛️ Claude Code 模型切换`
   - 用于切本地 Claude Code 环境
   - 通过本地脚本执行：`scripts/cc-model-switch.sh`

2. `🧠 OpenClaw 会话模型切换`
   - 用于切当前飞书会话模型
   - 通过 quick action 直接触发：
     - `/model feinian`
     - `/model deepseek`
     - `/model minimax`
     - `/model gpt-5.4`
     - `/model 5.4mini`
     - `/status`

## 用户约定
以后当雪子说：
- “切 OpenClaw 模型”
- “切这个会话的模型”
- “给我选 OpenClaw 模型”

默认动作：
**优先发送 `🧠 OpenClaw 会话模型切换` 卡片，让雪子自己点选。**

而不是直接替雪子切换。

## 相关文件
- `scripts/cc_model_card.py`
- `docs/cc-model-card.md`
- `summary/cards/cc-model-card.json`
- `scripts/openclaw_model_card.py`
- `docs/openclaw-model-card.md`
- `summary/cards/openclaw-model-card.json`

## 实测结果
已实测成功：
- Claude Code 模型切换卡
- OpenClaw 会话模型切换卡
- GPT-5.4 按钮补齐后可正常切换到 `feinian/gpt-5.4`
