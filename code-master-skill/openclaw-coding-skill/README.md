# OpenClaw 高水平编程技能包

> 编写可靠性强、易于维护、水平卓越的代码。代码审查安全细致，能够自动修复Bug和优化代码。

## 功能特性

### 1. 代码审查 (Code Review)
- **安全漏洞检测**: SQL注入、XSS、CSRF、硬编码密钥等
- **性能问题识别**: 低效算法、内存泄漏、不必要的计算
- **可维护性检查**: 代码复杂度、函数长度、命名规范
- **最佳实践验证**: Pythonic写法、设计模式应用

### 2. 代码优化 (Code Optimization)
- **性能优化**: 算法改进、缓存应用、循环优化
- **可读性提升**: 简化表达式、改进命名、重构复杂逻辑
- **Pythonic写法**: 列表推导式、生成器、上下文管理器
- **代码简化**: 消除冗余、合并重复代码

### 3. 自动修复 (Auto Fix)
- **风格问题**: 尾随空格、命名规范、import排序
- **常见错误**: 裸except、None比较、可变默认参数
- **安全问题**: 危险函数调用、硬编码敏感信息
- **代码简化**: 真值判断、链式比较

### 4. 安全检查 (Security Check)
- **OWASP Top 10**: 检测常见的Web安全漏洞
- **CWE分类**: 按通用弱点枚举分类问题
- **敏感信息**: 检测硬编码密码、API密钥、令牌
- **依赖安全**: 检查已知漏洞的依赖包

## 快速开始

### 安装

```bash
# 克隆技能包
git clone <repository-url> openclaw-coding-skill
cd openclaw-coding-skill

# 确保Python 3.8+
python --version
```

### 代码审查

```bash
# 审查单个文件
python scripts/code_review.py myfile.py

# 审查整个目录
python scripts/code_review.py ./src

# 生成HTML报告
python scripts/code_review.py ./src --format html --output report.html

# 只显示严重问题
python scripts/code_review.py ./src --min-severity high
```

### 代码优化

```bash
# 分析优化机会
python scripts/code_optimizer.py myfile.py

# 自动应用高信心度优化
python scripts/code_optimizer.py ./src --apply

# 模拟运行（不实际修改）
python scripts/code_optimizer.py ./src --apply --dry-run
```

### 自动修复

```bash
# 查看可修复的问题
python scripts/auto_fix.py myfile.py

# 应用修复
python scripts/auto_fix.py myfile.py --apply

# 只应用高信心度修复
python scripts/auto_fix.py ./src --apply --min-confidence high
```

### 安全检查

```bash
# 安全扫描
python scripts/security_check.py myfile.py

# 生成HTML安全报告
python scripts/security_check.py ./src --format html

# 只显示高危漏洞
python scripts/security_check.py ./src --min-severity high
```

## 目录结构

```
openclaw-coding-skill/
├── SKILL.md                    # 技能包主文档（编程规范）
├── README.md                   # 本文件
├── scripts/                    # 脚本工具
│   ├── code_review.py         # 代码审查脚本
│   ├── code_optimizer.py      # 代码优化脚本
│   ├── auto_fix.py            # 自动修复脚本
│   └── security_check.py      # 安全检查脚本
├── templates/                  # 代码模板
│   ├── python_class.py        # Python类模板
│   └── python_function.py     # Python函数模板
└── rules/                      # 规则配置（可选）
```

## 编程规范速查

### 命名规范

```python
# ✅ 正确的命名
class UserAuthenticationService:  # 类名：PascalCase
    MAX_RETRY_COUNT = 3           # 常量：UPPER_SNAKE_CASE
    
    def validate_credentials(self, username: str) -> bool:  # 函数：snake_case
        is_valid = self._check_password(password)  # 变量：snake_case
        return is_valid
```

### 函数设计

```python
# ✅ 优秀的函数设计
def calculate_price(
    original_price: Decimal,
    discount: Decimal,
    *,  # 强制关键字参数
    tax_rate: Decimal = Decimal('0.08')
) -> Result[Decimal, PricingError]:
    """
    计算折扣后的价格。
    
    Args:
        original_price: 原始价格
        discount: 折扣百分比
        tax_rate: 税率
        
    Returns:
        Result包含计算结果或错误信息
    """
    if original_price < 0:
        return Result.error(PricingError.NEGATIVE_PRICE)
    
    discounted = original_price * (1 - discount / 100)
    final_price = discounted * (1 + tax_rate)
    
    return Result.success(final_price.quantize(Decimal('0.01')))
```

### 错误处理

```python
# ✅ 完善的错误处理
def fetch_user(user_id: int) -> Result[User, DatabaseError]:
    """获取用户信息"""
    try:
        if user_id <= 0:
            return Result.error(DatabaseError.INVALID_ID)
        
        user = db.query(User).filter_by(id=user_id).first()
        
        if user is None:
            return Result.error(DatabaseError.NOT_FOUND)
        
        return Result.success(user)
        
    except SQLAlchemyError as e:
        logger.exception("Database error fetching user")
        return Result.error(DatabaseError.CONNECTION_FAILED)
```

### 安全检查

```python
# ✅ 安全的代码
def authenticate_user(username: str, password: str) -> bool:
    """安全地验证用户"""
    # 使用参数化查询防止SQL注入
    user = db.execute(
        "SELECT * FROM users WHERE username = %s",
        (username,)
    ).fetchone()
    
    if user is None:
        # 恒定时间比较防止时序攻击
        bcrypt.checkpw(b'', DUMMY_HASH)
        return False
    
    # 使用bcrypt验证密码
    return bcrypt.checkpw(
        password.encode('utf-8'),
        user.password_hash.encode('utf-8')
    )
```

## 集成到工作流

### Git Pre-commit Hook

```bash
# 创建pre-commit钩子
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# OpenClaw代码审查钩子

echo "Running OpenClaw code review..."

# 获取暂存的Python文件
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

# 运行代码审查
for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        python scripts/code_review.py "$file"
        if [ $? -ne 0 ]; then
            echo "Code review failed for $file"
            exit 1
        fi
    fi
done

# 运行安全检查
python scripts/security_check.py . --min-severity high
if [ $? -ne 0 ]; then
    echo "Security check failed!"
    exit 1
fi

echo "All checks passed!"
EOF

chmod +x .git/hooks/pre-commit
```

### CI/CD集成

```yaml
# .github/workflows/code-quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Run code review
        run: python scripts/code_review.py . --format json --output review.json
      
      - name: Run security check
        run: python scripts/security_check.py . --min-severity high
      
      - name: Upload review report
        uses: actions/upload-artifact@v2
        with:
          name: code-review-report
          path: review.json
```

## 报告解读

### 严重程度

- **CRITICAL (🔴)**: 必须立即修复，通常是安全漏洞或功能缺陷
- **HIGH (🟠)**: 强烈建议修复，性能问题或设计缺陷
- **MEDIUM (🟡)**: 建议修复，代码风格或可维护性问题
- **LOW (🟢)**: 可选修复，格式问题

### 问题类别

- **Security**: 安全漏洞
- **Performance**: 性能问题
- **Maintainability**: 可维护性问题
- **Correctness**: 正确性问题
- **Style**: 代码风格问题
- **Best Practice**: 最佳实践问题

## 自定义规则

你可以通过修改脚本来添加自定义规则：

```python
# 在code_review.py中添加自定义检查
def _check_custom_rule(self, node):
    """自定义检查规则"""
    # 你的检查逻辑
    if some_condition:
        self._add_issue(
            node=node,
            severity=Severity.MEDIUM,
            category=Category.BEST_PRACTICE,
            message="自定义规则消息",
            suggestion="修复建议",
            rule_id="CUSTOM-001"
        )
```

## 贡献指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

MIT License - 详见LICENSE文件

## 联系方式

- 项目主页: [Your Repository URL]
- 问题反馈: [Issues URL]
- 邮件联系: [Your Email]

---

**Happy Coding with OpenClaw! 🚀**
