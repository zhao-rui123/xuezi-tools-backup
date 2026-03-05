---
name: File to Mac
slug: file-to-mac
version: 1.0.0
description: 文件写入存档到Mac指定文件夹
metadata: {"emoji":"📁","requires":{"os":["darwin"]}}
---

## 功能

将文件写入存档到Mac的指定文件夹

## 文件夹结构

```
/Volumes/cu/ocu/
├── memory/      # 每天的记忆文件
├── backups/     # 备份的其他文件
├── downloads/   # 下载的文件
```

## 使用方法

### 写入文件到指定文件夹

```
写入 [文件名] 到 [memory/backups/downloads]
内容: [文件内容]
```

### 读取文件夹内容

```
查看 /Volumes/cu/ocu/[memory/backups/downloads]
```

## 示例

- "写入 test.txt 到 downloads，内容: Hello World"
- "查看 memory 文件夹"
- "把计算结果保存到 backups"

## 注意事项

- 只操作 /Volumes/cu/ocu/ 目录下的文件
- 不操作其他路径的文件
