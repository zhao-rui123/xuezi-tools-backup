# 股票月线趋势筛选工具配置

# 技术指标参数
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

KDJ_N = 23
KDJ_M1 = 3
KDJ_M2 = 3

# 均线周期
MA_PERIODS = [5, 10, 20]

# 筛选条件
VOLUME_RATIO = 1.2  # 成交量放大倍数
KDJ_BUY_ZONE = 50   # KDJ买入区域上限

# 数据获取
MAX_STOCKS = None  # None表示全部股票，可设置为数字限制数量

# 输出
OUTPUT_DIR = "output"
OUTPUT_FORMAT = "json"  # json 或 csv