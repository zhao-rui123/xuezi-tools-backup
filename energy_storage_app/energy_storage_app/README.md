# CALB工商业储能收资清单 Web应用

一个在线查看、填写、下载的收资清单管理系统。

## 功能特性

- 📋 **在线查看** - 在浏览器中直接查看收资清单表格
- ✏️ **在线填写** - 直接在网页填写收资信息并提交
- 📥 **下载模板** - 下载原始Excel模板线下填写
- 📊 **数据管理** - 查看所有已提交的记录
- 📤 **导出数据** - 导出所有提交数据为Excel

## 快速启动

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务
```bash
python app.py
```
或双击运行 `start.bat`

### 3. 访问
打开浏览器访问: http://localhost:5000

## 服务器部署

### Windows 服务器 (IIS)

1. 安装 Python
2. 安装依赖: `pip install -r requirements.txt`
3. 使用 Gunicorn (可选):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Linux 服务器

1. 安装 Python3 和 pip
2. 安装依赖: `pip3 install -r requirements.txt`
3. 使用 gunicorn:
```bash
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker 部署

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 目录结构

```
energy_storage_app/
├── app.py              # 主应用
├── requirements.txt     # 依赖
├── start.bat           # Windows启动脚本
├── templates/          # HTML模板
│   ├── index.html      # 首页
│   ├── view.html       # 在线查看
│   ├── form.html       # 在线填写
│   ├── submissions.html # 已提交列表
│   └── detail.html     # 详情页
├── uploads/            # 上传的文件
└── submissions/        # 提交的表单数据
    └── submissions.json
```

## 配置

端口: 5000 (可在 app.py 中修改)
数据存储:
- 附件文件: `uploads/`
- 表单数据: `submissions/submissions.json`

## 注意事项

1. 标 * 的字段为必填项
2. 照片、CAD图纸请以附件形式上传
3. 所有数据保存在服务器本地
4. 定期备份 `submissions/` 目录
