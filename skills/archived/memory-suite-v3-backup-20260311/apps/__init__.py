#!/usr/bin/env python3
"""
Memory Suite v3.0 - 应用层模块初始化
推荐系统、用户画像、问答、决策支持等应用模块

版本: 3.0.0
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# 应用层版本
__version__ = "3.0.0"
__apps_version__ = "3.0.0"

# 导出主要类
from .recommender import Recommender, Recommendation
from .profiler import Profiler, UserProfile
from .qa import QASystem
from .advisor import DecisionAdvisor

__all__ = [
    # 版本
    '__version__',
    '__apps_version__',
    # 推荐系统
    'Recommender',
    'Recommendation',
    # 用户画像
    'Profiler',
    'UserProfile',
    # 问答系统
    'QASystem',
    # 决策支持
    'DecisionAdvisor',
]

# 初始化日志
_logger = logging.getLogger(__name__)
_logger.debug("Memory Suite v3.0 应用层初始化完成")
