"""
股票筛选系统v2 - 配置文件
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# 加载.env文件
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)


@dataclass
class MACDConfig:
    """MACD指标参数"""
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9


@dataclass
class KDJConfig:
    """KDJ指标参数"""
    n: int = 23
    m1: int = 3
    m2: int = 3


@dataclass
class VolumeConfig:
    """成交量放大检测配置"""
    multiplier: float = 1.5
    lookback_days: int = 20


@dataclass
class DongfangCaiwuConfig:
    """东方财富API配置"""
    api_key: str = "mkt_zdTwvCWmIr9g4mHoM8sOsaK8M_ffrhinQPP-GAkhTNs"
    base_url: str = "https://mkapi2.dfcfs.com/finskillshub/api/claw"
    
    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv("DONGFANG_CAIWU_API_KEY", self.api_key)


@dataclass
class FeishuConfig:
    """飞书配置"""
    webhook_url: Optional[str] = None
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    chat_id: str = "oc_8ede204246201b4407dfeed8326df7c9"
    
    def __post_init__(self):
        if not self.webhook_url:
            self.webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
        if not self.app_id:
            self.app_id = os.getenv("FEISHU_APP_ID")
        if not self.app_secret:
            self.app_secret = os.getenv("FEISHU_APP_SECRET")
        if not self.chat_id:
            self.chat_id = os.getenv("FEISHU_CHAT_ID", self.chat_id)


class Config:
    """全局配置"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    
    MACD = MACDConfig()
    KDJ = KDJConfig()
    VOLUME = VolumeConfig()
    DONGFANG_CAIWU = DongfangCaiwuConfig()
    DONGFANG_CAIWU_API_KEY = DONGFANG_CAIWU.api_key
    FEISHU = FeishuConfig()
    FEISHU_APP_ID = FEISHU.app_id or os.getenv("FEISHU_APP_ID", "")
    FEISHU_APP_SECRET = FEISHU.app_secret or os.getenv("FEISHU_APP_SECRET", "")
    FEISHU_CHAT_ID = FEISHU.chat_id
    SCHEDULE_HOUR = 20
    SCHEDULE_MINUTE = 0
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    EASTMONEY_API_TIMEOUT = 30
    EASTMONEY_RETRY_TIMES = 3
    STOCK_LIST_CACHE_TTL = 3600
    MONTHLY_DATA_MONTHS = 36
    WEEKLY_DATA_WEEKS = 104
    RATING_LEVELS = {"A": "强烈推荐", "B": "推荐", "C": "关注", "D": "观望"}
    LOG_LEVEL = "INFO"


# 模块级常量
GRADE_A = "A"
GRADE_B = "B"
GRADE_C = "C"
MAX_STOCKS_PER_RUN = 100
MIN_VOLUME_RATIO = 1.5


# 全局配置实例
config = Config()
settings = config


# K线周期映射
PERIOD_MAP = {
    "daily": "101",    # 日K
    "weekly": "102",   # 周K
    "monthly": "103",  # 月K
}
