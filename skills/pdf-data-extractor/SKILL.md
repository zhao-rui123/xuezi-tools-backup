---
name: pdf-data-extractor
description: Extract data from PDF files, including general text extraction, table extraction, and specialized extraction for State Grid electricity bills and official documents.
---

# PDF 数据提取技能

## 适用场景

| 场景 | 示例 | 输出格式 |
|------|------|---------|
| **通用PDF文本提取** | 任意PDF文档转文本 | TXT/Markdown |
| **国网电费清单** | 月度电费明细 | Excel/CSV |
| **发改委文件** | 电价政策文件 | 结构化文本 |
| **技术规范** | 设备技术参数 | JSON/表格 |

## 核心工具

```python
import pdfplumber    # 表格提取首选
import PyPDF2        # 文本提取
import pandas as pd
```

## 1. 通用PDF文本提取 (新增)

### 基础文本提取
```bash
# 提取PDF文本
python3 pdf_text_extractor.py document.pdf -o output.txt

# 使用特定方法提取
python3 pdf_text_extractor.py document.pdf -m pdfplumber -o output.txt

# 保留布局提取
python3 pdf_text_extractor.py document.pdf -m layout -o output.txt
```

### Python调用
```python
from pdf_text_extractor import extract_pdf_text, search_in_pdf

# 提取文本
text = extract_pdf_text('document.pdf', method='auto')

# 在PDF中搜索关键词
results = search_in_pdf('document.pdf', '电价')
for r in results:
    print(f"行 {r['line']}: {r['content']}")
```

### 批量提取
```bash
# 批量提取目录下所有PDF
python3 pdf_text_extractor.py /path/to/pdfs/ -b -o ./extracted_texts/
```

### 提取方法对比

| 方法 | 优点 | 适用场景 |
|------|------|----------|
| **auto** (默认) | 自动选择最佳方法 | 通用 |
| **pdfplumber** | 精准度高 | 复杂排版 |
| **pypdf2** | 速度快 | 简单文本 |
| **layout** | 保留布局 | 表格混排 |

## 2. 国网电费清单提取

### 标准流程
```python
import pdfplumber
import pandas as pd
import re

def extract_state_grid_bill(pdf_path):
    """提取国网电费清单"""
    records = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            
            for table in tables:
                for row in table:
                    # 识别数据行（包含日期）
                    if len(row) >= 4 and any(re.match(r'\d{4}-\d{2}-\d{2}', str(cell)) for cell in row):
                        records.append({
                            'date': row[0],
                            'peak_kwh': extract_number(row[1]),
                            'valley_kwh': extract_number(row[2]),
                            'total_kwh': extract_number(row[3]),
                            'peak_cost': extract_number(row[4]) if len(row) > 4 else None,
                            'valley_cost': extract_number(row[5]) if len(row) > 5 else None,
                        })
    
    df = pd.DataFrame(records)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df.dropna(subset=['date'])

def extract_number(cell):
    """从单元格提取数字"""
    if not cell:
        return None
    numbers = re.findall(r'[\d.]+', str(cell))
    return float(numbers[0]) if numbers else None
```

### 提取负荷曲线
```python
def extract_load_curve(pdf_path):
    """提取24小时负荷曲线"""
    load_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            
            for table in tables:
                for row in table:
                    # 识别时间点格式 (00:00, 00:15等)
                    if len(row) >= 2 and re.match(r'\d{2}:\d{2}', str(row[0])):
                        load_data.append({
                            'time': row[0],
                            'load_kw': extract_number(row[1])
                        })
    
    return pd.DataFrame(load_data)
```

## 3. 发改委电价文件提取

```python
import PyPDF2
import re

def extract_policy_info(pdf_path):
    """提取电价政策关键信息"""
    
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ''.join(page.extract_text() for page in reader.pages)
    
    return {
        'province': extract_province(text),
        'effective_date': extract_date(text),
        'peak_price': extract_price(text, '峰'),
        'valley_price': extract_price(text, '谷'),
    }

def extract_province(text):
    provinces = ['山东', '河南', '河北', '浙江', '江苏', '广东']
    for p in provinces:
        if p in text:
            return p
    return None

def extract_price(text, period_type):
    pattern = rf'{period_type}.*?电.*?([\d.]+)\s*元'
    match = re.search(pattern, text)
    return float(match.group(1)) if match else None
```

## 输出格式

```python
# 导出Excel
df.to_excel('output.xlsx', index=False)

# 导出CSV
df.to_csv('output.csv', index=False, encoding='utf-8-sig')

# 导出JSON
import json
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 导出纯文本
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(text)
```

## 安装依赖

```bash
pip install pdfplumber PyPDF2 pandas openpyxl
```

---
*创建于: 2026-03-04*
*更新: 2026-03-07 - 添加通用PDF文本提取功能*
