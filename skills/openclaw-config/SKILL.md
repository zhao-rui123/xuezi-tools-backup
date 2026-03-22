# OpenClaw Config - 模型切换技能包

## 描述

智能识别用户切换大语言模型的意图，自动将对话切换到指定的模型 provider，支持 MiniMax M2.5、Kimi Coding、Kimi K2.5、通义千问等多种模型的无缝切换。

## 功能

- **意图检测**: 识别"切换到"、"切到"、"用"、"使用"、"改成"等多种切换表述
- **模型别名映射**: 支持直接输入模型名称或别名（如 `m25`、`k2p5`、`coding`）
- **多模型支持**:
  - MiniMax M2.5 (`m25`) - 支持推理，有思考过程
  - Kimi for Coding (`k2p5`) - 适合编程，支持长上下文
  - Kimi K2.5 (`kimi-k2.5`) - 通用模型，支持图片
  - 通义千问3.5 Plus (`qwen3.5-plus`) - 阿里模型，长上下文
- **模型信息查询**: 获取模型名称、provider、描述等详细信息

## 使用方法

```python
from model_switcher import ModelSwitcher

# 检测切换意图
message = "切换到 k2p5"
model = ModelSwitcher.detect_switch_intent(message)
# 返回: 'k2p5'

# 直接输入模型名
model = ModelSwitcher.detect_switch_intent("m25")
# 返回: 'm25'

# 获取模型信息
info = ModelSwitcher.get_model_info('k2p5')
# 返回: {'name': 'Kimi for Coding', 'provider': 'kimi-coding', 'desc': '适合编程，支持长上下文'}
```

支持的切换语句模式：
- `切换到 m25` / `切到 coding` / `换到 k2p5`
- `用 minimax` / `使用通义千问`
- `改成 kimi` / `模型 qwen`

## 依赖

- Python 3.x
- 无外部依赖，纯 Python 实现
