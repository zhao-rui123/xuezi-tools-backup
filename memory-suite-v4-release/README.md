# Memory Suite v4.0 - 智能记忆管理系统

## 简介
Memory Suite 是一个开源的智能记忆管理系统，帮助 AI 助手实现长期记忆、自我进化和知识管理。

## 核心功能
- 🧠 实时记忆保存（每10分钟自动保存）
- 📦 智能归档系统（7/30/90/365天多层归档）
- 🔍 语义索引与搜索
- 📊 自我进化分析
- 📚 知识图谱管理
- ⏰ 定时任务调度

## 安装
```bash
pip install -r requirements.txt
python3 cli.py --help
```

## 使用
```bash
# 启动调度器
python3 scheduler.py

# 手动保存
python3 cli.py save

# 查看状态
python3 cli.py status
```

## 配置
编辑 `config/config.json` 进行自定义配置。

## 开源协议
MIT License
