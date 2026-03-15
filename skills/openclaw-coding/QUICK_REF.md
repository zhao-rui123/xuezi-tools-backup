# OpenClaw Coding Skill - 快速参考

## 部署位置
`~/.openclaw/workspace/skills/openclaw-coding/`

## 核心功能

### 1. 代码审查
```bash
cd ~/.openclaw/workspace/skills/openclaw-coding

# 审查单个文件
python3 scripts/code_review.py myfile.py

# 审查整个目录
python3 scripts/code_review.py ./src

# 生成HTML报告
python3 scripts/code_review.py ./src --format html --output report.html

# 只显示严重问题
python3 scripts/code_review.py ./src --min-severity high
```

### 2. 安全检查
```bash
# 安全扫描
python3 scripts/security_check.py myfile.py

# 生成HTML安全报告
python3 scripts/security_check.py ./src --format html

# 只显示高危漏洞
python3 scripts/security_check.py ./src --min-severity high
```

### 3. 自动修复
```bash
# 查看可修复的问题
python3 scripts/auto_fix.py myfile.py

# 应用修复（模拟）
python3 scripts/auto_fix.py myfile.py --apply --dry-run

# 实际应用修复
python3 scripts/auto_fix.py myfile.py --apply

# 只应用高信心度修复
python3 scripts/auto_fix.py ./src --apply --min-confidence high
```

### 4. 代码优化
```bash
# 分析优化机会
python3 scripts/code_optimizer.py myfile.py

# 自动应用高信心度优化
python3 scripts/code_optimizer.py ./src --apply --dry-run
```

## 严重程度分级

| 级别 | 图标 | 说明 |
|------|------|------|
| CRITICAL | 🔴 | 必须立即修复，安全漏洞 |
| HIGH | 🟠 | 强烈建议修复，性能问题 |
| MEDIUM | 🟡 | 建议修复，可维护性 |
| LOW | 🟢 | 可选修复，代码风格 |

## 问题类别

- **Security**: 安全漏洞
- **Performance**: 性能问题
- **Maintainability**: 可维护性
- **Correctness**: 正确性
- **Style**: 代码风格
- **Best Practice**: 最佳实践

## 常见检测问题

### 安全问题
- eval() / exec() 使用
- SQL注入风险
- 硬编码密码/密钥
- 不安全的反序列化

### 性能问题
- 低效算法
- 内存泄漏
- 不必要的计算

### 代码风格
- 命名规范
- 函数长度
- 代码复杂度

## Python 用法示例

```python
import sys
sys.path.insert(0, '~/.openclaw/workspace/skills/openclaw-coding')

from scripts.code_review import CodeReviewer

reviewer = CodeReviewer()
result = reviewer.review_file('myfile.py')

for issue in result.issues:
    print(f"[{issue.severity}] {issue.message}")
```

## 测试结果

✅ 代码审查 - 检测23个问题（5个CRITICAL）
✅ 安全检查 - 检测5个安全漏洞（CWE分类）
✅ 自动修复 - 6个可修复问题
✅ 代码优化 - 支持性能优化建议

---
*快速参考 - 2026-03-13*
