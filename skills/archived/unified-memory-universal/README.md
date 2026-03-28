# Unified Memory System - 通用版

> 统一记忆管理系统 - 可分享给朋友的完全脱敏版本

**版本**: 2.0.0-universal  
**类型**: 通用技能包（可配置）

---

## 系统概述

**统一记忆管理系统 (Unified Memory System)** 是一个全功能的记忆管理解决方案，帮助 AI 助手高效地管理、存储和检索与用户交互过程中的重要信息。

### 核心理念
- **一个命令**搞定所有记忆操作
- **自动识别**重要信息并存储
- **智能检索**优先显示重要内容
- **永久保存**工作历史不丢失

---

## 功能特性

### 1. 三层记忆架构
- **日常记忆层**: 每天自动生成记忆文件
- **智能分析层**: 每月分析提取关键词和主题
- **增强记忆层**: 自动识别重要信息，重要性分级

### 2. 双模式记忆存储
- **自动识别**: 对话中自动识别"我喜欢"、"我决定"等重要信息
- **主动指令**: 用户明确说"记住..."时存储

### 3. 智能检索系统
- 重要性分级（0-1评分）
- 时间衰减（老记忆自动降级）
- 混合匹配（关键词+类别）

### 4. 会话持久化
- 切换模型时保存工作状态
- 新模型启动后恢复上下文

### 5. 月度智能分析
- 每月自动分析记忆文件
- 生成月度摘要报告
- 更新关键词/主题索引

---

## 安装配置

### 1. 配置路径
编辑 `config.json` 文件：

```json
{
  "paths": {
    "workspace": "~/.your-ai/workspace",
    "memory_dir": "~/.your-ai/workspace/memory",
    "knowledge_base": "~/.your-ai/workspace/knowledge-base"
  }
}
```

### 2. 安装依赖
```bash
pip install numpy jieba
```

### 3. 添加到 PATH
```bash
export PATH="$PATH:~/.your-ai/workspace/skills/unified-memory/bin"
```

---

## 使用方法

### 统一命令: `ums`

```bash
# 查看系统状态
ums status

# 保存每日记忆
ums daily save "今天完成了..."

# 月度智能分析
ums analyze monthly

# 存储增强记忆（带重要性）
ums recall store "内容" --importance 0.9

# 搜索记忆
ums recall search "关键词" --top 5

# 保存会话状态
ums session save

# 恢复会话状态
ums session restore
```

### 自动识别触发词

说这些话会自动存储：

| 句式 | 存储类别 | 示例 |
|------|---------|------|
| "我喜欢..." | preference | 我喜欢用 Python |
| "我决定..." | decision | 我决定使用 React |
| "我叫..." | identity | 我叫 xxx |
| "千万不要..." | constraint | 千万不要删除 |
| "我计划..." | schedule | 我计划明天开会 |

---

## 系统架构

```
统一记忆系统
│
├── 核心模块
│   ├── daily.py          # 每日记忆管理
│   ├── analyzer.py       # 月度智能分析
│   ├── recall.py         # 增强记忆检索
│   ├── session.py        # 会话持久化
│   └── smart_memory.py   # 智能识别引擎
│
├── 数据存储
│   ├── memory/           # 每日记忆文件
│   ├── memory/summary/   # 月度摘要
│   ├── memory/index/     # 关键词/主题索引
│   └── .memory/enhanced/ # 增强记忆数据
│
└── 接口层
    ├── ums (CLI)         # 命令行工具
    └── API (Python)      # Python API
```

---

## 评分算法

```
最终得分 = 匹配度 × 时间衰减 × 重要性加权

时间衰减 = 0.5 + 0.5 × exp(-年龄天数 / 60)
重要性加权 = 0.7 + 0.3 × 重要度(0-1)
```

---

## 定时任务配置

```bash
# 月度智能分析（每月1日 02:00）
0 2 1 * * ums analyze monthly

# 每日备份（可选）
0 22 * * * cp -r ~/.your-ai/workspace/memory ~/backups/
```

---

## 使用示例

### 示例 1：自动识别
```
用户：我喜欢用 Python 做数据分析
→ 系统自动识别，存储为 preference，重要度 0.7
```

### 示例 2：主动存储
```
用户：记住我的邮箱是 xxx@example.com
→ 立即存储，重要度 0.85
```

### 示例 3：智能检索
```bash
$ ums recall search "编程"
🔍 找到 3 条相关记忆:
  1. [preference] 用 Python 编程 (重要度: 0.8, 得分: 0.95)
  2. [decision] 使用 React 编程 (重要度: 0.7, 得分: 0.82)
  3. [project] 编程项目规划 (重要度: 0.6, 得分: 0.71)
```

---

## 系统优势

| 优势 | 说明 |
|------|------|
| **一体化** | 1个命令替代多个工具 |
| **Token节省** | 98% 节省（智能检索替代全文搜索） |
| **智能化** | 自动识别重要信息 |
| **可靠性** | 永久保存 + 自动备份 |
| **易用性** | 自然对话即可 |

---

## 文件结构

```
unified-memory/
├── README.md              # 本文档
├── skill.json             # 技能包配置
├── unified_memory.py      # 主程序
├── smart_memory.py        # 智能识别引擎
├── bin/
│   └── ums               # CLI入口
└── config.json           # 用户配置（需自行配置）
```

---

## 注意事项

1. **首次使用**: 必须配置 `config.json` 中的路径
2. **权限**: 确保对配置的目录有读写权限
3. **备份**: 建议定期备份 memory/ 目录
4. **依赖**: 需要安装 numpy 和 jieba

---

## 许可

MIT License - 可自由使用、修改、分享

---

*通用版 v2.0.0 - 完全脱敏，可安全分享*
