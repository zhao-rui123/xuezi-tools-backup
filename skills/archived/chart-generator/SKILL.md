---
name: chart-generator
description: Generate charts and visualizations for data analysis. Use for creating profit trend charts, comparison charts, and analytical visualizations for reports.
---

# 图表生成技能

## 支持图表类型

| 类型 | 用途 | 库 |
|------|------|-----|
| 折线图 | 趋势分析、时间序列 | matplotlib |
| 柱状图 | 对比分析、排名 | matplotlib |
| 饼图 | 占比分析 | matplotlib |
| 组合图 | 多维度分析 | matplotlib |

## 安装

```bash
pip install matplotlib pandas
```

## 储能收益趋势图

```python
import matplotlib.pyplot as plt
import pandas as pd

def plot_profit_trend(yearly_data, output_path='profit_trend.png'):
    """绘制年度收益趋势图"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    years = yearly_data['year']
    profits = yearly_data['profit']
    cumulative = yearly_data['cumulative']
    
    # 柱状图 - 年度收益
    bars = ax.bar(years, profits, label='年度收益', color='#4A90E2', alpha=0.7)
    
    # 折线图 - 累计收益
    ax2 = ax.twinx()
    line = ax2.plot(years, cumulative, color='#E24A4A', marker='o', 
                    linewidth=2, label='累计收益')
    
    # 设置标签
    ax.set_xlabel('年份', fontsize=12)
    ax.set_ylabel('年度收益（万元）', fontsize=12, color='#4A90E2')
    ax2.set_ylabel('累计收益（万元）', fontsize=12, color='#E24A4A')
    
    ax.set_title('储能项目收益趋势', fontsize=14, fontweight='bold')
    
    # 图例
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path
```

## 电价对比图

```python
def plot_price_comparison(province_data, output_path='price_comparison.png'):
    """绘制各省电价对比图"""
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    provinces = province_data['province']
    peak = province_data['peak_price']
    valley = province_data['valley_price']
    
    x = range(len(provinces))
    width = 0.35
    
    ax.bar([i - width/2 for i in x], peak, width, label='峰时电价', color='#E24A4A')
    ax.bar([i + width/2 for i in x], valley, width, label='谷时电价', color='#4A90E2')
    
    ax.set_xlabel('省份', fontsize=12)
    ax.set_ylabel('电价（元/kWh）', fontsize=12)
    ax.set_title('各省分时电价对比', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(provinces, rotation=45)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path
```

## 投资回收期图

```python
def plot_payback_analysis(cash_flow, output_path='payback_analysis.png'):
    """绘制投资回收期分析图"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    years = cash_flow['year']
    net_flow = cash_flow['net_flow']
    cumulative = cash_flow['cumulative']
    
    # 净现金流柱状图
    colors = ['#4A90E2' if x >= 0 else '#E24A4A' for x in net_flow]
    ax.bar(years, net_flow, color=colors, alpha=0.7)
    
    # 累计现金流线
    ax.plot(years, cumulative, color='#2ECC71', marker='o', 
            linewidth=2, label='累计现金流')
    
    # 零线
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    
    # 回收期标注
    payback_year = cash_flow[cash_flow['cumulative'] >= 0]['year'].iloc[0]
    ax.axvline(x=payback_year, color='red', linestyle=':', alpha=0.5)
    ax.text(payback_year, max(cumulative)*0.8, f'回收期: {payback_year}年', 
            color='red', fontweight='bold')
    
    ax.set_xlabel('年份', fontsize=12)
    ax.set_ylabel('现金流（万元）', fontsize=12)
    ax.set_title('投资回收期分析', fontsize=14, fontweight='bold')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path
```

## 股票走势图

```python
def plot_stock_trend(stock_data, output_path='stock_trend.png'):
    """绘制股票走势图"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                    gridspec_kw={'height_ratios': [3, 1]})
    
    dates = stock_data['date']
    prices = stock_data['close']
    volumes = stock_data['volume']
    
    # 价格走势
    ax1.plot(dates, prices, color='#4A90E2', linewidth=1.5)
    ax1.fill_between(dates, prices, alpha=0.3, color='#4A90E2')
    ax1.set_ylabel('价格（元）', fontsize=11)
    ax1.set_title('股票走势', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 成交量
    ax2.bar(dates, volumes, color='gray', alpha=0.5)
    ax2.set_ylabel('成交量', fontsize=11)
    ax2.set_xlabel('日期', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path
```

## 设置中文字体

```python
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
```

---
*创建于: 2026-03-04*  
*依赖: matplotlib, pandas*
