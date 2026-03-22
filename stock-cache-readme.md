# 股票数据缓存系统

## 概述
自动缓存A股市场股票数据（日/周/月线），支持增量更新。

## 数据目录
- 缓存位置: `/opt/stock-screener-v2/cache/`
- 股票数据: `/opt/stock-screener-v2/cache/data/`
- 元数据: `/opt/stock-screener-v2/cache/metadata.json`

## 使用方法

```bash
# 查看缓存状态
python3 cache_manager.py status

# 全量更新（首次运行或需要重建时）
python3 cache_manager.py full

# 增量更新（每天运行）
python3 cache_manager.py inc
```

## 定时任务
- 每天 16:00 - 增量更新
- 每周日 02:00 - 全量更新

## API配置
- API地址: http://lianghua.nanyangqiankun.top
- Token: (已配置)

## 缓存格式
每只股票一个JSON文件，包含：
- ts_code: 股票代码
- name: 股票名称
- industry: 所属行业
- daily: 日线数据
- weekly: 周线数据
- monthly: 月线数据
- updated: 更新时间
