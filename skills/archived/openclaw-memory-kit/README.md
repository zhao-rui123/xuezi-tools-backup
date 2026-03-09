# OpenClaw Memory Kit - 完整记忆解决方案

一套完整的 OpenClaw 记忆增强工具，包含**会话快照保存** + **智能记忆检索** + **自动恢复检测**。

## 📦 包含组件

```
openclaw-memory-kit/
├── enhanced-memory/          # 增强记忆技能包
│   ├── __init__.py           # 核心：混合检索记忆系统
│   ├── __main__.py           # CLI 管理工具
│   ├── session_distiller.py  # 从快照提取记忆
│   ├── SKILL.md              # 技能文档
│   └── README.md             # 快速指南
└── scripts/
    ├── session-snapshot.py   # 会话快照保存器
    └── recovery-detector.py  # 会话恢复检测器
```

## 🚀 快速安装

### 1. 解压到 workspace

```bash
cd ~/.openclaw/workspace
tar -xzvf openclaw-memory-kit.tar.gz

# 移动脚本到 scripts 目录（如果不存在）
mkdir -p scripts
mv openclaw-memory-kit/scripts/* scripts/
mv openclaw-memory-kit/enhanced-memory skills/
rm -rf openclaw-memory-kit
```

### 2. 安装依赖（可选）

```bash
pip install numpy jieba
```

## 🎯 三大核心功能

### 1️⃣ 会话快照保存（session-snapshot.py）

**作用**：每次重要操作后自动保存当前会话状态

**使用**：
```bash
# 保存当前会话
python3 ~/.openclaw/workspace/scripts/session-snapshot.py save --task "当前任务描述"

# 加载上次会话
python3 ~/.openclaw/workspace/scripts/session-snapshot.py load

# 查看快照信息
python3 ~/.openclaw/workspace/scripts/session-snapshot.py card
```

**自动保存触发点**：
- 完成重要任务后
- 用户说"记住这个"
- 切换模型前

### 2️⃣ 增强记忆系统（enhanced-memory）

**作用**：智能检索历史记忆，支持向量和文本混合搜索

**使用**：
```bash
cd ~/.openclaw/workspace/skills/enhanced-memory

# 存储记忆
python -m enhanced_memory add "用户喜欢Python" --category preference --importance 0.8

# 检索记忆
python -m enhanced_memory search "编程偏好"

# 从会话快照提取记忆
python session_distiller.py
```

**Python API**：
```python
import sys
sys.path.insert(0, '~/.openclaw/workspace/skills/enhanced-memory')
from enhanced_memory import store_memory, recall_memory

# 存储
store_memory(text="关键信息", category="fact", importance=0.9)

# 检索
results = recall_memory("查询内容", top_k=5)
```

### 3️⃣ 恢复检测器（recovery-detector.py）

**作用**：新会话时自动检测是否需要恢复上下文

**使用**：
```bash
# 检查是否有需要恢复的内容
python3 ~/.openclaw/workspace/scripts/recovery-detector.py

# 输出示例：
# 发现未完成的会话: 修复定时任务通知
# 建议恢复口令: 继续修复定时任务
```

## 🔗 三者如何协作

```
用户对话中
    ↓
session-snapshot.py 自动保存快照
    ↓
用户执行 /new
    ↓
recovery-detector.py 检测是否需要恢复
    ↓
是 → 提示用户恢复口令
    ↓
session_distiller.py 提取关键信息
    ↓
存储到 enhanced-memory
    ↓
新会话中 recall_memory() 随时检索
```

## 📝 完整工作流程示例

### 场景：多轮任务处理

**第1轮会话**：
```
用户: 帮我写个股票分析脚本
AI: 好的，开始写...（自动保存快照）
AI: 已完成基础版本（自动保存快照）

用户: /new
```

**系统自动执行**：
```bash
# 1. recovery-detector 检测到未完成任务
# 2. session_distiller 提取记忆：
#    - "任务：写股票分析脚本"
#    - "状态：基础版本已完成"
# 3. 存储到 enhanced-memory
```

**第2轮会话**：
```
用户: 继续之前的工作
AI: 检测到您之前在做"股票分析脚本"，基础版本已完成，需要继续完善吗？
（检索 enhanced-memory 自动回复）
```

## ⚙️ 配置建议

### 添加到 AGENTS.md

让 AI 自动使用这套系统：

```markdown
## 记忆管理规则

### 会话保存
- 完成重要任务后自动运行：`python3 scripts/session-snapshot.py save`
- 用户说"记住这个"时立即保存

### 记忆检索
- 用户提及"之前"、"上次"、"继续"时，检索 enhanced-memory
- 使用 `recall_memory(query, top_k=3)` 获取相关记忆

### 会话恢复
- 检测到 /new 时检查 recovery-detector
- 如有未完成事项，主动询问是否恢复

### 记忆存储（双层存储）
1. 技术层：保存具体信息（category=fact）
2. 原则层：保存决策规则（category=decision）
```

### 定时任务（可选）

```bash
# 每30分钟自动保存会话
*/30 * * * * python3 ~/.openclaw/workspace/scripts/session-snapshot.py save --task "自动保存"
```

## 🎓 使用技巧

### 技巧1：关键词触发

在对话中主动触发记忆：
- "记得我之前说的..." → 自动检索
- "继续之前的工作" → 自动恢复
- "把这条记下来" → 自动存储

### 技巧2：重要性分级

```python
# 0.9+ 非常重要（核心决策、关键配置）
store_memory(..., importance=0.95)

# 0.7-0.8 重要（任务状态、偏好设置）
store_memory(..., importance=0.8)

# 0.5-0.6 一般（临时信息、日常对话）
store_memory(..., importance=0.6)
```

### 技巧3：多作用域隔离

```python
# 全局共享
store_memory(..., scope="global")

# 特定 Agent 私有
store_memory(..., scope="agent:main")
store_memory(..., scope="agent:coding")
```

## 🔧 故障排查

### 问题1：记忆检索不到

检查：
```bash
python -m enhanced_memory stats
python -m enhanced_memory list --limit 10
```

### 问题2：快照没有保存

检查目录权限：
```bash
ls -la ~/.openclaw/workspace/memory/snapshots/
```

### 问题3：恢复检测失败

手动运行：
```bash
python3 scripts/session-snapshot.py card
python3 scripts/recovery-detector.py
```

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| 记忆检索速度 | < 100ms (1,000条) |
| 快照保存速度 | < 50ms |
| 存储格式 | JSON (可读可编辑) |
| 依赖数量 | 0 (核心) / 2 (可选加速) |

## 🆚 和官方 memory 对比

| 功能 | 官方 memory-core | OpenClaw Memory Kit |
|------|-----------------|---------------------|
| 存储方式 | 文件 | JSON (可编辑) |
| 向量搜索 | ❌ | ✅ |
| 时间衰减 | ❌ | ✅ |
| 重要性 | ❌ | ✅ |
| 会话快照 | ❌ | ✅ |
| 自动恢复 | ❌ | ✅ |
| BM25 | ❌ | ✅ |

## 📝 更新日志

- **v1.0** (2026-03-06)
  - 整合 enhanced-memory + session-snapshot + recovery-detector
  - 提供完整记忆解决方案

## 📄 许可证

MIT - 自由使用、修改、分享

---
*Made by 雪子助手 for OpenClaw Community*
