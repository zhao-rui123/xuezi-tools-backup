"""
数据格式化模块

提供全面的数据格式化功能，包括:
- 数据类型格式化
- 日期时间格式化
- 数值格式化
- 货币格式化
- 百分比格式化
- 自定义格式化
- 多格式输出
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, date, time
from decimal import Decimal, ROUND_HALF_UP
import base64
import io

# 设置日志
logger = logging.getLogger("openclaw.utils.formatter")


@dataclass
class FormatOptions:
    """格式化选项"""
    date_format: str = "%Y-%m-%d"
    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    time_format: str = "%H:%M:%S"
    number_decimal_places: int = 2
    number_thousands_separator: str = ","
    number_decimal_separator: str = "."
    currency_symbol: str = "¥"
    currency_position: str = "before"  # before, after
    percentage_decimal_places: int = 2
    percentage_symbol: str = "%"
    null_value: str = ""
    true_value: str = "是"
    false_value: str = "否"


class DataFormatter:
    """
    数据格式化器
    
    提供全面的数据格式化功能。
    
    Example:
        >>> from openclaw import DataFormatter, FormatOptions
        >>> options = FormatOptions(date_format="%Y/%m/%d", currency_symbol="$")
        >>> formatter = DataFormatter(options)
        >>> 
        >>> # 格式化数值
        >>> formatter.format_number(1234567.89)
        '1,234,567.89'
        >>> 
        >>> # 格式化货币
        >>> formatter.format_currency(1234.56)
        '$1,234.56'
        >>> 
        >>> # 格式化日期
        >>> formatter.format_date(datetime.now())
        '2024/01/15'
        
        >>> # 格式化DataFrame
        >>> df_formatted = formatter.format_dataframe(df)
    """
    
    def __init__(self, options: Optional[FormatOptions] = None):
        """
        初始化格式化器
        
        Args:
            options: 格式化选项
        """
        self.options = options or FormatOptions()
        self.logger = logging.getLogger("openclaw.utils.formatter")
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """检查依赖库"""
        try:
            import pandas as pd
            self.pandas = pd
        except ImportError:
            self.logger.warning("pandas未安装，DataFrame格式化功能受限")
            self.pandas = None
    
    def format_value(self, value: Any, data_type: Optional[str] = None) -> str:
        """
        格式化单个值
        
        Args:
            value: 要格式化的值
            data_type: 数据类型（自动检测如果为None）
        
        Returns:
            格式化后的字符串
        """
        if value is None:
            return self.options.null_value
        
        # 自动检测类型
        if data_type is None:
            data_type = self._detect_type(value)
        
        # 根据类型格式化
        if data_type == "date":
            return self.format_date(value)
        elif data_type == "datetime":
            return self.format_datetime(value)
        elif data_type == "time":
            return self.format_time(value)
        elif data_type == "integer":
            return self.format_integer(value)
        elif data_type == "float":
            return self.format_number(value)
        elif data_type == "currency":
            return self.format_currency(value)
        elif data_type == "percentage":
            return self.format_percentage(value)
        elif data_type == "boolean":
            return self.format_boolean(value)
        else:
            return str(value)
    
    def _detect_type(self, value: Any) -> str:
        """检测数据类型"""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, (int,))):
            return "integer"
        elif isinstance(value, (float, Decimal)):
            return "float"
        elif isinstance(value, datetime):
            return "datetime"
        elif isinstance(value, date):
            return "date"
        elif isinstance(value, time):
            return "time"
        else:
            return "string"
    
    def format_date(self, value: Union[date, datetime, str]) -> str:
        """
        格式化日期
        
        Args:
            value: 日期值
        
        Returns:
            格式化后的日期字符串
        """
        if value is None:
            return self.options.null_value
        
        if isinstance(value, str):
            try:
                # 尝试解析常见格式
                for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]:
                    try:
                        value = datetime.strptime(value, fmt).date()
                        break
                    except:
                        continue
                else:
                    return value
            except:
                return value
        
        if isinstance(value, datetime):
            value = value.date()
        
        return value.strftime(self.options.date_format)
    
    def format_datetime(self, value: Union[datetime, str]) -> str:
        """
        格式化日期时间
        
        Args:
            value: 日期时间值
        
        Returns:
            格式化后的日期时间字符串
        """
        if value is None:
            return self.options.null_value
        
        if isinstance(value, str):
            try:
                # 尝试解析ISO格式
                value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except:
                return value
        
        return value.strftime(self.options.datetime_format)
    
    def format_time(self, value: Union[time, datetime, str]) -> str:
        """
        格式化时间
        
        Args:
            value: 时间值
        
        Returns:
            格式化后的时间字符串
        """
        if value is None:
            return self.options.null_value
        
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, "%H:%M:%S").time()
            except:
                return value
        
        if isinstance(value, datetime):
            value = value.time()
        
        return value.strftime(self.options.time_format)
    
    def format_number(
        self,
        value: Union[int, float, Decimal, str],
        decimal_places: Optional[int] = None,
    ) -> str:
        """
        格式化数值
        
        Args:
            value: 数值
            decimal_places: 小数位数
        
        Returns:
            格式化后的数值字符串
        """
        if value is None:
            return self.options.null_value
        
        try:
            num = Decimal(str(value))
        except:
            return str(value)
        
        decimal_places = decimal_places or self.options.number_decimal_places
        
        # 四舍五入
        quantize_str = "0." + "0" * decimal_places
        num = num.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)
        
        # 格式化
        parts = str(num).split(".")
        integer_part = parts[0]
        
        # 添加千位分隔符
        if self.options.number_thousands_separator:
            integer_part = "{:,}".format(int(integer_part)).replace(",", self.options.number_thousands_separator)
        
        if len(parts) > 1 and decimal_places > 0:
            return integer_part + self.options.number_decimal_separator + parts[1]
        else:
            return integer_part
    
    def format_integer(self, value: Union[int, str]) -> str:
        """
        格式化整数
        
        Args:
            value: 整数值
        
        Returns:
            格式化后的整数字符串
        """
        return self.format_number(value, decimal_places=0)
    
    def format_currency(
        self,
        value: Union[int, float, Decimal, str],
        symbol: Optional[str] = None,
    ) -> str:
        """
        格式化货币
        
        Args:
            value: 数值
            symbol: 货币符号
        
        Returns:
            格式化后的货币字符串
        """
        if value is None:
            return self.options.null_value
        
        symbol = symbol or self.options.currency_symbol
        formatted = self.format_number(value)
        
        if self.options.currency_position == "before":
            return symbol + formatted
        else:
            return formatted + symbol
    
    def format_percentage(
        self,
        value: Union[int, float, Decimal, str],
        decimal_places: Optional[int] = None,
    ) -> str:
        """
        格式化百分比
        
        Args:
            value: 数值（0.25表示25%）
            decimal_places: 小数位数
        
        Returns:
            格式化后的百分比字符串
        """
        if value is None:
            return self.options.null_value
        
        try:
            num = float(value) * 100
        except:
            return str(value)
        
        decimal_places = decimal_places or self.options.percentage_decimal_places
        formatted = self.format_number(num, decimal_places)
        
        return formatted + self.options.percentage_symbol
    
    def format_boolean(self, value: Any) -> str:
        """
        格式化布尔值
        
        Args:
            value: 布尔值
        
        Returns:
            格式化后的布尔字符串
        """
        if value is None:
            return self.options.null_value
        
        if isinstance(value, str):
            value = value.lower() in ("true", "1", "yes", "是", "y", "t")
        
        return self.options.true_value if value else self.options.false_value
    
    def format_dataframe(
        self,
        df: Any,
        column_formats: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        格式化DataFrame
        
        Args:
            df: pandas DataFrame
            column_formats: 列格式化规则 {列名: 格式类型}
        
        Returns:
            格式化后的DataFrame
        """
        if not self.pandas or not isinstance(df, self.pandas.DataFrame):
            raise TypeError("需要pandas DataFrame")
        
        df_formatted = df.copy()
        column_formats = column_formats or {}
        
        for col in df_formatted.columns:
            format_type = column_formats.get(col)
            
            # 自动检测格式类型
            if not format_type:
                if df_formatted[col].dtype in ["int64"]:
                    format_type = "integer"
                elif df_formatted[col].dtype in ["float64"]:
                    format_type = "float"
                elif df_formatted[col].dtype == "datetime64[ns]":
                    format_type = "datetime"
                elif df_formatted[col].dtype == "bool":
                    format_type = "boolean"
            
            # 应用格式化
            if format_type:
                df_formatted[col] = df_formatted[col].apply(
                    lambda x: self.format_value(x, format_type)
                )
        
        return df_formatted
    
    def to_json(
        self,
        data: Any,
        indent: int = 2,
        ensure_ascii: bool = False,
        date_format: str = "iso",
    ) -> str:
        """
        转换为JSON字符串
        
        Args:
            data: 数据
            indent: 缩进空格数
            ensure_ascii: 是否转义非ASCII字符
            date_format: 日期格式
        
        Returns:
            JSON字符串
        """
        def json_serial(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            if isinstance(obj, Decimal):
                return float(obj)
            raise TypeError(f"类型 {type(obj)} 无法序列化")
        
        return json.dumps(
            data,
            indent=indent,
            ensure_ascii=ensure_ascii,
            default=json_serial,
        )
    
    def to_csv(
        self,
        df: Any,
        file_path: Optional[Union[str, Path]] = None,
        encoding: str = "utf-8-sig",
        index: bool = False,
        **kwargs,
    ) -> Optional[str]:
        """
        转换为CSV
        
        Args:
            df: pandas DataFrame
            file_path: 输出文件路径
            encoding: 编码
            index: 是否包含索引
            **kwargs: 其他pandas to_csv参数
        
        Returns:
            如果file_path为None，返回CSV字符串
        """
        if not self.pandas or not isinstance(df, self.pandas.DataFrame):
            raise TypeError("需要pandas DataFrame")
        
        if file_path:
            df.to_csv(file_path, encoding=encoding, index=index, **kwargs)
            return None
        else:
            return df.to_csv(encoding=encoding, index=index, **kwargs)
    
    def to_excel(
        self,
        df: Any,
        file_path: Union[str, Path],
        sheet_name: str = "Sheet1",
        index: bool = False,
        **kwargs,
    ) -> None:
        """
        转换为Excel
        
        Args:
            df: pandas DataFrame
            file_path: 输出文件路径
            sheet_name: 工作表名称
            index: 是否包含索引
            **kwargs: 其他pandas to_excel参数
        """
        if not self.pandas or not isinstance(df, self.pandas.DataFrame):
            raise TypeError("需要pandas DataFrame")
        
        df.to_excel(file_path, sheet_name=sheet_name, index=index, **kwargs)
    
    def to_markdown(
        self,
        df: Any,
        index: bool = False,
    ) -> str:
        """
        转换为Markdown表格
        
        Args:
            df: pandas DataFrame
            index: 是否包含索引
        
        Returns:
            Markdown表格字符串
        """
        if not self.pandas or not isinstance(df, self.pandas.DataFrame):
            raise TypeError("需要pandas DataFrame")
        
        return df.to_markdown(index=index)
    
    def to_html(
        self,
        df: Any,
        index: bool = False,
        classes: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        转换为HTML表格
        
        Args:
            df: pandas DataFrame
            index: 是否包含索引
            classes: CSS类名
            **kwargs: 其他pandas to_html参数
        
        Returns:
            HTML表格字符串
        """
        if not self.pandas or not isinstance(df, self.pandas.DataFrame):
            raise TypeError("需要pandas DataFrame")
        
        return df.to_html(index=index, classes=classes, **kwargs)
    
    def encode_base64(self, value: Union[str, bytes]) -> str:
        """
        Base64编码
        
        Args:
            value: 要编码的值
        
        Returns:
            Base64编码字符串
        """
        if isinstance(value, str):
            value = value.encode("utf-8")
        return base64.b64encode(value).decode("utf-8")
    
    def decode_base64(self, value: str) -> bytes:
        """
        Base64解码
        
        Args:
            value: Base64编码字符串
        
        Returns:
            解码后的字节
        """
        return base64.b64decode(value)
