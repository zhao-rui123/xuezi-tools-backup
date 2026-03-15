#!/usr/bin/env python3
"""
{class_name} - {description}

Author: {author}
Date: {date}
"""

from typing import Optional, List, Dict, Any, TypeVar, Generic
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging

T = TypeVar('T')


@dataclass
class {class_name}Config:
    """{class_name}配置"""
    {config_fields}


class {class_name}Error(Exception):
    """{class_name}异常基类"""
    pass


class {class_name}(ABC):
    """
    {class_description}
    
    Attributes:
        {attributes}
    
    Example:
        >>> config = {class_name}Config({example_config})
        >>> instance = {class_name}(config)
        >>> result = instance.process({example_input})
    """
    
    def __init__(self, config: {class_name}Config):
        """
        初始化{class_name}
        
        Args:
            config: 配置对象
        """
        self._config = config
        self._logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False
    
    def initialize(self) -> None:
        """初始化资源"""
        if self._initialized:
            return
        
        try:
            self._do_initialize()
            self._initialized = True
            self._logger.info(f"{self.__class__.__name__} initialized successfully")
        except Exception as e:
            self._logger.error(f"Failed to initialize: {e}")
            raise {class_name}Error(f"Initialization failed: {e}")
    
    def _do_initialize(self) -> None:
        """子类可以覆盖此方法进行自定义初始化"""
        pass
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """
        处理数据
        
        Args:
            data: 输入数据
            
        Returns:
            处理结果
            
        Raises:
            {class_name}Error: 处理失败时抛出
        """
        pass
    
    def validate(self, data: Any) -> bool:
        """
        验证输入数据
        
        Args:
            data: 待验证的数据
            
        Returns:
            验证是否通过
        """
        return data is not None
    
    def cleanup(self) -> None:
        """清理资源"""
        try:
            self._do_cleanup()
            self._initialized = False
            self._logger.info(f"{self.__class__.__name__} cleaned up")
        except Exception as e:
            self._logger.error(f"Error during cleanup: {e}")
    
    def _do_cleanup(self) -> None:
        """子类可以覆盖此方法进行自定义清理"""
        pass
    
    def __enter__(self):
        """上下文管理器入口"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()
        return False
    
    @property
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized
    
    @property
    def config(self) -> {class_name}Config:
        """获取配置"""
        return self._config


class {class_name}Builder:
    """{class_name}构建器"""
    
    def __init__(self):
        self._config = {class_name}Config()
    
    def with_option(self, value: Any) -> '{class_name}Builder':
        """设置选项"""
        # 设置配置
        return self
    
    def build(self) -> {class_name}:
        """构建实例"""
        # 返回具体的实现类
        raise NotImplementedError("Subclasses must implement build()")


# 使用示例
if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建配置
    config = {class_name}Config(
        {example_config}
    )
    
    # 使用上下文管理器
    with {class_name}(config) as instance:
        # 处理数据
        result = instance.process({example_input})
        print(f"Result: {result}")
