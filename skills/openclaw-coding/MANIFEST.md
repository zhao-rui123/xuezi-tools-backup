# OpenClaw 编程技能包 - 文件清单

## 文档文件

| 文件 | 说明 | 大小 |
|------|------|------|
| `SKILL.md` | 技能包主文档，包含完整的编程规范和最佳实践 | 54KB |
| `README.md` | 项目概述和使用说明 | 8.6KB |
| `USAGE.md` | 详细使用指南和集成方案 | 8.6KB |
| `QUICKSTART.md` | 5分钟快速开始指南 | 2.5KB |
| `MANIFEST.md` | 本文件，文件清单 | - |

## 脚本工具

| 文件 | 功能 | 大小 |
|------|------|------|
| `openclaw` | 统一入口脚本 | 2KB |
| `scripts/code_review.py` | 代码审查工具 | 40KB |
| `scripts/code_optimizer.py` | 代码优化工具 | 29KB |
| `scripts/auto_fix.py` | 自动修复工具 | 17KB |
| `scripts/security_check.py` | 安全检查工具 | 29KB |

## 代码模板

| 文件 | 说明 | 大小 |
|------|------|------|
| `templates/python_class.py` | Python类模板 | 4KB |
| `templates/python_function.py` | Python函数模板 | 5KB |

## 示例文件

| 文件 | 说明 | 大小 |
|------|------|------|
| `examples/example_bad_code.py` | 包含各种问题的示例代码 | 4KB |

## 功能特性

### 代码审查 (code_review.py)
- ✅ 安全漏洞检测（SQL注入、XSS、硬编码密钥等）
- ✅ 性能问题识别（低效算法、内存泄漏等）
- ✅ 可维护性检查（代码复杂度、函数长度等）
- ✅ 最佳实践验证（Pythonic写法、设计模式等）
- ✅ 支持多种输出格式（Console、JSON、HTML）
- ✅ 按严重程度和类别分类问题
- ✅ 提供详细的修复建议

### 代码优化 (code_optimizer.py)
- ✅ 性能优化建议（算法改进、缓存应用等）
- ✅ 可读性提升（简化表达式、改进命名等）
- ✅ Pythonic写法（列表推导式、生成器等）
- ✅ 代码简化（消除冗余、合并重复代码等）
- ✅ 信心度评估（高/中/低）
- ✅ 支持自动应用高信心度优化

### 自动修复 (auto_fix.py)
- ✅ 风格问题修复（尾随空格、命名规范等）
- ✅ 常见错误修复（裸except、None比较等）
- ✅ 安全问题修复（危险函数调用等）
- ✅ 代码简化（真值判断、链式比较等）
- ✅ 支持模拟运行（dry-run）
- ✅ 按信心度过滤修复

### 安全检查 (security_check.py)
- ✅ OWASP Top 10检测
- ✅ CWE分类（通用弱点枚举）
- ✅ 敏感信息检测（密码、API密钥、令牌）
- ✅ 危险函数检测（eval、exec等）
- ✅ SQL注入检测
- ✅ XSS漏洞检测
- ✅ 弱加密检测
- ✅ 生成详细的安全报告

## 检测规则统计

| 类别 | 规则数量 | 说明 |
|------|----------|------|
| Security | 20+ | 安全相关规则 |
| Performance | 10+ | 性能相关规则 |
| Maintainability | 15+ | 可维护性规则 |
| Correctness | 15+ | 正确性规则 |
| Style | 10+ | 代码风格规则 |
| Best Practice | 10+ | 最佳实践规则 |

## 使用方法

```bash
# 统一入口
./openclaw review <path>
./openclaw optimize <path>
./openclaw fix <path>
./openclaw security <path>

# 或直接运行脚本
python scripts/code_review.py <path>
python scripts/code_optimizer.py <path>
python scripts/auto_fix.py <path>
python scripts/security_check.py <path>
```

## 输出示例

### 控制台输出
```
================================================================================
代码审查报告
================================================================================
目标: examples/example_bad_code.py
时间: 2026-03-13T13:20:32
文件数: 1
问题总数: 23
================================================================================

按严重程度:
  🔴 CRITICAL: 5
  🟠 HIGH: 3
  🟡 MEDIUM: 1
  🟢 LOW: 14
```

### HTML报告
生成美观的HTML报告，支持：
- 按严重程度筛选
- 按类别筛选
- 代码高亮
- CWE链接
- 修复建议

### JSON报告
```json
[
  {
    "file": "example.py",
    "line": 10,
    "severity": "critical",
    "category": "security",
    "message": "使用危险函数 'eval'",
    "suggestion": "避免使用 eval"
  }
]
```

## 集成方案

- Git Pre-commit Hook
- GitHub Actions
- GitLab CI
- VS Code Tasks
- Jenkins Pipeline

## 系统要求

- Python 3.8+
- 无第三方依赖（纯标准库）

## 许可证

MIT License

---

**OpenClaw - 编写可靠、易维护、高质量的代码** 🚀
