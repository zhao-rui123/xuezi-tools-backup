---
name: document-suite
description: |
  文档处理完整套件 - 整合 Office、PDF、数据分析、图表生成
  一站式文档处理解决方案
version: 1.0.0
---

# 文档处理套件 (Document Suite)

一站式文档处理解决方案，整合 Office、PDF、数据分析、图表生成全流程。

## 包含组件

| 组件 | 功能 | 路径 |
|------|------|------|
| **office-pro** | Office文档生成处理 | `../office-pro/` |
| **pdf-data-extractor** | PDF数据提取 | `../pdf-data-extractor/` |
| **data-processor** | 数据处理 | `../data-processor/` |
| **chart-generator** | 图表生成 | `../chart-generator/` |

## 快速开始

### 生成完整报告
```bash
cd ~/.openclaw/workspace/skills/suites/document-suite
python3 suite_runner.py --generate-report data.csv
```

## 功能特性

### 📄 Office处理 (office-pro)
- Word文档生成
- Excel数据处理
- PowerPoint演示文稿
- PDF转换
- 批量处理

### 📑 PDF提取 (pdf-data-extractor)
- 文本提取
- 表格提取
- 国网电费清单专用提取
- 结构化数据输出

### 📊 数据处理 (data-processor)
- CSV/Excel读取
- 数据清洗转换
- 数据验证
- 批量导出

### 📈 图表生成 (chart-generator)
- 折线图、柱状图
- 饼图、散点图
- 组合图表
- 专业报告图表

## 使用示例

### 从数据生成完整报告
```bash
python3 suite_runner.py --full-report data.csv --title "项目分析报告"
```

### 处理PDF并提取数据
```bash
python3 suite_runner.py --process-pdf document.pdf --output data.json
```

### 生成图表
```bash
python3 suite_runner.py --chart data.csv --type line --output chart.png
```

## 目录结构

```
document-suite/
├── SKILL.md              # 本文档
├── suite_runner.py       # 套件统一入口
└── config/
    └── templates.json    # 模板配置
```

## 更新日志

### v1.0.0 (2026-03-09)
- ✅ 创建文档处理套件
- ✅ 整合4个文档相关技能包

---
*文档处理一站式解决方案*
