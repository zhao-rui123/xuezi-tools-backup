---
name: mx_selfselect
description: 妙想自选股管理skill - 查询、添加、删除东方财富自选股
metadata:
  openclaw:
    requires:
      bins: [curl]
    install: []
---

# 妙想自选股管理skill (mx_selfselect)

管理东方财富通行证账户下的自选股数据，支持自然语言操作。

## 功能

### 1. 查询自选股
- 查看当前自选股列表
- 显示股票代码、名称、现价、涨跌幅等

### 2. 添加自选股
- 将指定股票添加到自选列表

### 3. 删除自选股
- 将指定股票从自选列表移除

## API配置

已配置API Key：`mkt_zdTwvCWmIr9g4mHoM8sOsaK8M_ffrhinQPP-GAkhTNs`

## 使用示例

### 查询自选股列表
```bash
curl -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/self-select/get' \
  -H 'Content-Type: application/json' \
  -H 'apikey: mkt_zdTwvCWmIr9g4mHoM8sOsaK8M_ffrhinQPP-GAkhTNs' \
  --data '{"query": "查询我的自选股列表"}'
```

### 添加自选股
```bash
curl -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/self-select/manage' \
  -H 'Content-Type: application/json' \
  -H 'apikey: mkt_zdTwvCWmIr9g4mHoM8sOsaK8M_ffrhinQPP-GAkhTNs' \
  --data '{"query": "把贵州茅台添加到我的自选股列表"}'
```

### 删除自选股
```bash
curl -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/self-select/manage' \
  -H 'Content-Type: application/json' \
  -H 'apikey: mkt_zdTwvCWmIr9g4mHoM8sOsaK8M_ffrhinQPP-GAkhTNs' \
  --data '{"query": "把贵州茅台从我的自选股列表删除"}'
```

## 调用示例

### 查询自选股
```bash
mx_selfselect query
```

### 添加自选股
```bash
mx_selfselect add 贵州茅台
# 或
mx_selfselect add 600519
```

### 删除自选股
```bash
mx_selfselect remove 贵州茅台
# 或
mx_selfselect remove 600519
```

## 返回数据格式

查询返回JSON，包含自选股列表：
- SECURITY_CODE: 股票代码
- SECURITY_SHORT_NAME: 股票简称
- NEWEST_PRICE: 最新价
- CHG: 涨跌幅

## 注意事项

- 需要东方财富通行证账户
- API Key已配置在skill中
- 使用自然语言或直接指定股票代码/名称
