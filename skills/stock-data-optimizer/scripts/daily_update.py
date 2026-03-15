#!/usr/bin/env python3
"""
每日数据更新脚本
定时任务：每天收盘后更新缓存
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data_fetcher import DataFetcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('daily-update')


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始每日数据更新")
    logger.info("=" * 60)
    
    fetcher = DataFetcher()
    
    # 更新股票基础信息
    logger.info("\n1. 更新股票基础信息...")
    try:
        result = fetcher.fetch_stock_basic(force_update=True)
        if result is not None:
            logger.info(f"✅ 成功更新 {len(result)} 只股票基础信息")
        else:
            logger.error("❌ 更新失败")
    except Exception as e:
        logger.error(f"❌ 更新失败: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("每日数据更新完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
