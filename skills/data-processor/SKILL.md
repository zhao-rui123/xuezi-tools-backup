---
name: data-processor
description: Data processing for CSV, Excel, and tabular data. Use when processing electricity price data, energy bills, or any structured data files. Supports reading, transforming, filtering, and exporting data.
---

# 数据处理技能

## 支持格式

| 格式 | 读取 | 写入 | 用途 |
|------|------|------|------|
| CSV | ✅ | ✅ | 电价数据、简单表格 |
| Excel (.xlsx) | ✅ | ✅ | 复杂报表、多sheet |
| JSON | ✅ | ✅ | API数据、配置文件 |
| Markdown表格 | ✅ | ✅ | 文档展示 |

## 核心工具

### Python 库
```python
import pandas as pd
import openpyxl
import csv
```

### 常用操作

#### 1. 读取数据
```python
import pandas as pd

# CSV
df = pd.read_csv('data.csv', encoding='utf-8')

# Excel
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# 指定列类型
df = pd.read_csv('data.csv', dtype={'code': str})
```

#### 2. 数据清洗
```python
# 删除空行
df = df.dropna(how='all')

# 填充空值
df['column'] = df['column'].fillna(0)

# 删除重复
df = df.drop_duplicates()

# 重命名列
df = df.rename(columns={'old': 'new'})
```

#### 3. 数据转换
```python
# 筛选
df_filtered = df[df['province'] == '山东']

# 排序
df_sorted = df.sort_values('price', ascending=False)

# 分组统计
df_grouped = df.groupby('province')['price'].mean()

# 新增计算列
df['total'] = df['price'] * df['quantity']
```

#### 4. 导出数据
```python
# 导出CSV
df.to_csv('output.csv', index=False, encoding='utf-8-sig')

# 导出Excel
df.to_excel('output.xlsx', index=False, sheet_name='数据')

# 多sheet导出
with pd.ExcelWriter('output.xlsx') as writer:
    df1.to_excel(writer, sheet_name='Sheet1')
    df2.to_excel(writer, sheet_name='Sheet2')
```

## 电价数据处理场景

### 场景1：更新单省电价
```python
import pandas as pd

# 读取现有数据
df = pd.read_csv('electricity_prices.csv')

# 更新某省数据
df.loc[df['province'] == '山东', 'peak_price'] = 1.2
df.loc[df['province'] == '山东', 'valley_price'] = 0.3

# 保存
df.to_csv('electricity_prices.csv', index=False)
```

### 场景2：批量导入新电价
```python
# 新数据
new_data = pd.read_excel('new_prices_2026_03.xlsx')

# 合并（更新或追加）
df = pd.read_csv('electricity_prices.csv')
df = df.merge(new_data, on='province', how='left', suffixes=('', '_new'))

# 更新逻辑
df['peak_price'] = df['peak_price_new'].fillna(df['peak_price'])
df = df.drop(columns=[c for c in df.columns if '_new' in c])

df.to_csv('electricity_prices.csv', index=False)
```

### 场景3：生成电价对比表
```python
# 读取数据
df = pd.read_csv('electricity_prices.csv')

# 计算峰谷差
df['price_diff'] = df['peak_price'] - df['valley_price']
df['diff_ratio'] = (df['price_diff'] / df['valley_price'] * 100).round(2)

# 排序
df = df.sort_values('diff_ratio', ascending=False)

# 导出
df.to_excel('price_comparison.xlsx', index=False)
```

## 电费清单处理场景

### 读取国网电费清单
```python
# 国网导出的Excel通常有表头
df = pd.read_excel('electricity_bill.xlsx', skiprows=2)

# 标准化列名
df.columns = ['date', 'peak_kwh', 'valley_kwh', 'total_kwh', 
              'peak_cost', 'valley_cost', 'total_cost']

# 日期解析
df['date'] = pd.to_datetime(df['date'])

# 计算平均电价
df['avg_price'] = df['total_cost'] / df['total_kwh']
```

### 储能收益计算
```python
# 假设储能容量和策略
capacity_kwh = 1000  # 1MWh
efficiency = 0.9     # 90%效率
dod = 0.9            # 90%放电深度

# 计算可套利电量
usable_kwh = capacity_kwh * dod

# 计算每日收益
df['daily_profit'] = usable_kwh * efficiency * df['price_diff']

# 月度汇总
monthly = df.groupby(df['date'].dt.month)['daily_profit'].sum()
```

## 数据验证

### 检查数据质量
```python
# 缺失值检查
print(df.isnull().sum())

# 异常值检查
print(df['price'].describe())

# 重复检查
print(f"重复行数: {df.duplicated().sum()}")

# 数据类型检查
print(df.dtypes)
```

### 自动修复常见问题
```python
def clean_electricity_data(df):
    """清洗电价数据"""
    # 删除完全空行
    df = df.dropna(how='all')
    
    # 省份名称标准化
    province_map = {'山东省': '山东', '广东省': '广东'}
    df['province'] = df['province'].replace(province_map)
    
    # 价格列转数字
    price_cols = ['peak_price', 'valley_price', 'flat_price']
    for col in price_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 删除价格异常行
    df = df[df['peak_price'] > 0]
    
    return df
```

## 最佳实践

1. **备份原数据**: 处理前保存副本
2. **验证数据类型**: 确保数字列不是字符串
3. **处理编码**: CSV用 `utf-8-sig` 避免Excel乱码
4. **保留原始列**: 新增计算列，不覆盖原始数据
5. **记录处理日志**: 记录清洗前后的行数变化

---
*创建于: 2026-03-04*  
*依赖: pandas, openpyxl*
