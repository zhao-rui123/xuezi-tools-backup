# 数据分析快速使用指南（OpenClaw 用）

## 一、 环境检查

```bash
python --version  # 确认 Python 3.12+
pip list | grep -E "pandas|matplotlib|seaborn|scipy|statsmodels|sklearn"
```

如需安装：
```bash
pip install pandas matplotlib seaborn scipy statsmodels scikit-learn openpyxl
```

---

## 二、 常见任务

### 任务 1：读取 CSV / Excel 文件
```python
import pandas as pd

df = pd.read_csv("data.csv")
df = pd.read_excel("data.xlsx", sheet_name="Sheet1")
```

### 任务 2：数据清洗
```python
df.dropna()                      # 删除空值行
df.fillna(0)                     # 用0填充空值
df.drop_duplicates()              # 删除重复行
df["日期"] = pd.to_datetime(df["日期"])  # 类型转换
```

### 任务 3：统计分析
```python
df.describe()                     # 描述统计
df.corr()                         # 相关性矩阵

from scipy import stats
stats.ttest_ind(a, b)            # t检验
stats.pearsonr(x, y)              # 相关性检验
```

### 任务 4：可视化
```python
import matplotlib.pyplot as plt
import seaborn as sns

# 折线图
plt.plot(x, y); plt.savefig("output.png")

# 热力图
sns.heatmap(df.corr(), annot=True, cmap="coolwarm")

# 分布图
sns.histplot(df["金额"], kde=True)
```

### 任务 5：机器学习
```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, mean_squared_error

# 回归
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = LinearRegression().fit(X_train, y_train)
y_pred = model.predict(X_test)

# 分类
clf = RandomForestClassifier(n_estimators=100).fit(X_train, y_train)
accuracy_score(y_test, clf.predict(X_test))
```

### 任务 6：股票技术分析
```bash
# 云服务器执行
ssh -i ~/.ssh/id_ed25519 root@106.54.25.161
python3 /tmp/stock_technical_analysis.py 002460   # 自动识别沪深
python3 /tmp/stock_technical_analysis.py sh600519  # 沪市
```

本地直接运行脚本：
```bash
python D:/Claude\ Code/工具/stock_technical_analysis.py 002460
```

输出：MACD(12,26,9)、KDJ(23,3,3)、RSI(6,14,24)、布林带(11,3)、MA5/10/20/30

---

## 三、 Skills 调用索引

| 场景 | 调用技能 |
|------|---------|
| Excel 数据处理 | `minimax-xlsx` 或 Anthropic `xlsx` |
| 数据全流程分析 | `pandas-skill` |
| Word 文档生成 | `minimax-docx` |
| PDF 处理 | `minimax-pdf` |
| 股票技术分析 | 云服务器脚本（见上） |

---

## 四、 注意事项

1. **中文字体**：图表中文字体设置
   ```python
   import matplotlib
   matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
   matplotlib.rcParams['axes.unicode_minus'] = False
   ```

2. **大文件分块读取**
   ```python
   for chunk in pd.read_csv("big.csv", chunksize=10000):
       process(chunk)
   ```

3. **加速 pandas**
   ```python
   pip install pyarrow
   df = pd.read_csv("file.csv", engine="pyarrow")
   ```

---

## 五、 云服务器股票数据源

- **实时行情**：`curl https://qt.gtimg.cn/q=sz002460`
- **K 线数据**：`curl "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz002460&scale=240&ma=no&datalen=60"`
- **技术分析脚本**：`/tmp/stock_technical_analysis.py`（已上传）
