# 系统监控看板

一个简洁高效的系统监控看板，支持实时数据展示和历史数据分析。

## 功能特性

- 📊 实时系统监控数据展示
- 📈 历史数据趋势分析
- 🔔 告警通知管理
- 📱 响应式设计，支持移动端
- 🚀 一键部署，快速启动

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- Nginx (可选，用于生产环境)

### 一键启动

```bash
# 克隆项目后进入目录
cd dashboard

# 一键启动所有服务
./start.sh
```

启动后访问：
- 本地开发: http://localhost:8080
- 生产环境: http://your-server-ip/

## 部署指南

### 1. 本地开发部署

```bash
# 1. 安装依赖
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 2. 启动服务
./start.sh
```

### 2. 服务器生产部署

#### 步骤 1: 上传文件到服务器

```bash
# 使用 scp 或 rsync 上传项目
scp -r dashboard/ root@your-server:/usr/share/nginx/html/
```

#### 步骤 2: 配置 nginx

```bash
# 复制 nginx 配置
sudo cp /usr/share/nginx/html/dashboard/nginx.conf /etc/nginx/conf.d/dashboard.conf

# 测试配置
sudo nginx -t

# 重载 nginx
sudo nginx -s reload
```

#### 步骤 3: 配置 systemd 服务（可选）

```bash
# 复制服务文件
sudo cp /usr/share/nginx/html/dashboard/systemd-dashboard.service /etc/systemd/system/dashboard.service

# 创建日志目录
sudo mkdir -p /var/log/dashboard

# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start dashboard

# 设置开机自启
sudo systemctl enable dashboard
```

#### 步骤 4: 验证部署

```bash
# 检查服务状态
sudo systemctl status dashboard

# 查看日志
sudo tail -f /var/log/dashboard/service.log
```

### 3. Docker 部署（可选）

```bash
# 构建镜像
docker build -t dashboard .

# 运行容器
docker run -d -p 80:80 --name dashboard dashboard
```

## 管理命令

```bash
# 启动服务
./start.sh start

# 停止服务
./start.sh stop

# 重启服务
./start.sh restart

# 查看状态
./start.sh status

# 查看帮助
./start.sh help
```

## 目录结构

```
dashboard/
├── backend/              # 后端服务
│   ├── app.py           # Flask 应用入口
│   ├── requirements.txt  # Python 依赖
│   └── ...
├── frontend/             # 前端应用
│   ├── src/             # 源代码
│   ├── package.json     # Node 依赖
│   └── ...
├── logs/                 # 日志目录
├── pids/                 # PID 文件目录
├── data/                 # 数据目录
├── start.sh              # 启动脚本
├── nginx.conf            # nginx 配置
├── systemd-dashboard.service  # systemd 服务配置
└── README.md             # 本文档
```

## 配置文件

### 后端配置

编辑 `backend/config.py`：

```python
# 数据库配置
DATABASE_URL = "sqlite:///data/dashboard.db"

# API 配置
API_PORT = 5000
API_HOST = "0.0.0.0"

# 日志配置
LOG_LEVEL = "INFO"
```

### nginx 配置

编辑 `nginx.conf` 后重新加载：

```bash
sudo nginx -s reload
```

## 日志查看

```bash
# 后端日志
tail -f logs/backend.log

# nginx 访问日志
tail -f /var/log/nginx/dashboard_access.log

# nginx 错误日志
tail -f /var/log/nginx/dashboard_error.log

# systemd 服务日志
sudo journalctl -u dashboard -f
```

## 常见问题

### Q: 端口被占用怎么办？

A: 修改 `start.sh` 中的 `PORT` 变量，或修改 `backend/config.py` 中的端口配置。

### Q: 如何修改监听地址？

A: 编辑 `start.sh` 中的配置，或设置环境变量 `FLASK_HOST`。

### Q: 如何配置 HTTPS？

A: 编辑 `nginx.conf`，取消 HTTPS server 配置的注释，并配置 SSL 证书路径。

### Q: 服务无法启动？

A: 检查日志文件获取详细错误信息：
```bash
# 检查依赖
python3 --version
node --version
nginx -v

# 查看日志
cat logs/backend.log
```

## 更新维护

```bash
# 1. 停止服务
./start.sh stop

# 2. 备份数据
cp -r data/ data_backup_$(date +%Y%m%d)/

# 3. 更新代码
git pull

# 4. 更新依赖
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 5. 重新启动
./start.sh
```

## 技术支持

如有问题，请查看日志文件或提交 Issue。

---

**版本**: 1.0.0  
**更新日期**: 2026-03-11
