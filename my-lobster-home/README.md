# 🏠 雪子助手的温馨小家 - 完整版

像素风8-bit温馨小家，实时展示AI助手的工作状态。

🌐 **在线访问**: http://106.54.25.161/my-home/

---

## ✨ 功能特性

### 🏠 房子布局（客厅C位）
```
    🍵 茶水室      🍳 厨房      🎮 游戏室
       ↓           ↓           ↓
    🚽 卫生间 → 【📺 客厅】 ← 💻 工作室
                    ✨C位✨
                       ↓
                    🍽️ 餐厅
                       ↓
    🚽 卫生间 ← 🛏️ 主卧 → (门)
                       ↓
                  🌞 阳台运动场
```

### 📊 实时统计
- ✅ 今日完成任务数
- 🔥 Token消耗统计
- ⏱️ 工作时长记录
- 📍 当前位置追踪
- 🏠 房间停留时间

### 🤖 智能状态切换
| 触发条件 | 房间 | 动作 |
|---------|------|------|
| 开始任务 | 💻 工作室 | 自动移动，开始工作 |
| 完成任务 | 📺/🍽️/🍵 | 自动休息 |
| 高强度工作 | 🏃 运动场 | 运动放松 |
| 深夜23:00+ | 🛏️ 主卧 | 自动睡觉 |
| 随机摸鱼 | 🚽 卫生间 | 15%概率触发 |

### 📱 飞书日报推送
- ⏰ 每晚22:00自动生成日报
- 📊 包含：任务数、Token、工作时长、足迹、心情
- 🦞 小龙虾风格文案

---

## 🚀 技术架构

### 前端
- HTML5 + CSS3 (8-bit像素风)
- JavaScript (实时API轮询)
- VT323 像素字体

### 后端API
- Flask + Flask-CORS
- RESTful API
- 文件存储 (JSON)

### 部署
- Nginx 静态文件
- Python Flask API
- Crontab 定时任务

---

## 📁 文件结构

```
my-lobster-home/
├── index.html              # 前端页面
├── css/
│   └── style.css          # 8-bit像素风样式
├── js/
│   └── dashboard.js       # 前端逻辑 + API调用
├── api_fixed.py           # Flask API服务器
├── feishu_daily.py        # 飞书日报推送脚本
├── lobster_client.py      # Python客户端
└── deploy-full.sh         # 完整部署脚本
```

---

## 🔌 API接口

| 接口 | 方法 | 功能 |
|-----|------|------|
| `/api/status` | GET | 获取当前状态 |
| `/api/task/start` | POST | 开始任务 |
| `/api/task/complete` | POST | 完成任务（带token） |

### 调用示例

**开始任务:**
```bash
curl -X POST http://106.54.25.161:5000/api/task/start \
  -H "Content-Type: application/json" \
  -d '{"task_name": "开发看板"}'
```

**完成任务:**
```bash
curl -X POST http://106.54.25.161:5000/api/task/complete \
  -H "Content-Type: application/json" \
  -d '{"tokens_used": 1500}'
```

---

## 🛠️ 部署

### 完整部署
```bash
cd my-lobster-home
bash deploy-full.sh
```

### 手动部署
```bash
# 1. 前端
scp -r * root@106.54.25.161:/usr/share/nginx/html/my-home/

# 2. API
scp api_fixed.py root@106.54.25.161:/opt/lobster-home/
ssh root@106.54.25.161 "cd /opt/lobster-home && python3 api_fixed.py &"

# 3. 定时任务
crontab -e
# 添加: 0 22 * * * cd /opt/lobster-home && python3 feishu_daily.py
```

---

## 🎯 下一步计划

- [x] 像素风房子看板
- [x] C位客厅布局
- [x] API实时同步
- [x] Token/时长记录
- [x] 飞书日报推送
- [ ] 历史趋势图表
- [ ] 成就系统
- [ ] AI心情总结
- [ ] 智能提醒

---

Made with ❤️ by 雪子助手 🦞
