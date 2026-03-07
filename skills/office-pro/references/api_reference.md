# Office Pro API 参考

## 脚本命令参考

### word_report_generator.py

生成 Word 报告文档。

```bash
python3 word_report_generator.py --data DATA.json --output OUTPUT.docx [--template TEMPLATE.docx]
```

**参数：**
- `--data, -d`: 数据 JSON 文件路径（必需）
- `--output, -o`: 输出文件路径（必需）
- `--template, -t`: 模板文件路径（可选）

**数据 JSON 格式：**
```json
{
  "title": "报告标题",
  "sections": [
    {
      "title": "章节标题",
      "content": [
        "普通文本段落",
        {
          "type": "list",
          "items": ["列表项1", "列表项2"]
        },
        {
          "type": "table",
          "data": [
            ["表头1", "表头2"],
            ["数据1", "数据2"]
          ]
        }
      ]
    }
  ]
}
```

### excel_analyzer.py

分析数据并生成带图表的 Excel 报告。

```bash
python3 excel_analyzer.py --input INPUT --output OUTPUT.xlsx [--chart-type TYPE] [--sheet-name NAME]
```

**参数：**
- `--input, -i`: 输入文件（CSV/JSON/Excel）
- `--output, -o`: 输出 Excel 文件
- `--chart-type, -c`: 图表类型（bar/line/pie），默认 bar
- `--sheet-name, -s`: 工作表名称，默认"分析结果"

### pptx_generator.py

生成 PowerPoint 演示文稿。

```bash
python3 pptx_generator.py --data DATA.json --output OUTPUT.pptx [--template TEMPLATE.pptx]
```

**数据 JSON 格式：**
```json
{
  "title": "演示标题",
  "subtitle": "副标题",
  "slides": [
    {
      "title": "幻灯片标题",
      "content": ["要点1", "要点2", "要点3"]
    }
  ],
  "charts": [
    {
      "title": "图表标题",
      "columns": ["类别", "数值"],
      "data": [["A", 100], ["B", 200]]
    }
  ]
}
```

### pdf_processor.py

PDF 处理工具。

```bash
# 合并 PDF
python3 pdf_processor.py merge --input file1.pdf file2.pdf --output merged.pdf

# 拆分 PDF
python3 pdf_processor.py split --input file.pdf --output ./output --pages 5

# 提取文本
python3 pdf_processor.py extract --input file.pdf --output text.txt

# 添加水印
python3 pdf_processor.py watermark --input file.pdf --output watermarked.pdf --watermark "机密"
```

### format_converter.py

格式转换工具。

```bash
# Word 转 Markdown
python3 format_converter.py docx2md --input file.docx --output file.md

# Excel 转 CSV
python3 format_converter.py excel2csv --input file.xlsx --output ./csv_output

# Excel 转 JSON
python3 format_converter.py excel2json --input file.xlsx --output file.json

# PPT 转文本
python3 format_converter.py pptx2txt --input file.pptx --output file.txt
```

### batch_processor.py

批量文档处理。

```bash
# 批量转换
python3 batch_processor.py convert --input-dir ./docs --output-dir ./output --format txt

# 批量重命名
python3 batch_processor.py rename --input-dir ./docs --pattern "old" --replacement "new"

# 生成文件索引
python3 batch_processor.py index --input-dir ./docs --output-file index.xlsx
```

## Python API

### Word 操作
```python
from docx import Document
from docx.shared import Inches, Pt

doc = Document()
doc.add_heading('标题', 0)
doc.add_paragraph('内容')
doc.save('file.docx')
```

### Excel 操作
```python
from openpyxl import Workbook
from openpyxl.chart import BarChart

wb = Workbook()
ws = wb.active
ws['A1'] = '数据'
wb.save('file.xlsx')
```

### PowerPoint 操作
```python
from pptx import Presentation

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[0])
prs.save('file.pptx')
```

### PDF 操作
```python
from PyPDF2 import PdfMerger

merger = PdfMerger()
merger.append('file1.pdf')
merger.append('file2.pdf')
merger.write('merged.pdf')
```

## 依赖列表

```
python-docx>=0.8.11
openpyxl>=3.0.0
python-pptx>=0.6.21
reportlab>=3.6.0
PyPDF2>=3.0.0
pdfplumber>=0.6.0
pandas>=1.3.0
```

## 安装依赖

```bash
pip install python-docx openpyxl python-pptx reportlab PyPDF2 pdfplumber pandas
```
