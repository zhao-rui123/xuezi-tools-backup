# 飞书文件发送指南

## 核心规则

### ✅ 正确做法
1. **文件路径**: 必须放在 `~/.openclaw/workspace/` 目录
2. **目标参数**: 必须使用 `target` 参数指定接收者
3. **文件大小**: 确保文件存在且不为空

### ❌ 错误做法
1. **绝对路径**: 不要使用 `/tmp/` 目录
2. **遗漏参数**: 不要忘记 `target` 参数

## 正确示例

```python
message({
    "action": "send",
    "target": "ou_5a7b7ec0339ffe0c1d5bb6c5bc162579",
    "caption": "文件说明",
    "media": "/Users/zhaoruicn/.openclaw/workspace/filename.ext"
})
```


## 检查清单


发送文件前务必检查：
- [ ] 文件在 workspace 目录
- [ ] 使用了 target 参数
- [ ] 文件大小正常

---
*记录时间: 2026-03-13*
