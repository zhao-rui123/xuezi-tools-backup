import ast
import inspect
import unittest
from typing import Any, Callable, Dict, List, Optional, Set, Type
from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass
class TestCase:
    name: str
    code: str
    test_type: str
    tags: List[str] = field(default_factory=list)


class SignatureAnalyzer:
    def __init__(self):
        self.builtin_types = {
            'int', 'float', 'str', 'bool', 'list', 'dict', 'set', 'tuple',
            'bytes', 'bytearray', 'memoryview', 'range', 'frozenset',
            'type', 'object', 'None', 'Any', 'Optional', 'Union', 'List',
            'Dict', 'Set', 'Tuple', 'Callable', 'Type', 'Iterable'
        }
    
    def analyze_function(self, func: Callable) -> Dict[str, Any]:
        sig = inspect.signature(func)
        params = {}
        
        for name, param in sig.parameters.items():
            param_info = {
                'name': name,
                'has_default': param.default is not inspect.Parameter.empty,
                'default': param.default if param.default is not inspect.Parameter.empty else None,
                'kind': param.kind.name,
                'annotation': param.annotation if param.annotation is not inspect.Parameter.empty else None
            }
            params[name] = param_info
        
        return {
            'name': func.__name__,
            'params': params,
            'return_annotation': sig.return_annotation if sig.return_annotation is not inspect.Signature.empty else None,
            'is_async': inspect.iscoroutinefunction(func),
            'is_method': inspect.ismethod(func)
        }
    
    def infer_test_values(self, param_info: Dict) -> List[Any]:
        annotation = param_info.get('annotation')
        name = param_info.get('name', '').lower()
        has_default = param_info.get('has_default', False)
        default = param_info.get('default')
        
        values = []
        
        if annotation:
            type_name = self._get_type_name(annotation)
            
            if type_name in ('int', 'float'):
                values = [0, 1, -1, 100, -100]
                if has_default and isinstance(default, (int, float)):
                    values.append(default)
                    
            elif type_name == 'str':
                values = ['', 'test', 'hello world', 'a' * 100]
                if has_default and isinstance(default, str):
                    values.append(default)
                    
            elif type_name in ('list', 'List'):
                values = [[], [1, 2, 3], ['a', 'b'], [None]]
                if has_default and isinstance(default, list):
                    values.append(default)
                    
            elif type_name in ('dict', 'Dict'):
                values = [{}, {'key': 'value'}, {'a': 1, 'b': 2}]
                if has_default and isinstance(default, dict):
                    values.append(default)
                    
            elif type_name in ('bool', 'bool'):
                values = [True, False]
                if has_default and isinstance(default, bool):
                    values.append(default)
        
        if not values:
            if 'id' in name or 'count' in name or 'num' in name:
                values = [0, 1, 100, -1]
            elif 'name' in name or 'title' in name or 'text' in name:
                values = ['', 'test', 'sample']
            elif 'enabled' in name or 'active' in name or 'flag' in name:
                values = [True, False]
            else:
                values = [None, '', 0, [], {}]
        
        return values[:5]
    
    def _get_type_name(self, annotation: Any) -> str:
        if annotation is None:
            return 'None'
        name = getattr(annotation, '__name__', str(annotation))
        name = name.replace('typing.', '')
        return name


class FunctionTestGenerator:
    def __init__(self):
        self.analyzer = SignatureAnalyzer()
        self.edge_case_generator = EdgeCaseGenerator()
    
    def generate_tests(self, func: Callable, module_name: str = 'test_module') -> List[TestCase]:
        test_cases = []
        sig_info = self.analyzer.analyze_function(func)
        
        normal_tests = self._generate_normal_tests(func, sig_info)
        test_cases.extend(normal_tests)
        
        edge_tests = self._generate_edge_tests(func, sig_info)
        test_cases.extend(edge_tests)
        
        exception_tests = self._generate_exception_tests(func, sig_info)
        test_cases.extend(exception_tests)
        
        return test_cases
    
    def _generate_normal_tests(self, func: Callable, sig_info: Dict) -> List[TestCase]:
        tests = []
        params = sig_info['params']
        
        test_values = {}
        for name, info in params.items():
            test_values[name] = self.analyzer.infer_test_values(info)
        
        import itertools
        combinations = list(itertools.product(*test_values.values()))
        param_names = list(params.keys())
        
        max_combos = min(5, len(combinations))
        
        for i, combo in enumerate(combinations[:max_combos]):
            args_dict = dict(zip(param_names, combo))
            
            test_code = self._build_test_code(func, args_dict, sig_info)
            
            test_name = f"test_{func.__name__}_normal_{i+1}"
            tests.append(TestCase(
                name=test_name,
                code=test_code,
                test_type='normal',
                tags=['normal', 'signature_based']
            ))
        
        return tests
    
    def _build_test_code(self, func: Callable, args: Dict, sig_info: Dict) -> str:
        func_name = func.__name__
        is_async = sig_info.get('is_async', False)
        
        args_str = ', '.join(f'{k}={repr(v)}' for k, v in args.items())
        
        if is_async:
            return f'''async def test_{func_name}_case(self):
    result = await {func_name}({args_str})
    self.assertIsNotNone(result)'''
        else:
            return f'''def test_{func_name}_case(self):
    result = {func_name}({args_str})
    self.assertIsNotNone(result)'''
    
    def _generate_edge_tests(self, func: Callable, sig_info: Dict) -> List[TestCase]:
        tests = []
        params = sig_info['params']
        
        for name, info in params.items():
            edge_values = self.edge_case_generator.generate_edge_values(info)
            
            for value in edge_values[:3]:
                args = {name: value}
                test_code = self._build_test_code(func, args, sig_info)
                
                test_name = f"test_{func.__name__}_edge_{name}_{value!r}"
                tests.append(TestCase(
                    name=test_name,
                    code=test_code,
                    test_type='edge',
                    tags=['edge', name]
                ))
        
        return tests
    
    def _generate_exception_tests(self, func: Callable, sig_info: Dict) -> List[TestCase]:
        tests = []
        params = sig_info['params']
        
        for name in params.keys():
            invalid_values = [None, [], {}, '', -1, float('inf'), float('nan')]
            
            for value in invalid_values[:2]:
                args = {name: value}
                test_code = self._build_exception_test(func, args, sig_info)
                
                test_name = f"test_{func.__name__}_exception_{name}"
                tests.append(TestCase(
                    name=test_name,
                    code=test_code,
                    test_type='exception',
                    tags=['exception', 'error_handling']
                ))
        
        return tests
    
    def _build_exception_test(self, func: Callable, args: Dict, sig_info: Dict) -> str:
        func_name = func.__name__
        is_async = sig_info.get('is_async', False)
        
        args_str = ', '.join(f'{k}={repr(v)}' for k, v in args.items())
        
        if is_async:
            return f'''async def test_{func_name}_exception(self):
    with self.assertRaises(Exception):
        await {func_name}({args_str})'''
        else:
            return f'''def test_{func_name}_exception(self):
    with self.assertRaises(Exception):
        {func_name}({args_str})'''


class EdgeCaseGenerator:
    def generate_edge_values(self, param_info: Dict) -> List[Any]:
        annotation = param_info.get('annotation')
        name = param_info.get('name', '').lower()
        
        values = []
        
        if annotation:
            type_name = self._get_type_name(annotation)
            
            if type_name in ('int', 'float'):
                values = [
                    0, 1, -1, 
                    2147483647, -2147483648,
                    float('inf'), float('-inf'), float('nan')
                ]
            elif type_name == 'str':
                values = ['', ' ', '\n', '\t', 'a' * 10000, '\x00']
            elif type_name in ('list', 'List'):
                values = [[], [None], list(range(1000))]
            elif type_name in ('dict', 'Dict'):
                values = [{}, {None: None}, {i: i for i in range(100)}]
        
        if not values:
            values = [None, '', 0, [], {}, object()]
        
        return values
    
    def _get_type_name(self, annotation: Any) -> str:
        if annotation is None:
            return 'None'
        name = getattr(annotation, '__name__', str(annotation))
        name = name.replace('typing.', '')
        return name


class ClassTestGenerator:
    def __init__(self):
        self.analyzer = SignatureAnalyzer()
        self.edge_gen = EdgeCaseGenerator()
    
    def generate_tests(self, cls: Type, module_name: str = 'test_module') -> List[TestCase]:
        test_cases = []
        
        init_tests = self._generate_init_tests(cls)
        test_cases.extend(init_tests)
        
        method_tests = self._generate_method_tests(cls)
        test_cases.extend(method_tests)
        
        property_tests = self._generate_property_tests(cls)
        test_cases.extend(property_tests)
        
        return test_cases
    
    def _generate_init_tests(self, cls: Type) -> List[TestCase]:
        tests = []
        
        init_method = getattr(cls, '__init__', None)
        if not init_method or init_method is object.__init__:
            default_init = f'''def test_{cls.__name__}_init_default(self):
    instance = {cls.__name__}()
    self.assertIsInstance(instance, {cls.__name__})'''
            tests.append(TestCase(
                name=f"test_{cls.__name__}_init_default",
                code=default_init,
                test_type='init',
                tags=['init', 'default']
            ))
            return tests
        
        sig_info = self.analyzer.analyze_function(init_method)
        params = sig_info['params']
        
        if len(params) == 1:
            simple_init = f'''def test_{cls.__name__}_init_simple(self):
    instance = {cls.__name__}()
    self.assertIsInstance(instance, {cls.__name__})'''
            tests.append(TestCase(
                name=f"test_{cls.__name__}_init_simple",
                code=simple_init,
                test_type='init',
                tags=['init', 'simple']
            ))
        
        test_values = {}
        for name, info in params.items():
            if name == 'self':
                continue
            test_values[name] = self.analyzer.infer_test_values(info)
        
        import itertools
        if test_values:
            combinations = list(itertools.product(*test_values.values()))
            for combo in combinations[:3]:
                # 过滤掉空值
                filtered_combo = [(k, v) for k, v in zip(test_values.keys(), combo) if v is not None and v != ""]
                if not filtered_combo:
                    continue
                args_dict = dict(filtered_combo)
                args_str = ', '.join(f'{k}={repr(v)}' for k, v in args_dict.items())
                
                init_code = f'''def test_{cls.__name__}_init_with_args(self):
    instance = {cls.__name__}({args_str})
    self.assertIsInstance(instance, {cls.__name__})
'''
                
                tests.append(TestCase(
                    name=f"test_{cls.__name__}_init_with_args",
                    code=init_code,
                    test_type='init',
                    tags=['init', 'with_args']
                ))
                break
        
        return tests
    
    def _generate_method_tests(self, cls: Type) -> List[TestCase]:
        tests = []
        
        skip_methods = {'__init__', '__new__', '__class__', '__del__', '__dict__', '__module__'}
        
        for name in dir(cls):
            if name.startswith('_') and name not in ('__str__', '__repr__', '__len__', '__eq__', '__hash__'):
                continue
            if name in skip_methods:
                continue
            
            attr = getattr(cls, name, None)
            if not callable(attr) or isinstance(attr, property):
                continue
            
            try:
                sig_info = self.analyzer.analyze_function(attr)
                
                test_code = f'''def test_{cls.__name__}_{name}(self):
    instance = {cls.__name__}()
    try:
        result = instance.{name}()
        self.assertIsNotNone(result)
    except Exception as e:
        self.skipTest(f"Method raised: {{e}}")'''
                
                tests.append(TestCase(
                    name=f"test_{cls.__name__}_{name}",
                    code=test_code,
                    test_type='method',
                    tags=['method', name]
                ))
            except Exception:
                continue
        
        return tests
    
    def _generate_property_tests(self, cls: Type) -> List[TestCase]:
        tests = []
        
        for name in dir(cls):
            attr = getattr(cls, name, None)
            if isinstance(attr, property):
                if attr.fget:
                    test_code = f'''def test_{cls.__name__}_{name}_getter(self):
    instance = {cls.__name__}()
    try:
        result = instance.{name}
    except AttributeError:
        self.skipTest("Property not accessible")'''
                    
                    tests.append(TestCase(
                        name=f"test_{cls.__name__}_{name}_getter",
                        code=test_code,
                        test_type='property',
                        tags=['property', 'getter']
                    ))
                
                if attr.fset:
                    test_code = f'''def test_{cls.__name__}_{name}_setter(self):
    instance = {cls.__name__}()
    try:
        instance.{name} = "test_value"
    except AttributeError:
        self.skipTest("Property not settable")'''
                    
                    tests.append(TestCase(
                        name=f"test_{cls.__name__}_{name}_setter",
                        code=test_code,
                        test_type='property',
                        tags=['property', 'setter']
                    ))
        
        return tests


class TestGenerator:
    def __init__(self):
        self.func_generator = FunctionTestGenerator()
        self.class_generator = ClassTestGenerator()
    
    def generate(self, target, module_name: str = 'test_module') -> List[TestCase]:
        if inspect.isclass(target):
            return self.class_generator.generate_tests(target, module_name)
        elif callable(target):
            return self.func_generator.generate_tests(target, module_name)
        else:
            raise ValueError(f"Cannot generate tests for {type(target)}")
    
    def generate_test_file(self, target, output_path: str = None) -> str:
        test_cases = self.generate(target)
        
        module_name = getattr(target, '__module__', 'test_module')
        class_name = f"Test{getattr(target, '__name__', 'Target').capitalize()}"
        
        imports = ["import unittest", f"import {module_name}"]
        
        class_code = [f"class {class_name}(unittest.TestCase):"]
        
        for tc in test_cases:
            class_code.append(f"    {tc.code}")
        
        test_code = '\n\n'.join(imports) + '\n\n\n' + '\n\n'.join(class_code) + '\n\n'
        test_code += "if __name__ == '__main__':\n    unittest.main()"
        
        if output_path:
            Path(output_path).write_text(test_code, encoding='utf-8')
        
        return test_code
