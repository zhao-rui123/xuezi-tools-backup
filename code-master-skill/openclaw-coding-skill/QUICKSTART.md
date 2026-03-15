# OpenClaw 快速开始指南

## 5分钟上手

### 1. 测试示例代码

```bash
cd openclaw-coding-skill

# 运行代码审查（会发现23个问题）
./openclaw review examples/example_bad_code.py

# 运行安全检查（会发现5个安全漏洞）
./openclaw security examples/example_bad_code.py

# 查看可自动修复的问题
./openclaw fix examples/example_bad_code.py
```

### 2. 应用到你的项目

```bash
# 代码审查
./openclaw review /path/to/your/project

# 生成HTML报告
./openclaw review /path/to/your/project --format html --output report.html

# 安全检查
./openclaw security /path/to/your/project --format html --output security.html

# 自动修复（先查看）
./openclaw fix /path/to/your/project

# 应用修复
./openclaw fix /path/to/your/project --apply
```

### 3. 集成到Git

```bash
# 创建pre-commit钩子
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
./openclaw review . --min-severity high || exit 1
./openclaw security . --min-severity high || exit 1
EOF
chmod +x .git/hooks/pre-commit
```

## 核心功能

| 功能 | 命令 | 说明 |
|------|------|------|
| 代码审查 | `openclaw review <path>` | 检测代码问题 |
| 代码优化 | `openclaw optimize <path>` | 提供优化建议 |
| 自动修复 | `openclaw fix <path>` | 自动修复问题 |
| 安全检查 | `openclaw security <path>` | 检测安全漏洞 |

## 输出格式

```bash
# 控制台输出（默认）
./openclaw review myfile.py

# JSON格式
./openclaw review myfile.py --format json

# HTML报告
./openclaw review myfile.py --format html --output report.html
```

## 严重级别

| 级别 | 图标 | 说明 |
|------|------|------|
| CRITICAL | 🔴 | 必须立即修复 |
| HIGH | 🟠 | 强烈建议修复 |
| MEDIUM | 🟡 | 建议修复 |
| LOW | 🟢 | 可选修复 |

## 问题类别

- **Security**: 安全漏洞（SQL注入、XSS、硬编码密钥）
- **Performance**: 性能问题（低效算法、内存泄漏）
- **Maintainability**: 可维护性（代码复杂度、函数长度）
- **Correctness**: 正确性（裸except、可变默认参数）
- **Style**: 代码风格（命名规范、尾随空格）
- **Best Practice**: 最佳实践（使用logging替代print）

## 下一步

- 阅读 [SKILL.md](SKILL.md) 了解完整的编程规范
- 阅读 [USAGE.md](USAGE.md) 了解详细的使用方法
- 阅读 [README.md](README.md) 了解项目概述

## 获取帮助

```bash
./openclaw help
./openclaw review --help
./openclaw optimize --help
./openclaw fix --help
./openclaw security --help
```
