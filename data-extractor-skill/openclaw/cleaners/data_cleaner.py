"""
数据清洗与整理模块

提供全面的数据清洗功能，包括:
- 重复数据处理
- 缺失值处理
- 数据类型转换
- 文本清洗
- 异常值检测与处理
- 数据标准化
- 数据格式化
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, Set
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, date
import unicodedata

import numpy as np

# 设置日志
logger = logging.getLogger("openclaw.cleaners")


@dataclass
class CleaningReport:
    """清洗报告"""
    rows_before: int = 0
    rows_after: int = 0
    columns_before: int = 0
    columns_after: int = 0
    duplicates_removed: int = 0
    missing_values_filled: Dict[str, int] = field(default_factory=dict)
    missing_values_dropped: int = 0
    outliers_detected: int = 0
    outliers_removed: int = 0
    type_conversions: Dict[str, str] = field(default_factory=dict)
    text_cleaning_applied: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "rows": {
                "before": self.rows_before,
                "after": self.rows_after,
                "removed": self.rows_before - self.rows_after,
            },
            "columns": {
                "before": self.columns_before,
                "after": self.columns_after,
            },
            "duplicates_removed": self.duplicates_removed,
            "missing_values": {
                "filled": self.missing_values_filled,
                "dropped": self.missing_values_dropped,
            },
            "outliers": {
                "detected": self.outliers_detected,
                "removed": self.outliers_removed,
            },
            "type_conversions": self.type_conversions,
            "text_cleaning": self.text_cleaning_applied,
            "warnings": self.warnings,
        }


class DataCleaner:
    """
    数据清洗器
    
    提供全面的数据清洗功能，支持多种数据格式。
    
    Example:
        >>> from openclaw import DataCleaner, Config
        >>> cleaner = DataCleaner(Config().cleaning)
        >>> 
        >>> # 清洗DataFrame
        >>> df_cleaned = cleaner.clean_dataframe(df)
        >>> 
        >>> # 清洗字典列表
        >>> data_cleaned = cleaner.clean_records(records)
        >>> 
        >>> # 获取清洗报告
        >>> report = cleaner.get_report()
        >>> print(report.to_dict())
        
        >>> # 手动应用特定清洗
        >>> df_no_dup = cleaner.remove_duplicates(df)
        >>> df_filled = cleaner.fill_missing(df, strategy="mean")
    """
    
    def __init__(self, config=None):
        """
        初始化数据清洗器
        
        Args:
            config: DataCleaningConfig配置对象
        """
        self.config = config
        self.logger = logging.getLogger("openclaw.cleaners")
        self.report = CleaningReport()
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """检查依赖库"""
        try:
            import pandas as pd
            self.pandas = pd
        except ImportError:
            self.logger.warning("pandas未安装，DataFrame清洗功能受限")
            self.pandas = None
        
        try:
            import numpy as np
            self.numpy = np
        except ImportError:
            self.logger.warning("numpy未安装，数值处理功能受限")
            self.numpy = None
    
    def clean_dataframe(self, df: Any, **kwargs) -> Any:
        """
        清洗DataFrame
        
        Args:
            df: pandas DataFrame
            **kwargs: 额外的清洗参数
        
        Returns:
            清洗后的DataFrame
        """
        if not self.pandas:
            raise RuntimeError("pandas未安装，无法清洗DataFrame")
        
        if not isinstance(df, self.pandas.DataFrame):
            raise TypeError("输入必须是pandas DataFrame")
        
        # 重置报告
        self.report = CleaningReport()
        self.report.rows_before = len(df)
        self.report.columns_before = len(df.columns)
        
        self.logger.info(f"开始清洗数据: {self.report.rows_before}行 x {self.report.columns_before}列")
        
        # 复制数据避免修改原始数据
        df_cleaned = df.copy()
        
        # 1. 去除重复行
        if self._get_config("remove_duplicates", kwargs, True):
            df_cleaned = self._remove_duplicates_df(df_cleaned, **kwargs)
        
        # 2. 处理缺失值
        if self._get_config("handle_missing", kwargs, True):
            df_cleaned = self._handle_missing_df(df_cleaned, **kwargs)
        
        # 3. 数据类型转换
        if self._get_config("auto_convert_types", kwargs, True):
            df_cleaned = self._convert_types_df(df_cleaned, **kwargs)
        
        # 4. 文本清洗
        if self._get_config("strip_whitespace", kwargs, True):
            df_cleaned = self._clean_text_df(df_cleaned, **kwargs)
        
        # 5. 异常值处理
        if self._get_config("handle_outliers", kwargs, False):
            df_cleaned = self._handle_outliers_df(df_cleaned, **kwargs)
        
        # 更新报告
        self.report.rows_after = len(df_cleaned)
        self.report.columns_after = len(df_cleaned.columns)
        
        self.logger.info(f"清洗完成: {self.report.rows_after}行 x {self.report.columns_after}列")
        
        return df_cleaned
    
    def clean_records(
        self,
        records: List[Dict[str, Any]],
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        清洗字典记录列表
        
        Args:
            records: 字典列表
            **kwargs: 额外的清洗参数
        
        Returns:
            清洗后的记录列表
        """
        if not records:
            return []
        
        if self.pandas:
            # 转换为DataFrame清洗后再转回
            df = self.pandas.DataFrame(records)
            df_cleaned = self.clean_dataframe(df, **kwargs)
            return df_cleaned.to_dict("records")
        else:
            # 手动清洗
            return self._clean_records_manual(records, **kwargs)
    
    def _clean_records_manual(
        self,
        records: List[Dict[str, Any]],
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """手动清洗记录（无pandas时）"""
        cleaned = []
        seen = set()
        
        for record in records:
            # 清洗每个字段
            cleaned_record = {}
            for key, value in record.items():
                # 文本清洗
                if isinstance(value, str):
                    value = self._clean_text(value)
                cleaned_record[key] = value
            
            # 去重检查
            if self._get_config("remove_duplicates", kwargs, True):
                record_tuple = tuple(sorted(cleaned_record.items()))
                if record_tuple in seen:
                    continue
                seen.add(record_tuple)
            
            cleaned.append(cleaned_record)
        
        return cleaned
    
    def _get_config(self, key: str, kwargs: Dict, default: Any) -> Any:
        """获取配置值"""
        if key in kwargs:
            return kwargs[key]
        if self.config and hasattr(self.config, key):
            return getattr(self.config, key)
        return default
    
    def _remove_duplicates_df(self, df: Any, **kwargs) -> Any:
        """去除DataFrame重复行"""
        subset = kwargs.get("subset") or (self.config.duplicate_subset if self.config else None)
        keep = kwargs.get("keep") or (self.config.keep if self.config else "first")
        
        rows_before = len(df)
        df_cleaned = df.drop_duplicates(subset=subset, keep=keep)
        rows_after = len(df_cleaned)
        
        self.report.duplicates_removed = rows_before - rows_after
        
        if self.report.duplicates_removed > 0:
            self.logger.info(f"去除重复行: {self.report.duplicates_removed}行")
        
        return df_cleaned
    
    def _handle_missing_df(self, df: Any, **kwargs) -> Any:
        """处理DataFrame缺失值"""
        strategy = kwargs.get("missing_strategy") or (self.config.missing_strategy if self.config else "auto")
        fill_value = kwargs.get("fill_value") or (self.config.fill_value if self.config else None)
        
        if strategy == "auto":
            # 自动策略：数值列用中位数，文本列用众数
            for col in df.columns:
                if df[col].isna().sum() > 0:
                    missing_count = df[col].isna().sum()
                    
                    if df[col].dtype in ["int64", "float64"]:
                        fill_val = df[col].median()
                        df[col] = df[col].fillna(fill_val)
                        self.report.missing_values_filled[col] = missing_count
                    else:
                        mode_val = df[col].mode()
                        if len(mode_val) > 0:
                            df[col] = df[col].fillna(mode_val[0])
                            self.report.missing_values_filled[col] = missing_count
        
        elif strategy == "drop":
            rows_before = len(df)
            df = df.dropna()
            rows_after = len(df)
            self.report.missing_values_dropped = rows_before - rows_after
            
            if self.report.missing_values_dropped > 0:
                self.logger.info(f"删除缺失值行: {self.report.missing_values_dropped}行")
        
        elif strategy == "fill":
            if fill_value is not None:
                for col in df.columns:
                    missing_count = df[col].isna().sum()
                    if missing_count > 0:
                        df[col] = df[col].fillna(fill_value)
                        self.report.missing_values_filled[col] = missing_count
            else:
                # 使用列的均值/中位数/众数
                for col in df.columns:
                    missing_count = df[col].isna().sum()
                    if missing_count > 0:
                        if df[col].dtype in ["int64", "float64"]:
                            df[col] = df[col].fillna(df[col].median())
                        else:
                            mode_val = df[col].mode()
                            if len(mode_val) > 0:
                                df[col] = df[col].fillna(mode_val[0])
                        self.report.missing_values_filled[col] = missing_count
        
        elif strategy == "interpolate":
            # 仅对数值列进行插值
            numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
            for col in numeric_cols:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    df[col] = df[col].interpolate(method="linear")
                    self.report.missing_values_filled[col] = missing_count
        
        return df
    
    def _convert_types_df(self, df: Any, **kwargs) -> Any:
        """转换DataFrame数据类型"""
        date_columns = kwargs.get("date_columns") or (self.config.date_columns if self.config else None)
        numeric_columns = kwargs.get("numeric_columns") or (self.config.numeric_columns if self.config else None)
        
        for col in df.columns:
            # 尝试转换为数值类型
            if numeric_columns and col in numeric_columns:
                df[col] = self.pandas.to_numeric(df[col], errors="ignore")
                self.report.type_conversions[col] = "numeric"
            
            # 尝试转换为日期类型
            elif date_columns and col in date_columns:
                df[col] = self.pandas.to_datetime(df[col], errors="ignore")
                self.report.type_conversions[col] = "datetime"
            
            # 自动检测
            else:
                # 尝试转换为数值
                if df[col].dtype == "object":
                    try:
                        converted = self.pandas.to_numeric(df[col], errors="coerce")
                        if converted.notna().sum() / len(df) > 0.8:  # 80%以上成功转换
                            df[col] = converted
                            self.report.type_conversions[col] = "numeric"
                            continue
                    except:
                        pass
                    
                    # 尝试转换为日期
                    try:
                        converted = self.pandas.to_datetime(df[col], errors="coerce")
                        if converted.notna().sum() / len(df) > 0.8:
                            df[col] = converted
                            self.report.type_conversions[col] = "datetime"
                    except:
                        pass
        
        return df
    
    def _clean_text_df(self, df: Any, **kwargs) -> Any:
        """清洗DataFrame文本列"""
        strip_whitespace = self._get_config("strip_whitespace", kwargs, True)
        normalize_unicode = self._get_config("normalize_unicode", kwargs, True)
        remove_control_chars = self._get_config("remove_control_chars", kwargs, True)
        
        text_cleaning = []
        
        for col in df.columns:
            if df[col].dtype == "object":
                # 去除空白
                if strip_whitespace:
                    df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
                    text_cleaning.append("strip_whitespace")
                
                # Unicode规范化
                if normalize_unicode:
                    df[col] = df[col].apply(lambda x: self._normalize_unicode(x) if isinstance(x, str) else x)
                    text_cleaning.append("normalize_unicode")
                
                # 去除控制字符
                if remove_control_chars:
                    df[col] = df[col].apply(lambda x: self._remove_control_chars(x) if isinstance(x, str) else x)
                    text_cleaning.append("remove_control_chars")
        
        self.report.text_cleaning_applied = list(set(text_cleaning))
        
        return df
    
    def _handle_outliers_df(self, df: Any, **kwargs) -> Any:
        """处理DataFrame异常值"""
        method = kwargs.get("outlier_method") or (self.config.outlier_method if self.config else "iqr")
        threshold = kwargs.get("outlier_threshold") or (self.config.outlier_threshold if self.config else 3.0)
        
        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
        
        outlier_mask = self.pandas.Series([False] * len(df))
        
        for col in numeric_cols:
            if method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                col_outliers = (df[col] < lower) | (df[col] > upper)
                outlier_mask = outlier_mask | col_outliers
            
            elif method == "zscore":
                if self.numpy:
                    z_scores = self.numpy.abs((df[col] - df[col].mean()) / df[col].std())
                    col_outliers = z_scores > threshold
                    outlier_mask = outlier_mask | col_outliers
        
        self.report.outliers_detected = outlier_mask.sum()
        
        if self.report.outliers_detected > 0:
            self.logger.info(f"检测到异常值: {self.report.outliers_detected}行")
            df = df[~outlier_mask]
            self.report.outliers_removed = self.report.outliers_detected
        
        return df
    
    def _clean_text(self, text: str) -> str:
        """清洗单个文本"""
        if not isinstance(text, str):
            return text
        
        # 去除首尾空白
        text = text.strip()
        
        # Unicode规范化
        text = self._normalize_unicode(text)
        
        # 去除控制字符
        text = self._remove_control_chars(text)
        
        return text
    
    def _normalize_unicode(self, text: str) -> str:
        """Unicode规范化"""
        if not isinstance(text, str):
            return text
        return unicodedata.normalize("NFKC", text)
    
    def _remove_control_chars(self, text: str) -> str:
        """去除控制字符"""
        if not isinstance(text, str):
            return text
        # 保留换行符和制表符，去除其他控制字符
        return "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in "\n\t\r")
    
    def remove_duplicates(self, data: Any, **kwargs) -> Any:
        """
        去除重复数据
        
        Args:
            data: DataFrame或记录列表
            **kwargs: 额外参数
        
        Returns:
            去重后的数据
        """
        if self.pandas and isinstance(data, self.pandas.DataFrame):
            return self._remove_duplicates_df(data, **kwargs)
        elif isinstance(data, list):
            return self._clean_records_manual(data, **kwargs)
        else:
            raise TypeError("不支持的数据类型")
    
    def fill_missing(
        self,
        data: Any,
        strategy: str = "mean",
        fill_value: Any = None,
        **kwargs,
    ) -> Any:
        """
        填充缺失值
        
        Args:
            data: DataFrame或记录列表
            strategy: 填充策略 (mean, median, mode, constant, forward, backward)
            fill_value: 固定填充值（strategy=constant时使用）
            **kwargs: 额外参数
        
        Returns:
            填充后的数据
        """
        if not self.pandas or not isinstance(data, self.pandas.DataFrame):
            raise TypeError("需要pandas DataFrame")
        
        df = data.copy()
        
        for col in df.columns:
            if df[col].isna().sum() > 0:
                if strategy == "mean" and df[col].dtype in ["int64", "float64"]:
                    df[col] = df[col].fillna(df[col].mean())
                elif strategy == "median" and df[col].dtype in ["int64", "float64"]:
                    df[col] = df[col].fillna(df[col].median())
                elif strategy == "mode":
                    mode_val = df[col].mode()
                    if len(mode_val) > 0:
                        df[col] = df[col].fillna(mode_val[0])
                elif strategy == "constant":
                    df[col] = df[col].fillna(fill_value)
                elif strategy == "forward":
                    df[col] = df[col].fillna(method="ffill")
                elif strategy == "backward":
                    df[col] = df[col].fillna(method="bfill")
        
        return df
    
    def standardize_column_names(self, df: Any, **kwargs) -> Any:
        """
        标准化列名
        
        Args:
            df: DataFrame
            **kwargs: 额外参数
        
        Returns:
            标准化后的DataFrame
        """
        if not self.pandas or not isinstance(df, self.pandas.DataFrame):
            raise TypeError("需要pandas DataFrame")
        
        df = df.copy()
        
        new_columns = []
        for col in df.columns:
            # 转换为字符串
            col_str = str(col)
            
            # 去除空白
            col_str = col_str.strip()
            
            # 替换特殊字符
            col_str = re.sub(r"[^\w\s]", "_", col_str)
            
            # 替换空格
            col_str = re.sub(r"\s+", "_", col_str)
            
            # 小写
            col_str = col_str.lower()
            
            new_columns.append(col_str)
        
        df.columns = new_columns
        return df
    
    def detect_data_types(self, df: Any) -> Dict[str, str]:
        """
        检测每列的数据类型
        
        Args:
            df: DataFrame
        
        Returns:
            列名到数据类型的映射
        """
        if not self.pandas or not isinstance(df, self.pandas.DataFrame):
            raise TypeError("需要pandas DataFrame")
        
        type_mapping = {}
        
        for col in df.columns:
            if df[col].dtype in ["int64", "float64"]:
                type_mapping[col] = "numeric"
            elif df[col].dtype == "datetime64[ns]":
                type_mapping[col] = "datetime"
            elif df[col].dtype == "bool":
                type_mapping[col] = "boolean"
            else:
                # 进一步检测
                sample = df[col].dropna().head(100)
                
                # 检测是否为日期
                try:
                    self.pandas.to_datetime(sample, errors="raise")
                    type_mapping[col] = "datetime"
                    continue
                except:
                    pass
                
                # 检测是否为数值
                try:
                    self.pandas.to_numeric(sample, errors="raise")
                    type_mapping[col] = "numeric"
                    continue
                except:
                    pass
                
                type_mapping[col] = "text"
        
        return type_mapping
    
    def get_report(self) -> CleaningReport:
        """获取清洗报告"""
        return self.report
    
    def reset_report(self) -> None:
        """重置清洗报告"""
        self.report = CleaningReport()
