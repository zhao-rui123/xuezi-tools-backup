# Word 处理指南

## 基础操作

### 创建文档
```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# 添加标题
doc.add_heading('文档标题', 0)  # 0=标题, 1-9=各级标题

# 添加段落
para = doc.add_paragraph('这是普通段落文本')

# 添加带样式的段落
para = doc.add_paragraph()
run = para.add_run('粗体文本')
run.bold = True
run = para.add_run(' 普通文本 ')
run = para.add_run('斜体文本')
run.italic = True

# 保存
doc.save('document.docx')
```

### 设置中文字体
```python
from docx.oxml.ns import qn

def set_chinese_font(run, font_name='SimSun', font_size=12):
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = Pt(font_size)
```

### 添加表格
```python
table = doc.add_table(rows=3, cols=3)
table.style = 'Light Grid Accent 1'

# 填充数据
for i, row in enumerate(table.rows):
    for j, cell in enumerate(row.cells):
        cell.text = f'单元格 {i},{j}'

# 合并单元格
table.cell(0, 0).merge(table.cell(0, 2))
```

### 添加图片
```python
doc.add_picture('image.png', width=Inches(5.0))
```

### 页眉页脚
```python
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

# 页眉
header = doc.sections[0].header
header_para = header.paragraphs[0]
header_para.text = "页眉内容"
header_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

# 页脚
footer = doc.sections[0].footer
footer_para = footer.paragraphs[0]
footer_para.text = "页脚内容"
```

## 样式操作

### 应用样式
```python
para = doc.add_paragraph('标题文本', style='Heading 1')
para = doc.add_paragraph('引用文本', style='Intense Quote')
```

### 自定义样式
```python
from docx.shared import RGBColor

para = doc.add_paragraph()
run = para.add_run('自定义样式文本')
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(255, 0, 0)
run.font.bold = True
```

## 高级功能

### 目录生成
Word 会根据标题样式自动生成目录，需要在 Word 中手动更新域。

### 批注
```python
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# 添加批注（需要直接操作 XML）
```

### 修订模式
Word 原生支持，python-docx 不支持直接操作修订。

## 常见问题

### 中文显示问题
确保设置中文字体，使用 `w:eastAsia` 属性。

### 图片大小
建议使用 `width` 或 `height` 参数控制大小，不要同时设置两者。

### 表格样式
可用的表格样式：
- 'Light Grid Accent 1'
- 'Medium Grid 1'
- 'Table Grid'
- 更多参见 Word 表格样式
