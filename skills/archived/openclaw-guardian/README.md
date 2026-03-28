# OpenClaw Guardian - 安全守护技能包

OpenClaw Guardian 是一个全面的安全技能包，专为保护 OpenClaw 系统的安全与稳定而设计。它提供技能安全扫描、系统稳定性监控、自动Bug修复和安全漏洞检测等功能。

## 功能特性

### 1. 技能安全扫描
- 检测恶意代码和危险操作
- 识别敏感文件访问
- 监控网络操作
- 代码静态分析
- 威胁风险评估

### 2. 系统稳定性监控
- CPU/内存/磁盘使用率监控
- 进程状态监控
- 自动资源释放
- 警报系统
- 历史数据分析

### 3. 自动Bug修复
- 代码质量分析
- 常见错误检测
- 自动修复建议
- 代码重构建议
- 修复前自动备份

### 4. 漏洞检测
- CWE漏洞数据库
- 代码注入检测
- 路径遍历检测
- 不安全的反序列化
- 敏感信息泄露检测

## 安装

### 环境要求
- Python 3.8+
- psutil 库
- PyYAML 库

### 安装依赖
```bash
pip install psutil pyyaml
```

### 配置
复制默认配置文件并根据需要修改：
```bash
cp config/default_config.yaml config/my_config.yaml
```

## 使用方法

### 命令行接口

#### 1. 扫描技能包安全性
```bash
# 基本扫描
python main.py scan ./my_skill

# 输出JSON格式
python main.py scan ./my_skill --json

# 保存报告
python main.py scan ./my_skill --save-report report.json
```

#### 2. 启动系统监控
```bash
# 持续监控
python main.py monitor

# 监控指定时间（秒）
python main.py monitor --duration 3600

# 自定义检查间隔
python main.py monitor --interval 10
```

#### 3. 修复代码问题
```bash
# 修复单个文件
python main.py fix ./my_skill/main.py

# 预览修复（不执行）
python main.py fix ./my_skill --dry-run

# 修复指定严重级别的问题
python main.py fix ./my_skill --severity low medium
```

#### 4. 检查系统健康
```bash
# 基本检查
python main.py health

# JSON输出
python main.py health --json
```

#### 5. 安全安装技能包
```bash
# 安全安装
python main.py install ./my_skill ./skills

# 强制安装（忽略警告）
python main.py install ./my_skill ./skills --force
```

#### 6. 漏洞扫描
```bash
# 扫描漏洞
python main.py vuln-scan ./my_skill

# 保存漏洞报告
python main.py vuln-scan ./my_skill --save-report vuln_report.json
```

#### 7. 查看统计信息
```bash
python main.py stats
```

### Python API

```python
from openclaw_guardian import OpenClawGuardian

# 创建Guardian实例
guardian = OpenClawGuardian(config_path='config/my_config.yaml')

# 启动监控
guardian.start()

# 扫描技能包
result = guardian.scan_skill('./my_skill')
print(f"安全: {result['is_safe']}, 风险评分: {result['risk_score']}")

# 检查系统健康
health = guardian.check_system_health()
print(f"状态: {health['overall_status']}")

# 安全安装技能包
install_result = guardian.install_skill_safely('./my_skill', './skills')
print(f"安装成功: {install_result['success']}")

# 停止监控
guardian.stop()

# 获取统计
stats = guardian.get_stats()
print(f"扫描技能数: {stats['skills_scanned']}")
```

## 配置说明

### 安全配置
```yaml
security:
  # 白名单技能哈希列表
  whitelist: []
  
  # 黑名单技能哈希列表
  blacklist: []
  
  # 禁止的模块列表
  blocked_modules:
    - ctypes
    - mmap
    - resource
    - pty
  
  # 是否允许安装中等风险的技能包
  allow_medium_risk: false
```

### 稳定性配置
```yaml
stability:
  # 资源使用阈值
  thresholds:
    cpu_warning: 70.0
    cpu_critical: 90.0
    memory_warning: 75.0
    memory_critical: 90.0
  
  # 自动保护
  auto_protect: true
```

### Bug修复配置
```yaml
bug_fix:
  # 自动修复
  auto_fix: true
  
  # 修复前备份
  backup_before_fix: true
  
  # 自动修复的严重级别
  fix_severity:
    - low
    - medium
```

## 安全检测规则

### 检测的威胁类型
- **系统命令执行**: `os.system`, `subprocess` with `shell=True`
- **动态代码执行**: `eval`, `exec`, `compile`
- **危险模块导入**: `ctypes`, `mmap`, `resource` 等
- **敏感路径访问**: `/etc/passwd`, `.ssh/`, 等
- **网络操作**: 未经验证的URL请求
- **文件操作**: 未经验证的文件写入

### 检测的漏洞类型
- **CWE-94**: 代码注入
- **CWE-78**: OS命令注入
- **CWE-22**: 路径遍历
- **CWE-502**: 不安全的反序列化
- **CWE-89**: SQL注入
- **CWE-798**: 硬编码凭证
- **CWE-918**: 服务器端请求伪造(SSRF)
- **CWE-611**: XML外部实体注入(XXE)

## 项目结构

```
openclaw_guardian/
├── __init__.py
├── main.py                  # 命令行入口
├── core/                    # 核心模块
│   ├── guardian.py         # 主控制类
│   ├── security_manager.py # 安全管理器
│   ├── stability_monitor.py # 稳定性监控器
│   ├── bug_fixer.py        # Bug修复器
│   └── vulnerability_scanner.py # 漏洞扫描器
├── utils/                   # 工具模块
│   ├── logger.py           # 日志工具
│   └── config_loader.py    # 配置加载器
├── config/                  # 配置文件
│   └── default_config.yaml # 默认配置
└── README.md               # 说明文档
```

## 事件回调

```python
# 注册威胁检测回调
guardian.register_callback('threat_detected', lambda data: print(f"威胁: {data}"))

# 注册系统不稳定回调
guardian.register_callback('system_unstable', lambda data: print(f"系统不稳定: {data}"))

# 注册Bug修复回调
guardian.register_callback('bug_fixed', lambda data: print(f"修复: {data}"))

# 注册漏洞发现回调
guardian.register_callback('vulnerability_found', lambda data: print(f"漏洞: {data}"))
```

## 环境变量

- `GUARDIAN_LOG_LEVEL`: 日志级别 (DEBUG, INFO, WARNING, ERROR)
- `GUARDIAN_MONITOR_INTERVAL`: 监控间隔（秒）
- `GUARDIAN_AUTO_FIX`: 是否自动修复 (true/false)
- `GUARDIAN_AUTO_PROTECT`: 是否自动保护 (true/false)

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 实现安全扫描功能
- 实现稳定性监控
- 实现Bug自动修复
- 实现漏洞检测
