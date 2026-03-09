---
name: file-sender
description: |
  全面的文件管理发送技能包 - 整合文件发送、文件管理、文件传递、Mac文件操作。
  v2.0 整合: file-management + file-transfer + file-to-mac
---

# 文件管理发送技能包 v2.0

全面的文件解决方案，支持文件发送（飞书/腾讯云/坚果云）、文件管理、Mac文件操作。

## 功能特性

### 1. 文件发送
- **飞书发送** - 直接发送文件到群聊
- **腾讯云下载** - 大文件上传到服务器提供下载
- **坚果云备份** - 重要文件备份到坚果云

### 2. 文件管理 ⭐NEW v2.0
- **目录结构管理** - 确保标准目录结构
- **临时文件清理** - 自动清理过期文件
- **大文件查找** - 识别占用空间的大文件

### 3. Mac文件操作 ⭐NEW v2.0
- **写入Mac文件夹** - 保存文件到指定目录
- **查看文件夹内容** - 浏览Mac文件

## 使用方法

### 文件发送

#### 方式1: 飞书直接发送
```python
from file_sender import send_file
send_file('/path/to/file.xlsx', '文件说明')
```

#### 方式2: 腾讯云下载（大文件）
```bash
# 上传到服务器
scp 本地文件 root@106.54.25.161:/usr/share/nginx/html/downloads/

# 提供下载链接
http://106.54.25.161/downloads/文件名
```

#### 方式3: 坚果云备份
```bash
curl -u "1034440765@qq.com:Zr123456" \
  -T 本地文件 \
  "https://dav.jianguoyun.com/dav/OpenClaw/文件名"
```

### 文件管理 ⭐NEW v2.0
```bash
# 运行文件管理
cd ~/.openclaw/workspace/skills/file-sender
python3 file_manager.py
```

**功能**:
- 清理7天前的临时文件
- 确保标准目录结构
- 查找大于10MB的大文件

### Mac文件操作 ⭐NEW v2.0
```bash
# 写入文件到Mac
python3 file_sender.py --mac-write /path/to/file.txt --dest memory

# 查看Mac文件夹
python3 file_sender.py --mac-list memory
```

**目标目录**:
- `memory` - /Volumes/cu/ocu/memory/
- `backups` - /Volumes/cu/ocu/backups/
- `downloads` - /Volumes/cu/ocu/downloads/

## 目录结构

```
workspace/
├── assets/          # 静态资源
├── knowledge-base/  # 知识库
├── memory/          # 每日记忆
├── reports/         # 生成的报告
├── scripts/         # 脚本文件
├── skills/          # 技能包
└── tmp/             # 临时文件
    ├── screenshots/ # 截图（保留7天）
    ├── downloads/   # 下载文件（保留7天）
    └── cache/       # 缓存
```

## 文件说明

| 文件 | 功能 |
|------|------|
| file_sender.py | 主发送脚本 |
| file_manager.py | 文件管理工具 ⭐NEW |
| SKILL.md | 本文档 |

## 更新日志

### v2.0 (2026-03-09)
- ✅ 整合 file-management 文件管理
- ✅ 整合 file-transfer 文件传递方式
- ✅ 整合 file-to-mac Mac文件操作
- ✅ 创建全面的文件管理发送技能包

### v1.0
- 初始版本，飞书文件发送功能
