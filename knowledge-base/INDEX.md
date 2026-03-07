# 知识库全局索引

> 快速查找所有知识条目
> 
> **所有模型必读**: 回答前先查此索引，再深入对应文档

## 快速导航

| 找什么 | 去哪里 |
|--------|--------|
| 储能项目相关 | [projects/储能工具包](projects/储能工具包/) |
| 股票分析相关 | [projects/股票分析系统](projects/股票分析系统/) |
| Agent开发流程 | [projects/多Agent开发框架](projects/多Agent开发框架/) |
| 系统故障排查 | [problems/openclaw/](problems/openclaw/) |
| 系统备份恢复 | [system-backup 技能包](../skills/system-backup/SKILL.md) |
| 飞书文件发送 | [operations/飞书文件发送](operations/飞书文件发送.md) |
| 模型切换方法 | [operations/模型切换](operations/模型切换.md) |
| API/配置参考 | [references/](references/) |
| 重要决策记录 | [decisions/](decisions/) |

## 项目索引

### 🟢 储能工具包
| 文档 | 内容 | 标签 | 更新时间 |
|------|------|------|---------|
| [项目概览](projects/储能工具包/README.md) | 7个在线工具介绍 | #储能 #核心项目 | 2026-03-04 |

**核心功能**:
- 全国电价查询（31省份）
- 电气接线图绘制
- 储能智能排布
- 工商业储能测算

### 🟢 股票分析系统
| 文档 | 内容 | 标签 | 更新时间 |
|------|------|------|---------|
| [项目概览](projects/股票分析系统/README.md) | 自选股监控（A股+港股） | #股票 #自动化 #技术指标 | 2026-03-07 |

**核心功能**:
- 8只自选股实时监控（6只A股 + 2只港股）
- 新浪财经+雪球+腾讯K线融合数据源
- 技术指标：MA/RSI/趋势判断/偏离度
- 估值指标：PE/PB/换手率/52周位置
- 技术形态识别：杯柄形态/双底(W底)/头肩底
- 估值策略筛选：PB-ROE/PEG/综合评分
- 每日16:30自动推送详细报告（港股16:10收盘后）
- 交互式深度分析（按需查询完整报告）

### 🟢 多Agent开发框架
| 文档 | 内容 | 标签 | 更新时间 |
|------|------|------|---------|
| [开发流程](projects/多Agent开发框架/README.md) | 5-Agent并行开发 | #多Agent #开发 | 2026-03-04 |

**团队角色**: Alpha(Builder) / Bravo(Builder) / Charlie(Reviewer) / Delta(Reviewer) / Echo(Ops)

## 决策索引

| 日期 | 决策 | 状态 | 标签 |
|------|------|------|------|
| 2026-03-04 | [飞书文件发送路径规范](decisions/2026-03-04-飞书文件发送路径规范.md) | ✅已采纳 | #飞书 #运维 |
| 2026-03-04 | [知识库管理体系建立](decisions/2026-03-04-知识库管理体系建立.md) | ✅已采纳 | #知识库 #管理 |
| 2026-03-06 | [备份策略升级](decisions/2026-03-06-备份策略升级.md) | ✅已采纳 | #备份 #运维 |

## 运维知识索引

| 主题 | 文档 | 状态 | 标签 |
|------|------|------|------|
| 飞书文件发送 | [飞书文件发送](operations/飞书文件发送.md) | ✅已验证 | #飞书 #文件发送 |
| 模型切换 | [模型切换](operations/模型切换.md) | ✅已验证 | #OpenClaw #模型 |
| 模型切换指令规范 | [模型切换指令规范](operations/模型切换指令规范.md) | ✅已生效 | #OpenClaw #指令规范 |
| 灾难恢复 | [灾难恢复手册](operations/灾难恢复手册.md) | ✅已生效 | #OpenClaw #紧急 |
| 系统备份 | [system-backup 技能包](../skills/system-backup/SKILL.md) | ✅已部署 | #备份 #运维 |

## 问题索引

### OpenClaw
| 问题 | 解决方案 | 状态 | 位置 |
|------|---------|------|------|
| 模型不允许错误 | 检查配置 | ✅已解决 | problems/openclaw/ |
| 飞书图片发送失败 | 使用workspace目录 | ✅已解决 | [operations/飞书文件发送](operations/飞书文件发送.md) |

## 参考资料索引

| 文档 | 用途 | 标签 |
|------|------|------|
| [模型配置参考](references/模型配置参考.md) | OpenClaw模型切换 | #OpenClaw #配置 |
| [Office技能包整理](references/office-skills-overview.md) | ClawHub Office技能包对比 | #Office #技能包 |
| [ClawHub技能包调研](references/clawhub-skills-report.md) | ClawHub技能包完整调研 | #ClawHub #技能包 |
| [本地技能包索引](references/local-skills-index.md) | 自定义技能包清单 | #技能包 #本地 |

## 统计信息

- **项目数**: 3
- **决策数**: 3
- **运维文档**: 5
- **技能包**: 3 (office-pro, system-backup, xueqiu-stock-client)
- **最后更新**: 2026-03-07

---
*使用 [GUIDE.md](GUIDE.md) 了解知识库使用规范*
