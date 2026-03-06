# 全国31省分时电价查询工具 v2

基于 React + TypeScript + Vite + Recharts 构建的电价查询工具。

## 功能特性

- 📊 31省分时电价数据查询
- 📈 可视化图表展示（Recharts）
- 🔍 省份搜索功能
- 📅 月份选择
- 📱 响应式设计

## 技术栈

- React 18
- TypeScript 5
- Vite 5
- Recharts

## 开发

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建
npm run build

# 预览
npm run preview
```

## 数据结构

电价数据存储在 `src/data/electricityPriceData.ts`，包含：

- 省份列表
- 分时电价时段
- 电价类型（尖峰/高峰/平段/低谷/深谷）
- 颜色配置

## 维护说明

### 添加新省份数据

在 `src/data/electricityPriceData.ts` 中的 `provinceData` 数组添加：

```typescript
{
  name: '省份名称',
  hasTimeOfUsePricing: true,
  note: '备注说明（可选）',
  months: {
    1: {
      monthName: '1月',
      timeSlots: [
        { type: '高峰', startTime: '08:00', endTime: '12:00', description: '高峰时段' },
        // ...
      ]
    },
    // ...
  }
}
```

### 电价类型

- 尖峰：1.8x
- 高峰：1.5x
- 平段：1.0x
- 低谷：0.5x
- 深谷：0.3x

## 部署

项目配置了 GitHub Actions 自动部署到 GitHub Pages。

## 数据时间

2026年2月
