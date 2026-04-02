#!/usr/bin/env python3
"""
配电箱电气图生成脚本
1进8出（三相AC380V），每路125kW
"""

import math
import ezdxf

# 创建DXF文档
doc = ezdxf.new('R2010')
msp = doc.modelspace()

# ============================================================
# 图层定义
# ============================================================
doc.layers.add("BORDER", color=7)       # 白色 - 边框
doc.layers.add("COMPONENT", color=1)    # 红色 - 元器件
doc.layers.add("BUS", color=3)          # 绿色 - 母线
doc.layers.add("WIRE", color=2)         # 黄色 - 导线
doc.layers.add("TEXT", color=5)         # 蓝色 - 文字
doc.layers.add("TABLE", color=6)        # 青色 - 表格
doc.layers.add("DIM", color=4)          # 紫色 - 标注

# ============================================================
# 辅助函数
# ============================================================

def add_rect(msp, x, y, w, h, layer="COMPONENT", color=None):
    """画矩形"""
    attribs = {'layer': layer}
    if color:
        attribs['color'] = color
    msp.add_lwpolyline(
        [(x, y), (x+w, y), (x+w, y+h), (x, y+h), (x, y)],
        close=True, dxfattribs=attribs
    )

def add_line(msp, x1, y1, x2, y2, layer="WIRE", color=None):
    """画直线"""
    attribs = {'layer': layer}
    if color:
        attribs['color'] = color
    msp.add_line((x1, y1), (x2, y2), dxfattribs=attribs)

def add_text(msp, text, x, y, height=8, layer="TEXT", align="LEFT", color=None):
    """添加文字"""
    attribs = {'layer': layer, 'height': height}
    if color:
        attribs['color'] = color
    msp.add_text(text, dxfattribs=attribs)
    # 找到刚添加的文字设置位置
    for e in msp:
        if e.dxftype() == 'TEXT' and e.dxf.text == text:
            e.dxf.insert = (x, y)
            if align == "CENTER":
                e.dxf.halign = 1  # CENTER
            elif align == "RIGHT":
                e.dxf.halign = 2  # RIGHT
            break

def add_circle(msp, cx, cy, r, layer="COMPONENT", color=None):
    """画圆"""
    attribs = {'layer': layer}
    if color:
        attribs['color'] = color
    msp.add_circle((cx, cy), r, dxfattribs=attribs)

def add_arc(msp, cx, cy, r, start_angle, end_angle, layer="COMPONENT", color=None):
    """画圆弧"""
    attribs = {'layer': layer}
    if color:
        attribs['color'] = color
    msp.add_arc((cx, cy), r, start_angle, end_angle, dxfattribs=attribs)

def add_polygon(msp, cx, cy, r, sides, rot_deg=0, layer="COMPONENT", color=None):
    """画正多边形"""
    attribs = {'layer': layer}
    if color:
        attribs['color'] = color
    pts = []
    for i in range(sides):
        ang = math.radians(rot_deg + i * 360 / sides)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    msp.add_lwpolyline(pts, close=True, dxfattribs=attribs)

def add_bus_bar(msp, x, y, length, layer="BUS", color=3):
    """画母线"""
    attribs = {'layer': layer, 'color': color, 'lineweight': 50}
    msp.add_lwpolyline(
        [(x, y), (x+length, y)], dxfattribs=attribs
    )

def draw_main_breaker(msp, cx, cy, w=30, h=50, layer="COMPONENT"):
    """画主断路器符号"""
    # 主体矩形
    add_rect(msp, cx-w/2, cy-h/2, w, h, layer=layer)
    # 内部开关符号（横线表示合闸）
    add_line(msp, cx-w/2+4, cy, cx+w/2-4, cy, layer=layer)
    # 上下连接线
    add_line(msp, cx, cy-h/2, cx, cy-h/2-5, layer=layer)
    add_line(msp, cx, cy+h/2, cx, cy+h/2+5, layer=layer)

def draw_outgoing_breaker(msp, cx, cy, w=26, h=40, layer="COMPONENT"):
    """画出线断路器符号"""
    add_rect(msp, cx-w/2, cy-h/2, w, h, layer=layer)
    add_line(msp, cx-w/2+3, cy, cx+w/2-3, cy, layer=layer)
    add_line(msp, cx, cy-h/2, cx, cy-h/2-4, layer=layer)
    add_line(msp, cx, cy+h/2, cx, cy+h/2+4, layer=layer)

def draw_current_transformer(msp, cx, cy, r=10, layer="COMPONENT"):
    """画电流互感器符号（圆圈+点）"""
    add_circle(msp, cx, cy, r, layer=layer)
    add_circle(msp, cx, cy, 2, layer=layer, color=2)

def draw_current_meter(msp, cx, cy, w=18, h=28, layer="COMPONENT"):
    """画电流表符号"""
    add_rect(msp, cx-w/2, cy-h/2, w, h, layer=layer)
    # 表盘圆
    add_circle(msp, cx, cy+2, 6, layer=layer)
    # 指针
    add_line(msp, cx, cy+2, cx+4, cy+5, layer=layer)
    # A标识
    attribs = {'layer': layer, 'height': 5}
    msp.add_text("A", dxfattribs=attribs)
    for e in msp:
        if e.dxftype() == 'TEXT' and e.dxf.text == "A":
            e.dxf.insert = (cx-2, cy-6)

# ============================================================
# 绘制参数
# ============================================================
# 页面尺寸
PAGE_W = 1200
PAGE_H = 800

# 母线位置
BUS_Y_L1 = 620
BUS_Y_L2 = 590
BUS_Y_L3 = 560
BUS_Y_N  = 530
BUS_X0   = 180
BUS_X1   = 1100

# 进线区
IN_X = 60
IN_Y_TOP = 680

# 出线区起始x和间距
OUT_X_START = 280
OUT_SPACING = 100

# ============================================================
# 1. 绘制外边框和标题栏
# ============================================================
# 外边框
add_rect(msp, 10, 10, PAGE_W-20, PAGE_H-20, layer="BORDER", color=7)

# 标题栏
add_rect(msp, 10, 10, PAGE_W-20, 50, layer="BORDER", color=7)
add_text(msp, "配电箱电气图（1进8出 / 三相AC380V / 每路125kW）", 20, 38, height=14, layer="TEXT", color=7)
add_text(msp, "比例: 1:20", PAGE_W-200, 38, height=8, layer="TEXT", color=7)
add_text(msp, "单位: mm", PAGE_W-100, 38, height=8, layer="TEXT", color=7)

# ============================================================
# 2. 绘制母线 (L1/L2/L3/N)
# ============================================================
# L1母线
add_bus_bar(msp, BUS_X0, BUS_Y_L1, BUS_X1-BUS_X0)
add_text(msp, "L1", BUS_X0+5, BUS_Y_L1+5, height=7, layer="BUS", color=3)

# L2母线
add_bus_bar(msp, BUS_X0, BUS_Y_L2, BUS_X1-BUS_X0)
add_text(msp, "L2", BUS_X0+5, BUS_Y_L2+5, height=7, layer="BUS", color=3)

# L3母线
add_bus_bar(msp, BUS_X0, BUS_Y_L3, BUS_X1-BUS_X0)
add_text(msp, "L3", BUS_X0+5, BUS_Y_L3+5, height=7, layer="BUS", color=3)

# N母线
add_bus_bar(msp, BUS_X0, BUS_Y_N, BUS_X1-BUS_X0)
add_text(msp, "N", BUS_X0+5, BUS_Y_N+5, height=7, layer="BUS", color=3)

# ============================================================
# 3. 绘制主进线回路（左上区域）
# ============================================================
# 进线断路器位置
MAIN_BREAKER_X = 120
MAIN_BREAKER_Y = (BUS_Y_L1 + BUS_Y_N) / 2

# 画主断路器（3极，垂直排列）
# L1
add_rect(msp, MAIN_BREAKER_X-15, BUS_Y_L1-4, 30, 8, layer="COMPONENT")
add_line(msp, MAIN_BREAKER_X, BUS_Y_L1-4, MAIN_BREAKER_X, BUS_Y_L1+4, layer="WIRE")
# L2
add_rect(msp, MAIN_BREAKER_X-15, BUS_Y_L2-4, 30, 8, layer="COMPONENT")
add_line(msp, MAIN_BREAKER_X, BUS_Y_L2-4, MAIN_BREAKER_X, BUS_Y_L2+4, layer="WIRE")
# L3
add_rect(msp, MAIN_BREAKER_X-15, BUS_Y_L3-4, 30, 8, layer="COMPONENT")
add_line(msp, MAIN_BREAKER_X, BUS_Y_L3-4, MAIN_BREAKER_X, BUS_Y_L3+4, layer="WIRE")
# N
add_line(msp, MAIN_BREAKER_X, BUS_Y_N-4, MAIN_BREAKER_X, BUS_Y_N+4, layer="WIRE")

# 主断路器标注框
add_rect(msp, MAIN_BREAKER_X-15, BUS_Y_L3-25, 30, 50+25+8, layer="COMPONENT", color=1)
add_text(msp, "QFa", MAIN_BREAKER_X-12, BUS_Y_L3-18, height=6, layer="TEXT")
add_text(msp, "400A", MAIN_BREAKER_X-12, BUS_Y_L3-28, height=5, layer="TEXT")
add_text(msp, "250A", MAIN_BREAKER_X-12, BUS_Y_L3-36, height=5, layer="TEXT")
add_text(msp, "整定", MAIN_BREAKER_X-12, BUS_Y_L3-44, height=5, layer="TEXT")

# 进线到母线连接线
add_line(msp, MAIN_BREAKER_X+15, BUS_Y_L1, BUS_X0, BUS_Y_L1)
add_line(msp, MAIN_BREAKER_X+15, BUS_Y_L2, BUS_X0, BUS_Y_L2)
add_line(msp, MAIN_BREAKER_X+15, BUS_Y_L3, BUS_X0, BUS_Y_L3)
add_line(msp, MAIN_BREAKER_X+15, BUS_Y_N,  BUS_X0, BUS_Y_N)

# 进线电缆标注
add_text(msp, "进线电缆", 30, BUS_Y_L1+10, height=6, layer="TEXT", color=5)
add_text(msp, "3×185+1×95", 20, BUS_Y_L1, height=5, layer="TEXT", color=5)
add_text(msp, "mm²", 20, BUS_Y_L1-7, height=5, layer="TEXT", color=5)

# 主电流表
MAIN_METER_X = 60
MAIN_METER_Y = (BUS_Y_L1 + BUS_Y_L3) / 2 + 10
add_rect(msp, MAIN_METER_X-12, MAIN_METER_Y-18, 24, 36, layer="COMPONENT")
add_circle(msp, MAIN_METER_X, MAIN_METER_Y-2, 8, layer="COMPONENT")
add_line(msp, MAIN_METER_X, MAIN_METER_Y-2, MAIN_METER_X+5, MAIN_METER_Y+3, layer="COMPONENT")
add_text(msp, "PA", MAIN_METER_X-10, MAIN_METER_Y-22, height=6, layer="TEXT")
add_text(msp, "主电流表", MAIN_METER_X-18, MAIN_METER_Y-32, height=5, layer="TEXT", color=5)

# 母线与主断路器之间的连接
add_line(msp, MAIN_BREAKER_X+15, BUS_Y_L1, MAIN_BREAKER_X+15, MAIN_METER_Y, layer="WIRE")
add_line(msp, MAIN_BREAKER_X+15, MAIN_METER_Y, MAIN_METER_X+12, MAIN_METER_Y, layer="WIRE")

# ============================================================
# 4. 绘制8个出线回路
# ============================================================
NUM_CIRCUITS = 8

for i in range(NUM_CIRCUITS):
    cx = OUT_X_START + i * OUT_SPACING   # 回路中心x

    # 各相母线位置
    L1 = BUS_Y_L1
    L2 = BUS_Y_L2
    L3 = BUS_Y_L3
    N  = BUS_Y_N

    # 出线断路器框（垂直三极）
    br_w = 26
    br_h = 8

    # L1断路器
    add_rect(msp, cx-br_w/2, L1-4, br_w, br_h, layer="COMPONENT")
    # L2断路器
    add_rect(msp, cx-br_w/2, L2-4, br_w, br_h, layer="COMPONENT")
    # L3断路器
    add_rect(msp, cx-br_w/2, L3-4, br_w, br_h, layer="COMPONENT")
    # N线（无断路器）
    add_line(msp, cx-br_w/2, N, cx+br_w/2, N, layer="WIRE")

    # 断路器标注框（把三极包在一起）
    add_rect(msp, cx-br_w/2-2, L3-22, br_w+4, (L1-L3)+22+8, layer="COMPONENT", color=1)
    add_text(msp, f"QF{i+1}", cx-br_w/2+1, L3-15, height=5, layer="TEXT")
    add_text(msp, "250A", cx-br_w/2+1, L3-23, height=5, layer="TEXT")

    # 母线到断路器连接（母线出头线）
    add_line(msp, cx, L1, cx, L1+4, layer="WIRE")
    add_line(msp, cx, L2, cx, L2+4, layer="WIRE")
    add_line(msp, cx, L3, cx, L3+4, layer="WIRE")
    add_line(msp, cx, N,  cx, N+4,  layer="WIRE")

    # 电流互感器CT（画在L1和L3位置）
    ct_r = 7
    add_circle(msp, cx, L1+4+ct_r+4, ct_r, layer="COMPONENT")
    add_circle(msp, cx, L1+4+ct_r+4, 2, layer="COMPONENT", color=2)
    add_text(msp, f"CT{i+1}", cx-12, L1+4+ct_r+4, height=5, layer="TEXT")

    # 电流表
    meter_y = L3 - 60
    meter_w = 18
    meter_h = 28
    add_rect(msp, cx-meter_w/2, meter_y-meter_h/2, meter_w, meter_h, layer="COMPONENT")
    add_circle(msp, cx, meter_y-meter_h/2+14, 5, layer="COMPONENT")
    add_line(msp, cx, meter_y-meter_h/2+14, cx+3, meter_y-meter_h/2+17, layer="COMPONENT")
    add_text(msp, f"PA{i+1}", cx-meter_w/2-1, meter_y-meter_h/2-6, height=5, layer="TEXT")

    # 回路负载标注
    load_y = meter_y - meter_h/2 - 20
    add_text(msp, f"回路{i+1}", cx, load_y, height=6, layer="TEXT", align="CENTER")
    add_text(msp, "125kW", cx, load_y-8, height=5, layer="TEXT", align="CENTER", color=5)
    add_text(msp, "~224A", cx, load_y-15, height=5, layer="TEXT", align="CENTER", color=5)

    # 出线电缆标注（下方）
    cable_y = meter_y - meter_h/2 - 35
    add_text(msp, "3×185+1×95", cx, cable_y, height=4, layer="TEXT", align="CENTER", color=5)
    add_text(msp, "mm²", cx, cable_y-5, height=4, layer="TEXT", align="CENTER", color=5)

# ============================================================
# 5. 分隔线和分区标注
# ============================================================
# 左侧进线区
add_line(msp, 200, BUS_Y_N-30, 200, PAGE_H-60, layer="BORDER", color=7)
add_text(msp, "进线", 150, BUS_Y_N-40, height=7, layer="TEXT", align="CENTER")

# 右侧出线区
add_line(msp, 220, BUS_Y_N-30, 220, PAGE_H-60, layer="BORDER", color=7)
add_text(msp, "出线区", 650, BUS_Y_N-40, height=7, layer="TEXT", align="CENTER")

# ============================================================
# 6. 规格标注表格（右下角）
# ============================================================
tbl_x = 850
tbl_y = 380
tbl_w = 320
tbl_h = 140
row_h = 14

# 表格标题
add_rect(msp, tbl_x, tbl_y, tbl_w, row_h, layer="TABLE", color=6)
add_text(msp, "规格标注表", tbl_x+5, tbl_y+3, height=7, layer="TABLE", color=6)

rows = [
    ["项目", "规格/型号", "数量", "备注"],
    ["主断路器 QFa", "400A/250A 整定", "1", "框架400A"],
    ["出线断路器 QF1~8", "250A", "8", "三极"],
    ["电流互感器 CT1~8", "250A/5A", "8", "精度0.5级"],
    ["电流表 PA1~8", "0~300A", "8", "配电型"],
    ["主电流表 PA", "0~600A", "1", "配电型"],
    ["母线", "TMY-40×4", "4", "L1/L2/L3/N"],
    ["进线电缆", "3×185+1×95mm²", "1根", "YJV-0.6/1kV"],
    ["出线电缆", "3×185+1×95mm²", "8根", "YJV-0.6/1kV"],
]

for ri, row in enumerate(rows):
    ry = tbl_y - (ri+1)*row_h
    bg_color = 8 if ri == 0 else None
    # 单元格分隔线
    col_widths = [80, 120, 50, 70]
    x_pos = tbl_x
    for ci, (cell, cw) in enumerate(zip(row, col_widths)):
        add_rect(msp, x_pos, ry, cw, row_h, layer="TABLE", color=6)
        tx = x_pos + 3 if ci < len(col_widths)-1 else x_pos + 3
        h = 6 if ri == 0 else 5
        clr = 6 if ri == 0 else 7
        add_text(msp, cell, tx, ry+3, height=h, layer="TABLE", color=clr)
        x_pos += cw

# ============================================================
# 7. 材料表（右下角下方）
# ============================================================
mat_x = 850
mat_y = tbl_y - len(rows)*row_h - 20
mat_w = 320
mat_h = 80

add_rect(msp, mat_x, mat_y, mat_w, row_h, layer="TABLE", color=6)
add_text(msp, "材料表", mat_x+5, mat_y+3, height=7, layer="TABLE", color=6)

mat_rows = [
    ["序号", "名称", "型号规格", "单位", "数量"],
    ["1", "低压配电箱", "XL-21 800×1200×300", "台", "1"],
    ["2", "铜排", "TMY-40×4", "米", "8"],
    ["3", "断路器", "CM1-250L/3300 250A", "个", "8"],
    ["4", "电流互感器", "BH-0.66 250A/5A", "个", "8"],
]

for ri, row in enumerate(mat_rows):
    ry = mat_y - (ri+1)*row_h
    col_widths_m = [35, 80, 110, 45, 50]
    x_pos = mat_x
    for ci, (cell, cw) in enumerate(zip(row, col_widths_m)):
        add_rect(msp, x_pos, ry, cw, row_h, layer="TABLE", color=6)
        tx = x_pos + 3
        h = 6 if ri == 0 else 5
        clr = 6 if ri == 0 else 7
        add_text(msp, cell, tx, ry+3, height=h, layer="TABLE", color=clr)
        x_pos += cw

# ============================================================
# 8. 图例（左侧下方）
# ============================================================
leg_x = 20
leg_y = 400
leg_w = 160
leg_h = 120

add_rect(msp, leg_x, leg_y, leg_w, leg_h, layer="BORDER", color=7)
add_text(msp, "图例", leg_x+5, leg_y+leg_h-10, height=7, layer="TEXT", color=7)

# 断路器图例
add_rect(msp, leg_x+10, leg_y+leg_h-30, 20, 8, layer="COMPONENT")
add_text(msp, "断路器（空气开关）", leg_x+35, leg_y+leg_h-26, height=5, layer="TEXT")

# 电流互感器图例
add_circle(msp, leg_x+20, leg_y+leg_h-50, 8, layer="COMPONENT")
add_circle(msp, leg_x+20, leg_y+leg_h-50, 2, layer="COMPONENT", color=2)
add_text(msp, "电流互感器 CT", leg_x+35, leg_y+leg_h-47, height=5, layer="TEXT")

# 电流表图例
add_rect(msp, leg_x+10, leg_y+leg_h-72, 18, 16, layer="COMPONENT")
add_circle(msp, leg_x+19, leg_y+leg_h-62, 5, layer="COMPONENT")
add_text(msp, "电流表", leg_x+35, leg_y+leg_h-65, height=5, layer="TEXT")

# 母线图例
add_line(msp, leg_x+10, leg_y+leg_h-88, leg_x+35, leg_y+leg_h-88, layer="BUS", color=3)
add_text(msp, "母线/导线", leg_x+35, leg_y+leg_h-85, height=5, layer="TEXT")

# 电缆图例
add_line(msp, leg_x+10, leg_y+leg_h-102, leg_x+35, leg_y+leg_h-102, layer="WIRE", color=2)
add_text(msp, "电力电缆", leg_x+35, leg_y+leg_h-99, height=5, layer="TEXT")

# ============================================================
# 9. 技术说明（底部）
# ============================================================
note_y = 30
add_text(msp, "技术说明：", 20, note_y+20, height=7, layer="TEXT", color=7)
notes = [
    "1. 计算电流 I = P/(√3×U×cosφ) = 125000/(1.732×380×0.85) ≈ 224A，考虑1.2倍余量后约270A",
    "2. 电缆选型：3×185+1×95mm² YJV-0.6/1kV电力电缆（直埋或桥架敷设，根据实际选型）",
    "3. 主断路器QFa：框架电流400A，整定电流250A（三极，型号：CM1-400L/3300）",
    "4. 出线断路器QF1~8：额定电流250A（三极，型号：CM1-250L/3300）",
    "5. 电流互感器CT1~8：变比250A/5A，精度等级0.5级，型号：BH-0.66",
    "6. 本图按每路125kW负载设计，总装机容量1000kW，请根据实际复核设计",
]
for ni, note in enumerate(notes):
    add_text(msp, note, 20, note_y+10-ni*8, height=5, layer="TEXT", color=7)

# ============================================================
# 保存文件
# ============================================================
output_path = "/Users/zhaoruicn/.openclaw/workspace/配电箱电气图.dxf"
doc.saveas(output_path)
print(f"完成！文件已保存至: {output_path}")
