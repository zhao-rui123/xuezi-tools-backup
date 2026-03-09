# 统一记忆系统 - 快速参考

## 一键命令

```bash
# 查看状态
ums status

# 测试自动识别
python3 ~/.openclaw/workspace/skills/unified-memory/smart_memory.py test
```

## 自动识别关键词

说这些话会自动存储：

| 句式 | 存储类别 | 示例 |
|------|---------|------|
| "我喜欢..." | preference | 我喜欢用 Python |
| "我决定..." | decision | 我决定用 React |
| "我叫..." | identity | 我叫雪子 |
| "我的股票..." | finance | 我的股票代码是... |
| "千万不要..." | constraint | 千万不要上传... |
| "计划..." | schedule | 我计划明天... |

## 主动存储

```bash
# 方式1: 直接说
记住我的邮箱是 xxx@qq.com

# 方式2: 命令行
ums recall store "内容" --importance 0.9
```

## 搜索记忆

```bash
ums recall search "关键词" --top 5
```

## 文件位置

- 代码: `~/.openclaw/workspace/skills/unified-memory/`
- 数据: `~/.openclaw/workspace/memory/`
- 增强记忆: `~/.openclaw/workspace/.memory/enhanced/`

## 定时任务

每月1日 02:00 自动执行月度分析

---
*unified-memory v2.0*
