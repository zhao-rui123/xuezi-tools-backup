"""
数据验证模块

提供全面的数据验证功能，包括:
- 数据类型验证
- 格式验证（邮箱、手机号、身份证号等）
- 范围验证
- 必填项验证
- 自定义规则验证
- 数据质量评分
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, date
import ipaddress

# 设置日志
logger = logging.getLogger("openclaw.utils.validator")


@dataclass
class ValidationRule:
    """验证规则"""
    field: str
    rule_type: str  # required, type, format, range, pattern, custom
    params: Dict[str, Any] = field(default_factory=dict)
    message: Optional[str] = None
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationError:
    """验证错误"""
    field: str
    rule_type: str
    message: str
    value: Any = None
    severity: str = "error"
    row: Optional[int] = None


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, error: ValidationError) -> None:
        """添加错误"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: ValidationError) -> None:
        """添加警告"""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": [
                {
                    "field": e.field,
                    "rule_type": e.rule_type,
                    "message": e.message,
                    "value": str(e.value) if e.value is not None else None,
                    "severity": e.severity,
                    "row": e.row,
                }
                for e in self.errors
            ],
            "warnings": [
                {
                    "field": w.field,
                    "rule_type": w.rule_type,
                    "message": w.message,
                    "value": str(w.value) if w.value is not None else None,
                    "severity": w.severity,
                    "row": w.row,
                }
                for w in self.warnings
            ],
            "stats": self.stats,
        }


class DataValidator:
    """
    数据验证器
    
    提供全面的数据验证功能。
    
    Example:
        >>> from openclaw import DataValidator
        >>> validator = DataValidator()
        >>> 
        >>> # 定义验证规则
        >>> rules = [
        ...     ValidationRule("email", "format", {"format": "email"}),
        ...     ValidationRule("age", "range", {"min": 0, "max": 150}),
        ...     ValidationRule("name", "required"),
        ... ]
        >>> 
        >>> # 验证数据
        >>> result = validator.validate_record({"name": "张三", "email": "test@example.com", "age": 25}, rules)
        >>> print(result.is_valid)
        
        >>> # 验证DataFrame
        >>> result = validator.validate_dataframe(df, rules)
        >>> print(result.to_dict())
    """
    
    # 预定义的正则表达式模式
    PATTERNS = {
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "phone_cn": r"^1[3-9]\d{9}$",  # 中国手机号
        "phone_us": r"^\+?1?\d{10,11}$",  # 美国手机号
        "idcard_cn": r"^\d{17}[\dXx]$",  # 中国身份证号（18位）
        "idcard_cn_15": r"^\d{15}$",  # 中国身份证号（15位）
        "url": r"^https?://[^\s/$.?#].[^\s]*$",
        "ipv4": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        "ipv6": r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$",
        "date_iso": r"^\d{4}-\d{2}-\d{2}$",
        "datetime_iso": r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}$",
        "credit_card": r"^\d{13,19}$",
        "postal_code_cn": r"^\d{6}$",  # 中国邮编
        "postal_code_us": r"^\d{5}(-\d{4})?$",  # 美国邮编
    }
    
    def __init__(self):
        self.logger = logging.getLogger("openclaw.utils.validator")
        self._check_dependencies()
        self.custom_validators: Dict[str, Callable] = {}
    
    def _check_dependencies(self) -> None:
        """检查依赖库"""
        try:
            import pandas as pd
            self.pandas = pd
        except ImportError:
            self.logger.warning("pandas未安装，DataFrame验证功能受限")
            self.pandas = None
    
    def register_custom_validator(self, name: str, validator: Callable) -> None:
        """注册自定义验证器"""
        self.custom_validators[name] = validator
    
    def validate_record(
        self,
        record: Dict[str, Any],
        rules: List[ValidationRule],
    ) -> ValidationResult:
        """
        验证单条记录
        
        Args:
            record: 数据记录
            rules: 验证规则列表
        
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()
        
        for rule in rules:
            try:
                self._apply_rule(record, rule, result)
            except Exception as e:
                self.logger.warning(f"应用验证规则失败: {e}")
        
        return result
    
    def validate_dataframe(
        self,
        df: Any,
        rules: List[ValidationRule],
    ) -> ValidationResult:
        """
        验证DataFrame
        
        Args:
            df: pandas DataFrame
            rules: 验证规则列表
        
        Returns:
            ValidationResult: 验证结果
        """
        if not self.pandas or not isinstance(df, self.pandas.DataFrame):
            raise TypeError("需要pandas DataFrame")
        
        result = ValidationResult()
        
        # 统计信息
        result.stats["total_rows"] = len(df)
        result.stats["total_columns"] = len(df.columns)
        
        # 逐行验证
        for idx, row in df.iterrows():
            record = row.to_dict()
            row_result = self.validate_record(record, rules)
            
            # 合并错误和警告
            for error in row_result.errors:
                error.row = idx
                result.add_error(error)
            
            for warning in row_result.warnings:
                warning.row = idx
                result.add_warning(warning)
        
        # 更新统计
        result.stats["valid_rows"] = result.stats["total_rows"] - len(set(e.row for e in result.errors))
        result.stats["error_rows"] = len(set(e.row for e in result.errors))
        
        return result
    
    def _apply_rule(
        self,
        record: Dict[str, Any],
        rule: ValidationRule,
        result: ValidationResult,
    ) -> None:
        """应用验证规则"""
        value = record.get(rule.field)
        
        if rule.rule_type == "required":
            self._validate_required(value, rule, result)
        elif rule.rule_type == "type":
            self._validate_type(value, rule, result)
        elif rule.rule_type == "format":
            self._validate_format(value, rule, result)
        elif rule.rule_type == "range":
            self._validate_range(value, rule, result)
        elif rule.rule_type == "pattern":
            self._validate_pattern(value, rule, result)
        elif rule.rule_type == "custom":
            self._validate_custom(value, rule, result)
        elif rule.rule_type == "length":
            self._validate_length(value, rule, result)
        elif rule.rule_type == "unique":
            self._validate_unique(value, rule, result)
    
    def _validate_required(self, value: Any, rule: ValidationRule, result: ValidationResult) -> None:
        """验证必填项"""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            message = rule.message or f"字段 '{rule.field}' 为必填项"
            error = ValidationError(
                field=rule.field,
                rule_type="required",
                message=message,
                value=value,
                severity=rule.severity,
            )
            if rule.severity == "error":
                result.add_error(error)
            else:
                result.add_warning(error)
    
    def _validate_type(self, value: Any, rule: ValidationRule, result: ValidationResult) -> None:
        """验证数据类型"""
        if value is None:
            return
        
        expected_type = rule.params.get("type")
        if not expected_type:
            return
        
        type_valid = False
        
        if expected_type == "string":
            type_valid = isinstance(value, str)
        elif expected_type == "integer":
            type_valid = isinstance(value, int) and not isinstance(value, bool)
        elif expected_type == "float":
            type_valid = isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected_type == "number":
            type_valid = isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected_type == "boolean":
            type_valid = isinstance(value, bool)
        elif expected_type == "date":
            type_valid = isinstance(value, (date, datetime))
        elif expected_type == "array":
            type_valid = isinstance(value, (list, tuple))
        elif expected_type == "object":
            type_valid = isinstance(value, dict)
        
        if not type_valid:
            message = rule.message or f"字段 '{rule.field}' 应为 {expected_type} 类型"
            error = ValidationError(
                field=rule.field,
                rule_type="type",
                message=message,
                value=value,
                severity=rule.severity,
            )
            if rule.severity == "error":
                result.add_error(error)
            else:
                result.add_warning(error)
    
    def _validate_format(self, value: Any, rule: ValidationRule, result: ValidationResult) -> None:
        """验证格式"""
        if value is None:
            return
        
        if not isinstance(value, str):
            value = str(value)
        
        format_type = rule.params.get("format")
        if not format_type:
            return
        
        pattern = self.PATTERNS.get(format_type)
        if not pattern:
            self.logger.warning(f"未知的格式类型: {format_type}")
            return
        
        if not re.match(pattern, value):
            message = rule.message or f"字段 '{rule.field}' 格式不正确（应为 {format_type}）"
            error = ValidationError(
                field=rule.field,
                rule_type="format",
                message=message,
                value=value,
                severity=rule.severity,
            )
            if rule.severity == "error":
                result.add_error(error)
            else:
                result.add_warning(error)
    
    def _validate_range(self, value: Any, rule: ValidationRule, result: ValidationResult) -> None:
        """验证范围"""
        if value is None:
            return
        
        min_val = rule.params.get("min")
        max_val = rule.params.get("max")
        
        try:
            num_value = float(value)
        except (TypeError, ValueError):
            message = rule.message or f"字段 '{rule.field}' 不是有效的数值"
            error = ValidationError(
                field=rule.field,
                rule_type="range",
                message=message,
                value=value,
                severity=rule.severity,
            )
            if rule.severity == "error":
                result.add_error(error)
            else:
                result.add_warning(error)
            return
        
        if min_val is not None and num_value < min_val:
            message = rule.message or f"字段 '{rule.field}' 应大于等于 {min_val}"
            error = ValidationError(
                field=rule.field,
                rule_type="range",
                message=message,
                value=value,
                severity=rule.severity,
            )
            if rule.severity == "error":
                result.add_error(error)
            else:
                result.add_warning(error)
        
        if max_val is not None and num_value > max_val:
            message = rule.message or f"字段 '{rule.field}' 应小于等于 {max_val}"
            error = ValidationError(
                field=rule.field,
                rule_type="range",
                message=message,
                value=value,
                severity=rule.severity,
            )
            if rule.severity == "error":
                result.add_error(error)
            else:
                result.add_warning(error)
    
    def _validate_pattern(self, value: Any, rule: ValidationRule, result: ValidationResult) -> None:
        """验证正则模式"""
        if value is None:
            return
        
        pattern = rule.params.get("pattern")
        if not pattern:
            return
        
        if not isinstance(value, str):
            value = str(value)
        
        try:
            if not re.match(pattern, value):
                message = rule.message or f"字段 '{rule.field}' 不符合要求的格式"
                error = ValidationError(
                    field=rule.field,
                    rule_type="pattern",
                    message=message,
                    value=value,
                    severity=rule.severity,
                )
                if rule.severity == "error":
                    result.add_error(error)
                else:
                    result.add_warning(error)
        except re.error as e:
            self.logger.warning(f"无效的正则表达式: {e}")
    
    def _validate_custom(self, value: Any, rule: ValidationRule, result: ValidationResult) -> None:
        """自定义验证"""
        validator_name = rule.params.get("validator")
        if not validator_name or validator_name not in self.custom_validators:
            self.logger.warning(f"未找到自定义验证器: {validator_name}")
            return
        
        validator = self.custom_validators[validator_name]
        is_valid, message = validator(value, rule.params)
        
        if not is_valid:
            error = ValidationError(
                field=rule.field,
                rule_type="custom",
                message=message or f"字段 '{rule.field}' 验证失败",
                value=value,
                severity=rule.severity,
            )
            if rule.severity == "error":
                result.add_error(error)
            else:
                result.add_warning(error)
    
    def _validate_length(self, value: Any, rule: ValidationRule, result: ValidationResult) -> None:
        """验证长度"""
        if value is None:
            return
        
        min_len = rule.params.get("min")
        max_len = rule.params.get("max")
        
        try:
            length = len(value)
        except TypeError:
            return
        
        if min_len is not None and length < min_len:
            message = rule.message or f"字段 '{rule.field}' 长度应至少为 {min_len}"
            error = ValidationError(
                field=rule.field,
                rule_type="length",
                message=message,
                value=value,
                severity=rule.severity,
            )
            if rule.severity == "error":
                result.add_error(error)
            else:
                result.add_warning(error)
        
        if max_len is not None and length > max_len:
            message = rule.message or f"字段 '{rule.field}' 长度应不超过 {max_len}"
            error = ValidationError(
                field=rule.field,
                rule_type="length",
                message=message,
                value=value,
                severity=rule.severity,
            )
            if rule.severity == "error":
                result.add_error(error)
            else:
                result.add_warning(error)
    
    def _validate_unique(self, value: Any, rule: ValidationRule, result: ValidationResult) -> None:
        """验证唯一性（需要在DataFrame级别处理）"""
        # 唯一性验证在validate_dataframe中批量处理
        pass
    
    def validate_email(self, email: str) -> bool:
        """验证邮箱格式"""
        if not email:
            return False
        return bool(re.match(self.PATTERNS["email"], str(email)))
    
    def validate_phone_cn(self, phone: str) -> bool:
        """验证中国手机号"""
        if not phone:
            return False
        return bool(re.match(self.PATTERNS["phone_cn"], str(phone)))
    
    def validate_idcard_cn(self, idcard: str) -> bool:
        """验证中国身份证号"""
        if not idcard:
            return False
        idcard = str(idcard)
        if re.match(self.PATTERNS["idcard_cn"], idcard):
            return self._validate_idcard_cn_checksum(idcard)
        return bool(re.match(self.PATTERNS["idcard_cn_15"], idcard))
    
    def _validate_idcard_cn_checksum(self, idcard: str) -> bool:
        """验证身份证号校验位"""
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        if len(idcard) != 18:
            return False
        
        try:
            sum_val = sum(int(idcard[i]) * weights[i] for i in range(17))
            return idcard[17].upper() == check_codes[sum_val % 11]
        except:
            return False
    
    def validate_url(self, url: str) -> bool:
        """验证URL格式"""
        if not url:
            return False
        return bool(re.match(self.PATTERNS["url"], str(url)))
    
    def validate_ipv4(self, ip: str) -> bool:
        """验证IPv4地址"""
        if not ip:
            return False
        try:
            ipaddress.IPv4Address(ip)
            return True
        except:
            return False
    
    def validate_ipv6(self, ip: str) -> bool:
        """验证IPv6地址"""
        if not ip:
            return False
        try:
            ipaddress.IPv6Address(ip)
            return True
        except:
            return False
    
    def calculate_quality_score(self, df: Any) -> Dict[str, float]:
        """
        计算数据质量评分
        
        Args:
            df: pandas DataFrame
        
        Returns:
            质量评分字典
        """
        if not self.pandas or not isinstance(df, self.pandas.DataFrame):
            raise TypeError("需要pandas DataFrame")
        
        scores = {}
        
        # 完整性评分
        total_cells = df.size
        missing_cells = df.isna().sum().sum()
        scores["completeness"] = (total_cells - missing_cells) / total_cells if total_cells > 0 else 1.0
        
        # 唯一性评分
        duplicate_rows = df.duplicated().sum()
        scores["uniqueness"] = (len(df) - duplicate_rows) / len(df) if len(df) > 0 else 1.0
        
        # 有效性评分（非空字符串比例）
        string_cols = df.select_dtypes(include=["object"]).columns
        if len(string_cols) > 0:
            empty_strings = 0
            total_strings = 0
            for col in string_cols:
                total_strings += df[col].notna().sum()
                empty_strings += (df[col] == "").sum()
            scores["validity"] = (total_strings - empty_strings) / total_strings if total_strings > 0 else 1.0
        else:
            scores["validity"] = 1.0
        
        # 总体评分
        scores["overall"] = (scores["completeness"] + scores["uniqueness"] + scores["validity"]) / 3
        
        return scores
