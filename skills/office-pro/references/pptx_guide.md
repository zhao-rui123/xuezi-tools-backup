# PowerPoint 处理指南

## 基础操作

### 创建演示文稿
```python
from pptx import Presentation
from pptx.util import Inches, Pt

# 创建空白演示文稿
prs = Presentation()

# 或使用模板
prs = Presentation('template.pptx')
```

### 幻灯片布局
```python
# 可用的布局
# 0: 标题页
# 1: 标题和内容
# 2: 章节标题
# 3: 两栏内容
# 4: 比较
# 5: 空白
# 6: 仅标题
# 7: 空白

slide_layout = prs.slide_layouts[1]  # 标题和内容
slide = prs.slides.add_slide(slide_layout)
```

### 添加标题和内容
```python
title = slide.shapes.title
content = slide.placeholders[1]

title.text = '幻灯片标题'
content.text = '这是内容区域'

# 或使用文本框
textbox = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(5))
text_frame = textbox.text_frame
text_frame.text = '自定义文本框内容'
```

## 文本处理

### 段落和样式
```python
tf = textbox.text_frame
tf.text = '第一段'

p = tf.add_paragraph()
p.text = '第二段'
p.level = 1  # 缩进级别

p = tf.add_paragraph()
p.text = '第三段'
p.font.size = Pt(20)
p.font.bold = True
```

### 字体设置
```python
from pptx.dml.color import RGBColor

run = paragraph.add_run()
run.text = '彩色文字'
run.font.size = Pt(24)
run.font.bold = True
run.font.color.rgb = RGBColor(255, 0, 0)
```

## 添加元素

### 图片
```python
slide.shapes.add_picture('image.png', Inches(1), Inches(2), width=Inches(4))
```

### 表格
```python
rows, cols = 3, 3
left = Inches(1)
top = Inches(2)
width = Inches(8)
height = Inches(4)

table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# 填充数据
table.cell(0, 0).text = '表头1'
table.cell(0, 1).text = '表头2'
table.cell(1, 0).text = '数据1'
table.cell(1, 1).text = '数据2'
```

### 图表
```python
from pptx.chart.data import ChartData
from pptx.enum.chart import XL_CHART_TYPE

chart_data = ChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
chart_data.add_series('销售额', (100, 200, 300, 400))

x, y, cx, cy = Inches(2), Inches(2), Inches(6), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
).chart

chart.has_title = True
chart.chart_title.text_frame.text = '季度销售'
```

## 母版操作

### 访问母版
```python
# 获取所有幻灯片母版
for slide_master in prs.slide_masters:
    print(slide_master.name)

# 修改母版背景
slide_master = prs.slide_master
background = slide_master.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = RGBColor(240, 240, 240)
```

### 占位符
```python
# 查看幻灯片中的所有占位符
for shape in slide.placeholders:
    print(f'{shape.placeholder_format.idx}: {shape.name}')
```

## 批量生成

### 从数据生成幻灯片
```python
data = [
    {'title': '第一章', 'content': ['要点1', '要点2', '要点3']},
    {'title': '第二章', 'content': ['要点4', '要点5', '要点6']},
]

for item in data:
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = item['title']
    
    tf = slide.placeholders[1].text_frame
    tf.text = item['content'][0]
    
    for content in item['content'][1:]:
        p = tf.add_paragraph()
        p.text = content
        p.level = 0
```

## 高级功能

### 演讲者备注
```python
notes_slide = slide.notes_slide
text_frame = notes_slide.notes_text_frame
text_frame.text = '这是演讲者备注'
```

### 超链接
```python
from pptx.enum.action import PP_ACTION

run = paragraph.add_run()
run.text = '点击访问'
run.hyperlink.address = 'https://example.com'
```

### 动画（有限支持）
python-pptx 对动画的支持有限，复杂动画需要在 PowerPoint 中手动添加。

## 最佳实践

1. **使用模板**：预先设计好模板，程序填充内容
2. **保持简洁**：每页内容不要过多
3. **图片优化**：提前调整好图片大小
4. **字体统一**：保持全文风格一致
5. **保存备份**：先生成到临时文件，确认无误后再覆盖
