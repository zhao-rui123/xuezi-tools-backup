"""
数据缓存管理
"""
import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
import pandas as pd
from config import settings
from utils.logger import logger


class DataCache:
    """数据缓存管理器"""
    
    def __init__(self):
        self.data_dir = Path(settings.DATA_DIR)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_metadata_file = self.data_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """加载缓存元数据"""
        if self.cache_metadata_file.exists():
            try:
                with open(self.cache_metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载缓存元数据失败: {e}")
        return {}
    
    def _save_metadata(self):
        """保存缓存元数据"""
        try:
            with open(self.cache_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存元数据失败: {e}")
    
    def _get_cache_file(self, key: str) -> Path:
        """获取缓存文件路径"""
        return self.data_dir / f"{key}.pkl"
    
    def is_cache_valid(self, key: str, max_age_hours: int = 24) -> bool:
        """检查缓存是否有效"""
        if key not in self.metadata:
            return False
        
        cache_time = datetime.fromisoformat(self.metadata[key]['timestamp'])
        if datetime.now() - cache_time > timedelta(hours=max_age_hours):
            return False
        
        cache_file = self._get_cache_file(key)
        return cache_file.exists()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if not self.is_cache_valid(key):
            return None
        
        try:
            cache_file = self._get_cache_file(key)
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            logger.debug(f"从缓存加载数据: {key}")
            return data
        except Exception as e:
            logger.error(f"加载缓存失败 {key}: {e}")
            return None
    
    def set(self, key: str, data: Any):
        """设置缓存数据"""
        try:
            cache_file = self._get_cache_file(key)
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            self.metadata[key] = {
                'timestamp': datetime.now().isoformat(),
                'size': cache_file.stat().st_size
            }
            self._save_metadata()
            logger.debug(f"缓存数据已保存: {key}")
        except Exception as e:
            logger.error(f"保存缓存失败 {key}: {e}")
    
    def clear_expired(self, max_age_hours: int = 48):
        """清理过期缓存"""
        expired_keys = []
        for key, meta in self.metadata.items():
            cache_time = datetime.fromisoformat(meta['timestamp'])
            if datetime.now() - cache_time > timedelta(hours=max_age_hours):
                expired_keys.append(key)
        
        for key in expired_keys:
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                cache_file.unlink()
            del self.metadata[key]
            logger.info(f"清理过期缓存: {key}")
        
        if expired_keys:
            self._save_metadata()
    
    def save_stock_list(self, stocks: List[Dict], grade: str):
        """保存股票列表到JSON（供API使用）"""
        try:
            output_file = self.data_dir / f"stocks_grade_{grade}_{datetime.now().strftime('%Y%m%d')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(stocks, f, ensure_ascii=False, indent=2)
            logger.info(f"股票列表已保存: {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"保存股票列表失败: {e}")
            return None
    
    def get_latest_stock_file(self, grade: str) -> Optional[Path]:
        """获取最新的股票列表文件"""
        try:
            pattern = f"stocks_grade_{grade}_*.json"
            files = sorted(self.data_dir.glob(pattern), reverse=True)
            return files[0] if files else None
        except Exception:
            return None
    
    def save_kline_data(self, stock_code: str, period: str, data: pd.DataFrame):
        """保存K线数据"""
        key = f"kline_{stock_code}_{period}"
        self.set(key, data)
    
    def get_kline_data(self, stock_code: str, period: str) -> Optional[pd.DataFrame]:
        """获取K线数据"""
        key = f"kline_{stock_code}_{period}"
        return self.get(key)


# 全局缓存实例
cache = DataCache()