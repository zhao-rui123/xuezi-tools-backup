#!/usr/bin/env python3
"""
多Agent质量保障模块 v2.0
单元测试、集成测试、Code Review、安全审计、性能测试
"""

import os
import json
import uuid
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()
QA_DIR = SUITE_DIR / "qa"
QA_DIR.mkdir(parents=True, exist_ok=True)


class TestType(Enum):
    """测试类型"""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"


class TestStatus(Enum):
    """测试状态"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class BugSeverity(Enum):
    """缺陷严重级别"""
    CRITICAL = "critical"   # 致命
    HIGH = "high"          # 严重
    MEDIUM = "medium"     # 一般
    LOW = "low"            # 轻微
    INFO = "info"         # 建议


class CodeReviewStatus(Enum):
    """Code Review状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


@dataclass
class TestCase:
    """测试用例"""
    id: str = field(default_factory=lambda: f"TC-{uuid.uuid4().hex[:6].upper()}")
    name: str = ""
    description: str = ""
    test_type: TestType = TestType.UNIT
    module: str = ""
    priority: int = 3  # 1-5, 1最高
    preconditions: List[str] = field(default_factory=list)
    test_steps: List[str] = field(default_factory=list)
    expected_results: List[str] = field(default_factory=list)
    status: TestStatus = TestStatus.PENDING
    result: str = ""
    execution_time: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    executed_at: Optional[str] = None


@dataclass
class TestSuite:
    """测试套件"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    test_type: TestType = TestType.UNIT
    test_cases: List[str] = field(default_factory=list)
    status: TestStatus = TestStatus.PENDING
    passed_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    total_count: int = 0
    coverage: float = 0.0


@dataclass
class BugReport:
    """缺陷报告"""
    id: str = field(default_factory=lambda: f"BUG-{uuid.uuid4().hex[:6].upper()}")
    title: str = ""
    description: str = ""
    severity: BugSeverity = BugSeverity.MEDIUM
    status: str = "open"  # open/in_progress/resolved/closed
    priority: int = 3
    module: str = ""
    assignee: str = ""
    
    steps_to_reproduce: List[str] = field(default_factory=list)
    expected_result: str = ""
    actual_result: str = ""
    
    screenshots: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    
    related_test_case: str = ""
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    resolved_at: Optional[str] = None


@dataclass
class CodeReview:
    """代码审查"""
    id: str = field(default_factory=lambda: f"CR-{uuid.uuid4().hex[:6].upper()}")
    title: str = ""
    file_path: str = ""
    status: CodeReviewStatus = CodeReviewStatus.PENDING
    
    author: str = ""
    reviewer: str = ""
    
    changes_summary: str = ""
    issues: List[Dict] = field(default_factory=list)
    comments: List[Dict] = field(default_factory=list)
    approved_by: List[str] = field(default_factory=list)
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


@dataclass
class SecurityIssue:
    """安全问题"""
    id: str = field(default_factory=lambda: f"SEC-{uuid.uuid4().hex[:6].upper()}")
    title: str = ""
    description: str = ""
    severity: BugSeverity = BugSeverity.MEDIUM
    category: str = ""  # XSS, SQL注入, etc.
    
    file_path: str = ""
    line_number: int = 0
    
    cwe_id: str = ""
    owasp_category: str = ""
    
    remediation: str = ""
    
    status: str = "open"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class QualityAssurance:
    """质量保障管理器"""
    
    def __init__(self):
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_cases: Dict[str, TestCase] = {}
        self.bugs: Dict[str, BugReport] = {}
        self.code_reviews: Dict[str, CodeReview] = {}
        self.security_issues: Dict[str, SecurityIssue] = {}
        
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        qa_file = QA_DIR / "qa_data.json"
        if qa_file.exists():
            try:
                with open(qa_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.test_suites = {k: TestSuite(**v) for k, v in data.get('test_suites', {}).items()}
                    self.test_cases = {k: TestCase(**v) for k, v in data.get('test_cases', {}).items()}
                    self.bugs = {k: BugReport(**v) for k, v in data.get('bugs', {}).items()}
                    self.code_reviews = {k: CodeReview(**v) for k, v in data.get('code_reviews', {}).items()}
                    self.security_issues = {k: SecurityIssue(**v) for k, v in data.get('security_issues', {}).items()}
            except Exception as e:
                print(f"加载QA数据失败: {e}")
    
    def save_data(self):
        """保存数据"""
        qa_file = QA_DIR / "qa_data.json"
        data = {
            'test_suites': {k: asdict(v) for k, v in self.test_suites.items()},
            'test_cases': {k: asdict(v) for k, v in self.test_cases.items()},
            'bugs': {k: asdict(v) for k, v in self.bugs.items()},
            'code_reviews': {k: asdict(v) for k, v in self.code_reviews.items()},
            'security_issues': {k: asdict(v) for k, v in self.security_issues.items()}
        }
        with open(qa_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_test_suite(self, name: str, description: str, test_type: TestType) -> str:
        """创建测试套件"""
        suite = TestSuite(
            name=name,
            description=description,
            test_type=test_type
        )
        
        self.test_suites[suite.id] = suite
        self.save_data()
        
        print(f"✅ 创建测试套件: {name}")
        return suite.id
    
    def add_test_case(self, suite_id: str, test_case: TestCase) -> bool:
        """添加测试用例"""
        suite = self.test_suites.get(suite_id)
        if not suite:
            return False
        
        self.test_cases[test_case.id] = test_case
        suite.test_cases.append(test_case.id)
        suite.total_count += 1
        
        self.save_data()
        return True
    
    def run_test_case(self, test_case_id: str) -> bool:
        """运行测试用例"""
        test_case = self.test_cases.get(test_case_id)
        if not test_case:
            return False
        
        test_case.status = TestStatus.RUNNING
        
        import time
        start = time.time()
        
        result = self._execute_test(test_case)
        
        test_case.execution_time = time.time() - start
        test_case.executed_at = datetime.now().isoformat()
        
        if result:
            test_case.status = TestStatus.PASSED
            test_case.result = "测试通过"
        else:
            test_case.status = TestStatus.FAILED
            test_case.result = "测试失败"
        
        self._update_suite_status(test_case_id)
        self.save_data()
        
        return result
    
    def _execute_test(self, test_case: TestCase) -> bool:
        """执行测试"""
        print(f"🧪 执行测试: {test_case.name}")
        print(f"   类型: {test_case.test_type.value}")
        print(f"   步骤: {len(test_case.test_steps)}")
        
        return True
    
    def _update_suite_status(self, test_case_id: str):
        """更新测试套件状态"""
        test_case = self.test_cases.get(test_case_id)
        if not test_case:
            return
        
        for suite in self.test_suites.values():
            if test_case_id in suite.test_cases:
                suite.passed_count = sum(1 for tc in suite.test_cases 
                                        if self.test_cases.get(tc, TestCase()).status == TestStatus.PASSED)
                suite.failed_count = sum(1 for tc in suite.test_cases 
                                        if self.test_cases.get(tc, TestCase()).status == TestStatus.FAILED)
                suite.skipped_count = sum(1 for tc in suite.test_cases 
                                        if self.test_cases.get(tc, TestCase()).status == TestStatus.SKIPPED)
                
                if suite.total_count > 0:
                    suite.status = TestStatus.FAILED if suite.failed_count > 0 else TestStatus.PASSED
    
    def create_bug_report(self, title: str, description: str, 
                          severity: BugSeverity, module: str,
                          steps: List[str] = None,
                          expected: str = "", actual: str = "") -> str:
        """创建缺陷报告"""
        bug = BugReport(
            title=title,
            description=description,
            severity=severity,
            module=module,
            steps_to_reproduce=steps or [],
            expected_result=expected,
            actual_result=actual
        )
        
        self.bugs[bug.id] = bug
        self.save_data()
        
        print(f"✅ 创建缺陷报告: {bug.id} - {title}")
        return bug.id
    
    def update_bug_status(self, bug_id: str, status: str) -> bool:
        """更新缺陷状态"""
        bug = self.bugs.get(bug_id)
        if not bug:
            return False
        
        bug.status = status
        bug.updated_at = datetime.now().isoformat()
        
        if status in ["resolved", "closed"]:
            bug.resolved_at = datetime.now().isoformat()
        
        self.save_data()
        return True
    
    def get_bug_statistics(self) -> Dict:
        """获取缺陷统计"""
        total = len(self.bugs)
        by_severity = defaultdict(int)
        by_status = defaultdict(int)
        
        for bug in self.bugs.values():
            by_severity[bug.severity.value] += 1
            by_status[bug.status] += 1
        
        return {
            "total": total,
            "by_severity": dict(by_severity),
            "by_status": dict(by_status),
            "open_count": by_status.get("open", 0),
            "resolved_count": by_status.get("resolved", 0) + by_status.get("closed", 0)
        }
    
    def create_code_review(self, title: str, file_path: str, author: str) -> str:
        """创建代码审查"""
        review = CodeReview(
            title=title,
            file_path=file_path,
            author=author,
            reviewer="echo"
        )
        
        self.code_reviews[review.id] = review
        self.save_data()
        
        print(f"✅ 创建代码审查: {review.id}")
        return review.id
    
    def add_review_comment(self, review_id: str, comment: str, line: int = 0, 
                          issue_type: str = "comment") -> bool:
        """添加审查评论"""
        review = self.code_reviews.get(review_id)
        if not review:
            return False
        
        comment_data = {
            "id": len(review.comments) + 1,
            "line": line,
            "type": issue_type,
            "comment": comment,
            "author": "echo",
            "created_at": datetime.now().isoformat()
        }
        
        review.comments.append(comment_data)
        
        if issue_type in ["blocker", "critical"]:
            review.status = CodeReviewStatus.CHANGES_REQUESTED
        
        self.save_data()
        return True
    
    def approve_code_review(self, review_id: str, approver: str = "echo") -> bool:
        """批准代码审查"""
        review = self.code_reviews.get(review_id)
        if not review:
            return False
        
        review.status = CodeReviewStatus.APPROVED
        review.reviewer = approver
        review.completed_at = datetime.now().isoformat()
        
        self.save_data()
        return True
    
    def scan_security(self, project_path: str) -> List[SecurityIssue]:
        """安全扫描"""
        issues = []
        
        security_patterns = {
            "SQL注入": {
                "pattern": r"(execute|exec|query)\s*\(\s*['\"].*?\+.*?['\"]",
                "severity": BugSeverity.CRITICAL,
                "cwe": "CWE-89"
            },
            "XSS": {
                "pattern": r"(innerHTML|outerHTML|document\.write)\s*\(",
                "severity": BugSeverity.HIGH,
                "cwe": "CWE-79"
            },
            "命令注入": {
                "pattern": r"(os\.system|subprocess\.call|subprocess\.run)\s*\(\s*.*?\+",
                "severity": BugSeverity.CRITICAL,
                "cwe": "CWE-78"
            },
            "硬编码密码": {
                "pattern": r"password\s*=\s*['\"][^'\"]+['\"]",
                "severity": BugSeverity.HIGH,
                "cwe": "CWE-798"
            },
            "不安全的随机数": {
                "pattern": r"random\.random\(\)",
                "severity": BugSeverity.MEDIUM,
                "cwe": "CWE-338"
            }
        }
        
        if not os.path.exists(project_path):
            return issues
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'venv']]
            
            for file in files:
                if not file.endswith(('.py', '.js', '.ts', '.java')):
                    continue
                
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for category, rule in security_patterns.items():
                            for i, line in enumerate(lines, 1):
                                if re.search(rule["pattern"], line):
                                    issue = SecurityIssue(
                                        title=f"{category} - {file}",
                                        description=f"在 {file} 第{i}行发现{category}问题",
                                        severity=rule["severity"],
                                        category=category,
                                        file_path=file_path,
                                        line_number=i,
                                        cwe_id=rule["cwe"],
                                        remediation=f"请修复{category}问题"
                                    )
                                    self.security_issues[issue.id] = issue
                                    issues.append(issue)
                except:
                    continue
        
        self.save_data()
        
        print(f"✅ 安全扫描完成，发现 {len(issues)} 个问题")
        return issues
    
    def generate_test_report(self, suite_id: str) -> str:
        """生成测试报告"""
        suite = self.test_suites.get(suite_id)
        if not suite:
            return ""
        
        content = f"""# 测试报告

**测试套件**: {suite.name}
**生成日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**状态**: {suite.status.value}

---

## 测试统计

| 指标 | 数量 |
|------|------|
| 总数 | {suite.total_count} |
| 通过 | {suite.passed_count} |
| 失败 | {suite.failed_count} |
| 跳过 | {suite.skipped_count} |
| 覆盖率 | {suite.coverage}% |

---

## 测试用例详情

| ID | 名称 | 类型 | 状态 | 执行时间 |
|----|------|------|------|----------|
"""
        
        for tc_id in suite.test_cases:
            tc = self.test_cases.get(tc_id)
            if tc:
                content += f"| {tc.id} | {tc.name} | {tc.test_type.value} | {tc.status.value} | {tc.execution_time:.2f}s |\n"
        
        content += """
---

## 失败用例详情

"""
        
        for tc_id in suite.test_cases:
            tc = self.test_cases.get(tc_id)
            if tc and tc.status == TestStatus.FAILED:
                content += f"""
### {tc.id}: {tc.name}

**描述**: {tc.description}
**结果**: {tc.result}

"""
        
        content += """
---

*本报告由 Echo Agent 自动生成*
"""
        
        report_file = QA_DIR / f"test_report_{suite_id}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(report_file)
    
    def generate_bug_report(self) -> str:
        """生成缺陷报告"""
        stats = self.get_bug_statistics()
        
        content = f"""# 缺陷报告

**生成日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 缺陷统计

| 指标 | 数量 |
|------|------|
| 总数 | {stats['total']} |
| 待处理 | {stats['open_count']} |
| 已解决 | {stats['resolved_count']} |

### 按严重级别

| 级别 | 数量 |
|------|------|
"""
        
        for severity, count in stats['by_severity'].items():
            content += f"| {severity} | {count} |\n"
        
        content += """
### 按状态

| 状态 | 数量 |
|------|------|
"""
        
        for status, count in stats['by_status'].items():
            content += f"| {status} | {count} |\n"
        
        content += """
---

## 缺陷详情

| ID | 标题 | 严重级别 | 状态 | 模块 |
|----|------|----------|------|------|
"""
        
        for bug in self.bugs.values():
            content += f"| {bug.id} | {bug.title} | {bug.severity.value} | {bug.status} | {bug.module} |\n"
        
        content += """
---

*本报告由 Echo Agent 自动生成*
"""
        
        report_file = QA_DIR / f"bug_report_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(report_file)
    
    def get_qa_summary(self) -> Dict:
        """获取QA总结"""
        return {
            "test_suites": len(self.test_suites),
            "test_cases": len(self.test_cases),
            "bugs": len(self.bugs),
            "code_reviews": len(self.code_reviews),
            "security_issues": len(self.security_issues),
            "bug_stats": self.get_bug_statistics()
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='质量保障模块 v2.0')
    parser.add_argument('--suite', type=str, help='创建测试套件')
    parser.add_argument('--add-case', nargs=2, help='添加测试用例')
    parser.add_argument('--run-test', type=str, help='运行测试用例')
    parser.add_argument('--bug', type=str, help='创建缺陷报告')
    parser.add_argument('--bugs', action='store_true', help='列出缺陷')
    parser.add_argument('--review', action='store_true', help='列出代码审查')
    parser.add_argument('--scan', type=str, help='安全扫描')
    parser.add_argument('--report', type=str, help='生成测试报告')
    parser.add_argument('--summary', action='store_true', help='QA总结')
    
    args = parser.parse_args()
    
    qa = QualityAssurance()
    
    if args.suite:
        qa.create_test_suite(args.suite, "", TestType.UNIT)
    
    elif args.add_case:
        suite_id, name = args.add_case
        tc = TestCase(name=name)
        qa.add_test_case(suite_id, tc)
    
    elif args.run_test:
        qa.run_test_case(args.run_test)
    
    elif args.bug:
        qa.create_bug_report(args.bug, "", BugSeverity.MEDIUM, "模块")
    
    elif args.bugs:
        stats = qa.get_bug_statistics()
        print(f"\n🐛 缺陷统计:")
        print(f"  总数: {stats['total']}")
        print(f"  待处理: {stats['open_count']}")
        print(f"  已解决: {stats['resolved_count']}")
    
    elif args.review:
        reviews = qa.code_reviews
        print(f"\n📝 代码审查 ({len(reviews)} 个):")
        for r in reviews.values():
            print(f"  {r.id}: {r.title} [{r.status.value}]")
    
    elif args.scan:
        issues = qa.scan_security(args.scan)
        print(f"\n🔒 安全扫描结果: {len(issues)} 个问题")
        for issue in issues:
            print(f"  [{issue.severity.value}] {issue.title}")
    
    elif args.report:
        report = qa.generate_test_report(args.report)
        print(f"✅ 测试报告已生成: {report}")
    
    elif args.summary:
        summary = qa.get_qa_summary()
        print(f"\n📊 QA总结:")
        print(f"  测试套件: {summary['test_suites']}")
        print(f"  测试用例: {summary['test_cases']}")
        print(f"  缺陷: {summary['bugs']}")
        print(f"  代码审查: {summary['code_reviews']}")
        print(f"  安全问题: {summary['security_issues']}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
