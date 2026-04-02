# Electrical CAD Skill - 电气设计绘图技能包

*为雪子储能项目电气设计而生 · 国标GB/T · DXF格式输出*

---

## 1. 技能包概述

### 定位
本技能包让AI能够按照雪子的标准绘制配电箱电气图、一次接线图、二次接线图等储能项目相关图纸。输出格式为DXF，可直接用AutoCAD/EPlan/ZW3D打开。

### 核心能力
- ✅ 符合GB/T国标的电气符号（断路器、接触器、电流互感器、继电器等）
- ✅ 标准图层分层（供电设计常用结构）
- ✅ 自动电缆标注与线号生成
- ✅ 元器件选型辅助（电缆截面、断路器容量计算）
- ✅ 通过参考图学习雪子的个人绘图风格
- ✅ 与Claude Code无缝集成

### 依赖
```bash
pip install ezdxf numpy
```

---

## 2. 文件结构

```
~/.openclaw/workspace/skills/electrical-cad/
├── SKILL.md                          # 本文件（主入口）
├── symbols/
│   ├── __init__.py
│   ├── gb_symbols.py               # 国标电气符号库（核心）
│   ├── wire_labels.py               # 电缆/线号标注
│   └── components.py                # 元器件封装（配电箱、柜体）
├── templates/
│   ├── distribution_box.dxf         # 配电箱模板参考
│   ├── main_circuit.dxf            # 一次接线图模板
│   ├── secondary_circuit.dxf       # 二次接线图模板
│   └── cabinet_layout.dxf          # 电气柜布局模板
├── standards/
│   ├── layer_std.py                 # 图层标准配置
│   ├── text_std.py                  # 文字/标注标准
│   └── cable_selection.py           # 电缆选型数据库
├── reference/
│   └── .gitkeep                     # 存放雪子的参考图纸（.dxf）
└── scripts/
    ├── generate_panel.py            # 配电箱出图脚本
    ├── generate_wiring.py           # 接线图生成脚本
    └── dxf_to_svg.py                # DXF转SVG预览
```

---

## 3. 电气符号库 Python 代码

### 3.1 国标符号库 `symbols/gb_symbols.py`

> **设计原则**：所有符号基于 GB/T 4728（电气简图用图形符号）系列标准。
> 坐标系单位：毫米（mm）。符号默认以连接点为原点，便于布线。

```python
"""
GB/T 4728 电气符号库 - 储能项目常用符号
Author: 雪子助手
"""

import math
import ezdxf
from ezdxf import mm

# ─────────────────────────────────────────────
# 基础工具函数
# ─────────────────────────────────────────────

def add_line(msp, start, end, layer="WIRE", color=None):
    """通用画线（默认WIRE层）"""
    line = msp.add_line(start, end, dxfattribs={"layer": layer})
    if color:
        line.dxf.color = color
    return line


def add_circle(msp, center, radius, layer="SYMBOL", color=1):
    """通用画圆"""
    c = msp.add_circle(center, radius, dxfattribs={"layer": layer})
    c.dxf.color = color
    return c


def add_text(msp, text, insert, height=3.5, layer="TEXT", align="LEFT"):
    """通用写文字"""
    return msp.add_text(
        text,
        height=height,
        dxfattribs={
            "insert": insert,
            "layer": layer,
            "align": align,
        }
    )


def add_polyline_closed(msp, points, layer="SYMBOL", color=1):
    """通用封闭多段线"""
    pts = points + [points[0]]
    pl = msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})
    pl.dxf.color = color
    return pl


def add_arc_center(msp, center, radius, start_angle, end_angle, layer="SYMBOL", color=1):
    """画圆弧（中心定义）"""
    a = msp.add_arc(center, radius, start_angle, end_angle, dxfattribs={"layer": layer})
    a.dxf.color = color
    return a


# ─────────────────────────────────────────────
# 断路器符号（GB/T 4728.2）
# ─────────────────────────────────────────────

def draw_mcb(msp, pos, rating="C63", width=40, height=60, label=None, layer="SYMBOL"):
    """
    绘制小型断路器（MCB）符号
    pos: 左下角坐标 (x, y)
    rating: 额定电流，如 "C63"（C型脱扣特性，63A）
    width/height: 符号框体尺寸
    """
    x, y = pos

    # 框体矩形
    add_polyline_closed(msp, [
        (x, y), (x + width, y),
        (x + width, y + height), (x, y + height)
    ], layer=layer, color=1)

    # 上接线端（左L进、右L出）
    add_line(msp, (x + 5, y + height), (x + width - 5, y + height), layer=layer)
    add_line(msp, (x + 5, y + height + 5), (x + width - 5, y + height + 5), layer=layer)
    # 上端竖线
    add_line(msp, (x + 5, y + height), (x + 5, y + height + 5), layer=layer)
    add_line(msp, (x + width - 5, y + height), (x + width - 5, y + height + 5), layer=layer)

    # 下接线端
    add_line(msp, (x + 5, y), (x + width - 5, y), layer=layer)
    add_line(msp, (x + 5, y - 5), (x + width - 5, y - 5), layer=layer)
    add_line(msp, (x + 5, y), (x + 5, y - 5), layer=layer)
    add_line(msp, (x + width - 5, y), (x + width - 5, y - 5), layer=layer)

    # 内部断开符号（两条短横线表示触点断开）
    mid_x = x + width / 2
    mid_y = y + height * 0.65
    add_line(msp, (mid_x - 6, mid_y), (mid_x + 6, mid_y), layer=layer)

    # 字符标识（断路器编号 + 额定电流标注）
    label_text = label if label else "QF1"
    add_text(msp, label_text, (x + width / 2, y + height / 2),
             height=4, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, rating, (x + width / 2, y + height + 8),
             height=2.5, layer="TEXT", align="MIDDLE_CENTER")


def draw_acb(msp, pos, rating="630A", width=60, height=100, label="QF1", layer="SYMBOL"):
    """
    绘制万能式断路器（ACB）符号
    用于一次主电路
    """
    x, y = pos

    # 主框体（矩形）
    add_polyline_closed(msp, [
        (x, y), (x + width, y),
        (x + width, y + height), (x, y + height)
    ], layer=layer, color=1)

    # 进线/出线接线柱
    for offset in [0, 20]:
        add_line(msp, (x + 10 + offset, y + height), (x + 10 + offset, y + height + 10), layer=layer)
        add_line(msp, (x + width - 10 - offset, y + height), (x + width - 10 - offset, y + height + 10), layer=layer)

    # 触点断开符号
    mid_x = x + width / 2
    mid_y = y + height * 0.6
    add_line(msp, (mid_x - 10, mid_y), (mid_x + 10, mid_y), layer=layer)

    # 标注
    add_text(msp, label, (mid_x, y + height * 0.5), height=5, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, rating, (mid_x, y + height * 0.75), height=3.5, layer="TEXT", align="MIDDLE_CENTER")


# ─────────────────────────────────────────────
# 接触器符号（GB/T 4728.2）
# ─────────────────────────────────────────────

def add_rect(msp, pos, width, height, layer="SYMBOL", color=1, label=None):
    """通用矩形"""
    x, y = pos
    add_polyline_closed(msp, [(x, y), (x + width, y), (x + width, y + height), (x, y + height)],
                        layer=layer, color=color)
    if label:
        add_text(msp, label, (x + width / 2, y + height / 2),
                 height=3, layer="TEXT", align="MIDDLE_CENTER")


def draw_contactor(msp, pos, coil_voltage="220V", rating="40A", width=50, height=80,
                   label="KM1", layer="SYMBOL"):
    """
    绘制接触器符号（含线圈和主触点）
    注意：接触器线圈和触点组分开画，通过标签关联
    """
    x, y = pos

    # 主触点框
    add_polyline_closed(msp, [
        (x, y), (x + width, y),
        (x + width, y + height * 0.6), (x, y + height * 0.6)
    ], layer=layer, color=1)

    # 上端母线连接
    add_line(msp, (x, y + height * 0.6), (x, y + height), layer="WIRE")
    add_line(msp, (x + width, y + height * 0.6), (x + width, y + height), layer="WIRE")

    # 线圈框（单独画在旁边）
    coil_x = x + width + 15
    coil_y = y
    add_rect(msp, (coil_x, coil_y), width=25, height=30, layer=layer, label=f"{label}线圈")
    add_text(msp, coil_voltage, (coil_x + 12.5, coil_y + 12), height=2.5, layer="TEXT", align="MIDDLE_CENTER")

    # 标注
    add_text(msp, label, (x + width / 2, y + height * 0.3), height=4, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, rating, (x + width / 2, y + height * 0.45), height=3, layer="TEXT", align="MIDDLE_CENTER")


# ─────────────────────────────────────────────
# 电流互感器（CT）符号（GB/T 4728.2）
# ─────────────────────────────────────────────

def draw_ct(msp, pos, ratio="100/5", accuracy="0.5", width=30, height=60,
            label="TA1", layer="SYMBOL"):
    """
    绘制电流互感器符号
    图形为两个圆叠在一起（空心电流互感器）
    """
    x, y = pos
    cx, cy = x + width / 2, y + height / 2

    # 外圆（大圆）
    add_circle(msp, (cx, cy), radius=width / 2, layer=layer, color=1)
    # 内圆（小圆）
    add_circle(msp, (cx, cy), radius=width / 4, layer=layer, color=1)

    # 一次侧引线（L1进、L2出）
    add_line(msp, (cx, y), (cx, y - 10), layer="WIRE")
    add_line(msp, (cx, y + height), (cx, y + height + 10), layer="WIRE")

    # P1/P2 标识
    add_text(msp, "P1", (cx + width / 2 + 3, y + 5), height=2.5, layer="TEXT")
    add_text(msp, "P2", (cx + width / 2 + 3, y + height - 5), height=2.5, layer="TEXT")

    # 标注
    add_text(msp, label, (cx, y - 18), height=3, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, ratio, (cx + width / 2 + 5, cy), height=2.5, layer="TEXT")
    add_text(msp, accuracy, (cx - width / 2 - 2, cy), height=2, layer="TEXT")


# ─────────────────────────────────────────────
# 熔断器符号（GB/T 4728.4）
# ─────────────────────────────────────────────

def draw_fuse(msp, pos, rating="63A", width=15, height=40, label="FU1", layer="SYMBOL"):
    """
    绘制熔断器符号
    矩形+对角线表示熔丝元件
    """
    x, y = pos

    # 熔体座（矩形）
    add_polyline_closed(msp, [
        (x, y), (x + width, y),
        (x + width, y + height), (x, y + height)
    ], layer=layer, color=1)

    # 对角线（熔丝）
    add_line(msp, (x, y + height), (x + width, y), layer=layer, color=1)

    # 接线引线
    add_line(msp, (x + width / 2, y + height), (x + width / 2, y + height + 8), layer="WIRE")
    add_line(msp, (x + width / 2, y), (x + width / 2, y - 8), layer="WIRE")

    # 标注
    add_text(msp, label, (x + width / 2, y + height / 2),
             height=3, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, rating, (x + width / 2, y - 12), height=2.5, layer="TEXT", align="MIDDLE_CENTER")


# ─────────────────────────────────────────────
# 避雷器符号
# ─────────────────────────────────────────────

def draw_surge_arrester(msp, pos, rating="DC1500V", width=20, height=40,
                        label="SA1", layer="SYMBOL"):
    """
    绘制浪涌保护器（避雷器）符号
    三角形朝下接地
    """
    x, y = pos

    # 三角形（3个点）
    triangle_pts = [
        (x + width / 2, y),           # 顶点
        (x, y + height),              # 左下
        (x + width, y + height),      # 右下
        (x + width / 2, y),           # 闭合
    ]
    add_polyline_closed(msp, triangle_pts, layer=layer, color=1)

    # 接地线
    add_line(msp, (x + width / 2, y + height), (x + width / 2, y + height + 10), layer="PE", color=3)
    add_line(msp, (x + width / 2 - 5, y + height + 10), (x + width / 2 + 5, y + height + 10), layer="PE", color=3)
    add_line(msp, (x + width / 2 - 3, y + height + 13), (x + width / 2 + 3, y + height + 13), layer="PE", color=3)

    # 标注
    add_text(msp, label, (x + width / 2, y - 8), height=3, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, rating, (x + width / 2, y + height + 18), height=2.5, layer="TEXT", align="MIDDLE_CENTER")


# ─────────────────────────────────────────────
# 储能电池簇符号
# ─────────────────────────────────────────────

def draw_battery_cluster(msp, pos, voltage="1536V", capacity="200Ah",
                         num_modules=10, width=200, height=80,
                         label="BAT1", layer="BATTERY"):
    """
    绘制电池簇示意符号
    用于储能系统一次图
    """
    x, y = pos

    # 外框
    add_polyline_closed(msp, [
        (x, y), (x + width, y),
        (x + width, y + height), (x, y + height)
    ], layer=layer, color=2)

    # 内部电池模组（矩形堆叠）
    module_w = (width - 30) / num_modules
    for i in range(num_modules):
        mx = x + 15 + i * module_w
        add_polyline_closed(msp, [
            (mx, y + 15), (mx + module_w - 4, y + 15),
            (mx + module_w - 4, y + height - 15), (mx, y + height - 15)
        ], layer=layer, color=2)
        add_text(msp, f"B{i + 1}", (mx + module_w / 2, y + height / 2),
                 height=3, layer="TEXT", align="MIDDLE_CENTER")

    # 正负极端
    add_text(msp, "+", (x - 10, y + height / 2), height=8, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, "-", (x + width + 5, y + height / 2), height=8, layer="TEXT", align="MIDDLE_CENTER")

    # 总标注
    add_text(msp, label, (x + width / 2, y + height + 8),
             height=4, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, f"{voltage} {capacity}", (x + width / 2, y - 10),
             height=3, layer="TEXT", align="MIDDLE_CENTER")


# ─────────────────────────────────────────────
# 逆变器/PCS 符号
# ─────────────────────────────────────────────

def draw_pcs(msp, pos, rating="500kW", voltage="AC380V",
             width=120, height=80, label="PCS1", layer="SYMBOL"):
    """
    绘制储能变流器（PCS）符号
    长方形 + 内部AC/DC标识
    """
    x, y = pos

    # 主体矩形
    add_polyline_closed(msp, [
        (x, y), (x + width, y),
        (x + width, y + height), (x, y + height)
    ], layer=layer, color=1)

    # 内部分隔线（DC侧 / AC侧）
    mid_x = x + width * 0.4
    add_line(msp, (mid_x, y), (mid_x, y + height), layer=layer, color=1)

    # DC侧标识
    add_text(msp, "DC", (x + mid_x / 2, y + height / 2),
             height=6, layer="TEXT", align="MIDDLE_CENTER")

    # AC侧标识
    add_text(msp, "AC", (x + mid_x + (width - mid_x) / 2, y + height / 2),
             height=6, layer="TEXT", align="MIDDLE_CENTER")

    # 标注
    add_text(msp, label, (x + width / 2, y - 10),
             height=4, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, rating, (x + width / 2, y + height + 8),
             height=3, layer="TEXT", align="MIDDLE_CENTER")


# ─────────────────────────────────────────────
# 继电器符号
# ─────────────────────────────────────────────

def draw_relay(msp, pos, type="DJ", label="K1", width=40, height=50,
               layer="SYMBOL"):
    """
    绘制继电器符号（线圈+触点组）
    type: DJ=中间继电器, OJ=过载继电器, LJ=漏电继电器
    """
    x, y = pos

    # 线圈框
    add_polyline_closed(msp, [
        (x, y), (x + width, y),
        (x + width, y + height * 0.4), (x, y + height * 0.4)
    ], layer=layer, color=1)
    add_text(msp, label, (x + width / 2, y + height * 0.2),
             height=4, layer="TEXT", align="MIDDLE_CENTER")

    # 触点组（常开NO/常闭NC）
    # 常开触点
    cx = x + width + 10
    add_line(msp, (cx, y), (cx, y + height), layer="WIRE")
    add_line(msp, (cx, y + height * 0.4), (cx + 12, y + height * 0.6), layer=layer, color=1)
    add_line(msp, (cx + 12, y + height * 0.6), (cx + 12, y + height), layer="WIRE")

    # 标注 NO/NC
    add_text(msp, "NO", (cx + 12, y + height * 0.3), height=2.5, layer="TEXT")


# ─────────────────────────────────────────────
# 测量仪表符号
# ─────────────────────────────────────────────

def draw_ammeter(msp, pos, range="200A", label="PA1", size=30, layer="SYMBOL"):
    """绘制电流表"""
    x, y = pos
    add_circle(msp, (x + size / 2, y + size / 2), size / 2, layer=layer, color=1)
    add_text(msp, "A", (x + size / 2, y + size / 2), height=8, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, label, (x + size / 2, y - 8), height=2.5, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, range, (x + size / 2, y + size + 5), height=2.5, layer="TEXT", align="MIDDLE_CENTER")


def draw_voltmeter(msp, pos, range="500V", label="PV1", size=30, layer="SYMBOL"):
    """绘制电压表"""
    x, y = pos
    add_circle(msp, (x + size / 2, y + size / 2), size / 2, layer=layer, color=1)
    add_text(msp, "V", (x + size / 2, y + size / 2), height=8, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, label, (x + size / 2, y - 8), height=2.5, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, range, (x + size / 2, y + size + 5), height=2.5, layer="TEXT", align="MIDDLE_CENTER")


def draw_wattmeter(msp, pos, label="PW1", width=40, height=25, layer="SYMBOL"):
    """绘制功率表"""
    x, y = pos
    add_circle(msp, (x + width / 2, y + height / 2), height / 2, layer=layer, color=1)
    add_text(msp, "W", (x + width / 2, y + height / 2), height=6, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, label, (x + width / 2, y - 8), height=2.5, layer="TEXT", align="MIDDLE_CENTER")


# ─────────────────────────────────────────────
# 隔离开关符号（GB/T 4728.2 §07）
# ─────────────────────────────────────────────

def draw_isolator(msp, pos, rating="630A", width=50, height=60, 
                  label="QS1", layer="SYMBOL"):
    """
    绘制隔离开关符号（有明显断口的刀闸）
    """
    x, y = pos
    
    # 绘制断开点（对角线表示断开）
    add_line(msp, (x, y + height), (x + width, y), layer=layer, color=1)
    
    # 上下连接线
    add_line(msp, (x + width/2, y + height), (x + width/2, y + height + 8), layer="WIRE")
    add_line(msp, (x + width/2, y), (x + width/2, y - 8), layer="WIRE")
    
    # 标注
    add_text(msp, label, (x + width/2, y + height/2), height=4, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, rating, (x + width/2, y + height + 12), height=2.5, layer="TEXT", align="MIDDLE_CENTER")


# ─────────────────────────────────────────────
# 接地符号（GB/T 4728.2 §02）
# ─────────────────────────────────────────────

def draw_ground(msp, pos, label="PE", layer="PE"):
    """
    绘制接地符号
    """
    x, y = pos
    
    # 斜线
    add_line(msp, (x - 10, y), (x + 10, y + 20), layer=layer, color=3)
    
    # 水平线（逐条递减）
    add_line(msp, (x - 8, y + 20), (x + 8, y + 20), layer=layer, color=3)
    add_line(msp, (x - 6, y + 25), (x + 6, y + 25), layer=layer, color=3)
    add_line(msp, (x - 4, y + 30), (x + 4, y + 30), layer=layer, color=3)
    
    # 标注
    add_text(msp, label, (x + 15, y + 10), height=3, layer="TEXT")


# ─────────────────────────────────────────────
# 三相电力变压器符号
# ─────────────────────────────────────────────

def draw_transformer_3phase(msp, pos, rating="5200kVA/35kV", 
                           voltage="690V/35kV", label="T1",
                           width=100, height=80, layer="SYMBOL"):
    """
    绘制三相双绕组变压器符号（储能系统升压变压器）
    """
    x, y = pos
    
    # 高压侧圆（35kV侧）
    add_circle(msp, (x + 20, y + height/2), 15, layer=layer, color=1)
    
    # 低压侧圆（690V侧）
    add_circle(msp, (x + width - 20, y + height/2), 15, layer=layer, color=1)
    
    # 连接线
    add_line(msp, (x + 35, y + height/2), (x + width - 35, y + height/2), layer="BUS", color=1)
    
    # 三相标识
    add_text(msp, "A", (x + 15, y + height/2 + 5), height=3, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, "a", (x + width - 20, y + height/2 + 5), height=3, layer="TEXT", align="MIDDLE_CENTER")
    
    # 标注
    add_text(msp, label, (x + width/2, y - 15), height=4, layer="TEXT", align="MIDDLE_CENTER")
    add_text(msp, rating, (x + width/2, y + height + 8), height=2.5, layer="S-25TXT", align="MIDDLE_CENTER")
    add_text(msp, voltage, (x + width/2, y + height + 20), height=2.5, layer="S-25TXT", align="MIDDLE_CENTER")


# ─────────────────────────────────────────────
# 端子排符号
# ─────────────────────────────────────────────

def draw_terminal_block(msp, pos, num_terminals=10, width=120, height=8,
                        label="TB1", layer="TERMINAL"):
    """
    绘制端子排符号
    """
    x, y = pos
    
    # 端子排主体线
    add_line(msp, (x, y), (x + width, y), layer=layer, color=1)
    
    # 每个端子的圆点
    for i in range(num_terminals):
        tx = x + 10 + i * (width - 20) / (num_terminals - 1) if num_terminals > 1 else x + width/2
        add_circle(msp, (tx, y), 3, layer=layer, color=1)
        add_text(msp, str(i + 1), (tx, y - 5), height=2, layer="TEXT", align="MIDDLE_CENTER")
    
    # 标注
    add_text(msp, label, (x, y - 12), height=3, layer="TEXT")


# ─────────────────────────────────────────────
# 按钮/信号灯符号
# ─────────────────────────────────────────────

def draw_pushbutton(msp, pos, button_type="NO", label="SB1",
                    size=15, layer="SYMBOL"):
    """
    绘制按钮或信号灯符号
    button_type: "NO"=常开按钮, "NC"=常闭按钮, "指示灯"=信号灯
    """
    x, y = pos
    
    if button_type == "指示灯":
        # 信号灯（圆形）
        add_circle(msp, (x + size/2, y + size/2), size/2, layer=layer, color=3)
        add_text(msp, "⊗", (x + size/2, y + size/2), height=8, layer="TEXT", align="MIDDLE_CENTER")
    else:
        # 按钮（矩形）
        add_polyline_closed(msp, [
            (x, y), (x + size, y),
            (x + size, y + size), (x, y + size)
        ], layer=layer, color=1)
        
        if button_type == "NO":
            add_line(msp, (x + 2, y + size/2), (x + size - 2, y + size/2), layer=layer, color=1)
        else:  # NC
            add_line(msp, (x + 2, y + size/2 - 3), (x + size - 2, y + size/2 + 3), layer=layer, color=1)
            add_line(msp, (x + 2, y + size/2 + 3), (x + size - 2, y + size/2 - 3), layer=layer, color=1)
    
    add_text(msp, label, (x + size/2, y - 8), height=2.5, layer="TEXT", align="MIDDLE_CENTER")


# ─────────────────────────────────────────────
# 电缆桥架/线槽符号
# ─────────────────────────────────────────────

def draw_cable_tray(msp, start, end, width=40, label="CT-01", layer="WIRE"):
    """
    绘制电缆桥架走向（矩形线槽）
    """
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = (dx**2 + dy**2)**0.5
    angle = 0
    
    if abs(dx) > abs(dy):
        # 水平走向
        add_line(msp, (start[0], start[1] - width/2), (end[0], end[1] - width/2), layer=layer, color=4)
        add_line(msp, (start[0], start[1] + width/2), (end[0], end[1] + width/2), layer=layer, color=4)
    else:
        # 垂直走向
        add_line(msp, (start[0] - width/2, start[1]), (end[0] - width/2, end[1]), layer=layer, color=4)
        add_line(msp, (start[0] + width/2, start[1]), (end[0] + width/2, end[1]), layer=layer, color=4)
    
    # 标注
    mid_x = (start[0] + end[0]) / 2
    mid_y = (start[1] + end[1]) / 2
    add_text(msp, label, (mid_x + 5, mid_y), height=2.5, layer="LABEL")
```

---

### 3.2 电缆/线号标注 `symbols/wire_labels.py`

```python
"""
电缆标注与线号生成工具
"""

def draw_cable_label(msp, start, end, cable_spec, label=None, layer="LABEL"):
    """
    在两点之间绘制电缆标注
    start/end: 电缆起点/终点坐标
    cable_spec: 电缆规格字符串，如 "ZRYJV-0.6/1kV-3×70+1×35"
    label: 电缆编号，如 "WL1"
    """
    from ezdxf import mm

    # 计算电缆走向（水平或垂直）
    dx = end[0] - start[0]
    dy = end[1] - start[1]

    if abs(dx) > abs(dy):
        # 水平电缆 - 标注在线上方
        mid_x = (start[0] + end[0]) / 2
        mid_y = max(start[1], end[1]) + 8

        # 标注文字
        if label:
            msp.add_text(label, height=3, dxfattribs={"insert": (mid_x, mid_y + 3), "layer": layer})
        msp.add_text(cable_spec, height=2.5, dxfattribs={"insert": (mid_x, mid_y - 3), "layer": layer})

        # 引出线
        msp.add_line((mid_x, mid_y - 5), (mid_x, mid_y - 8), dxfattribs={"layer": "WIRE"})
    else:
        # 垂直电缆 - 标注在线右侧
        mid_x = max(start[0], end[0]) + 8
        mid_y = (start[1] + end[1]) / 2

        if label:
            msp.add_text(label, height=3, dxfattribs={"insert": (mid_x, mid_y + 3), "layer": layer})
        msp.add_text(cable_spec, height=2.5, dxfattribs={"insert": (mid_x, mid_y - 3), "layer": layer})
        msp.add_line((mid_x - 5, mid_y), (mid_x - 8, mid_y), dxfattribs={"layer": "WIRE"})


def generate_wire_numbers(circuit, prefix="WC", start=1):
    """
    自动生成线号
    circuit: 电路类型，如 "power", "control", "signal"
    start: 起始编号
    返回格式：WC001, WC002, ...
    """
    if circuit == "power":
        return f"{prefix}{start:02d}"
    elif circuit == "control":
        return f"{prefix}{start:03d}"
    elif circuit == "signal":
        return f"{prefix}{start:03d}S"
    return f"{prefix}{start}"


def draw_terminal(msp, pos, label="1", size=8, layer="TERMINAL"):
    """
    绘制端子符号（圆点）
    pos: 端子位置
    label: 端子号
    """
    from ezdxf.boundary import Inspectors
    c = msp.add_circle(pos, size / 2, dxfattribs={"layer": layer})
    c.dxf.color = 1  # 红色端子
    msp.add_text(label, height=size * 0.6,
                 dxfattribs={"insert": pos, "layer": "TEXT", "align": "MIDDLE_CENTER"})


def draw_jump_wire(msp, points, wire_no=None, layer="WIRE"):
    """
    绘制跳线（多段连续线）
    points: 线段点列表 [(x1,y1), (x2,y2), ...]
    wire_no: 线号
    """
    for i in range(len(points) - 1):
        msp.add_line(points[i], points[i + 1], dxfattribs={"layer": layer})

    # 在中点标注线号
    if wire_no and len(points) >= 2:
        mid_idx = len(points) // 2
        mid = points[mid_idx]
        msp.add_text(wire_no, height=2.5,
                     dxfattribs={"insert": (mid[0] + 3, mid[1] + 3), "layer": "WIRE_NO"})
```

---

## 4. 标注规范

### 4.1 图层标准 `standards/layer_std.py`

> **图层命名原则**：`类型_名称`，全英文，简洁。颜色按国标习惯设置。

```python
"""
图层标准配置 - 供电/储能项目常用分层
参考：GB/T 18112-2010《CAD工程制图规则》
"""

LAYER_STANDARD = {
    # ═══════════════════════════════════════════
    # 结构层
    # ═══════════════════════════════════════════
    "BORDER": {
        "name": "图框",
        "color": 7,      # 白色
        "lineweight": 0.5,
        "description": "图纸边界、图框线"
    },
    "CENTER": {
        "name": "中心线",
        "color": 1,      # 红色
        "lineweight": 0.25,
        "linetype": "CENTER",
        "description": "对称轴、中心线"
    },
    "OUTLINE": {
        "name": "轮廓线",
        "color": 7,
        "lineweight": 0.5,
        "description": "箱体、柜体、面板外轮廓"
    },
    "HATCH": {
        "name": "填充",
        "color": 8,
        "lineweight": 0.18,
        "description": "剖面填充、设备填充"
    },

    # ═══════════════════════════════════════════
    # 电气层
    # ═══════════════════════════════════════════
    "WIRE": {
        "name": "导线",
        "color": 1,      # 红色（主回路）
        "lineweight": 0.5,
        "description": "主回路导线/母线"
    },
    "WIRE_AC": {
        "name": "交流线",
        "color": 1,
        "lineweight": 0.5,
        "description": "交流回路导线"
    },
    "WIRE_DC": {
        "name": "直流线",
        "color": 3,      # 绿色（直流）
        "lineweight": 0.5,
        "description": "直流回路导线（储能电池侧）"
    },
    "WIRE_CT": {
        "name": "电流回路",
        "color": 5,      # 蓝色（测量回路）
        "lineweight": 0.35,
        "description": "电流互感器回路、二次测量线"
    },
    "WIRE_CTRL": {
        "name": "控制回路",
        "color": 4,      # 青色（控制）
        "lineweight": 0.35,
        "description": "二次控制回路"
    },
    "BUS": {
        "name": "母线",
        "color": 1,
        "lineweight": 0.7,
        "description": "主母线、汇流排"
    },

    # ═══════════════════════════════════════════
    # 符号层
    # ═══════════════════════════════════════════
    "SYMBOL": {
        "name": "电气符号",
        "color": 1,
        "lineweight": 0.35,
        "description": "断路器、接触器、继电器等设备符号"
    },
    "BATTERY": {
        "name": "电池符号",
        "color": 2,      # 黄色（储能特征）
        "lineweight": 0.5,
        "description": "电池簇、模组符号"
    },
    "TERMINAL": {
        "name": "端子",
        "color": 1,
        "lineweight": 0.5,
        "description": "接线端子、插针"
    },
    "PE": {
        "name": "保护接地",
        "color": 3,      # 绿色
        "lineweight": 0.5,
        "linetype": "PHANTOM",
        "description": "PE保护接地线"
    },

    # ═══════════════════════════════════════════
    # 标注层
    # ═══════════════════════════════════════════
    "TEXT": {
        "name": "文字标注",
        "color": 7,
        "lineweight": 0.18,
        "description": "设备编号、型号规格"
    },
    "TEXT_MAIN": {
        "name": "主标注",
        "color": 7,
        "lineweight": 0.25,
        "description": "图纸标题、主要说明"
    },
    "WIRE_NO": {
        "name": "线号",
        "color": 7,
        "lineweight": 0.18,
        "description": "导线编号（如 WC001）"
    },
    "LABEL": {
        "name": "电缆标注",
        "color": 4,
        "lineweight": 0.18,
        "description": "电缆规格、起止点"
    },
    "DIM": {
        "name": "尺寸标注",
        "color": 2,
        "lineweight": 0.18,
        "description": "几何尺寸标注"
    },

    # ═══════════════════════════════════════════
    # 特殊层
    # ═══════════════════════════════════════════
    "HIDDEN": {
        "name": "隐藏线",
        "color": 8,
        "lineweight": 0.18,
        "linetype": "DASHED",
        "description": "不可见轮廓线"
    },
}


def setup_layers(doc):
    """
    在DXF文档中创建标准图层
    doc: ezdxf.Document 对象
    """
    for layer_name, cfg in LAYER_STANDARD.items():
        if layer_name.upper() in doc.layers:
            continue  # 已存在则跳过

        doc.layers.add(
            layer_name.upper(),
            name=cfg["name"],
            color=cfg["color"],
            lineweight=cfg["lineweight"],
            description=cfg["description"]
        )

        # 设置线型
        if "linetype" in cfg:
            try:
                doc.linetypes.add(cfg["linetype"])  # 确保线型存在
            except Exception:
                pass  # 线型不存在则忽略
```

### 4.2 文字/标注标准 `standards/text_std.py`

```python
"""
文字与标注样式标准
参考：GB/T 14691-1993《技术制图 字体》
"""

TEXT_STYLE_STANDARD = {
    # 图纸标题
    "TITLE": {
        "height": 7.0,
        "width_factor": 0.7,
        "font": "gbenor.shx",
        "layer": "TEXT_MAIN",
        "color": 7,
        "description": "图纸名称、大标题"
    },
    # 图纸比例
    "SUBTITLE": {
        "height": 5.0,
        "width_factor": 0.7,
        "font": "gbeitc.shx",
        "layer": "TEXT",
        "color": 7,
        "description": "副标题、比例说明"
    },
    # 设备编号（QF1、KM1等）
    "COMPONENT": {
        "height": 4.0,
        "width_factor": 0.7,
        "font": "gbeitc.shx",
        "layer": "TEXT",
        "color": 1,
        "description": "元器件编号"
    },
    # 规格参数
    "SPEC": {
        "height": 3.5,
        "width_factor": 0.7,
        "font": "gbeitc.shx",
        "layer": "TEXT",
        "color": 7,
        "description": "额定电流、电压等规格"
    },
    # 线号标注
    "WIRE_NO": {
        "height": 2.5,
        "width_factor": 0.7,
        "font": "gbeitc.shx",
        "layer": "WIRE_NO",
        "color": 7,
        "description": "导线编号"
    },
    # 电缆标注
    "CABLE": {
        "height": 3.0,
        "width_factor": 0.7,
        "font": "gbeitc.shx",
        "layer": "LABEL",
        "color": 4,
        "description": "电缆型号规格"
    },
    # 图框信息
    "BORDER_INFO": {
        "height": 3.5,
        "width_factor": 0.7,
        "font": "gbenor.shx",
        "layer": "BORDER",
        "color": 7,
        "description": "图框内公司名、日期、版本"
    },
}


def setup_text_styles(doc):
    """
    在DXF文档中创建标准文字样式
    """
    for style_name, cfg in TEXT_STYLE_STANDARD.items():
        style = doc.styles.new(style_name)
        style.height = cfg["height"]
        style.width = cfg["width_factor"]
        try:
            style.font = cfg["font"]
        except Exception:
            style.font = "Standard"  # 回退字体


# ─────────────────────────────────────────────
# 常用标注高度速查表
# ─────────────────────────────────────────────
"""
| 标注类型        | 文字高度(mm) | 用途                    |
|----------------|-------------|------------------------|
| 图名（TITLE）   | 7.0         | 图纸标题                 |
| 副标题          | 5.0         | 项目名、图别               |
| 设备编号        | 4.0         | QF1、KM1、TA1等          |
| 规格参数        | 3.5         | 63A、220V等              |
| 线号（圆圈内）  | 2.5         | WC001等                 |
| 电缆标注        | 3.0         | ZRYJV-3×70+1×35        |
| 图框信息        | 3.5         | 日期、版本、公司名         |

线宽标准（mm）：
| 对象类型       | 线宽        | 说明           |
|---------------|------------|----------------|
| 图框           | 0.50       | 外框线          |
| 主回路导线      | 0.50       | 红色            |
| 控制回路       | 0.35       | 青色            |
| 直流回路       | 0.50       | 绿色            |
| 符号轮廓       | 0.35       | 红色            |
| 尺寸标注       | 0.18       | 随层            |
| 文字           | 随层       | —               |
"""


---

## 4. 雪子图层规范（基于20尺集装箱储能系统参考图）

> 本图层规范基于雪子实际的20尺集装箱储能系统（5MW/10MWh）DXF参考图
> 共46个图层，涵盖储能集装箱电气设计的完整规范

### 4.1 颜色标准（ACI标准）

| 颜色号 | 颜色 | 含义/用途 |
|--------|------|----------|
| 1 | 红 | 动力线、主回路导线 |
| 2 | 黄 | 剖面线、填充图案 |
| 3 | 绿 | 符号、电气元器件轮廓 |
| 4 | 蓝 | 低压回路、标注尺寸线 |
| 5 | 洋红 | 预留回路、远期规划 |
| 6 | 紫红 | 虚线（不可见轮廓） |
| 7 | 白/黑 | 默认、文字、图框 |

### 4.2 线型标准

| 线型名 | 用途 |
|--------|------|
| Continuous | 实线（主要导线、符号轮廓） |
| CENTER2 | 中心线（轴线、对称线） |
| DASHED2 / DASH | 虚线（隐藏线、预留管路） |
| PHANTOM4 | 双点划线（延伸线、切断线） |
| BORDER2 | 边界线 |

### 4.3 推荐图层结构（精简版）

以下图层是从46个图层中提炼的核心图层：

```python
LAYER_STANDARD = {
    # === 导线/主回路 ===
    "粗实线": {"color": 3, "linetype": "Continuous", "description": "主回路导线、粗实线"},
    "细实线": {"color": 3, "linetype": "Continuous", "description": "二次回路、辅助线"},
    "WIRE-动力": {"color": 2, "linetype": "Continuous", "description": "动力回路"},
    
    # === 中心线/虚线 ===
    "中心线": {"color": 1, "linetype": "CENTER2", "description": "中心线、对称轴"},
    "虚线层": {"color": 6, "linetype": "DASHED2", "description": "隐藏轮廓、预留"},
    
    # === 标注/文字 ===
    "标注层": {"color": 4, "linetype": "Continuous", "description": "尺寸标注"},
    "符号标注": {"color": 31, "linetype": "Continuous", "description": "符号说明"},
    "文字层": {"color": 3, "linetype": "Continuous", "description": "文字标注"},
    
    # === 图框/结构 ===
    "图框层": {"color": 7, "linetype": "Continuous", "description": "图框、边框"},
    "TK": {"color": 7, "linetype": "Continuous", "description": "标题栏"},
    "轮廓实线": {"color": 7, "linetype": "Continuous", "description": "结构轮廓"},
    "轮廓虚线": {"color": 7, "linetype": "DASHED2", "description": "隐藏轮廓"},
    
    # === 专业分类 ===
    "组串": {"color": 7, "linetype": "Continuous", "description": "电池组串"},
    "电池簇": {"color": 7, "linetype": "Continuous", "description": "电池簇标识"},
    "LWIRE": {"color": 4, "linetype": "Continuous", "description": "低压线路"},
}
```

### 4.4 完整图层清单（46层）

来自参考图实际分析结果：

| 图层名 | 颜色 | 线型 | 用途 |
|--------|------|------|------|
| 0 | 7 | Continuous | 默认层 |
| TK | 7 | Continuous | 标题栏 |
| SYMBOL | 3 | Continuous | 符号层 |
| S-25TXT | 3 | Continuous | 2.5号文字 |
| 组串 | 7 | Continuous | 电池组串 |
| ABDE_DENG | 4 | Continuous | 照明配电 |
| WIRE-动力 | 2 | Continuous | 动力回路 |
| 01 | 7 | Continuous | 图层1 |
| 远期 | 5 | DASH | 远期规划 |
| 基础 | 6 | Continuous | 基础结构 |
| TEL_TEXT | 7 | Continuous | 图例文字 |
| TEL_DIM | 3 | Continuous | 图例标注 |
| TEL_SYMB | 3 | Continuous | 图例符号 |
| TEL_ELEV | 3 | Continuous | 图例标高 |
| TEL_LEAD | 3 | Continuous | 图例引线 |
| LWIRE | 4 | Continuous | 低压线路 |
| 粗实线 | 3 | Continuous | 主回路 |
| 细实线 | 3 | Continuous | 二次线 |
| 中心线层 | 1 | CENTER2 | 中心线 |
| 虚线层 | 6 | DASHED2 | 隐藏线 |
| 剖面线层 | 2 | Continuous | 填充 |
| 文字层 | 3 | Continuous | 文字 |
| 标注层 | 4 | Continuous | 尺寸 |
| 符号标注层 | 31 | Continuous | 符号说明 |
| 双点划线层 | 6 | PHANTOM4 | 延伸线 |
| 图框层 | 7 | Continuous | 图框 |

### 4.5 元器件标注标准

来自参考图的储能系统参数：

| 参数类型 | 示例 | 标注位置 |
|----------|------|----------|
| 电池簇容量 | 电池簇容量：417.99kWh | 元器件附近 |
| 电压范围 | 工作电压：11164.8-1497.6VDC | 参数标注 |
| 额定电压 | 额定电压：1331.2VDC | 参数标注 |
| 成组方式 | 成组方式：1P416S | 参数标注 |
| 电芯规格 | 电芯：3.2V 314Ah | 参数标注 |
| PCS功率 | 交流额定功率：1250kW | PCS附近 |
| 变压器参数 | SCB13 5200kVA/35kV | 变压器附近 |
| 电流值 | In=4200A 3P | 断路器附近 |
| 输出配置 | 输出：4路 / 输入：24路 | 配电柜附近 |

---

## 5. ESS储能集装箱专用符号库

基于20尺集装箱储能系统（5MW/10MWh）参考图：

### 5.1 电池簇符号

```python
def draw_battery_cluster(msp, pos, capacity="417.99kWh", voltage="1331.2VDC", 
                         layer="组串", color=7):
    """
    绘制电池簇符号
    pos: 左下角坐标
    capacity: 簇容量
    voltage: 额定电压
    """
    x, y = pos
    
    # 电池簇框体
    add_polyline_closed(msp, [
        (x, y), (x + 200, y),
        (x + 200, y + 80), (x, y + 80)
    ], layer=layer, color=color)
    
    # 簇编号
    add_text(msp, "电池簇", (x + 5, y + 60), height=4, layer="文字层")
    
    # 参数标注
    add_text(msp, f"容量：{capacity}", (x + 5, y + 35), height=3, layer="S-25TXT")
    add_text(msp, f"电压：{voltage}", (x + 5, y + 15), height=3, layer="S-25TXT")
    
    # 直流端子
    add_circle(msp, (x - 10, y + 40), 5, layer=layer, color=1)  # 正极
    add_circle(msp, (x - 10, y + 20), 5, layer=layer, color=4)  # 负极
```

### 5.2 PCS（储能变流器）符号

```python
def draw_pcs(msp, pos, power="1250kW", voltage="690V", layer="SYMBOL", color=3):
    """
    绘制储能变流器符号
    pos: 左下角坐标
    power: 额定功率
    voltage: 输出电压
    """
    x, y = pos
    
    # PCS框体
    add_polyline_closed(msp, [
        (x, y), (x + 120, y),
        (x + 120, y + 100), (x, y + 100)
    ], layer=layer, color=color)
    
    # 标签
    add_text(msp, "PCS", (x + 40, y + 75), height=6, layer="SYMBOL")
    add_text(msp, "储能变流器", (x + 20, y + 55), height=3, layer="文字层")
    add_text(msp, f"功率：{power}", (x + 5, y + 30), height=2.5, layer="S-25TXT")
    add_text(msp, f"电压：{voltage}", (x + 5, y + 10), height=2.5, layer="S-25TXT")
```

### 5.3 升压变压器符号

```python
def draw_transformer(msp, pos, rating="5200kVA/35kV", voltage="690V/35kV",
                     layer="SYMBOL", color=3):
    """
    绘制升压变压器符号
    """
    x, y = pos
    
    # 变压器框体（双矩形=变压器国标符号）
    add_polyline_closed(msp, [(x, y), (x + 80, y),
                               (x + 80, y + 60), (x, y + 60)], layer=layer, color=color)
    add_polyline_closed(msp, [(x + 85, y), (x + 165, y),
                               (x + 165, y + 60), (x + 85, y + 60)], layer=layer, color=color)
    
    # 连接线
    add_line(msp, (x + 80, y + 30), (x + 85, y + 30), layer="粗实线", color=3)
    
    # 标注
    add_text(msp, "升压变压器", (x + 25, y + 70), height=3, layer="文字层")
    add_text(msp, rating, (x + 5, y - 15), height=2.5, layer="S-25TXT")
```

### 5.4 汇流柜符号

```python
def draw_busbar_cabinet(msp, pos, in_count=24, out_count=4,
                        layer="SYMBOL", color=3):
    """
    绘制汇流柜符号
    in_count: 输入路数
    out_count: 输出路数
    """
    x, y = pos
    
    # 柜体
    add_polyline_closed(msp, [
        (x, y), (x + 200, y),
        (x + 200, y + 120), (x, y + 120)
    ], layer=layer, color=color)
    
    # 标签
    add_text(msp, "汇流柜", (x + 60, y + 100), height=4, layer="SYMBOL")
    add_text(msp, f"输入：{in_count}路", (x + 5, y + 70), height=3, layer="S-25TXT")
    add_text(msp, f"输出：{out_count}路", (x + 5, y + 40), height=3, layer="S-25TXT")
```

---

## 6. 参考图学习机制

### 6.1 如何让AI学习新的参考图

当雪子提供新的参考DXF图纸时，AI会自动执行以下分析流程：

```python
def analyze_reference_dxf(dxf_path):
    """
    分析参考图，提取图层规范和符号标准
    """
    import ezdxf
    
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    
    results = {
        "layers": [],
        "symbols": [],
        "text_styles": [],
        "line_types": []
    }
    
    # 1. 提取所有图层
    for layer in doc.layers:
        results["layers"].append({
            "name": layer.dxf.name,
            "color": layer.dxf.color,
            "linetype": getattr(layer.dxf, 'linetype', 'Continuous')
        })
    
    # 2. 提取所有文字
    for e in msp:
        if e.dxftype() == 'TEXT':
            results["text_styles"].append(e.dxf.text)
    
    # 3. 提取所有图块（符号）
    for block in doc.blocks:
        results["symbols"].append(block.name)
    
    return results
```

### 6.2 输出分析报告

AI分析完参考图后，会输出以下报告：

```
=== 参考图分析报告 ===
文件名: 20尺集装箱图纸模板V1.dxf
图纸类型: 储能集装箱电气系统图
图层数量: 46
图块数量: 2951
符号库: [户外柜, 交流汇流柜, 5MW一体机, 电池簇, ...]
颜色规范: 符合ACI标准
线型规范: CENTER2/DASHED2/Continuous
```

### 6.3 学习后的画图流程

```
1. 雪子提供参考图（.dxf）
       ↓
2. AI分析图层、符号、颜色、线型
       ↓
3. 生成"雪子画图标准"配置文件
       ↓
4. 以后画图自动应用此标准
       ↓
5. 输出符合雪子风格的DXF图纸
```

---

## 7. 完整画图示例

### 7.1 生成20尺集装箱储能电气图

```python
import ezdxf
from electrical_cad import (
    draw_battery_cluster, draw_pcs, draw_transformer, 
    draw_busbar_cabinet, setup_layer_standard
)

def generate_20ft_ess_dxf(output_path):
    """
    生成20尺集装箱储能系统电气图
    规格: 5MW/10MWh, 12电池簇, 4×1250kW PCS
    """
    doc = ezdxf.new('R2010')
    setup_layer_standard(doc)  # 应用雪子图层标准
    
    msp = doc.modelspace()
    
    # === 绘制电池簇 (12个) ===
    for i in range(12):
        row = i // 6
        col = i % 6
        x = 100 + col * 220
        y = 500 + row * 100
        draw_battery_cluster(
            msp, (x, y), 
            capacity="417.99kWh",
            voltage="1331.2VDC"
        )
    
    # === 绘制PCS (4个) ===
    for i in range(4):
        draw_pcs(msp, (100 + i * 250, 200), 
                 power="1250kW", voltage="690V")
    
    # === 绘制汇流柜 ===
    draw_busbar_cabinet(msp, (1200, 300), in_count=24, out_count=4)
    
    # === 绘制升压变压器 ===
    draw_transformer(msp, (1500, 200), 
                     rating="5200kVA/35kV")
    
    # === 添加参数表 ===
    add_spec_table(msp, [
        ("合计容量", "5MW/10MWh"),
        ("电池簇", "12个 × 417.99kWh"),
        ("成组方式", "1P416S"),
        ("电芯规格", "3.2V 314Ah"),
    ])
    
    doc.saveas(output_path)
    print(f"✅ 已保存: {output_path}")

generate_20ft_ess_dxf("20尺集装箱储能系统.dxf")
```

---

---

## 8. 电缆清册模板

### 8.1 电缆清册格式

储能项目电缆清册标准格式（CSV格式）：

```csv
电缆编号,电缆型号,起点设备,起点位置,终点设备,终点位置,长度(m),用途说明
WL001,ZRYJV-0.6/1kV-3×70+1×35,汇流柜,QP1-1,PCS1,DC+,45,直流动力线
WL002,ZRYJV-0.6/1kV-3×70+1×35,汇流柜,QP1-2,PCS1,DC-,45,直流动力线
WL003,ZRYJV-0.6/1kV-3×50+1×25,PCS1,AC1,变压器,10kV侧,30,交流输出
WL004,ZRYJV-8.7/15kV-3×95,变压器,35kV侧,中压柜,35kV馈线,25,高压输出
WL005,ZRYJV-0.6/1kV-5×16,配电箱,QF1,照明柜,L1,20,照明配电
```

### 8.2 电缆选型标准

| 电流范围 | 电缆截面 | 电缆型号 |
|----------|----------|----------|
| I ≤ 25A | 4×4m㎡ | ZRYJV-0.6/1kV-4×4 |
| 25A < I ≤ 40A | 4×6m㎡ | ZRYJV-0.6/1kV-4×6 |
| 40A < I ≤ 63A | 4×10m㎡ | ZRYJV-0.6/1kV-4×10 |
| 63A < I ≤ 100A | 4×16m㎡ | ZRYJV-0.6/1kV-4×16 |
| 100A < I ≤ 140A | 4×25m㎡ | ZRYJV-0.6/1kV-4×25 |
| 140A < I ≤ 180A | 4×35m㎡ | ZRYJV-0.6/1kV-4×35 |
| 180A < I ≤ 220A | 3×70+1×35m㎡ | ZRYJV-0.6/1kV-3×70+1×35 |
| 220A < I ≤ 280A | 3×95+1×50m㎡ | ZRYJV-0.6/1kV-3×95+1×50 |
| 280A < I ≤ 350A | 3×120+1×70m㎡ | ZRYJV-0.6/1kV-3×120+1×70 |
| 350A < I ≤ 420A | 3×150+1×95m㎡ | ZRYJV-0.6/1kV-3×150+1×95 |
| 420A < I ≤ 500A | 3×185+1×95m㎡ | ZRYJV-0.6/1kV-3×185+1×95 |

### 8.3 电缆清册生成函数

```python
def generate_cable_schedule(cables, output_path):
    """
    生成电缆清册Excel文件
    cables: list of dict，含电缆信息
    """
    import csv
    
    headers = ["电缆编号", "电缆型号", "起点设备", "起点位置", 
               "终点设备", "终点位置", "长度(m)", "用途说明"]
    
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for cable in cables:
            writer.writerow([
                cable.get('id', ''),
                cable.get('type', ''),
                cable.get('from_device', ''),
                cable.get('from_point', ''),
                cable.get('to_device', ''),
                cable.get('to_point', ''),
                cable.get('length', ''),
                cable.get('purpose', '')
            ])
    
    print(f"✅ 电缆清册已生成: {output_path}")
```

---

## 9. 快速入门

### 5分钟上手流程

**Step 1: 安装依赖**
```bash
pip install ezdxf numpy
```

**Step 2: 调用Claude Code画图**
```
请画一个20尺集装箱储能系统电气图
规格：5MW/10MWh，12电池簇，4台1250kW PCS
输出DXF文件到 ~/.openclaw/workspace/储能系统电气图.dxf
```

**Step 3: 用AutoCAD打开DXF文件编辑**

### 常用画图命令

| 场景 | 命令示例 |
|------|----------|
| 配电箱电气图 | "画一个1进8出配电箱，每路125kW" |
| 储能系统图 | "画5MW/10MWh储能系统单线图" |
| 电气柜布局 | "画一个400×600mm电气柜布局图" |
| 接线图 | "画PCS到变压器的接线图" |

---

*本技能包由雪子和雪子助手共同维护*
*基于20尺集装箱储能系统5MW/10MWh实际项目图纸标准*
*最后更新: 2026-03-31*
