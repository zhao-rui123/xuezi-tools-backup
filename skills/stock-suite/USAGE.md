# Stock Suite v3.0 - 快速使用指南

## 安装
已安装到: ~/.openclaw/workspace/skills/stock-suite/

## 使用方法

### 方法1: 命令行
```bash
cd ~/.openclaw/workspace/skills/stock-suite
python3 __main__.py daily              # 生成日报
python3 __main__.py quote              # 实时行情
python3 __main__.py analyze 002460     # 深度分析
python3 __main__.py pattern 002460     # 形态识别
python3 __main__.py alert              # 预警检查
python3 __main__.py monitor            # 监控面板
```

### 方法2: Python导入
```python
from stock_suite import (
    generate_daily_report,
    deep_analyze,
    check_alerts,
    classify_stock,
)

# 生成日报
report = generate_daily_report()

# 深度分析
result = deep_analyze("002460", "赣锋锂业")

# 检查预警
alerts = check_alerts()
```

## 配置文件
- config/watchlist.py - 自选股列表
- config/xueqiu_config.py - 雪球Cookie（可选）

## 定时任务建议
```bash
# 每日收盘后生成日报
0 16 * * 1-5 cd ~/.openclaw/workspace/skills/stock-suite && python3 __main__.py daily

# 每10分钟检查预警
*/10 * * * 1-5 cd ~/.openclaw/workspace/skills/stock-suite && python3 __main__.py alert
```

