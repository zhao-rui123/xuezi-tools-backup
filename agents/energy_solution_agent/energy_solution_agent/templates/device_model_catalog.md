# 设备模型目录（第一版）

## 光伏组件模型

### `mono_pperc_550w`
- area_per_mwp: 7000 m²/MWp
- derating_factor: 0.92
- performance_ratio: 0.84
- temp_coefficient_pct_per_c: -0.34
- noct_c: 45

### `desert_utility_pv`
- area_per_mwp: 7600 m²/MWp
- derating_factor: 0.90
- performance_ratio: 0.82
- temp_coefficient_pct_per_c: -0.35
- noct_c: 46
- 适合：沙漠/高温地面电站

---

## 风机模型

### `onshore_3mw_ieciii`
- hub_height_m: 100
- reference_height_m: 10
- shear_exponent: 0.14
- cut_in_mps: 3.0
- rated_mps: 12.0
- cut_out_mps: 25.0

### `high_wind_5mw`
- hub_height_m: 120
- reference_height_m: 10
- shear_exponent: 0.12
- cut_in_mps: 3.0
- rated_mps: 11.5
- cut_out_mps: 25.0
- 适合：高风速海边/高原场景

---

## 使用建议
- 海外荒漠矿区：优先 `desert_utility_pv`
- 一般工商业屋顶：优先 `mono_pperc_550w`
- 默认陆上风电：优先 `onshore_3mw_ieciii`
- 若项目地年均风速较高：可尝试 `high_wind_5mw`
