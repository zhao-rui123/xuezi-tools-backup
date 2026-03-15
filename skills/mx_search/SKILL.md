---
name: mx_search
description: 基于东方财富妙想搜索的金融资讯搜索skill，用于获取时效性信息、新闻、公告、研报、政策等金融信息
metadata:
  openclaw:
    requires:
      bins: [curl]
    install: []
---

# 妙想资讯搜索 (mx_search)

根据用户问句搜索相关金融资讯，获取与问句相关的资讯信息（如研报、新闻、解读等）。

## 功能

- 个股资讯搜索（最新研报、机构观点）
- 板块/主题搜索（新闻、政策解读）
- 宏观/风险分析
- 综合解读（大盘异动、资金流向）

## 使用方式

### API配置

需要在环境变量中设置 `MX_APIKEY`：
```bash
export MX_APIKEY="你的APIKEY"
```

### 调用示例

```bash
curl -X POST --location 'https://mkapi2.dfcfs.com/finskillshub/api/claw/news-search' \
--header 'Content-Type: application/json' \
--header 'apikey: ${MX_APIKEY}' \
--data '{"query":"立讯精密的资讯"}'
```

### 问句示例

|类型|示例问句|
|----|----|
|个股资讯|格力电器最新研报、贵州茅台机构观点|
|板块/主题|商业航天板块近期新闻、新能源政策解读|
|宏观/风险|A股具备自然对冲优势的公司 汇率风险、美联储加息对A股影响|
|综合解读|今日大盘异动原因、北向资金流向解读|

## 返回说明

|字段路径|简短释义|
|----|----|
|title|信息标题，高度概括核心内容|
|secuList|关联证券列表，含代码、名称、类型等|
|trunk|信息核心正文，承载具体业务数据|

## 注意事项

- 需要妙想API KEY才能使用
- 金融场景专用，避免搜索到非权威或过时信息
- 适用于需要时效性的新闻、公告、研报等
