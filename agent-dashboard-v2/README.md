# 🏠 雪子助手的小龙虾之家 v2.0

像素风俯视房子看板，实时展示AI助手的工作状态。

🌐 **在线访问**: http://106.54.25.161/agent-dashboard/

---

## 🎮 房子结构

```
┌─────────┬─────────┬─────────┐
│  📚书房  │  💻工作室 │  🎮游戏室 │
│  思考区   │  工作区   │  娱乐区   │
├─────────┼─────────┼─────────┤
│  🛏️休息室 │  🚽卫生间 │  🍜厨房  │
│  恢复区   │  摸鱼区   │  干饭区   │
├─────────┴─────────┴─────────┤
│        🏃 操场（运动/高强度）   │
└─────────────────────────────┘
```

---

## ✨ 功能特点

### 🦞 小龙虾角色
- 俯视角度像素形象
- 走路动画（1-2秒移动到目标房间）
- 每个房间有不同动作
- 情绪表情气泡
- 对话系统

### 🏠 智能房间切换
| 状态 | 房间 | 触发条件 |
|-----|------|---------|
| 工作中 | 💻 工作室 | 开始任务 |
| 思考中 | 📚 书房 | 完成任务后随机 |
| 游戏中 | 🎮 游戏室 | 休息10分钟后 |
| 休息中 | 🛏️ 休息室 | 5分钟无任务 |
| 睡觉中 | 🛏️ 休息室 | 23:00-07:00 |
| 摸鱼中 | 🚽 卫生间 | 随机触发(15%) |
| 吃饭中 | 🍜 厨房 | 饭点完成任务 |
| 运动中 | 🏃 操场 | 高强度工作(>30分钟) |

### 📊 统计数据
- ✅ 今日完成任务数
- 🔥 Token消耗
- ⏱️ 工作时长
- 📈 近7天趋势图表
- 🏠 房间停留时间分布

---

## 🚀 快速开始

### 1. 启动追踪器

```bash
cd ~/.openclaw/workspace/agent-dashboard-v2
./start.sh
```

### 2. 在Python中记录任务

```python
import sys
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/agent-dashboard-v2')
from tracker import start_task, complete_task

# 开始任务
room = start_task("开发储能看板")
print(f"小龙虾去了: {room}")

# ... 执行任务 ...

# 完成任务
room = complete_task(tokens_used=1500)
print(f"小龙虾去了: {room}")
```

### 3. 部署网页

```bash
./deploy.sh
```

访问: http://106.54.25.161/agent-dashboard/

---

## 📁 文件结构

```
agent-dashboard-v2/
├── index.html          # 主页面（房子场景）
├── css/
│   └── style.css       # 像素风样式
├── js/
│   └── dashboard.js    # 房子逻辑+图表
├── data/               # 数据存储
│   ├── stats.json      # 当前统计
│   └── history/        # 历史归档（30天）
├── tracker.py          # Python状态追踪器
├── daily_push.py       # 飞书每日推送
├── deploy.sh           # 部署脚本
├── start.sh            # 启动追踪器
└── stop.sh             # 停止追踪器
```

---

## 🕙 定时任务

### 每晚22:00推送飞书总结

添加到 crontab:
```bash
0 22 * * * cd ~/.openclaw/workspace/agent-dashboard-v2 && python3 daily_push.py
```

推送内容包括：
- 今日足迹（房间停留时间）
- 任务完成数
- Token消耗
- 工作时长
- 最耗时任务
- 今日心情

---

## 💡 与OpenClaw集成

在OpenClaw会话中自动记录：

```python
# 在 session_integration.py 中
from tracker import start_task, complete_task, add_tokens

# 会话开始时
start_task(f"会话_{task_type}")

# 每次工具调用后
add_tokens(tokens_used)

# 会话结束时
complete_task(total_tokens)
```

---

## 🎨 像素风设计

- 字体: VT323 (Google Fonts)
- 颜色: 复古游戏配色
- 动画: CSS keyframes
- 图表: Chart.js

---

Made with ❤️ by 雪子助手 🦞
