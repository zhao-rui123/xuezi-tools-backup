# 合并任务说明

## 问题
5个Agent生成的代码格式不一致：
- Alpha: 使用 TimeSlot[] 格式（正确）
- Bravo: 使用 TimePeriodPolicy 格式（需转换）
- Charlie: 使用 ProvinceConfig 格式（需转换）
- Delta: 使用 ProvincePolicy 格式（需转换）
- Echo: 使用 ProvincePricePolicy 格式（需转换）

## 解决方案
统一转换为现有代码使用的格式：
```typescript
const xxTimeSlots: Record<number, TimeSlot[]> = {
  1: [ { type: '高峰', start: 8, end: 12, price: 0 }, ... ],
  ...
};
```

## 任务
1. 读取现有 electricityPriceData.ts 文件结构
2. 整合所有 Agent 输出的省份数据
3. 统一转换为 TimeSlot[] 格式
4. 更新 getProvinceData 函数
5. 添加 2026年2月、3月电价数据
6. 构建并部署

## 状态
- [x] 所有 Agent 完成
- [ ] 格式统一转换
- [ ] 合并代码
- [ ] 构建部署
