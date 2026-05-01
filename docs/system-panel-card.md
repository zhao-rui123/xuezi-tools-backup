# 系统面板卡片 V1

## 目标
把主控制台里的系统相关能力拆成专题面板，避免首页塞太多细节。

## 脚本
- `scripts/system_panel_card.py`

## 输出
- `summary/cards/system-panel-card.json`

## 当前内容
- Gateway 状态
- Feishu 通道状态
- 任务系统状态
- Tailscale 状态
- 云服务器 SSH / V2Ray 状态
- 备份时间摘要
- 风险提示

## 按钮
- 系统面板（从主控制台进入）
- 全面检查
- 备份状态
- 会话状态
- 返回主控台

## 设计原则
1. 首页只显示摘要，系统细节下钻到这里
2. 优先复用 `healthcheck_openclaw.py --json`
3. 先做稳定可读，再考虑更多交互按钮
