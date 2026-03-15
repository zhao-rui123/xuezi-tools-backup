import unittest.mock as mock
from unittest.mock import Mock, MagicMock, patch, AsyncMock, PropertyMock
from typing import Any, Callable, Dict, List, Optional, Set, Type
from dataclasses import dataclass
import functools
import importlib
import sys


EXTERNAL_MODULES = {
    'requests': ['get', 'post', 'put', 'delete', 'patch', 'Session'],
    'urllib': ['request', 'parse', 'error'],
    'http': ['client', 'server', 'cookies', 'cookiejar'],
    'json': ['loads', 'dumps'],
    'datetime': ['datetime', 'date', 'time', 'timedelta'],
    'time': ['time', 'sleep', 'gmtime', 'localtime'],
    'random': ['random', 'randint', 'choice', 'sample', 'shuffle'],
    'hashlib': ['md5', 'sha1', 'sha256', 'sha512'],
    'uuid': ['uuid', 'UUID'],
    'os': ['path', 'getcwd', 'getenv', 'environ'],
    'pathlib': ['Path'],
    'subprocess': ['run', 'Popen', 'call', 'check_output'],
    'socket': ['socket', 'create_connection'],
    'sqlite3': ['connect'],
    'psycopg2': ['connect'],
    'pymongo': ['MongoClient'],
    'redis': ['Redis', 'StrictRedis'],
    'elasticsearch': ['Elasticsearch'],
    'aiohttp': ['ClientSession', 'request'],
    'asyncio': ['sleep', 'create_task', 'gather'],
    'filelock': ['FileLock'],
}


@dataclass
class MockConfig:
    module_name: str
    function_names: List[str]
    return_values: Dict[str, Any]
    side_effects: Dict[str, Callable] = None


class DependencyAnalyzer:
    def __init__(self):
        self.external_modules = EXTERNAL_MODULES
    
    def analyze_function(self, func: Callable) -> List[MockConfig]:
        configs = []
        
        try:
            source = func.__code__.co_names
        except Exception:
            return configs
        
        for module_name, functions in self.external_modules.items():
            for func_name in functions:
                if func_name in source:
                    config = MockConfig(
                        module_name=module_name,
                        function_names=[func_name],
                        return_values={},
                        side_effects=None
                    )
                    configs.append(config)
        
        return configs
    
    def analyze_module(self, module_name: str) -> List[str]:
        if module_name in self.external_modules:
            return self.external_modules[module_name]
        return []


class AutoMocker:
    def __init__(self):
        self.analyzer = DependencyAnalyzer()
        self.active_patches = []
    
    def auto_mock_function(self, func: Callable) -> Callable:
        configs = self.analyzer.analyze_function(func)
        
        if not configs:
            return func
        
        patch_decorators = []
        for config in configs:
            target = f"{config.module_name}.{config.function_names[0]}"
            patch_decorators.append(patch(target, return_value=self._get_default_return(config.function_names[0])))
        
        def decorator(fn):
            for p in reversed(patch_decorators):
                fn = p(fn)
            return fn
        
        return decorator(func)
    
    def auto_mock_module(self, module_name: str, functions: List[str] = None) -> Dict[str, Mock]:
        if functions is None:
            functions = self.analyzer.analyze_module(module_name)
        
        mocks = {}
        
        for func_name in functions:
            mock_obj = self._create_mock_for_function(module_name, func_name)
            mocks[func_name] = mock_obj
        
        return mocks
    
    def create_context_manager_mock(self, module_name: str, func_name: str) -> MagicMock:
        mock_obj = MagicMock()
        mock_obj.__enter__ = MagicMock(return_value=MagicMock())
        mock_obj.__exit__ = MagicMock(return_value=False)
        return mock_obj
    
    def create_iterator_mock(self, module_name: str, func_name: str) -> MagicMock:
        mock_obj = MagicMock()
        mock_obj.__iter__ = MagicMock(return_value=iter([]))
        mock_obj.__next__ = MagicMock(side_effect=StopIteration)
        return mock_obj
    
    def _create_mock_for_function(self, module_name: str, func_name: str) -> Mock:
        common_patterns = {
            'get': MagicMock(status_code=200, json=MagicMock(return_value={})),
            'post': MagicMock(status_code=201, json=MagicMock(return_value={})),
            'put': MagicMock(status_code=200, json=MagicMock(return_value={})),
            'delete': MagicMock(status_code=204),
            'patch': MagicMock(status_code=200, json=MagicMock(return_value={})),
            'connect': MagicMock(),
            'run': MagicMock(return_value=MagicMock(returncode=0, stdout=b'', stderr=b'')),
            'sleep': MagicMock(),
            'random': MagicMock(return_value=0.5),
            'uuid': MagicMock(return_value='test-uuid-1234'),
            'md5': MagicMock(return_value=MagicMock(hexdigest=MagicMock(return_value='d41d8cd98f00b204e9800998ecf8427e'))),
            'sha256': MagicMock(return_value=MagicMock(hexdigest=MagicMock(return_value='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'))),
        }
        
        if func_name in common_patterns:
            return common_patterns[func_name]
        
        if func_name in ('open',):
            mock_file = MagicMock()
            mock_file.__enter__ = MagicMock(return_value=MagicMock(read=MagicMock(return_value=''), write=MagicMock()))
            mock_file.__exit__ = MagicMock(return_value=False)
            return mock_file
        
        return MagicMock()
    
    def _get_default_return(self, func_name: str) -> Any:
        returns = {
            'get': MagicMock(status_code=200, json=MagicMock(return_value={})),
            'post': MagicMock(status_code=201, json=MagicMock(return_value={})),
            'put': MagicMock(status_code=200, json=MagicMock(return_value={})),
            'delete': MagicMock(status_code=204),
            'sleep': None,
            'random': 0.5,
            'connect': MagicMock(),
        }
        return returns.get(func_name, MagicMock())
    
    def patch_external_calls(self, func: Callable) -> Callable:
        configs = self.analyzer.analyze_function(func)
        
        if not configs:
            return func
        
        patches = []
        for config in configs:
            for func_name in config.function_names:
                target = f"{config.module_name}.{func_name}"
                patches.append(patch(target, return_value=self._get_default_return(func_name)))
        
        def decorator(fn):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                with patch.multiple(*[p.target for p in patches], 
                                   **{p.target.split('.')[-1]: p.new for p in patches}):
                    return fn(*args, **kwargs)
            return wrapper
        
        return decorator


class MockFactory:
    @staticmethod
    def create_http_mock(method: str = 'get', status_code: int = 200, json_data: Any = None) -> MagicMock:
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json = MagicMock(return_value=json_data or {})
        mock_response.text = str(json_data or {})
        mock_response.content = b''
        mock_response.raise_for_status = MagicMock()
        
        if status_code >= 400:
            mock_response.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
        
        return mock_response
    
    @staticmethod
    def create_file_mock(content: str = '', mode: str = 'r') -> MagicMock:
        mock_file = MagicMock()
        
        if 'r' in mode:
            mock_file.read = MagicMock(return_value=content)
            mock_file.readlines = MagicMock(return_value=content.splitlines())
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=False)
        
        if 'w' in mode:
            mock_file.write = MagicMock()
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=False)
        
        return mock_file
    
    @staticmethod
    def create_db_mock(rows: List[Dict] = None) -> MagicMock:
        mock_cursor = MagicMock()
        mock_cursor.fetchall = MagicMock(return_value=rows or [])
        mock_cursor.fetchone = MagicMock(return_value=rows[0] if rows else None)
        mock_cursor.fetchmany = MagicMock(return_value=rows[:10] if rows else [])
        
        mock_connection = MagicMock()
        mock_connection.cursor = MagicMock(return_value=mock_cursor)
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=False)
        
        return mock_connection
    
    @staticmethod
    def create_api_response_mock(data: Any = None, error: str = None) -> MagicMock:
        mock_response = MagicMock()
        mock_response.status_code = 200 if not error else 500
        mock_response.json = MagicMock(return_value=data or {})
        mock_response.text = str(data or {})
        
        if error:
            mock_response.raise_for_status = MagicMock(side_effect=Exception(error))
        else:
            mock_response.raise_for_status = MagicMock()
        
        return mock_response
    
    @staticmethod
    def create_time_mock(return_value: float = 1234567890.0) -> MagicMock:
        mock_time = MagicMock()
        mock_time.time = MagicMock(return_value=return_value)
        mock_time.sleep = MagicMock()
        mock_time.gmtime = MagicMock(return_value=time.struct_time((2020, 1, 1, 0, 0, 0, 0, 1, 0)))
        mock_time.localtime = MagicMock(return_value=time.struct_time((2020, 1, 1, 8, 0, 0, 0, 1, 0)))
        return mock_time
    
    @staticmethod
    def create_random_mock(return_value: float = 0.5) -> MagicMock:
        mock_random = MagicMock()
        mock_random.random = MagicMock(return_value=return_value)
        mock_random.randint = MagicMock(return_value=1)
        mock_random.choice = MagicMock(return_value='choice')
        mock_random.sample = MagicMock(return_value=['a', 'b'])
        mock_random.shuffle = MagicMock()
        return mock_random


class MockContext:
    def __init__(self):
        self.patches = []
        self.mocks = {}
    
    def add_patch(self, target: str, return_value: Any = None, side_effect: Callable = None):
        p = patch(target, return_value=return_value, side_effect=side_effect)
        self.patches.append(p)
    
    def __enter__(self):
        for p in self.patches:
            p.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for p in self.patches:
            p.stop()
        return False


import time


def auto_mock(func: Callable = None, *, module: str = None, functions: List[str] = None) -> Callable:
    mocker = AutoMocker()
    
    def decorator(fn):
        if module and functions:
            for func_name in functions:
                target = f"{module}.{func_name}"
                patch(target, return_value=MagicMock()).start()
        
        return mocker.auto_mock_function(fn)
    
    if func is None:
        return decorator
    else:
        return decorator(func)
