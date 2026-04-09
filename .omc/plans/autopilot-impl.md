# 小龙虾之家 AI 助手工作状态看板 - 实施计划

## 阶段 1: 后端 API 开发

### 1.1 Flask 后端
- **文件**: `/opt/lobster-home/app.py`
- **功能**:
  - GET `/api/status` - 获取当前状态
  - POST `/api/status` - 更新状态
  - GET `/api/stats/week` - 近7天统计
  - GET `/api/achievements` - 成就列表
  - POST `/api/archive` - 手动归档
- **数据存储**: `/opt/lobster-home/data/data.json`

### 1.2 数据模型
```python
data = {
    "current_status": {
        "position": "studio",
        "status": "coding",
        "task_count": 0,
        "token_consumed": 0,
        "work_hours": 0.0,
        "last_update": "ISO时间"
    },
    "daily_stats": [],  # 近7天数据
    "achievements": {} # 12个成就
}
```

## 阶段 2: 前端页面结构

### 2.1 主页面 `index.html`
- 整体布局: 左侧9宫格 + 右侧统计面板
- 像素风格 meta 标签
- 引入 CSS 和 JS 文件

### 2.2 像素风格 `css/pixel.css`
- CSS 变量定义颜色
- 像素网格基础样式
- 9宫格房间布局
- 小龙虾角色 CSS 像素画
- 家具像素元素
- 成就徽章样式
- 柱状图样式
- 动画定义

### 2.3 房间配置 `js/house.js`
```javascript
const ROOMS = [
    { id: 'living', name: '客厅', status: ['idle', 'rest'] },
    { id: 'studio', name: '工作室', status: ['coding', 'working'] },
    { id: 'tea', name: '茶水室', status: ['thinking'] },
    { id: 'kitchen', name: '厨房', status: ['eating'] },
    { id: 'restaurant', name: '餐厅', status: ['dining'] },
    { id: 'game', name: '游戏室', status: ['gaming'] },
    { id: 'bath1', name: '卫生间', status: ['grooming'] },
    { id: 'bedroom', name: '卧室', status: ['sleeping'] },
    { id: 'balcony', name: '阳台', status: ['exercising'] }
];
```

### 2.4 小龙虾角色 `js/lobster.js`
- CSS 像素画渲染
- 状态动画 (呼吸、敲键盘、闪烁、咀嚼)
- 房间移动动画
- 表情变化

### 2.5 统计模块 `js/stats.js`
- 今日统计渲染
- 近7天柱状图 (Canvas)
- 成就徽章渲染

### 2.6 主应用 `js/app.js`
- 状态轮询 (30秒)
- API 调用
- 成就检查逻辑
- 自动归档检查

## 阶段 3: 小龙虾角色像素画详细设计

### CSS 像素画实现
```css
/* 小龙虾身体 */
.lobster-body {
    width: 32px;
    height: 24px;
    background: #E74C3C;
    box-shadow:
        /* 腿部 */
        -8px 8px 0 #C0392B,
        -4px 8px 0 #C0392B,
        4px 8px 0 #C0392B,
        8px 8px 0 #C0392B,
        /* 钳子 */
        -16px 0 0 #E74C3C,
        16px 0 0 #E74C3C;
}
```

### 房间家具像素
- 客厅: 沙发 (蓝绿), TV (灰)
- 工作室: 电脑桌 (棕), 显示器 (蓝)
- 茶水室: 茶几 (浅棕), 茶杯 (白)
- 厨房: 灶台 (银), 冰箱 (白)
- 餐厅: 餐桌 (棕), 椅子 (棕)
- 游戏室: 游戏机 (黑), 手柄 (灰)
- 卫生间: 马桶 (白), 洗手台 (银)
- 卧室: 床 (蓝), 衣柜 (棕)
- 阳台: 跑步机 (灰)

## 阶段 4: 数据持久化

### 4.1 初始化数据
首次运行时创建默认数据结构

### 4.2 自动归档
- 每日 00:00 检查并归档
- 将前一天数据保存到 `archive/YYYY-MM-DD.json`
- 重置今日统计

### 4.3 成就检查
每次状态更新时检查成就解锁条件

## 阶段 5: 部署

### 5.1 文件结构
```
/opt/lobster-home/
├── app.py              # Flask API
├── data/
│   └── data.json       # 数据文件
├── archive/            # 归档目录
├── requirements.txt    # Python依赖
└── init.sh            # 初始化脚本

/usr/share/nginx/html/my-home/
├── index.html
├── css/
│   └── pixel.css
└── js/
    ├── app.js
    ├── lobster.js
    ├── house.js
    └── stats.js
```

### 5.2 依赖
- Flask (Python)
- 无需前端依赖 (纯原生JS)

## 任务列表

1. [ ] 创建目录结构
2. [ ] 实现 Flask 后端 API
3. [ ] 创建 index.html
4. [ ] 编写 pixel.css 像素样式
5. [ ] 实现 house.js 房间系统
6. [ ] 实现 lobster.js 小龙虾角色
7. [ ] 实现 stats.js 统计模块
8. [ ] 实现 app.js 主应用
9. [ ] 初始化数据文件
10. [ ] 部署到 /opt/lobster-home/
11. [ ] 验证功能完整性
