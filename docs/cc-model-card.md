# Claude Code 模型切换卡片

## 目标
通过 Feishu 交互卡片切换本地 Claude Code 模型环境。

## 脚本
- `scripts/cc_model_card.py`
- 底层切换脚本：`scripts/cc-model-switch.sh`

## 按钮
- 切 Feinian
- 切 DeepSeek
- 切 MiniMax
- 查看当前

## 说明
卡片按钮将发送 quick action 命令：
- `cc model feinian`
- `cc model deepseek`
- `cc model minimax`
- `cc model status`

后续需在 Feishu quick action 分支中识别这些命令并执行本地脚本。
