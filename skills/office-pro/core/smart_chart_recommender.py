#!/usr/bin/env python3
"""
智能图表推荐系统
根据数据特征自动推荐最佳图表类型
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json


class ChartType(Enum):
    BAR = "bar"
    HORIZONTAL_BAR = "horizontal_bar"
    STACKED_BAR = "stacked_bar"
    LINE = "line"
    AREA = "area"
    STACKED_AREA = "stacked_area"
    PIE = "pie"
    DONUT = "donut"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    HEATMAP = "heatmap"
    BOX = "box"
    VIOLIN = "violin"
    RADAR = "radar"
    TREEMAP = "treemap"
    FUNNEL = "funnel"
    GANTT = "gantt"
    HISTOGRAM = "histogram"
    WATERFALL = "waterfall"
    COMBO = "combo"


class DataPattern(Enum):
    TIME_SERIES = "time_series"
    CATEGORICAL_COMPARISON = "categorical_comparison"
    PROPORTION = "proportion"
    CORRELATION = "correlation"
    DISTRIBUTION = "distribution"
    RANKING = "ranking"
    DEVIATION = "deviation"
    COMPOSITION = "composition"
    FLOW = "flow"
    UNKNOWN = "unknown"


@dataclass
class ChartRecommendation:
    chart_type: ChartType
    confidence: float
    pattern: DataPattern
    reason: str
    alternatives: List[ChartType]
    suggested_config: Dict[str, Any]


class SmartChartRecommender:
    CHART_PATTERNS = {
        DataPattern.TIME_SERIES: {
            "primary": ChartType.LINE,
            "alternatives": [ChartType.AREA, ChartType.COMBO, ChartType.LINE],
            "conditions": ["has_date_column", "has_numeric_data", "has_multiple_series"],
            "min_rows": 5
        },
        DataPattern.CATEGORICAL_COMPARISON: {
            "primary": ChartType.BAR,
            "alternatives": [ChartType.HORIZONTAL_BAR, ChartType.RADAR, ChartType.BAR],
            "conditions": ["has_category_column", "has_numeric_data"],
            "max_categories": 15
        },
        DataPattern.PROPORTION: {
            "primary": ChartType.PIE,
            "alternatives": [ChartType.DONUT, ChartType.TREEMAP, ChartType.PIE],
            "conditions": ["single_series", "parts_to_whole"],
            "max_categories": 8
        },
        DataPattern.CORRELATION: {
            "primary": ChartType.SCATTER,
            "alternatives": [ChartType.HEATMAP, ChartType.BUBBLE, ChartType.SCATTER],
            "conditions": ["multiple_numeric_columns", "correlation_analysis"],
            "min_numeric_cols": 2
        },
        DataPattern.DISTRIBUTION: {
            "primary": ChartType.HISTOGRAM,
            "alternatives": [ChartType.BOX, ChartType.VIOLIN, ChartType.HISTOGRAM],
            "conditions": ["single_numeric_column", "distribution_analysis"],
            "min_rows": 30
        },
        DataPattern.RANKING: {
            "primary": ChartType.HORIZONTAL_BAR,
            "alternatives": [ChartType.BAR, ChartType.BAR],
            "conditions": ["ranking_order", "has_category_column"]
        },
        DataPattern.COMPOSITION: {
            "primary": ChartType.STACKED_BAR,
            "alternatives": [ChartType.TREEMAP, ChartType.STACKED_AREA],
            "conditions": ["multiple_series", "parts_to_whole"]
        }
    }

    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.analysis: Dict[str, Any] = {}

    def load_data(self, data: pd.DataFrame) -> "SmartChartRecommender":
        self.df = data
        self._analyze_data()
        return self

    def _analyze_data(self):
        if self.df is None:
            return

        df = self.df

        self.analysis = {
            "n_rows": len(df),
            "n_cols": len(df.columns),
            "numeric_cols": list(df.select_dtypes(include=[np.number]).columns),
            "category_cols": list(df.select_dtypes(include=["object", "category"]).columns),
            "date_cols": self._detect_date_columns(df),
            "null_counts": df.isnull().sum().to_dict(),
            "numeric_stats": df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {}
        }

    def _detect_date_columns(self, df: pd.DataFrame) -> List[str]:
        date_cols = []
        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    pd.to_datetime(df[col], infer_datetime_format=True)
                    date_cols.append(col)
                except:
                    pass
            elif pd.api.types.is_datetime64_any_dtype(df[col].dtype):
                date_cols.append(col)
        return date_cols

    def detect_pattern(self) -> DataPattern:
        if self.df is None:
            return DataPattern.UNKNOWN

        n_rows = len(self.df)
        n_numeric = len(self.analysis["numeric_cols"])
        n_category = len(self.analysis["category_cols"])
        has_date = len(self.analysis["date_cols"]) > 0
        n_unique_categories = {}
        for col in self.analysis["category_cols"]:
            n_unique_categories[col] = self.df[col].nunique()

        if has_date and n_numeric >= 1:
            if n_rows >= 5:
                return DataPattern.TIME_SERIES

        if n_category >= 1 and n_numeric >= 1:
            for col, n_unique in n_unique_categories.items():
                if n_unique <= 8:
                    return DataPattern.PROPORTION

            return DataPattern.CATEGORICAL_COMPARISON

        if n_numeric >= 2:
            return DataPattern.CORRELATION

        if n_numeric == 1 and n_rows >= 30:
            return DataPattern.DISTRIBUTION

        if n_category >= 1 and n_numeric >= 1:
            return DataPattern.RANKING

        return DataPattern.UNKNOWN

    def recommend(self, preferred_type: Optional[ChartType] = None) -> ChartRecommendation:
        if self.df is None:
            return ChartRecommendation(
                chart_type=ChartType.BAR,
                confidence=0.0,
                pattern=DataPattern.UNKNOWN,
                reason="No data loaded",
                alternatives=[],
                suggested_config={}
            )

        pattern = self.detect_pattern()

        if pattern == DataPattern.UNKNOWN:
            if len(self.analysis["numeric_cols"]) >= 1:
                pattern = DataPattern.CATEGORICAL_COMPARISON

        pattern_config = self.CHART_PATTERNS.get(pattern, self.CHART_PATTERNS[DataPattern.CATEGORICAL_COMPARISON])

        if preferred_type:
            return ChartRecommendation(
                chart_type=preferred_type,
                confidence=0.8,
                pattern=pattern,
                reason=f"User preferred: {preferred_type.value}",
                alternatives=pattern_config["alternatives"],
                suggested_config=self._generate_config(preferred_type, pattern)
            )

        chart_type = pattern_config["primary"]
        confidence = self._calculate_confidence(pattern, chart_type)

        return ChartRecommendation(
            chart_type=chart_type,
            confidence=confidence,
            pattern=pattern,
            reason=self._generate_reason(pattern),
            alternatives=pattern_config["alternatives"],
            suggested_config=self._generate_config(chart_type, pattern)
        )

    def _calculate_confidence(self, pattern: DataPattern, chart_type: ChartType) -> float:
        confidence = 0.7

        n_rows = self.analysis.get("n_rows", 0)

        if pattern == DataPattern.TIME_SERIES:
            if n_rows >= 12:
                confidence = 0.95
            elif n_rows >= 6:
                confidence = 0.85
        elif pattern == DataPattern.PROPORTION:
            confidence = 0.9
        elif pattern == DataPattern.CATEGORICAL_COMPARISON:
            confidence = 0.85

        return confidence

    def _generate_reason(self, pattern: DataPattern) -> str:
        reasons = {
            DataPattern.TIME_SERIES: "检测到时间序列数据，适合使用趋势图展示",
            DataPattern.CATEGORICAL_COMPARISON: "检测到分类数据和数值数据，适合对比分析",
            DataPattern.PROPORTION: "检测到占比关系，适合饼图或环形图",
            DataPattern.CORRELATION: "检测到多组数值数据，适合相关性分析",
            DataPattern.DISTRIBUTION: "检测到大量数值数据，适合分布分析",
            DataPattern.RANKING: "检测到排名需求，适合条形图",
            DataPattern.COMPOSITION: "检测到组合数据，适合堆叠图",
            DataPattern.UNKNOWN: "数据模式不明确，使用默认柱状图"
        }
        return reasons.get(pattern, "根据数据特征推荐")

    def _generate_config(self, chart_type: ChartType, pattern: DataPattern) -> Dict[str, Any]:
        config = {
            "chart_type": chart_type.value,
            "title": self._generate_title(chart_type),
            "colors": self._get_color_palette(chart_type),
            "show_legend": True,
            "show_grid": True,
            "animate": False
        }

        if chart_type in [ChartType.PIE, ChartType.DONUT]:
            config["show_percentage"] = True
            config["donut_hole_size"] = 40 if chart_type == ChartType.DONUT else 0
        elif chart_type == ChartType.LINE:
            config["smooth"] = True
            config["fill_area"] = False
        elif chart_type == ChartType.HEATMAP:
            config["color_scheme"] = "RdYlBu_r"

        return config

    def _generate_title(self, chart_type: ChartType) -> str:
        titles = {
            ChartType.BAR: "数据对比分析",
            ChartType.HORIZONTAL_BAR: "排名分析",
            ChartType.LINE: "趋势变化",
            ChartType.AREA: "累积趋势",
            ChartType.PIE: "占比分析",
            ChartType.DONUT: "占比分析",
            ChartType.SCATTER: "相关性分析",
            ChartType.HEATMAP: "热力图分析",
            ChartType.HISTOGRAM: "分布分析",
            ChartType.BOX: "箱线图分析",
            ChartType.RADAR: "雷达图分析",
            ChartType.TREEMAP: "树图分析",
            ChartType.FUNNEL: "漏斗分析"
        }
        return titles.get(chart_type, "数据可视化")

    def _get_color_palette(self, chart_type: ChartType) -> List[str]:
        palettes = {
            "default": ["#4A90E2", "#E24A4A", "#2ECC71", "#F39C12", "#9B59B6", "#1ABC9C", "#E67E22", "#34495E"],
            "warm": ["#E74C3C", "#F39C12", "#F1C40F", "#E67E22", "#D35400", "#C0392B", "#FF6B6B", "#FFE66D"],
            "cool": ["#3498DB", "#2ECC71", "#1ABC9C", "#00CED1", "#4169E1", "#6B5B95", "#88B04B", "#F7CAC9"],
            "professional": ["#2C3E50", "#34495E", "#7F8C8D", "#95A5A6", "#BDC3C7", "#ECF0F1", "#1A1A2E", "#16213E"],
            "vibrant": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9"]
        }
        return palettes["default"]

    def get_all_recommendations(self) -> List[ChartRecommendation]:
        recommendations = []

        recommendations.append(self.recommend())

        for alt in self.CHART_PATTERNS.get(self.detect_pattern(), {}).get("alternatives", []):
            recommendations.append(self.recommend(preferred_type=alt))

        return recommendations[:5]


def recommend_chart(data, preferred_type: str = None) -> Dict[str, Any]:
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    elif isinstance(data, str):
        if data.endswith('.csv'):
            df = pd.read_csv(data)
        elif data.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(data)
        elif data.endswith('.json'):
            df = pd.read_json(data)
        else:
            raise ValueError(f"Unsupported file format: {data}")
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        raise ValueError("Unsupported data format")

    recommender = SmartChartRecommender().load_data(df)

    if preferred_type:
        try:
            preferred = ChartType(preferred_type)
            result = recommender.recommend(preferred_type=preferred)
        except ValueError:
            result = recommender.recommend()
    else:
        result = recommender.recommend()

    return {
        "recommended_chart": result.chart_type.value,
        "confidence": result.confidence,
        "pattern": result.pattern.value,
        "reason": result.reason,
        "alternatives": [alt.value for alt in result.alternatives],
        "config": result.suggested_config
    }


if __name__ == "__main__":
    sample_data = {
        "month": ["1月", "2月", "3月", "4月", "5月", "6月"],
        "sales": [120, 150, 180, 160, 200, 250],
        "profit": [30, 45, 55, 48, 65, 80]
    }

    result = recommend_chart(sample_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
