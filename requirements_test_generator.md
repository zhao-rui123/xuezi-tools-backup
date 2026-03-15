# 测试自动生成技能包 - 开发要求

## 技能包名称
`openclaw-test-generator`

## 技能包描述
根据Python代码自动生成单元测试（pytest），支持函数测试、类测试、边缘 case 测试等。

## 核心功能要求

### 1. 函数级测试生成
- 根据函数签名自动生成测试用例
- 分析参数类型，生成边界值测试
- 处理不同参数类型的测试：
  - 整数：正数、负数、零、最大/最小值
  - 字符串：空字符串、正常字符串、特殊字符
  - 列表/字典：空、正常、异常
  - 浮点数：精度问题
  - None/空值处理

### 2. 类级测试生成
- __init__ 方法测试
- 公共方法测试
- 属性测试
- 继承关系测试

### 3. Mock和Stub支持
- 自动 mock 外部依赖
- 处理 time.sleep、requests、文件IO 等
- 数据库mock配置

### 4. 测试覆盖优化
- 覆盖率分析
- 缺失测试提示
- 边缘case补充建议

### 5. 测试运行与报告
- 一键运行测试
- 生成测试报告
- 失败case调试建议

## 技术要求

### 输入
- Python源代码文件(.py)
- 或源代码目录
- 可指定测试框架（pytest/unittest）

### 输出
- 测试文件（test_xxx.py）
- 符合pytest规范
- 包含docstring说明

### 代码质量
- 测试代码符合PEP8
- 清晰的测试用例命名
- 适当的assertion message

## 使用示例

```bash
# 生成单个文件的测试
python3 -g /path/to/source.py

# 生成整个目录的测试
python3 -g /path/to/module/

# 指定测试框架
python3 -g /path/to/source.py --framework pytest

# 生成并运行测试
python3 -g /path/to/source.py --run

# 只生成边缘case测试
python3 -g /path/to/source.py --edge-cases-only
```

## 目录结构

```
openclaw-test-generator/
├── __init__.py
├── cli.py                 # 命令行入口
├── core/
│   ├── __init__.py
│   ├── analyzer.py       # 代码分析器
│   ├── generator.py       # 测试生成器
│   └── templates.py       # 测试模板
├── extractors/
│   ├── __init__.py
│   ├── function_extractor.py
│   ├── class_extractor.py
│   └── type_analyzer.py
├── templates/
│   ├── __init__.py
│   ├── pytest_template.py
│   └── unittest_template.py
├── utils/
│   ├── __init__.py
│   ├── mock_helper.py
│   └── coverage.py
├── requirements.txt
└── README.md
```

## 验收标准

1. ✅ 能够分析Python函数签名
2. ✅ 生成基本测试用例
3. ✅ 边缘case测试
4. ✅ Mock外部依赖
5. ✅ 命令行工具可用
6. ✅ 测试文件可直接运行

## 依赖

- pytest >= 7.0
- ast (Python标准库)
- typing (Python标准库)

---
*开发要求 - 2026-03-13*
