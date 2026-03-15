"""
安全的示例技能包
================

这是一个符合安全规范的示例技能包。
"""

__version__ = "1.0.0"


def process_data(data: str) -> str:
    """
    安全地处理数据
    
    Args:
        data: 输入数据
        
    Returns:
        处理后的数据
    """
    # 使用安全的字符串操作
    if data is None:
        return ""
    
    # 输入验证
    if not isinstance(data, str):
        raise ValueError("数据必须是字符串类型")
    
    # 安全处理
    result = data.strip().lower()
    return result


def read_config(config_path: str) -> dict:
    """
    安全地读取配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    import json
    from pathlib import Path
    
    # 验证路径
    config_file = Path(config_path)
    
    # 检查文件是否存在
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    # 检查是否是文件
    if not config_file.is_file():
        raise ValueError(f"路径不是文件: {config_path}")
    
    # 安全读取
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config


def safe_api_call(endpoint: str, params: dict = None) -> dict:
    """
    安全地进行API调用
    
    Args:
        endpoint: API端点
        params: 请求参数
        
    Returns:
        API响应
    """
    import requests
    from urllib.parse import urlparse
    
    # 验证URL
    parsed = urlparse(endpoint)
    if parsed.scheme not in ['http', 'https']:
        raise ValueError("只支持HTTP/HTTPS协议")
    
    # 使用参数化请求
    response = requests.get(
        endpoint,
        params=params,
        timeout=30,
        verify=True  # 验证SSL证书
    )
    
    response.raise_for_status()
    return response.json()


class DataProcessor:
    """安全的数据处理器"""
    
    def __init__(self, config: dict = None):
        """
        初始化处理器
        
        Args:
            config: 配置字典
        """
        # 使用不可变默认值
        self.config = config or {}
        self._data = []
    
    def add_item(self, item: str) -> None:
        """
        添加数据项
        
        Args:
            item: 数据项
        """
        if not isinstance(item, str):
            raise TypeError("数据项必须是字符串")
        
        self._data.append(item)
    
    def get_items(self) -> list:
        """
        获取所有数据项
        
        Returns:
            数据项列表
        """
        # 返回副本，防止外部修改
        return self._data.copy()
    
    def clear(self) -> None:
        """清空数据"""
        self._data.clear()


# 模块级别常量（不可变）
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
ALLOWED_SCHEMES = ('http', 'https')
