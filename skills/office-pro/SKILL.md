---
name: office-pro
description: Professional Office document generation and processing suite. Use when creating, editing, converting, or analyzing Microsoft Office documents (Word, Excel, PowerPoint) and PDFs. Supports report generation, data visualization, template-based document creation, batch processing, and format conversion. Ideal for automated reporting, professional document creation, data export with charts, and multi-format document workflows.
---

# Office Pro - 专业办公文档处理套件

综合性的 Office 文档处理技能包，支持 Word、Excel、PowerPoint、PDF 的创建、编辑、转换和分析。

## 核心功能

### 1. Word 文档处理
- 创建专业报告和文档
- 模板驱动文档生成
- 样式管理（标题、段落、列表）
- 表格、图片、图表插入
- 目录自动生成
- 页眉页脚设置

### 2. Excel 数据处理
- 工作簿/工作表创建
- 数据导入导出（支持 Pandas）
- 公式计算和单元格格式化
- 图表生成（柱状图、折线图、饼图）
- 条件格式设置
- 数据透视表

### 3. PowerPoint 演示文稿
- 幻灯片创建和编辑
- 母版设计应用
- 图表和表格插入
- 批量幻灯片生成
- 演讲者备注

### 4. PDF 处理
- PDF 创建和编辑
- 多 PDF 合并/拆分
- 文本提取
- 图片插入
- 密码保护

### 5. 格式转换
- Office 转 Markdown
- Word ↔ PDF
- Excel ↔ CSV/JSON
- PPTX 转图片

## 快速开始

### 生成 Word 报告
```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()
doc.add_heading('报告标题', 0)
doc.add_paragraph('这是正文内容...')
doc.save('report.docx')
```

### 生成 Excel 报表
```python
import openpyxl
from openpyxl.chart import BarChart

wb = openpyxl.Workbook()
ws = wb.active
ws['A1'] = '数据'
chart = BarChart()
ws.add_chart(chart, 'E5')
wb.save('report.xlsx')
```

### 使用脚本工具

**Word 报告生成器**
```bash
python3 ~/.openclaw/workspace/skills/office-pro/scripts/word_report_generator.py \
  --template monthly_report \
  --data data.json \
  --output report.docx
```

**Excel 数据分析器**
```bash
python3 ~/.openclaw/workspace/skills/office-pro/scripts/excel_analyzer.py \
  --input data.csv \
  --chart-type bar \
  --output analysis.xlsx
```

**批量文档处理器**
```bash
python3 ~/.openclaw/workspace/skills/office-pro/scripts/batch_processor.py \
  --input-dir ./docs/ \
  --output-format pdf \
  --output-dir ./output/
```

**Office 转 Markdown (新增)**
```bash
# Word 转 Markdown
python3 ~/.openclaw/workspace/skills/office-pro/scripts/office_to_markdown.py \
  document.docx -o document.md

# Excel 转 Markdown 表格
python3 ~/.openclaw/workspace/skills/office-pro/scripts/office_to_markdown.py \
  data.xlsx -o data.md

# PPT 转 Markdown 大纲
python3 ~/.openclaw/workspace/skills/office-pro/scripts/office_to_markdown.py \
  presentation.pptx -o presentation.md

# 批量转换整个目录
python3 ~/.openclaw/workspace/skills/office-pro/scripts/office_to_markdown.py \
  ./office_docs/ -b -o ./markdown_output/
```

**Python 调用 Office 转 Markdown**
```python
from scripts.office_to_markdown import convert_office_to_md

# Word 转 Markdown
md_content = convert_office_to_md('report.docx', 'report.md')

# Excel 转 Markdown
md_content = convert_office_to_md('data.xlsx', 'data.md')

# PPT 转 Markdown
md_content = convert_office_to_md('slides.pptx', 'slides.md')
```

## 脚本参考

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `word_report_generator.py` | Word 报告生成 | 自动化报告 |
| `excel_analyzer.py` | Excel 数据分析和图表 | 数据分析 |
| `pptx_generator.py` | PPT 批量生成 | 演示文稿 |
| `pdf_processor.py` | PDF 合并/拆分/提取 | PDF 处理 |
| `format_converter.py` | 格式转换 | 文档转换 |
| `batch_processor.py` | 批量文档处理 | 批量任务 |
| `office_to_markdown.py` | Office 转 Markdown | 文档格式转换 |

## 模板系统

模板存储在 `assets/templates/`：
- `monthly_report.docx` - 月度报告模板
- `project_proposal.docx` - 项目提案模板
- `data_report.xlsx` - 数据分析报告模板
- `presentation.pptx` - 演示文稿模板

使用模板：
```python
from docx import Document

doc = Document('assets/templates/monthly_report.docx')
# 替换占位符
doc.save('output.docx')
```

## 详细文档

- [Word 处理指南](references/word_guide.md)
- [Excel 处理指南](references/excel_guide.md)
- [PowerPoint 处理指南](references/pptx_guide.md)
- [PDF 处理指南](references/pdf_guide.md)
- [API 参考](references/api_reference.md)

## 依赖安装

```bash
pip install python-docx openpyxl python-pptx reportlab pdfplumber pypdf pandas
```

## 典型工作流

### 1. 月度报告自动化
1. 从数据库/CSV 读取数据
2. 使用 `excel_analyzer.py` 生成数据图表
3. 使用 `word_report_generator.py` 生成 Word 报告
4. 使用 `pdf_processor.py` 转换为 PDF
5. 发送邮件或保存到指定位置

### 2. 项目提案生成
1. 填写项目信息 JSON
2. 使用模板生成 Word 提案
3. 自动生成 Excel 财务分析
4. 创建 PPT 演示文稿
5. 打包为项目文档集

### 3. 批量数据处理
1. 扫描输入目录中的所有文件
2. 使用 `batch_processor.py` 统一处理
3. 转换为目标格式
4. 按规则重命名和归档
