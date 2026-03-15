import argparse
import sys
import ast
import inspect
from pathlib import Path
from typing import Any, Optional

from test_generator import TestGenerator
from test_runner import TestRunner
from mock_engine import AutoMocker, MockFactory, DependencyAnalyzer


def load_target_from_file(file_path: str, target_name: str = None) -> Any:
    module_path = Path(file_path)
    
    if not module_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    module_name = module_path.stem
    
    import importlib.util
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if target_name:
        if hasattr(module, target_name):
            return getattr(module, target_name)
        else:
            raise AttributeError(f"'{target_name}' not found in module")
    
    classes = [obj for name, obj in inspect.getmembers(module, inspect.isclass) 
               if name == module_name.capitalize() or not name.startswith('_')]
    
    functions = [obj for name, obj in inspect.getmembers(module, inspect.isfunction)
                 if not name.startswith('_')]
    
    if classes:
        return classes[0]
    elif functions:
        return functions[0]
    else:
        return module


def generate_tests_cli(args):
    target = load_target_from_file(args.file, args.target)
    
    generator = TestGenerator()
    
    if args.output:
        test_code = generator.generate_test_file(target, args.output)
        print(f"Test file generated: {args.output}")
    else:
        test_code = generator.generate_test_file(target)
        print(test_code)


def run_tests_cli(args):
    runner = TestRunner(verbosity=args.verbosity)
    
    if args.file:
        result = runner.run_from_module(args.file)
    elif args.class_name:
        module = __import__(args.module, fromlist=[args.class_name])
        test_class = getattr(module, args.class_name)
        result = runner.run(test_class)
    else:
        print("Error: Please specify --file or --module/--class", file=sys.stderr)
        return 1
    
    if args.report:
        runner.save_report(result, args.report)
        print(f"Report saved: {args.report}")
    
    if args.json_report:
        runner.save_json_report(result, args.json_report)
        print(f"JSON report saved: {args.json_report}")
    
    print(runner.generate_report(result))
    
    return 0 if result.failed == 0 and result.errors == 0 else 1


def analyze_dependencies_cli(args):
    target = load_target_from_file(args.file, args.target)
    
    analyzer = DependencyAnalyzer()
    
    if callable(target):
        configs = analyzer.analyze_function(target)
        print(f"External dependencies found for {target.__name__}:")
        for config in configs:
            print(f"  - {config.module_name}: {config.function_names}")
    else:
        print(f"External modules in file:")
        modules = analyzer.analyze_module(args.file)
        print(f"  {modules}")


def auto_mock_cli(args):
    target = load_target_from_file(args.file, args.target)
    
    mocker = AutoMocker()
    
    if callable(target):
        mock_func = mocker.auto_mock_function(target)
        print(f"Auto-mock applied to {target.__name__}")
        
        test_code = f'''
from unittest.mock import patch, MagicMock

# Auto-generated mocks for {target.__name__}
'''
        configs = mocker.analyzer.analyze_function(target)
        for config in configs:
            for func_name in config.function_names:
                target_path = f"{config.module_name}.{func_name}"
                test_code += f'''
@patch('{target_path}')
def test_{target.__name__}_mocked(mock_{func_name}):
    mock_{func_name}.return_value = MagicMock()
    # Your test code here
'''
        print(test_code)


def generate_edge_cases_cli(args):
    from test_generator import EdgeCaseGenerator
    
    target = load_target_from_file(args.file, args.target)
    
    generator = EdgeCaseGenerator()
    
    if callable(target):
        sig = inspect.signature(target)
        params = sig.parameters
        
        print(f"Edge cases for {target.__name__}:")
        for name, param in params.items():
            values = generator.generate_edge_values({'name': name, 'annotation': param.annotation})
            print(f"\n  {name}:")
            for v in values[:5]:
                print(f"    - {repr(v)}")


def main():
    parser = argparse.ArgumentParser(description='Auto Test Generator CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    gen_parser = subparsers.add_parser('generate', help='Generate test cases')
    gen_parser.add_argument('-f', '--file', required=True, help='Target Python file')
    gen_parser.add_argument('-t', '--target', help='Target function/class name')
    gen_parser.add_argument('-o', '--output', help='Output test file path')
    
    run_parser = subparsers.add_parser('run', help='Run tests')
    run_parser.add_argument('-f', '--file', help='Test file path')
    run_parser.add_argument('-m', '--module', help='Test module name')
    run_parser.add_argument('-c', '--class', dest='class_name', help='Test class name')
    run_parser.add_argument('-v', '--verbosity', type=int, default=2, help='Verbosity level')
    run_parser.add_argument('--report', help='Save text report to file')
    run_parser.add_argument('--json-report', help='Save JSON report to file')
    
    dep_parser = subparsers.add_parser('deps', help='Analyze dependencies')
    dep_parser.add_argument('-f', '--file', required=True, help='Target Python file')
    dep_parser.add_argument('-t', '--target', help='Target function/class name')
    
    mock_parser = subparsers.add_parser('mock', help='Generate auto-mock code')
    mock_parser.add_argument('-f', '--file', required=True, help='Target Python file')
    mock_parser.add_argument('-t', '--target', help='Target function/class name')
    
    edge_parser = subparsers.add_parser('edge', help='Generate edge cases')
    edge_parser.add_argument('-f', '--file', required=True, help='Target Python file')
    edge_parser.add_argument('-t', '--target', help='Target function/class name')
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        generate_tests_cli(args)
    elif args.command == 'run':
        sys.exit(run_tests_cli(args))
    elif args.command == 'deps':
        analyze_dependencies_cli(args)
    elif args.command == 'mock':
        auto_mock_cli(args)
    elif args.command == 'edge':
        generate_edge_cases_cli(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
