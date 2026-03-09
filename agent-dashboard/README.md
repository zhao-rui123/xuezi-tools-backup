# 🦞 雪子助手的小龙虾工作室

一个像素风格的任务看板，实时展示AI助手的工作状态和统计数据。

![像素小龙虾](assets/preview.png)

## ✨ 功能特点

- 🎮 **像素风界面** - 复古游戏风格的视觉体验
- 🦞 **小龙虾形象** - 可爱的像素小龙虾作为AI助手形象
- 📊 **实时统计** - 今日完成任务数、Token消耗、工作时长
- 🎭 **多种场景** - 工作、休息、思考、运动、吃饭、睡觉
- 😊 **情绪表达** - 根据状态显示不同的情绪和对话
- ⏰ **自动切换** - 5分钟无任务自动进入休息状态

## 🚀 快速开始

### 1. 启动状态追踪器

```bash
cd ~/.openclaw/workspace/agent-dashboard
./start-tracker.sh
```

### 2. 部署到服务器

```bash
./deploy.sh
```

访问: http://106.54.25.161/agent-dashboard/

### 3. 在Python代码中记录任务

```python
import sys
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/agent-dashboard')
from status_tracker import start_task, complete_task, add_tokens

# 开始任务
start_task("处理电价数据")

# ... 执行任务 ...

# 完成任务（记录消耗的tokens）
complete_task(tokens_used=1500)
```

## 📁 文件结构

```
agent-dashboard/
├── index.html          # 主页面
├── css/
│   └── style.css       # 像素风样式
├── js/
│   └── dashboard.js    # 前端逻辑
├── assets/             # 静态资源
├── data/               # 数据存储
│   ├── stats.json      # 统计数据
│   └── history/        # 历史归档
├── status_tracker.py   # Python状态追踪器
├── deploy.sh           # 部署脚本
├── start-tracker.sh    # 启动追踪器
└── stop-tracker.sh     # 停止追踪器
```

## 🎨 场景说明

| 场景 | 图标 | 触发条件 |
|------|------|---------|
| 工作中 | 💻 | 开始任务时 |
| 休息中 | 🏠 | 5分钟无任务 |
| 思考中 | 📚 | 完成任务后随机 |
| 运动中 | 💪 | 完成任务后随机 |
| 吃饭中 | 🍜 | 饭点完成任务 |
| 睡觉中 | 😴 | 23:00-07:00 |

## 📝 开发计划

- [x] 像素风界面设计
- [x] 小龙虾CSS动画
- [x] 状态追踪器
- [x] 统计数据记录
- [ ] 与OpenClaw集成（自动记录会话）
- [ ] 历史趋势图表
- [ ] 飞书通知推送

## 🔧 技术栈

- **前端**: HTML5 + CSS3 + JavaScript
- **后端**: Python 3
- **部署**: Nginx + SCP

## 🐛 故障排查

### 状态追踪器无法启动
```bash
# 检查Python环境
python3 --version

# 检查日志
cat /tmp/agent_status.log
```

### 网页无法访问
```bash
# 检查服务器状态
openclaw gateway status

# 手动部署
scp -r ~/.openclaw/workspace/agent-dashboard/* root@106.54.25.161:/usr/share/nginx/html/agent-dashboard/
```

---

Made with ❤️ by 雪子助手 🦞
