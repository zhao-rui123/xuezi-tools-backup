# ⚡ 能源解决方案 Agent

**本地可运行的新能源电力方案分析工具**

---

## 🎯 定位

方案分析底座 — 在本地基线规则、年度时序、调度、结算和省级差异规则之上，**稳定输出结构化结论**。

不是正式可研软件，而是**快速验证思路、生成专业报告**的好帮手。

---

## 💡 能做什么

### 📦 场景覆盖

| 场景 | 说明 |
|------|------|
| 工商业储能 | 容量测算、收益模拟、调度策略 |
| 光储充 | 充电站与储能协同、削峰填谷 |
| 源网荷储 | 光伏/风电压低净负荷后储能选型 |
| 零碳工厂 | 碳核算、减排路径、行业模板 |
| 电力交易 | 日内套利、现货价差、收益分解 |
| 微电网 | 离网系统、冷热电联供 |

### 🔧 核心能力

- **光伏/风电资源建模** — P50/P90、LCOE、PR修正
- **储能年度调度** — 寿命、衰减、循环次数、SOC策略
- **中国电力市场** — 分时电价、需量、交易结算、省级规则
- **碳排放核算** — 范围一/二、减排路径拆分
- **敏感性分析** — 价差、设备成本、折现率敏感度
- **在线规则刷新** — 联网抓取省级最新政策

---

## 📊 输出形式

```
✅ JSON 结构化数据  — 程序二次处理
✅ Markdown 报告   — 快速查看结论
✅ Word 设计院报告 — 专业可交付（带图表）
✅ Excel 财务表    — 投资测算明细
```

---

## 🚀 快速开始

**分析一个项目：**
```bash
python -m energy_solution_agent analyze \
  --input 项目.json \
  --output result.json \
  --report report.md \
  --report-docx 设计院报告.docx
```

**开启联网规则刷新：**
```bash
python -m energy_solution_agent analyze \
  --input 项目.json \
  --output result.json \
  --live-rules
```

**批量跑 Benchmark：**
```bash
python -m energy_solution_agent benchmark \
  --examples examples \
  --output summary.json
```

---

## 📁 内置示例

- `examples/charging_station_input.json` — 光储充充电站
- `examples/power_trading_storage_input.json` — 电力交易储能
- `examples/source_grid_load_storage_input.json` — 源网荷储
- `examples/zero_carbon_factory_input.json` — 零碳工厂
- `examples/data_center_input.json` — 数据中心
- `examples/microgrid_offgrid_template.json` — 微电网离网

---

## ⚙️ 系统要求

- Python 3.10+
- pandas、numpy、matplotlib（自动安装）
- 无需联网即可运行基础分析
- 联网时可刷新各省最新电价/规则

---

**适用对象：** 能源项目投资、储能系统设计、零碳园区规划、电力交易策略分析
