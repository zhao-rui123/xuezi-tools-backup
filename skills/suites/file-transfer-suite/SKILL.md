---
name: file-transfer-suite
description: |
  文件传输完整套件 - 整合文件发送、管理、Mac操作
  一站式文件传输解决方案
version: 1.0.0
---

# 文件传输套件 (File Transfer Suite)

一站式文件传输解决方案，整合文件发送、管理、Mac操作全流程。

## 包含组件

| 组件 | 功能 | 路径 |
|------|------|------|
| **file-sender** | 文件发送和管理 | `../file-sender/` |

## 快速开始

### 发送文件
```bash
cd ~/.openclaw/workspace/skills/suites/file-transfer-suite
python3 suite_runner.py --send /path/to/file "文件说明"
```

## 功能特性

### 📤 文件发送 (file-sender)
- 飞书直接发送
- 腾讯云下载链接
- 坚果云备份
- 文件管理
- Mac文件操作

## 传输方式

### 方式1: 飞书直接发送
适合：小文件、快速传递

### 方式2: 腾讯云下载
适合：大文件、稳定下载

### 方式3: 坚果云备份
适合：重要文件、长期存档

## 使用示例

### 发送文件
```bash
python3 suite_runner.py --send report.xlsx "项目报告"
```

### 上传到腾讯云
```bash
python3 suite_runner.py --upload-cloud /path/to/file
```

### 备份到坚果云
```bash
python3 suite_runner.py --backup-nutstore /path/to/file
```

### 文件管理
```bash
python3 suite_runner.py --cleanup
```

## 目录结构

```
file-transfer-suite/
├── SKILL.md              # 本文档
├── suite_runner.py       # 套件统一入口
└── config/
    └── transfer.json     # 传输配置
```

## 更新日志

### v1.0.0 (2026-03-09)
- ✅ 创建文件传输套件
- ✅ 整合 file-sender 全部功能

---
*文件传输一站式解决方案*
