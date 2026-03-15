# OpenClaw 使用指南

## 快速开始

### 1. 代码审查

```bash
# 基本用法
./openclaw review myfile.py

# 审查目录
./openclaw review ./src

# 生成HTML报告
./openclaw review ./src --format html --output report.html

# 只显示严重问题
./openclaw review ./src --min-severity high

# JSON格式输出
./openclaw review ./src --format json --output report.json
```

### 2. 代码优化

```bash
# 分析优化机会
./openclaw optimize myfile.py

# 自动应用高信心度优化
./openclaw optimize ./src --apply

# 模拟运行（不实际修改）
./openclaw optimize ./src --apply --dry-run

# 只显示高信心度优化
./openclaw optimize ./src --min-confidence high
```

### 3. 自动修复

```bash
# 查看可修复的问题
./openclaw fix myfile.py

# 应用修复
./openclaw fix myfile.py --apply

# 模拟运行
./openclaw fix ./src --apply --dry-run

# 只应用高信心度修复
./openclaw fix ./src --apply --min-confidence high
```

### 4. 安全检查

```bash
# 安全扫描
./openclaw security myfile.py

# 生成HTML安全报告
./openclaw security ./src --format html --output security_report.html

# 只显示高危漏洞
./openclaw security ./src --min-severity high

# JSON格式输出
./openclaw security ./src --format json
```

## 示例演示

### 测试示例代码

```bash
# 进入技能包目录
cd openclaw-coding-skill

# 运行代码审查（示例代码包含各种问题）
./openclaw review examples/example_bad_code.py

# 运行安全检查
./openclaw security examples/example_bad_code.py

# 运行代码优化分析
./openclaw optimize examples/example_bad_code.py

# 运行自动修复（查看可修复的问题）
./openclaw fix examples/example_bad_code.py
```

## 集成到开发工作流

### Git Pre-commit Hook

创建 `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# OpenClaw Pre-commit Hook

echo "🔍 Running OpenClaw code checks..."

# 获取暂存的Python文件
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)

if [ -z "$STAGED_FILES" ]; then
    echo "✅ No Python files to check"
    exit 0
fi

# 代码审查
echo "📋 Running code review..."
for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        python scripts/code_review.py "$file" --min-severity high
        if [ $? -ne 0 ]; then
            echo "❌ Code review failed for $file"
            echo "Run './openclaw review $file' for details"
            exit 1
        fi
    fi
done

# 安全检查
echo "🔒 Running security check..."
python scripts/security_check.py . --min-severity high
if [ $? -ne 0 ]; then
    echo "❌ Security check failed!"
    echo "Run './openclaw security .' for details"
    exit 1
fi

echo "✅ All checks passed!"
```

设置权限:
```bash
chmod +x .git/hooks/pre-commit
```

### GitHub Actions 集成

创建 `.github/workflows/code-quality.yml`:

```yaml
name: Code Quality

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Run code review
        run: |
          python scripts/code_review.py . --format json --output review.json
        continue-on-error: true
      
      - name: Run security check
        run: |
          python scripts/security_check.py . --format html --output security_report.html
        continue-on-error: true
      
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: code-quality-reports
          path: |
            review.json
            security_report.html
```

### VS Code 集成

创建 `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "OpenClaw: Code Review",
            "type": "shell",
            "command": "${workspaceFolder}/openclaw",
            "args": ["review", "${file}"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "OpenClaw: Security Check",
            "type": "shell",
            "command": "${workspaceFolder}/openclaw",
            "args": ["security", "${file}"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "OpenClaw: Auto Fix",
            "type": "shell",
            "command": "${workspaceFolder}/openclaw",
            "args": ["fix", "${file}", "--apply"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        }
    ]
}
```

## 报告解读

### 严重程度

| 级别 | 图标 | 说明 | 处理建议 |
|------|------|------|----------|
| CRITICAL | 🔴 | 严重问题 | 必须立即修复 |
| HIGH | 🟠 | 高危问题 | 强烈建议修复 |
| MEDIUM | 🟡 | 中等问题 | 建议修复 |
| LOW | 🟢 | 低优先级 | 可选修复 |
| INFO | 🔵 | 信息提示 | 仅供参考 |

### 问题类别

| 类别 | 说明 | 示例 |
|------|------|------|
| Security | 安全漏洞 | SQL注入、XSS、硬编码密钥 |
| Performance | 性能问题 | 低效算法、内存泄漏 |
| Maintainability | 可维护性 | 代码复杂度过高、函数过长 |
| Correctness | 正确性 | 裸except、可变默认参数 |
| Style | 代码风格 | 命名规范、尾随空格 |
| Best Practice | 最佳实践 | 使用logging替代print |

## 常见问题

### Q: 如何忽略特定的问题？

A: 在代码中添加注释:

```python
# openclaw: ignore=RULE-001
dangerous_function()  # 这行会被忽略
```

### Q: 如何自定义规则？

A: 编辑 `scripts/code_review.py` 添加自定义检查:

```python
def _check_custom_rule(self, node):
    """自定义检查"""
    if some_condition:
        self._add_issue(
            node=node,
            severity=Severity.MEDIUM,
            category=Category.BEST_PRACTICE,
            message="自定义消息",
            suggestion="修复建议",
            rule_id="CUSTOM-001"
        )
```

### Q: 如何批量处理整个项目？

A: 使用目录作为参数:

```bash
./openclaw review ./src --format html --output report.html
```

### Q: 如何集成到其他工具？

A: 使用JSON格式输出:

```bash
./openclaw review . --format json > review.json
# 然后解析JSON文件
```

## 高级用法

### 自定义配置

创建 `.openclawrc` 配置文件:

```ini
[review]
min_severity = medium
exclude_patterns = test_*, *_test.py

[security]
min_severity = high
check_dangerous_functions = true

[optimize]
min_confidence = high
auto_apply = false

[fix]
min_confidence = medium
dry_run = true
```

### 批量修复

```bash
# 修复整个目录
./openclaw fix ./src --apply --min-confidence high

# 修复后运行测试
pytest

# 如果测试通过，提交更改
git add .
git commit -m "Apply OpenClaw auto fixes"
```

### 生成综合报告

```bash
#!/bin/bash
# generate_report.sh

OUTPUT_DIR="reports/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "Generating comprehensive report..."

# 代码审查
./openclaw review ./src --format html --output "$OUTPUT_DIR/review.html"
./openclaw review ./src --format json --output "$OUTPUT_DIR/review.json"

# 安全检查
./openclaw security ./src --format html --output "$OUTPUT_DIR/security.html"
./openclaw security ./src --format json --output "$OUTPUT_DIR/security.json"

# 优化建议
./openclaw optimize ./src --format json --output "$OUTPUT_DIR/optimize.json"

echo "Reports generated in $OUTPUT_DIR"
```

## 最佳实践

1. **定期运行**: 建议每次提交前运行代码审查
2. **CI集成**: 在CI/CD流程中集成安全检查
3. **逐步改进**: 先修复严重问题，再处理低优先级问题
4. **团队规范**: 统一团队的代码规范配置
5. **持续学习**: 关注新的安全漏洞和最佳实践

## 获取帮助

```bash
# 显示帮助
./openclaw help

# 命令帮助
./openclaw review --help
./openclaw optimize --help
./openclaw fix --help
./openclaw security --help
```

## 更新日志

### v1.0.0 (2024)
- 初始版本发布
- 代码审查功能
- 代码优化功能
- 自动修复功能
- 安全检查功能
- HTML/JSON报告生成
