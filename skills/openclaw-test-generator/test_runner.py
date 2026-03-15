import unittest
import sys
import io
import traceback
import time
import json
from typing import Any, Dict, List, Optional, TextIO
from dataclasses import dataclass, field
from pathlib import Path
from unittest import TextTestResult


class ColoredTextTestResult(TextTestResult):
    COLORS = {
        'reset': '\033[0m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m',
    }
    
    def __init__(self, stream: TextIO, descriptions: bool, verbosity: int):
        super().__init__(stream, descriptions, verbosity)
        self.stream = stream
    
    def _get_color(self, status: str) -> str:
        colors = {
            'ok': self.COLORS['green'],
            'fail': self.COLORS['red'],
            'error': self.COLORS['red'],
            'skip': self.COLORS['yellow'],
            'expected': self.COLORS['green'],
            'unexpected': self.COLORS['red'],
        }
        return colors.get(status, self.COLORS['white'])
    
    def _colored(self, text: str, status: str) -> str:
        color = self._get_color(status)
        return f"{color}{text}{self.COLORS['reset']}"
    
    def addSuccess(self, test: unittest.TestCase) -> None:
        super().addSuccess(test)
        if self.showAll:
            self.stream.writeln(self._colored(f"OK", 'ok'))
        elif self.dots:
            self.stream.write(self._colored('.', 'ok'))
    
    def addFailure(self, test: unittest.TestCase, err: tuple) -> None:
        super().addFailure(test, err)
        if self.showAll:
            self.stream.writeln(self._colored(f"FAIL: {str(err[1])}", 'fail'))
        elif self.dots:
            self.stream.write(self._colored('F', 'fail'))
    
    def addError(self, test: unittest.TestCase, err: tuple) -> None:
        super().addError(test, err)
        if self.showAll:
            self.stream.writeln(self._colored(f"ERROR: {str(err[1])}", 'error'))
        elif self.dots:
            self.stream.write(self._colored('E', 'error'))
    
    def addSkip(self, test: unittest.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        if self.showAll:
            self.stream.writeln(self._colored(f"SKIP: {reason}", 'skip'))
        elif self.dots:
            self.stream.write(self._colored('S', 'skip'))
    
    def addExpectedFailure(self, test: unittest.TestCase, err: tuple) -> None:
        super().addExpectedFailure(test, err)
        if self.showAll:
            self.stream.writeln(self._colored("EXPECTED FAILURE", 'expected'))
        elif self.dots:
            self.stream.write(self._colored('x', 'expected'))
    
    def addUnexpectedSuccess(self, test: unittest.TestCase) -> None:
        super().addUnexpectedSuccess(test)
        if self.showAll:
            self.stream.writeln(self._colored("UNEXPECTED SUCCESS", 'unexpected'))
        elif self.dots:
            self.stream.write(self._colored('u', 'unexpected'))


@dataclass
class TestResult:
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    expected_failures: int = 0
    unexpected_successes: int = 0
    duration: float = 0.0
    test_details: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'total': self.total,
            'passed': self.passed,
            'failed': self.failed,
            'errors': self.errors,
            'skipped': self.skipped,
            'expected_failures': self.expected_failures,
            'unexpected_successes': self.unexpected_successes,
            'duration': self.duration,
            'success_rate': f"{(self.passed / self.total * 100):.1f}%" if self.total > 0 else "0%",
            'tests': self.test_details
        }


class TestRunner:
    def __init__(self, verbosity: int = 2, capture_output: bool = True):
        self.verbosity = verbosity
        self.capture_output = capture_output
        self.result = TestResult()
        self._old_stdout = None
        self._old_stderr = None
    
    def run(self, test: unittest.TestSuite | unittest.TestCase) -> TestResult:
        self.result = TestResult()
        
        if isinstance(test, unittest.TestCase):
            suite = unittest.TestLoader().loadTestsFromTestCase(test.__class__)
        else:
            suite = test
        
        self.result.total = suite.countTestCases()
        
        stream = io.StringIO()
        
        test_result = ColoredTextTestResult(
            stream,
            descriptions=True,
            verbosity=self.verbosity
        )
        
        if self.capture_output:
            self._old_stdout = sys.stdout
            self._old_stderr = sys.stderr
            sys.stdout = stream
            sys.stderr = stream
        
        start_time = time.time()
        
        try:
            unittest.TextTestRunner(
                verbosity=self.verbosity,
                resultclass=ColoredTextTestResult,
                stream=stream
            ).run(suite)
        except Exception:
            pass
        
        test_result = unittest.TextTestRunner(
            verbosity=self.verbosity,
            resultclass=ColoredTextTestResult,
            stream=stream
        ).run(suite)
        
        self.result.passed = test_result.testsRun - len(test_result.failures) - len(test_result.errors) - len(test_result.skipped)
        self.result.failed = len(test_result.failures)
        self.result.errors = len(test_result.errors)
        self.result.skipped = len(test_result.skipped)
        
        for test_case, trace in test_result.failures:
            self.result.test_details.append({
                'name': str(test_case),
                'status': 'failed',
                'traceback': trace
            })
        
        for test_case, trace in test_result.errors:
            self.result.test_details.append({
                'name': str(test_case),
                'status': 'error',
                'traceback': trace
            })
        
        self.result.duration = time.time() - start_time
        
        if self.capture_output and self._old_stdout:
            sys.stdout = self._old_stdout
            sys.stderr = self._old_stderr
        
        return self.result
    
    def run_from_module(self, module_path: str) -> TestResult:
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        suite = unittest.TestLoader().loadTestsFromModule(module)
        
        return self.run(suite)
    
    def run_from_class(self, test_class: type) -> TestResult:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        return self.run(suite)
    
    def generate_report(self, result: TestResult = None) -> str:
        if result is None:
            result = self.result
        
        lines = []
        lines.append("=" * 60)
        lines.append("                    TEST REPORT")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append(f"{'Total Tests:':<25} {result.total}")
        lines.append(f"{'Passed:':<25} {self._colored(str(result.passed), 'green')}")
        
        if result.failed > 0:
            lines.append(f"{'Failed:':<25} {self._colored(str(result.failed), 'red')}")
        else:
            lines.append(f"{'Failed:':<25} {result.failed}")
        
        if result.errors > 0:
            lines.append(f"{'Errors:':<25} {self._colored(str(result.errors), 'red')}")
        else:
            lines.append(f"{'Errors:':<25} {result.errors}")
        
        lines.append(f"{'Skipped:':<25} {result.skipped}")
        lines.append(f"{'Duration:':<25} {result.duration:.3f}s")
        
        if result.total > 0:
            success_rate = (result.passed / result.total) * 100
            lines.append(f"{'Success Rate:':<25} {success_rate:.1f}%")
        
        lines.append("")
        
        if result.test_details:
            lines.append("Failed/Error Details:")
            lines.append("-" * 40)
            for detail in result.test_details:
                lines.append(f"\nTest: {detail['name']}")
                lines.append(f"Status: {self._colored(detail['status'].upper(), 'red')}")
                if 'traceback' in detail:
                    lines.append(f"Traceback:\n{detail['traceback']}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def _colored(self, text: str, color: str) -> str:
        colors = {
            'green': '\033[92m',
            'red': '\033[91m',
            'yellow': '\033[93m',
        }
        reset = '\033[0m'
        return f"{colors.get(color, '')}{text}{reset}"
    
    def save_report(self, result: TestResult = None, output_path: str = None) -> str:
        report = self.generate_report(result)
        
        if output_path:
            Path(output_path).write_text(report, encoding='utf-8')
        
        return report
    
    def save_json_report(self, result: TestResult = None, output_path: str = None) -> str:
        if result is None:
            result = self.result
        
        json_data = result.to_dict()
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        if output_path:
            Path(output_path).write_text(json_str, encoding='utf-8')
        
        return json_str


class SimpleTestRunner:
    @staticmethod
    def run(test_code: str, test_class_name: str = 'TestClass') -> TestResult:
        import importlib.util
        
        spec = importlib.util.spec_from_loader("dynamic_test", loader=None)
        module = importlib.util.module_from_spec(spec)
        
        exec(test_code, module.__dict__)
        
        test_class = getattr(module, test_class_name, None)
        if not test_class:
            for item in module.__dict__.values():
                if isinstance(item, type) and issubclass(item, unittest.TestCase):
                    test_class = item
                    break
        
        if not test_class:
            raise ValueError("No test class found in test code")
        
        runner = TestRunner(verbosity=2)
        return runner.run(test_class)
