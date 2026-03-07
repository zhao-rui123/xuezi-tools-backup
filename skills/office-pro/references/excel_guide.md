# Excel 处理指南

## 基础操作

### 创建工作簿
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wb = Workbook()
ws = wb.active
ws.title = "工作表1"

# 写入数据
ws['A1'] = '标题'
ws['B1'] = 100

# 写入多行数据
data = [
    ['姓名', '年龄', '城市'],
    ['张三', 25, '北京'],
    ['李四', 30, '上海'],
]
for row in data:
    ws.append(row)

wb.save('workbook.xlsx')
```

### 单元格样式
```python
from openpyxl.styles import Font, PatternFill, Border, Side

# 字体
ws['A1'].font = Font(name='Arial', size=12, bold=True, color='FF0000')

# 填充
ws['A1'].fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')

# 对齐
ws['A1'].alignment = Alignment(horizontal='center', vertical='center')

# 边框
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)
ws['A1'].border = thin_border
```

### 列宽和行高
```python
ws.column_dimensions['A'].width = 20
ws.row_dimensions[1].height = 30
```

## 图表操作

### 柱状图
```python
from openpyxl.chart import BarChart, Reference

chart = BarChart()
chart.type = 'col'  # 垂直柱状图
chart.style = 10
chart.title = '销售数据'
chart.y_axis.title = '金额'
chart.x_axis.title = '月份'

data = Reference(ws, min_col=2, min_row=1, max_row=7, max_col=2)
cats = Reference(ws, min_col=1, min_row=2, max_row=7)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.shape = 4

ws.add_chart(chart, 'E5')
```

### 折线图
```python
from openpyxl.chart import LineChart

chart = LineChart()
chart.title = '趋势图'
chart.style = 2
chart.y_axis.title = '数值'
chart.x_axis.title = '时间'

data = Reference(ws, min_col=2, min_row=1, max_col=3, max_row=7)
chart.add_data(data, titles_from_data=True)

ws.add_chart(chart, 'E5')
```

### 饼图
```python
from openpyxl.chart import PieChart
from openpyxl.chart.label import DataLabelList

pie = PieChart()
labels = Reference(ws, min_col=1, min_row=2, max_row=7)
data = Reference(ws, min_col=2, min_row=1, max_row=7)
pie.add_data(data, titles_from_data=True)
pie.set_categories(labels)
pie.title = '占比图'

# 显示百分比
pie.dataLabels = DataLabelList()
pie.dataLabels.showPercent = True

ws.add_chart(pie, 'E5')
```

## 公式和计算

### 基本公式
```python
ws['C2'] = '=A2+B2'
ws['C3'] = '=SUM(A2:A10)'
ws['C4'] = '=AVERAGE(A2:A10)'
ws['C5'] = '=MAX(A2:A10)'
ws['C6'] = '=MIN(A2:A10)'
```

### 条件格式
```python
from openpyxl.formatting.rule import ColorScaleRule

# 色阶
rule = ColorScaleRule(
    start_type='min', start_color='F8696B',
    mid_type='percentile', mid_value=50, mid_color='FFEB84',
    end_type='max', end_color='63BE7B'
)
ws.conditional_formatting.add('A2:A10', rule)
```

## 数据处理

### 与 Pandas 集成
```python
import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows

# DataFrame 转 Excel
df = pd.DataFrame({
    '姓名': ['张三', '李四'],
    '年龄': [25, 30]
})

for r in dataframe_to_rows(df, index=False, header=True):
    ws.append(r)

# Excel 转 DataFrame
df = pd.read_excel('file.xlsx', sheet_name='Sheet1')
```

### 筛选和排序
```python
# 添加自动筛选
ws.auto_filter.ref = ws.dimensions

# 冻结窗格
ws.freeze_panes = 'B2'  # 冻结首行和首列
```

## 高级功能

### 数据验证
```python
from openpyxl.worksheet.datavalidation import DataValidation

dv = DataValidation(type="list", formula1='"选项1,选项2,选项3"', allow_blank=True)
ws.add_data_validation(dv)
dv.add(ws['A1'])
```

### 合并单元格
```python
ws.merge_cells('A1:C1')
ws.unmerge_cells('A1:C1')
```

### 插入删除行列
```python
ws.insert_rows(2)  # 在第2行前插入一行
ws.delete_rows(2)  # 删除第2行
ws.insert_cols(2)  # 在第2列前插入一列
```
