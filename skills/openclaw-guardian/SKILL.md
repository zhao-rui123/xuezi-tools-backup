# OpenClaw Guardian - 安全守护技能包

## 描述

全面的 OpenClaw 系统安全技能包，提供技能安全扫描、系统稳定性监控、自动 Bug 修复和安全漏洞检测功能，保护系统安全稳定运行。

## 功能

### 技能安全扫描
- 恶意代码和危险操作检测
- 敏感文件访问识别
- 网络操作监控
- 代码静态分析与威胁风险评估

### 系统稳定性监控
- CPU / 内存 / 磁盘使用率实时监控
- 进程状态监控与资源自动释放
- 监控警报与历史数据分析

### 自动 Bug 修复
- 代码质量分析
- 常见错误检测与自动修复建议
- 修复前自动备份

### 漏洞检测
- CWE 漏洞数据库（代码注入、路径遍历、敏感信息泄露等）
- 安全漏洞扫描与修复建议

### 安全安装
- 技能包安装前安全扫描
- 安装过程威胁拦截
- 强制安装选项（带风险警告）

## 使用方法

```bash
# 扫描技能包安全性
python main.py scan ./my_skill
python main.py scan ./my_skill --json
python main.py scan ./my_skill --save-report report.json

# 启动系统监控
python main.py monitor
python main.py monitor --duration 3600  # 监控1小时

# 修复代码问题
python main.py fix ./my_skill/main.py
python main.py fix ./my_skill --dry-run  # 预览不执行

# 检查系统健康
python main.py health
python main.py health --json

# 安全安装技能包
python main.py install ./my_skill ./skills
python main.py install ./my_skill ./skills --force  # 强制安装

# 漏洞扫描
python main.py vuln-scan ./my_skill
python main.py vuln-scan ./my_skill --save-report vuln.json

# 查看统计信息
python main.py stats
```

Python API：
```python
from openclaw_guardian import OpenClawGuardian

guardian = OpenClawGuardian(config_path='config/my_config.yaml')
guardian.start()

result = guardian.scan_skill('./my_skill')
print(f"安全: {result['is_safe']}, 风险评分: {result['risk_score']}")

health = guardian.check_system_health()
print(f"状态: {health['overall_status']}")

guardian.stop()
```

## 依赖

- Python >= 3.8
- `psutil` - 系统资源监控
- `PyYAML` - 配置文件解析
