# OpenClaw Guardian 用户指南

## 目录
1. [快速开始](#快速开始)
2. [核心功能](#核心功能)
3. [命令行使用](#命令行使用)
4. [Python API](#python-api)
5. [配置详解](#配置详解)
6. [安全规则](#安全规则)
7. [故障排除](#故障排除)

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/openclaw/guardian.git
cd guardian

# 安装依赖
pip install -r requirements.txt

# 或者使用setup.py安装
pip install -e .
```

### 基本使用

```bash
# 扫描技能包
python main.py scan ./my_skill

# 检查系统健康
python main.py health

# 启动监控
python main.py monitor
```

## 核心功能

### 1. 技能安全扫描

安全扫描器会检查技能包中的：
- 恶意代码模式
- 危险函数调用
- 敏感文件访问
- 不安全的网络操作

**风险评分说明：**
- 0-20: 安全，可以放心使用
- 21-50: 低风险，需要注意
- 51-80: 中等风险，建议审查
- 81-100: 高风险，不建议使用

### 2. 系统稳定性监控

监控器会持续跟踪：
- CPU使用率
- 内存使用情况
- 磁盘空间
- 进程状态

**阈值配置：**
```yaml
thresholds:
  cpu_warning: 70.0      # CPU警告阈值
  cpu_critical: 90.0     # CPU严重阈值
  memory_warning: 75.0   # 内存警告阈值
  memory_critical: 90.0  # 内存严重阈值
```

### 3. 自动Bug修复

修复器可以检测和修复：
- 语法错误
- 代码风格问题
- 常见编程错误
- 性能问题

**自动修复级别：**
- low: 代码风格问题
- medium: 潜在bug
- high: 严重问题（默认不自动修复）

### 4. 漏洞检测

基于CWE标准检测：
- 代码注入（CWE-94）
- 命令注入（CWE-78）
- 路径遍历（CWE-22）
- SQL注入（CWE-89）
- 不安全的反序列化（CWE-502）
- 硬编码凭证（CWE-798）

## 命令行使用

### scan - 扫描技能包

```bash
# 基本扫描
python main.py scan ./my_skill

# JSON格式输出
python main.py scan ./my_skill --json

# 保存详细报告
python main.py scan ./my_skill --save-report report.json

# 扫描并显示详细信息
python main.py scan ./my_skill -v
```

**输出示例：**
```
扫描时间: 2024-01-01T12:00:00
风险评分: 25/100
安全状态: ✗ 存在风险

发现 3 个安全威胁:
  🟡 [MEDIUM] 网络请求
     文件: /path/to/skill.py:15
     代码: requests.get(url)
     建议: 验证目标地址
```

### monitor - 系统监控

```bash
# 持续监控
python main.py monitor

# 监控1小时
python main.py monitor --duration 3600

# 每10秒检查一次
python main.py monitor --interval 10
```

**监控输出：**
```
启动系统监控...
按 Ctrl+C 停止监控
------------------------------------------------------------
[12:00:00] CPU: 15.2% | 内存: 45.3% | 磁盘: 62.1%
[12:00:05] CPU: 12.8% | 内存: 45.5% | 磁盘: 62.1%
...
```

### fix - 代码修复

```bash
# 修复单个文件
python main.py fix ./skill/main.py

# 预览修复（不执行）
python main.py fix ./skill --dry-run

# 修复指定级别的问题
python main.py fix ./skill --severity low medium

# 修复整个目录
python main.py fix ./skill --recursive
```

**修复输出：**
```
分析路径: ./skill
------------------------------------------------------------
文件数: 5
总问题数: 12
可自动修复: 8
代码质量评分: 78/100

修复完成:
  成功: 8
  失败: 0

修复详情:
  ✓ none_check: 成功修复
  ✓ bare_except: 成功修复
  ...
```

### health - 健康检查

```bash
# 基本检查
python main.py health

# JSON格式输出
python main.py health --json

# 详细输出
python main.py health -v
```

**健康报告：**
```
检查系统健康状态...
------------------------------------------------------------
整体状态: ✓ HEALTHY

资源使用:
  CPU: 23.5%
  内存: 56.2% (可用: 3456 MB)
  磁盘: 45.8% (可用: 123.4 GB)

检测到的问题:
  无

建议:
  • 系统运行正常
  • 定期进行安全扫描
```

### install - 安全安装

```bash
# 安全安装技能包
python main.py install ./my_skill ./skills

# 强制安装（忽略警告）
python main.py install ./my_skill ./skills --force

# 安装前扫描
python main.py install ./my_skill ./skills --scan-first
```

**安装过程：**
```
准备安装技能包: ./my_skill
目标目录: ./skills
------------------------------------------------------------
扫描结果:
  风险评分: 15/100
  安全状态: ✓ 安全
  威胁数: 0
  漏洞数: 0

✓ 安装成功: ./skills/my_skill
```

### vuln-scan - 漏洞扫描

```bash
# 扫描漏洞
python main.py vuln-scan ./my_skill

# JSON格式输出
python main.py vuln-scan ./my_skill --json

# 保存漏洞报告
python main.py vuln-scan ./my_skill --save-report vuln.json
```

**漏洞报告：**
```
正在扫描漏洞: ./my_skill
------------------------------------------------------------
扫描文件数: 10
风险评分: 30/100

发现 5 个漏洞:

🟡 MEDIUM (3个):
  [CWE-377] 不安全的临时文件
    位置: ./skill/utils.py:45
    描述: 使用不安全的临时文件创建方式
    修复: 使用tempfile.mkstemp或NamedTemporaryFile
...
```

### stats - 统计信息

```bash
# 查看统计
python main.py stats

# 详细统计
python main.py stats -v
```

**统计输出：**
```
OpenClaw Guardian 统计信息
------------------------------------------------------------
启动时间: 2024-01-01 10:00:00
运行时间: 3600.5 秒

操作统计:
  扫描技能数: 15
  阻止威胁数: 3
  修复Bug数: 12
  发现漏洞数: 8
```

## Python API

### 基础用法

```python
from openclaw_guardian import OpenClawGuardian

# 创建实例
guardian = OpenClawGuardian()

# 启动监控
guardian.start()

# 扫描技能包
result = guardian.scan_skill('./my_skill')
print(f"安全: {result['is_safe']}")
print(f"风险评分: {result['risk_score']}")

# 停止监控
guardian.stop()
```

### 事件回调

```python
# 威胁检测回调
def on_threat_detected(data):
    print(f"检测到威胁: {data['skill_path']}")
    for threat in data['threats']:
        send_alert(threat)  # 发送警报

guardian.register_callback('threat_detected', on_threat_detected)

# 系统不稳定回调
def on_system_unstable(data):
    print("系统资源不足！")
    free_resources()  # 释放资源

guardian.register_callback('system_unstable', on_system_unstable)

# Bug修复回调
def on_bug_fixed(data):
    print(f"修复了 {data['fixed_count']} 个问题")

guardian.register_callback('bug_fixed', on_bug_fixed)

# 漏洞发现回调
def on_vulnerability_found(data):
    for vuln in data['vulnerabilities']:
        if vuln['severity'] == 'critical':
            block_skill(data['skill_path'])  # 阻止技能

guardian.register_callback('vulnerability_found', on_vulnerability_found)
```

### 单独使用模块

```python
from openclaw_guardian import SecurityManager
from openclaw_guardian import StabilityMonitor
from openclaw_guardian import BugFixer
from openclaw_guardian import VulnerabilityScanner

# 安全扫描
security = SecurityManager()
result = security.scan_skill('./my_skill')

# 稳定性监控
monitor = StabilityMonitor()
monitor.start()
resources = monitor.check_resources()
monitor.stop()

# Bug修复
fixer = BugFixer()
analysis = fixer.analyze_skill('./my_skill')
fixer.fix_issues(analysis['issues'])

# 漏洞扫描
scanner = VulnerabilityScanner()
result = scanner.scan_skill('./my_skill')
scanner.generate_report(result, 'vuln_report.json')
```

## 配置详解

### 完整配置示例

```yaml
# 日志配置
log_level: INFO
log_file: logs/guardian.log

# 监控配置
monitoring:
  interval: 60
  enabled: true

# 安全配置
security:
  whitelist: []
  blacklist: []
  allowed_modules: []
  blocked_modules:
    - ctypes
    - mmap
    - resource
    - pty
    - gc
    - sysconfig
  allow_medium_risk: false

# 稳定性配置
stability:
  thresholds:
    cpu_warning: 70.0
    cpu_critical: 90.0
    memory_warning: 75.0
    memory_critical: 90.0
    disk_warning: 80.0
    disk_critical: 95.0
  check_interval: 5
  auto_protect: true
  max_history: 1000
  max_alerts: 100

# Bug修复配置
bug_fix:
  auto_fix: true
  backup_before_fix: true
  fix_severity:
    - low
    - medium

# 漏洞扫描配置
vulnerability:
  severity_filter:
    - critical
    - high
    - medium
    - low
  include_patterns:
    - "*.py"
  exclude_patterns:
    - "test_*.py"
    - "*_test.py"

# 报告配置
reports_dir: reports
backup_dir: backups
```

### 环境变量

```bash
# 日志级别
export GUARDIAN_LOG_LEVEL=DEBUG

# 监控间隔
export GUARDIAN_MONITOR_INTERVAL=30

# 自动修复
export GUARDIAN_AUTO_FIX=true

# 自动保护
export GUARDIAN_AUTO_PROTECT=true
```

## 安全规则

### 检测的威胁类型

| 类型 | 严重级别 | 说明 |
|------|----------|------|
| eval执行 | critical | 使用eval执行动态代码 |
| exec执行 | critical | 使用exec执行动态代码 |
| os.system | critical | 执行系统命令 |
| shell=True | critical | 使用shell执行命令 |
| pickle.loads | critical | 不安全的反序列化 |
| 硬编码密码 | high | 源代码中包含密码 |
| 硬编码密钥 | high | 源代码中包含API密钥 |
| 路径遍历 | high | 动态构造文件路径 |
| SQL注入 | critical | 字符串拼接SQL |
| SSRF | high | 服务器端请求伪造 |

### CWE覆盖

- **CWE-94**: 代码注入
- **CWE-78**: OS命令注入
- **CWE-22**: 路径遍历
- **CWE-502**: 不安全的反序列化
- **CWE-89**: SQL注入
- **CWE-798**: 硬编码凭证
- **CWE-338**: 不安全的随机数
- **CWE-918**: SSRF
- **CWE-611**: XXE
- **CWE-916**: 不充分的哈希
- **CWE-532**: 敏感数据日志
- **CWE-377**: 不安全的临时文件

## 故障排除

### 常见问题

**Q: 扫描时内存不足**
```bash
# 解决方案：增加内存限制或分批扫描
python main.py scan ./large_skill --batch-size 100
```

**Q: 误报太多**
```yaml
# 在配置中添加白名单
security:
  whitelist:
    - "safe_function"
    - "trusted_module"
```

**Q: 监控占用CPU过高**
```yaml
# 增加检查间隔
stability:
  check_interval: 30  # 改为30秒
```

**Q: 自动修复破坏了代码**
```bash
# 恢复备份
mv file.py.backup.1234567890 file.py

# 或者禁用自动修复
export GUARDIAN_AUTO_FIX=false
```

### 调试模式

```bash
# 启用详细日志
python main.py -v scan ./my_skill

# 调试模式
export GUARDIAN_LOG_LEVEL=DEBUG
python main.py scan ./my_skill
```

### 获取帮助

```bash
# 查看帮助
python main.py --help

# 查看具体命令帮助
python main.py scan --help
python main.py monitor --help
```

## 最佳实践

1. **定期扫描**: 建议每周扫描一次所有技能包
2. **监控常驻**: 在生产环境保持监控运行
3. **及时修复**: 发现高危漏洞立即修复
4. **备份重要**: 修复前确保已启用备份
5. **审查配置**: 根据实际需求调整阈值
