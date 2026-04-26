# Agent Reference

低频说明、长教程、工具参考统一放这里，避免主规则文件继续膨胀。

## OMC / 多Agent 参考

### 常见模式
- `autopilot:`：从想法到代码的全流程执行
- `ralph:`：持续循环直到完成
- `ulw:` / `ultrawork:`：最大并行化
- `deep-interview:`：需求不清时先深度澄清
- `team N:`：多Agent协作

### 常见场景
- 小功能快速开发 → `autopilot:`
- 复杂系统设计 → `team N:architect`
- 修复多个 bug → `ulw:`
- 需求不清晰 → `deep-interview:`

### 典型命令示例
```bash
omc team 3:claude "修复bug"
omc team 2:codex:architect "设计系统"
omc ralphthon "构建REST API"
omc autoresearch --topic "AI趋势"
```

## 图片识别参考

**默认优先链路**：`mmx vision describe`（直接调用，最轻最快）

```bash
mmx vision describe <图片路径>
```

适用：
- 股票K线
- 数据报表
- 复杂截图
- 需要上下文理解的图像问题

如 `mmx` 不可用或失败，可退回 Claude Code + MiniMax MCP 链路。

## 排障参考

### 五步法
1. 找关键引用 + 断点定位
2. 并排对比新旧版本
3. 追踪调用链
4. 本地最小验证
5. 分层修复交付

### 常用命令
```bash
rg "问题关键词" ~/.openclaw -g '!.git'
rg "目标脚本名" ~/.openclaw/workspace/scripts/ -l
crontab -l
openclaw config validate
```

## 说明
- 高频硬规则留在 `AGENTS.md`
- 人格与边界留在 `SOUL.md`
- 身份与能力摘要留在 `IDENTITY.md`
- 这里仅收纳低频参考内容
