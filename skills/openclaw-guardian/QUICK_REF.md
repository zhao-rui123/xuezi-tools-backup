# OpenClaw Guardian 快速参考

## 命令速查

### 扫描
```bash
python main.py scan <skill_path> [--json] [--save-report <file>]
```

### 监控
```bash
python main.py monitor [--duration <seconds>] [--interval <seconds>]
```

### 修复
```bash
python main.py fix <path> [--dry-run] [--severity <level>...]
```

### 健康检查
```bash
python main.py health [--json]
```

### 安装
```bash
python main.py install <skill_path> <target_dir> [--force]
```

### 漏洞扫描
```bash
python main.py vuln-scan <skill_path> [--json] [--save-report <file>]
```

### 统计
```bash
python main.py stats
```

## 风险评分

| 分数 | 级别 | 建议 |
|------|------|------|
| 0-20 | 安全 | 可以放心使用 |
| 21-50 | 低风险 | 需要注意 |
| 51-80 | 中等风险 | 建议审查 |
| 81-100 | 高风险 | 不建议使用 |

## 严重级别

| 级别 | 图标 | 说明 |
|------|------|------|
| critical | 🔴 | 严重问题，立即处理 |
| high | 🟠 | 高危问题，优先处理 |
| medium | 🟡 | 中等问题，计划处理 |
| low | 🟢 | 低风险，可选处理 |

## Python API 速查

```python
from openclaw_guardian import OpenClawGuardian

# 创建和启动
guardian = OpenClawGuardian(config_path='config.yaml')
guardian.start()

# 扫描
result = guardian.scan_skill('./skill')
print(result['is_safe'], result['risk_score'])

# 健康检查
health = guardian.check_system_health()
print(health['overall_status'])

# 安全安装
result = guardian.install_skill_safely('./skill', './skills')
print(result['success'])

# 停止
guardian.stop()

# 统计
stats = guardian.get_stats()
print(stats['skills_scanned'])
```

## 配置速查

```yaml
# 日志
log_level: INFO  # DEBUG, INFO, WARNING, ERROR

# 监控阈值
stability:
  thresholds:
    cpu_warning: 70
    cpu_critical: 90
    memory_warning: 75
    memory_critical: 90

# 自动修复
bug_fix:
  auto_fix: true
  fix_severity: [low, medium]

# 安全
security:
  allow_medium_risk: false
  blocked_modules: [ctypes, mmap, resource]
```

## 环境变量

```bash
GUARDIAN_LOG_LEVEL=DEBUG
GUARDIAN_MONITOR_INTERVAL=30
GUARDIAN_AUTO_FIX=true
GUARDIAN_AUTO_PROTECT=true
```

## CWE 列表

- **CWE-94**: 代码注入
- **CWE-78**: 命令注入
- **CWE-22**: 路径遍历
- **CWE-502**: 不安全反序列化
- **CWE-89**: SQL注入
- **CWE-798**: 硬编码凭证
- **CWE-918**: SSRF
- **CWE-611**: XXE
