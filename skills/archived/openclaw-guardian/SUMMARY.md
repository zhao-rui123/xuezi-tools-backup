# OpenClaw Guardian - 技能包总结

## 概述

OpenClaw Guardian 是一个全面的安全守护技能包，专为保护本地部署的 OpenClaw 系统而设计。它提供多层次的安全保护机制，确保技能包的安全性和系统的稳定性。

## 核心功能

### 1. 技能安全扫描 (SecurityManager)
- **恶意代码检测**: 识别eval、exec、os.system等危险函数
- **危险操作识别**: 检测shell命令执行、动态代码编译
- **敏感文件访问检查**: 监控对/etc/passwd、.ssh/等敏感路径的访问
- **网络操作监控**: 检测未经验证的URL请求
- **模块导入控制**: 阻止ctypes、mmap等危险模块
- **风险评分系统**: 0-100分风险评估

**检测能力**:
- 8+ 种严重级别威胁模式
- 15+ 种高危操作检测
- 10+ 种敏感路径监控
- 实时代码静态分析

### 2. 系统稳定性监控 (StabilityMonitor)
- **资源监控**: CPU、内存、磁盘使用率实时跟踪
- **进程监控**: 监控指定进程的资源使用
- **阈值警报**: 可配置的警告和严重级别阈值
- **自动保护**: 资源不足时自动执行保护措施
- **历史数据**: 保存资源使用历史用于分析

**监控指标**:
- CPU使用率 (警告: 70%, 严重: 90%)
- 内存使用率 (警告: 75%, 严重: 90%)
- 磁盘使用率 (警告: 80%, 严重: 95%)

### 3. 自动Bug修复 (BugFixer)
- **代码质量分析**: 评估代码质量评分
- **常见错误检测**: 识别语法错误、逻辑错误
- **自动修复**: 修复代码风格问题和常见bug
- **修复前备份**: 自动备份原始文件
- **修复建议**: 提供详细的修复指导

**修复能力**:
- 语法错误检测
- None比较修复 (== None → is None)
- 裸except修复 (except: → except Exception:)
- 未使用导入清理
- 可变默认参数检测

### 4. 漏洞检测 (VulnerabilityScanner)
- **CWE标准覆盖**: 基于通用缺陷枚举标准
- **代码注入检测**: CWE-94
- **命令注入检测**: CWE-78
- **路径遍历检测**: CWE-22
- **反序列化检测**: CWE-502
- **SQL注入检测**: CWE-89
- **硬编码凭证检测**: CWE-798
- **SSRF检测**: CWE-918
- **XXE检测**: CWE-611

**漏洞数据库**:
- 12+ CWE漏洞类型
- 30+ 检测模式
- 严重/高危/中危/低危分级

## 技术架构

```
openclaw_guardian/
├── core/                      # 核心模块
│   ├── guardian.py           # 主控制类 (400+ 行)
│   ├── security_manager.py   # 安全管理器 (500+ 行)
│   ├── stability_monitor.py  # 稳定性监控器 (400+ 行)
│   ├── bug_fixer.py          # Bug修复器 (500+ 行)
│   └── vulnerability_scanner.py # 漏洞扫描器 (600+ 行)
├── utils/                     # 工具模块
│   ├── logger.py             # 日志工具 (支持彩色输出)
│   └── config_loader.py      # 配置加载器 (支持YAML/JSON)
├── config/                    # 配置文件
│   └── default_config.yaml   # 默认配置
├── examples/                  # 示例技能包
│   ├── safe_skill/           # 安全示例
│   └── unsafe_skill/         # 不安全示例 (用于测试)
├── main.py                    # CLI入口 (400+ 行)
├── test_guardian.py          # 测试脚本 (300+ 行)
└── skill.yaml                # 技能包清单
```

**总代码量**: 3500+ 行Python代码

## 使用方法

### 命令行接口

```bash
# 扫描技能包
python main.py scan ./my_skill

# 启动监控
python main.py monitor

# 修复代码
python main.py fix ./my_skill

# 健康检查
python main.py health

# 安全安装
python main.py install ./my_skill ./skills

# 漏洞扫描
python main.py vuln-scan ./my_skill
```

### Python API

```python
from openclaw_guardian import OpenClawGuardian

# 创建实例
guardian = OpenClawGuardian()

# 启动监控
guardian.start()

# 扫描技能包
result = guardian.scan_skill('./my_skill')

# 安全安装
install_result = guardian.install_skill_safely('./my_skill', './skills')

# 停止监控
guardian.stop()
```

## 安全特性

### 多层防护
1. **安装前扫描**: 阻止高风险技能包安装
2. **运行时监控**: 持续监控系统稳定性
3. **自动修复**: 检测并修复常见问题
4. **漏洞检测**: 基于CWE标准的全面扫描

### 风险评分系统
- **0-20分**: 安全，可以放心使用
- **21-50分**: 低风险，需要注意
- **51-80分**: 中等风险，建议审查
- **81-100分**: 高风险，不建议使用

### 白名单/黑名单
```yaml
security:
  whitelist: []  # 可信技能包哈希
  blacklist: []  # 禁止技能包哈希
```

## 配置选项

### 完整配置
```yaml
log_level: INFO

monitoring:
  interval: 60

security:
  blocked_modules: [ctypes, mmap, resource, pty]
  allow_medium_risk: false

stability:
  thresholds:
    cpu_warning: 70.0
    cpu_critical: 90.0
    memory_warning: 75.0
    memory_critical: 90.0
  auto_protect: true

bug_fix:
  auto_fix: true
  backup_before_fix: true
  fix_severity: [low, medium]

vulnerability:
  severity_filter: [critical, high, medium, low]
```

## 测试结果

运行 `python test_guardian.py`:

```
============================================================
测试: 安全扫描功能
============================================================
1. 扫描安全技能包...
   风险评分: 20/100
   威胁数: 1
   ✓ 安全扫描测试通过

2. 扫描不安全技能包...
   风险评分: 100/100
   威胁数: 8
   ✓ 成功检测到安全问题

============================================================
测试: 稳定性监控功能
============================================================
✓ 稳定性监控测试通过

============================================================
测试: Bug修复功能
============================================================
✓ 成功检测到代码问题

============================================================
测试: 漏洞扫描功能
============================================================
✓ 成功检测到安全漏洞

============================================================
测试: Guardian集成功能
============================================================
✓ Guardian实例创建成功
✓ 扫描完成
✓ 健康检查完成
✓ 统计信息获取完成

============================================================
测试: 命令行接口
============================================================
✓ 帮助命令正常
✓ 扫描命令正常
✓ 健康检查命令正常
```

## 文档

- **README.md**: 项目概述和基本使用
- **USER_GUIDE.md**: 详细用户指南 (500+ 行)
- **QUICK_REF.md**: 快速参考卡片
- **SUMMARY.md**: 本总结文档

## 依赖

- Python >= 3.8
- psutil >= 5.9.0 (系统监控)
- PyYAML >= 6.0 (配置解析)

## 安装

```bash
# 方式1: 使用安装脚本
bash install.sh

# 方式2: 手动安装
pip install -r requirements.txt
python main.py --version
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新计划

### v1.1.0 (计划中)
- [ ] 机器学习威胁检测
- [ ] 行为分析监控
- [ ] 自动隔离可疑技能包
- [ ] 安全报告生成器

### v1.2.0 (计划中)
- [ ] 网络流量监控
- [ ] 文件完整性检查
- [ ] 沙箱执行环境
- [ ] 安全策略引擎

---

**OpenClaw Guardian - 守护您的OpenClaw系统安全**
