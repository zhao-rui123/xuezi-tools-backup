# 系统监控看板 - 后端API

## 功能

提供系统监控数据API接口，零Token消耗（只读本地文件）。

### API接口

| 接口 | 描述 |
|------|------|
| `GET /api/system/status` | 系统整体状态（磁盘、内存、CPU、进程） |
| `GET /api/memory/stats` | Memory Suite完整统计 |
| `GET /api/cron/tasks` | 定时任务完整列表 |

### 详细接口

**系统状态**
- `/api/system/disk` - 磁盘使用情况
- `/api/system/memory` - 内存使用情况
- `/api/system/cpu` - CPU使用情况
- `/api/system/processes` - 进程信息
- `/api/system/workspace` - 工作空间统计

**Memory Suite**
- `/api/memory/skills` - 技能记忆统计
- `/api/memory/scores` - 记忆评分统计
- `/api/memory/files` - 记忆文件状态

**定时任务**
- `/api/cron/crontab` - 系统crontab任务
- `/api/cron/managed` - Cron Manager管理的任务
- `/api/cron/logs` - 定时任务日志状态

## 启动

```bash
# 方式1：使用启动脚本
./start.sh

# 方式2：直接运行
python3 app.py --port 5000

# 方式3：调试模式
python3 app.py --debug
```

## 依赖

```bash
pip3 install flask flask-cors psutil --break-system-packages
```

## 测试

```bash
# 测试API
curl http://localhost:5000/api/health
curl http://localhost:5000/api/system/status
curl http://localhost:5000/api/memory/stats
curl http://localhost:5000/api/cron/tasks
```

## 文件结构

```
backend/
├── app.py           # Flask主应用
├── system_monitor.py # 系统监控模块
├── start.sh         # 启动脚本
└── README.md        # 本文件
```
