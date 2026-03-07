---
name: web-search
description: 联网搜索技能包 - 基于Tavily AI搜索引擎，无需翻墙，快速获取网页信息
metadata:
  openclaw:
    requires:
      bins: [python3]
      env: [TAVILY_API_KEY]
---

# Web Search - 联网搜索

## 功能概述

基于Tavily AI搜索引擎，专为AI助手设计的搜索API：
- ✅ 无需翻墙，国内可用
- ✅ AI自动总结搜索结果
- ✅ 返回结构化数据
- ✅ 比传统搜索引擎更适合AI使用

## 安装

```bash
# 1. 获取Tavily API Key
# 访问 https://tavily.com 注册获取免费API Key

# 2. 设置环境变量
export TAVILY_API_KEY=your_api_key_here

# 3. 添加到 ~/.zshrc 或 ~/.bash_profile
echo 'export TAVILY_API_KEY=your_api_key' >> ~/.zshrc
```

## 使用方法

### 快速搜索

```bash
cd ~/.openclaw/workspace/skills/web-search
python3 web_search.py "Python最新特性"
```

### Python调用

```python
from web_search import search, quick_search

# 搜索并获取AI总结
result = search("特斯拉股价", max_results=5)
print(result['answer'])  # AI总结

# 快速搜索
print(quick_search("OpenAI GPT-5"))
```

## 输出示例

```
======================================================================
🔍 搜索结果
======================================================================

📝 AI总结:
Python 3.12 引入了多项新特性，包括改进的错误消息、f-string优化、
类型注解增强等...

📄 相关网页 (5个结果):

1. Python 3.12 新特性官方文档
   URL: https://docs.python.org/3.12/whatsnew/3.12.html
   Python 3.12 是 Python 编程语言的最新主要版本...

2. Python 3.12: 你需要知道的10个新特性
   URL: https://realpython.com/python312-new-features/
   深入了解 Python 3.12 的改进...

======================================================================
```

## 与现有技能包对比

| 功能 | 新浪财经API | Tavily搜索 |
|------|------------|-----------|
| 股票数据 | ✅ 专业 | ❌ 无 |
| 通用搜索 | ❌ 无 | ✅ 专业 |
| AI总结 | ❌ 无 | ✅ 自动 |
| 国内访问 | ✅ 快 | ✅ 可用 |

## 注意事项

- 免费账户有调用限制（每月约1000次）
- 需要设置 TAVILY_API_KEY 环境变量
- 适合补充股票分析以外的通用搜索需求
