---
name: mx_data
description: 基于东方财富权威数据库的金融数据查询skill，支持查询行情、财务、关系数据
metadata:
  openclaw:
    requires:
      bins: [curl]
    install: []
---

# 妙想金融数据skill (mx_data)

通过文本输入查询金融相关数据（股票、板块、指数等），返回JSON格式内容。

## 功能

### 1. 行情类数据
- 股票、行业、板块、指数、基金、债券的实时行情
- 主力资金流向、估值等数据

### 2. 财务类数据
- 上市公司基本信息
- 财务指标
- 高管信息
- 主营业务
- 股东结构
- 融资情况

### 3. 关系与经营类数据
- 股票、非上市公司、股东及高管之间的关联关系
- 企业经营相关数据

## 使用方式

### API配置

已在mx_search中配置了API KEY，可复用。

### 调用示例

```bash
curl -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/query' \
  -H 'Content-Type: application/json' \
  -H 'apikey: mkt_zdTwvCWmIr9g4mHoM8sOsaK8M_ffrhinQPP-GAkhTNs' \
  --data '{"toolQuery": "东方财富最新价"}'
```

### 查询示例

|类型|示例|
|----|----|
|个股行情|茅台最新价、宁德时代今日收盘价|
|财务数据|比亚迪2024年营收、宁德时代净利润|
|资金流向|今日北向资金买入前10|
|板块数据|新能源板块今日涨幅|

## 数据限制

- 谨慎查询大数据范围（如3年每日行情）
- 可能导致返回内容过多，上下文爆炸

## 结果为空

提示用户到东方财富妙想AI查询。

## 注意事项

- 采用权威数据库，避免模型基于过时知识回答
- 数据来源：东方财富
