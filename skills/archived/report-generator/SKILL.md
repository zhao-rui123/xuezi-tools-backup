---
name: report-generator
description: Generate professional reports in Word, Excel, and PowerPoint formats. Use for project calculation reports, analysis summaries, and presentation materials.
---

# 报告生成技能

## 支持格式

| 格式 | 用途 | 库 |
|------|------|-----|
| Word (.docx) | 项目报告、合同文档 | python-docx |
| Excel (.xlsx) | 数据报表、财务模型 | openpyxl |
| PowerPoint (.pptx) | 项目汇报、路演 | python-pptx |

## Word 报告生成

```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_project_report(project_name, data):
    doc = Document()
    
    # 标题
    title = doc.add_heading(f'{project_name} - 项目测算报告', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 项目信息
    doc.add_heading('一、项目概况', level=1)
    doc.add_paragraph(f'项目名称：{project_name}')
    doc.add_paragraph(f'测算日期：{data["date"]}')
    
    # 技术参数表格
    doc.add_heading('二、技术参数', level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light Grid Accent 1'
    
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = '参数'
    hdr_cells[1].text = '数值'
    
    for key, value in data['params'].items():
        row_cells = table.add_row().cells
        row_cells[0].text = key
        row_cells[1].text = str(value)
    
    # 财务指标
    doc.add_heading('三、财务指标', level=1)
    doc.add_paragraph(f'静态投资回收期：{data["payback_period"]} 年')
    doc.add_paragraph(f'全投资IRR：{data["irr"]}%')
    
    return doc

# 保存
doc.save('project_report.docx')
```

## Excel 报表生成

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

def create_financial_model(data):
    wb = Workbook()
    ws = wb.active
    ws.title = '财务测算'
    
    # 标题
    ws['A1'] = '工商业储能项目财务测算模型'
    ws['A1'].font = Font(size=16, bold=True)
    ws.merge_cells('A1:F1')
    
    # 输入参数
    ws['A3'] = '输入参数'
    ws['A3'].font = Font(bold=True)
    
    params = [
        ['储能容量', data['capacity'], 'kWh'],
        ['设备成本', data['equipment_cost'], '元/kWh'],
        ['运营年限', data['operation_years'], '年'],
    ]
    for row in params:
        ws.append(row)
    
    return wb

wb.save('financial_model.xlsx')
```

## PowerPoint 生成

```python
from pptx import Presentation
from pptx.util import Inches

def create_project_ppt(data):
    prs = Presentation()
    
    # 标题页
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = data['name']
    slide.placeholders[1].text = f"项目测算汇报\n{data['date']}"
    
    # 内容页
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = '项目概况'
    body = slide.placeholders[1].text_frame
    body.text = f"储能容量：{data['capacity']} kWh"
    
    return prs

prs.save('project_presentation.pptx')
```

## 安装依赖

```bash
pip install python-docx openpyxl python-pptx
```

---
*创建于: 2026-03-04*
