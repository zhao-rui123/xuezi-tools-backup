"""
智能数据识别模块

提供智能数据识别和分类功能，包括:
- 数据类型自动检测
- 表头自动识别
- 数据分类
- 语义识别
- 列名智能匹配
- 数据关系检测
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union, Set
from pathlib import Path
from dataclasses import dataclass, field
from collections import Counter
import keyword

# 设置日志
logger = logging.getLogger("openclaw.utils.smart_recognizer")


@dataclass
class ColumnInfo:
    """列信息"""
    name: str
    suggested_name: Optional[str] = None
    data_type: str = "unknown"
    confidence: float = 0.0
    sample_values: List[Any] = field(default_factory=list)
    null_count: int = 0
    unique_count: int = 0
    is_primary_key: bool = False
    is_foreign_key: bool = False
    semantic_type: Optional[str] = None  # email, phone, idcard, etc.


@dataclass
class TableSchema:
    """表结构信息"""
    table_name: str
    columns: List[ColumnInfo] = field(default_factory=list)
    row_count: int = 0
    has_header: bool = True
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "table_name": self.table_name,
            "row_count": self.row_count,
            "has_header": self.has_header,
            "columns": [
                {
                    "name": c.name,
                    "suggested_name": c.suggested_name,
                    "data_type": c.data_type,
                    "confidence": c.confidence,
                    "semantic_type": c.semantic_type,
                    "null_count": c.null_count,
                    "unique_count": c.unique_count,
                    "is_primary_key": c.is_primary_key,
                }
                for c in self.columns
            ],
            "relationships": self.relationships,
        }


class SmartRecognizer:
    """
    智能数据识别器
    
    提供智能数据识别和分类功能。
    
    Example:
        >>> from openclaw import SmartRecognizer
        >>> recognizer = SmartRecognizer()
        >>> 
        >>> # 识别DataFrame结构
        >>> schema = recognizer.recognize_dataframe(df, table_name="users")
        >>> print(schema.to_dict())
        >>> 
        >>> # 检测数据类型
        >>> col_info = recognizer.detect_column_type(df['email'])
        >>> print(col_info.semantic_type)  # 'email'
        >>> 
        >>> # 智能匹配列名
        >>> matched = recognizer.match_column_name("手机号", ["phone", "mobile", "tel"])
    """
    
    # 语义类型模式
    SEMANTIC_PATTERNS = {
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "phone_cn": r"^1[3-9]\d{9}$",
        "phone_us": r"^\+?1?\d{10}$",
        "idcard_cn": r"^\d{17}[\dXx]$",
        "url": r"^https?://[^\s/$.?#].[^\s]*$",
        "ipv4": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        "date_iso": r"^\d{4}-\d{2}-\d{2}$",
        "datetime_iso": r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}$",
        "credit_card": r"^\d{13,19}$",
        "postal_code_cn": r"^\d{6}$",
        "uuid": r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
    }
    
    # 列名关键词映射
    COLUMN_KEYWORDS = {
        "id": ["id", "编号", "序号", "标识", "identifier", "no", "code"],
        "name": ["name", "名称", "姓名", "名字", "标题", "title"],
        "email": ["email", "邮箱", "邮件", "e-mail", "mail"],
        "phone": ["phone", "tel", "mobile", "电话", "手机", "手机号", "联系方式"],
        "address": ["address", "地址", "住址", "location", "位置"],
        "date": ["date", "日期", "时间", "time", "创建时间", "更新时间"],
        "amount": ["amount", "金额", "价格", "price", "费用", "cost", "total"],
        "quantity": ["quantity", "数量", "count", "qty", "num"],
        "status": ["status", "状态", "state", "condition"],
        "type": ["type", "类型", "类别", "category", "kind", "class"],
        "description": ["description", "描述", "说明", "备注", "comment", "note"],
        "gender": ["gender", "sex", "性别", "男女"],
        "age": ["age", "年龄", "岁数"],
        "company": ["company", "公司", "企业", "单位", "organization", "org"],
        "department": ["department", "部门", "dept", "division"],
        "job": ["job", "职位", "岗位", "职务", "title", "position"],
        "salary": ["salary", "工资", "薪资", "薪酬", "收入", "income"],
    }
    
    def __init__(self):
        self.logger = logging.getLogger("openclaw.utils.smart_recognizer")
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """检查依赖库"""
        try:
            import pandas as pd
            self.pandas = pd
        except ImportError:
            self.logger.warning("pandas未安装，DataFrame识别功能受限")
            self.pandas = None
    
    def recognize_dataframe(
        self,
        df: Any,
        table_name: str = "table",
    ) -> TableSchema:
        """
        识别DataFrame结构
        
        Args:
            df: pandas DataFrame
            table_name: 表名
        
        Returns:
            TableSchema: 表结构信息
        """
        if not self.pandas or not isinstance(df, self.pandas.DataFrame):
            raise TypeError("需要pandas DataFrame")
        
        schema = TableSchema(table_name=table_name)
        schema.row_count = len(df)
        
        # 检测是否有表头
        schema.has_header = self._detect_header(df)
        
        # 识别每列
        for col_name in df.columns:
            col_info = self._analyze_column(df[col_name], col_name)
            schema.columns.append(col_info)
        
        # 检测主键
        self._detect_primary_key(schema)
        
        return schema
    
    def _analyze_column(self, series: Any, col_name: str) -> ColumnInfo:
        """分析单列"""
        info = ColumnInfo(name=str(col_name))
        
        # 采样值
        sample = series.dropna().head(10).tolist()
        info.sample_values = sample
        
        # 统计信息
        info.null_count = series.isna().sum()
        info.unique_count = series.nunique()
        
        # 检测数据类型
        info.data_type, info.confidence = self._detect_dtype(series)
        
        # 检测语义类型
        info.semantic_type = self._detect_semantic_type(series)
        
        # 建议列名
        info.suggested_name = self._suggest_column_name(col_name, info.semantic_type)
        
        return info
    
    def _detect_dtype(self, series: Any) -> Tuple[str, float]:
        """检测数据类型"""
        # 基于pandas dtype
        if series.dtype == "int64":
            return "integer", 0.9
        elif series.dtype == "float64":
            return "float", 0.9
        elif series.dtype == "bool":
            return "boolean", 0.95
        elif series.dtype == "datetime64[ns]":
            return "datetime", 0.95
        elif series.dtype == "object":
            # 进一步检测
            non_null = series.dropna()
            if len(non_null) == 0:
                return "unknown", 0.0
            
            # 尝试转换为数值
            try:
                converted = self.pandas.to_numeric(non_null, errors="coerce")
                if converted.notna().sum() / len(non_null) > 0.8:
                    if (converted == converted.astype(int)).all():
                        return "integer", 0.8
                    return "float", 0.8
            except:
                pass
            
            # 尝试转换为日期
            try:
                converted = self.pandas.to_datetime(non_null, errors="coerce")
                if converted.notna().sum() / len(non_null) > 0.8:
                    return "datetime", 0.8
            except:
                pass
            
            return "string", 0.7
        
        return "unknown", 0.0
    
    def _detect_semantic_type(self, series: Any) -> Optional[str]:
        """检测语义类型"""
        non_null = series.dropna()
        if len(non_null) == 0:
            return None
        
        # 采样检查
        sample = non_null.head(100).astype(str)
        
        for sem_type, pattern in self.SEMANTIC_PATTERNS.items():
            matches = sum(1 for val in sample if re.match(pattern, str(val)))
            match_rate = matches / len(sample)
            
            if match_rate > 0.8:
                return sem_type
        
        return None
    
    def _detect_header(self, df: Any) -> bool:
        """检测是否有表头"""
        # 简单启发式：如果第一行都是字符串且列名看起来像表头
        if len(df) == 0:
            return True
        
        # 检查列名是否像默认值（如 0, 1, 2）
        col_names = list(df.columns)
        
        # 如果列名都是整数，可能没有表头
        if all(isinstance(c, int) for c in col_names):
            return False
        
        # 如果列名包含Python关键字，可能是数据而不是表头
        if any(str(c).lower() in keyword.kwlist for c in col_names):
            return False
        
        return True
    
    def _detect_primary_key(self, schema: TableSchema) -> None:
        """检测主键"""
        # 寻找唯一值比例100%的列
        for col in schema.columns:
            if col.unique_count == schema.row_count and col.null_count == 0:
                # 进一步检查是否为ID列
                if any(keyword in col.name.lower() for keyword in ["id", "编号", "序号", "code"]):
                    col.is_primary_key = True
                    break
    
    def _suggest_column_name(self, current_name: str, semantic_type: Optional[str]) -> Optional[str]:
        """建议列名"""
        # 基于语义类型建议
        if semantic_type:
            type_to_name = {
                "email": "email",
                "phone_cn": "phone",
                "phone_us": "phone",
                "idcard_cn": "id_card",
                "url": "url",
                "ipv4": "ip_address",
                "date_iso": "date",
                "datetime_iso": "datetime",
            }
            if semantic_type in type_to_name:
                return type_to_name[semantic_type]
        
        # 标准化当前名称
        clean_name = str(current_name).strip().lower()
        
        # 检查是否需要改进
        for standard_name, keywords in self.COLUMN_KEYWORDS.items():
            if any(kw in clean_name for kw in keywords):
                return standard_name
        
        return None
    
    def match_column_name(
        self,
        target: str,
        candidates: List[str],
        threshold: float = 0.6,
    ) -> List[Tuple[str, float]]:
        """
        智能匹配列名
        
        Args:
            target: 目标列名
            candidates: 候选列名列表
            threshold: 匹配阈值
        
        Returns:
            匹配结果列表 (列名, 相似度)
        """
        matches = []
        target_lower = target.lower()
        
        for candidate in candidates:
            candidate_lower = candidate.lower()
            
            # 精确匹配
            if target_lower == candidate_lower:
                matches.append((candidate, 1.0))
                continue
            
            # 包含匹配
            if target_lower in candidate_lower or candidate_lower in target_lower:
                similarity = 0.8
                matches.append((candidate, similarity))
                continue
            
            # 关键词匹配
            for standard_name, keywords in self.COLUMN_KEYWORDS.items():
                if any(kw in target_lower for kw in keywords):
                    if any(kw in candidate_lower for kw in keywords):
                        matches.append((candidate, 0.7))
                        break
            
            # 编辑距离匹配（简单实现）
            similarity = self._calculate_similarity(target_lower, candidate_lower)
            if similarity >= threshold:
                matches.append((candidate, similarity))
        
        # 排序并去重
        matches = sorted(set(matches), key=lambda x: x[1], reverse=True)
        return matches
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """计算字符串相似度（Levenshtein距离的简化版）"""
        if len(s1) < len(s2):
            return self._calculate_similarity(s2, s1)
        
        if len(s2) == 0:
            return 0.0
        
        # 计算公共子串比例
        max_len = max(len(s1), len(s2))
        common = 0
        
        for i in range(len(s1)):
            for j in range(len(s2)):
                k = 0
                while i + k < len(s1) and j + k < len(s2) and s1[i+k] == s2[j+k]:
                    k += 1
                common = max(common, k)
        
        return common / max_len
    
    def detect_column_relationships(
        self,
        df1: Any,
        df2: Any,
        df1_name: str = "table1",
        df2_name: str = "table2",
    ) -> List[Dict[str, Any]]:
        """
        检测两个DataFrame之间的列关系
        
        Args:
            df1: 第一个DataFrame
            df2: 第二个DataFrame
            df1_name: 第一个表名
            df2_name: 第二个表名
        
        Returns:
            关系列表
        """
        if not self.pandas:
            raise RuntimeError("pandas未安装")
        
        relationships = []
        
        for col1 in df1.columns:
            for col2 in df2.columns:
                # 检查列名相似度
                name_similarity = self._calculate_similarity(str(col1).lower(), str(col2).lower())
                
                if name_similarity > 0.7:
                    # 检查数据重叠度
                    values1 = set(df1[col1].dropna().astype(str))
                    values2 = set(df2[col2].dropna().astype(str))
                    
                    if len(values1) > 0 and len(values2) > 0:
                        overlap = len(values1 & values2) / min(len(values1), len(values2))
                        
                        if overlap > 0.5:
                            relationships.append({
                                "from_table": df1_name,
                                "from_column": col1,
                                "to_table": df2_name,
                                "to_column": col2,
                                "relationship_type": "potential_foreign_key",
                                "confidence": (name_similarity + overlap) / 2,
                            })
        
        return relationships
    
    def classify_data(self, df: Any) -> Dict[str, List[str]]:
        """
        对数据进行分类
        
        Args:
            df: pandas DataFrame
        
        Returns:
            分类结果 {类别: [列名列表]}
        """
        if not self.pandas or not isinstance(df, self.pandas.DataFrame):
            raise TypeError("需要pandas DataFrame")
        
        categories = {
            "identifiers": [],
            "personal_info": [],
            "contact_info": [],
            "temporal": [],
            "financial": [],
            "categorical": [],
            "numerical": [],
            "textual": [],
            "other": [],
        }
        
        schema = self.recognize_dataframe(df)
        
        for col in schema.columns:
            if col.semantic_type in ["email", "phone_cn", "phone_us"]:
                categories["contact_info"].append(col.name)
            elif col.semantic_type in ["idcard_cn"]:
                categories["personal_info"].append(col.name)
            elif col.semantic_type in ["date_iso", "datetime_iso"]:
                categories["temporal"].append(col.name)
            elif col.is_primary_key:
                categories["identifiers"].append(col.name)
            elif col.data_type in ["integer", "float"]:
                if any(kw in col.name.lower() for kw in ["price", "amount", "cost", "salary", "金额", "价格"]):
                    categories["financial"].append(col.name)
                else:
                    categories["numerical"].append(col.name)
            elif col.unique_count / schema.row_count < 0.1:
                categories["categorical"].append(col.name)
            elif col.data_type == "string":
                categories["textual"].append(col.name)
            else:
                categories["other"].append(col.name)
        
        return categories
    
    def generate_schema_description(self, schema: TableSchema) -> str:
        """
        生成表结构的自然语言描述
        
        Args:
            schema: 表结构
        
        Returns:
            描述字符串
        """
        lines = [
            f"表 '{schema.table_name}' 包含 {schema.row_count} 行数据，",
            f"共有 {len(schema.columns)} 个字段：",
        ]
        
        for col in schema.columns:
            desc = f"  - {col.name}"
            if col.suggested_name and col.suggested_name != col.name:
                desc += f" (建议改为: {col.suggested_name})"
            desc += f": {col.data_type}"
            if col.semantic_type:
                desc += f" ({col.semantic_type})"
            if col.is_primary_key:
                desc += " [主键]"
            lines.append(desc)
        
        return "\n".join(lines)
