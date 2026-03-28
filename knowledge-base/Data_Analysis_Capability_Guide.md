# 数据分析能力指南

## 概述

本工具具备完整的数据分析能力，涵盖数据读取、清洗、可视化、统计分析全链路。所有功能基于 Python 库实现，**无需 API Key**。

---

## 一、环境要求

### Python 版本
- Python 3.12+
- pip 25+

### 已安装库

| 库 | 版本 | 用途 |
|----|------|------|
| pandas | 3.0.1 | 数据处理核心 |
| matplotlib | 3.10.8 | 基础可视化 |
| seaborn | 0.13.2 | 统计图表 |
| scipy | 1.17.1 | 科学计算 |
| statsmodels | 0.14.6 | 统计建模 |
| openpyxl | 3.1.5 | Excel 读写 |
| scikit-learn | - | 机器学习（如需） |
| numpy | - | 底层数值计算 |

安装命令：
```bash
pip install pandas matplotlib seaborn scipy statsmodels openpyxl
```

---

## 二、数据读取

### 支持格式
- CSV / TSV
- Excel（.xlsx / .xls）
- JSON
- HTML（网页表格）
- SQL（通过 SQLAlchemy）
- 剪贴板

### 代码示例

```python
import pandas as pd

# CSV
df = pd.read_csv("data.csv")

# Excel（指定 sheet）
df = pd.read_excel("data.xlsx", sheet_name="Sheet1")

# JSON
df = pd.read_json("data.json")

# HTML 表格
dfs = pd.read_html("http://example.com/table.html")
```

---

## 三、数据清洗

```python
# 缺失值处理
df.dropna()                    # 删除含缺失值的行
df.fillna(0)                  # 用 0 填充
df.fillna(df.mean())           # 用均值填充

# 重复值
df.drop_duplicates()

# 类型转换
df["日期"] = pd.to_datetime(df["日期"])
df["金额"] = pd.to_numeric(df["金额"])

# 筛选
df_filtered = df[df["金额"] > 1000]
```

---

## 四、数据可视化

### matplotlib 基础图表

```python
import matplotlib.pyplot as plt

# 折线图
plt.figure(figsize=(10, 6))
plt.plot(x, y)
plt.title("标题")
plt.xlabel("X轴")
plt.ylabel("Y轴")
plt.grid(True)
plt.savefig("output.png")
plt.show()

# 柱状图
plt.bar(categories, values)

# 散点图
plt.scatter(x, y)

# 饼图
plt.pie(values, labels=labels)
```

### seaborn 统计图表

```python
import seaborn as sns

# 热力图（相关性矩阵）
corr = df.corr()
sns.heatmap(corr, annot=True, cmap="coolwarm")

# 分布图
sns.histplot(df["金额"], kde=True)

# 箱线图
sns.boxplot(x="类别", y="金额", data=df)

# pairplot（多变量关系）
sns.pairplot(df)

# 回归图
sns.regplot(x="x", y="y", data=df)
```

---

## 五、统计分析

### scipy 基本统计

```python
from scipy import stats

# 描述统计
df.describe()

# t 检验
t_stat, p_value = stats.ttest_ind(group_a, group_b)

# 卡方检验
chi2, p, dof, expected = stats.chi2_contingency(contingency_table)

# 正态性检验
stats.shapiro(data)

# 相关性检验
stats.pearsonr(x, y)
stats.spearmanr(x, y)
```

### statsmodels 回归分析

```python
import statsmodels.api as sm

# 线性回归
X = df[["x1", "x2"]]
y = df["y"]
X = sm.add_constant(X)
model = sm.OLS(y, X).fit()
print(model.summary())

# 时间序列（简单指数平滑）
from statsmodels.tsa.holtwinters import ExponentialSmoothing
model = ExponentialSmoothing(data, trend="add").fit()
```

---

## 六、股票技术分析

专用脚本：`D:\Claude Code\工具\stock_technical_analysis.py`

### 使用方法
```bash
python stock_technical_analysis.py 002460   # 自动识别沪深
python stock_technical_analysis.py sh600519 # 沪市
python stock_technical_analysis.py sz002460 # 深市
```

### 输出指标
| 指标 | 参数 |
|------|------|
| MACD | (12, 26, 9) |
| KDJ | (23, 3, 3) |
| RSI | (6, 14, 24) |
| 布林带 | (11, 3) |
| MA | 5/10/20/30 均线 |

### 也可调用 API（云服务器）

```bash
# 实时行情（腾讯财经，无需认证）
curl https://qt.gtimg.cn/q=sz002460

# K 线数据（新浪财经）
curl "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz002460&scale=240&ma=no&datalen=60"
```

---

## 七、Skills 索引

处理数据相关任务时，按需调用：

| 场景 | 调用 |
|------|------|
| Excel 数据处理 | `minimax-xlsx` 或 Anthropic `xlsx` |
| 数据全流程分析 | `pandas-skill` |
| 股票/金融数据 | 云服务器脚本 |
| 生成分析报告 | `minimax-docx` 导出 Word |
| 生成图表 PPT | `minimax-pptx` |

---

## 八、典型任务模板

### 任务：分析 CSV 文件并生成报告
```
1. 读取数据 → pd.read_csv()
2. 清洗数据 → dropna / fillna / drop_duplicates
3. 统计分析 → df.describe() / corr()
4. 可视化 → matplotlib / seaborn
5. 导出报告 → df.to_excel() / to_word()
```

### 任务：实时分析股票
```
1. SSH 到云服务器（106.54.25.161）
2. 运行：python3 /tmp/stock_technical_analysis.py [代码]
3. 查看 MACD/KDJ/RSI/布林带输出
```

### 任务：对比两只股票
```
分别在云服务器运行两个代码，对比输出指标。
```

---

## 九、常见问题

**Q: 图表中文字体显示乱码？**
```python
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False
```

**Q: 读取大文件内存不够？**
```python
# 分块读取
for chunk in pd.read_csv("big.csv", chunksize=10000):
    process(chunk)
```

**Q: 怎么加速 pandas？**
```python
# 用 pyarrow 引擎
df = pd.read_csv("file.csv", engine="pyarrow")

# 或者安装 pyarrow
pip install pyarrow
```
