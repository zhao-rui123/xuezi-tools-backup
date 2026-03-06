#!/usr/bin/env node
/**
 * 电价数据提取转换脚本
 * 从主站编译后的JS文件中提取31省电价数据，转换为TypeScript格式
 */

const fs = require('fs');
const path = require('path');

// 读取源文件
const sourceFile = process.argv[2] || '/tmp/main-site/assets/index-DryG4KlC.js?v=3';
const outputFile = process.argv[3] || './src/data/electricityPriceData.ts';

console.log(`读取源文件: ${sourceFile}`);
const content = fs.readFileSync(sourceFile, 'utf-8');

// 提取 y3 数组（省份数据）
const y3Match = content.match(/y3=\[.*?\],sL=/s);
if (!y3Match) {
  console.error('未找到 y3 数据');
  process.exit(1);
}

// 清理数据
let dataStr = y3Match[0]
  .replace('y3=', '')
  .replace(',sL=', '')
  .replace(/!0/g, 'true')
  .replace(/!1/g, 'false')
  .replace(/void 0/g, 'undefined');

// 尝试解析
let provinceData;
try {
  // 使用 Function 构造器安全解析
  provinceData = new Function('return ' + dataStr)();
} catch (e) {
  console.error('解析失败:', e.message);
  // 尝试手动提取关键信息
  provinceData = extractProvincesManually(content);
}

function extractProvincesManually(content) {
  const provinces = [];
  
  // 匹配省份定义模式
  const provincePattern = /\{name:"([^"]+)",hasTimeOfUsePricing:([^,]+)(?:,note:"([^"]*)")?,months:/g;
  let match;
  
  while ((match = provincePattern.exec(content)) !== null) {
    const name = match[1];
    const hasTimeOfUsePricing = match[2] === 'true';
    const note = match[3] || undefined;
    
    provinces.push({
      name,
      hasTimeOfUsePricing,
      note,
      months: {} // 月份数据需要另外提取
    });
  }
  
  return provinces;
}

console.log(`提取到 ${provinceData.length} 个省份`);

// 生成 TypeScript 文件
const tsContent = generateTypeScript(provinceData);
fs.writeFileSync(outputFile, tsContent);
console.log(`已写入: ${outputFile}`);

function generateTypeScript(provinces) {
  const header = `/** 全国31省分时电价数据 */

export type PriceType = '尖峰' | '高峰' | '平段' | '低谷' | '深谷';

export interface TimeSlot {
  type: PriceType;
  startTime: string;
  endTime: string;
  description: string;
}

export interface MonthData {
  monthName: string;
  timeSlots: TimeSlot[];
}

export interface ProvinceData {
  name: string;
  hasTimeOfUsePricing: boolean;
  note?: string;
  months: Record<number, MonthData>;
}

// 电价相对比例（用于图表展示）
export const PRICE_RATIOS: Record<PriceType, number> = {
  '尖峰': 1.8,
  '高峰': 1.5,
  '平段': 1.0,
  '低谷': 0.5,
  '深谷': 0.3
};

// 电价类型颜色
export const PRICE_COLORS: Record<PriceType, string> = {
  '尖峰': '#ef4444',  // 红色
  '高峰': '#f97316',  // 橙色
  '平段': '#22c55e',  // 绿色
  '低谷': '#3b82f6',  // 蓝色
  '深谷': '#6366f1'   // 紫色
};

// 31省电价数据
export const provinceData: ProvinceData[] = [
`;

  const footer = `];

// 辅助函数：获取省份数据
export function getProvinceByName(name: string): ProvinceData | undefined {
  return provinceData.find(p => p.name === name);
}

// 辅助函数：获取省份列表（用于搜索）
export function searchProvinces(term: string): ProvinceData[] {
  return provinceData.filter(p => p.name.toLowerCase().includes(term.toLowerCase()));
}

// 辅助函数：获取有分时电价的省份
export function getProvincesWithTimeOfUsePricing(): ProvinceData[] {
  return provinceData.filter(p => p.hasTimeOfUsePricing);
}
`;

  // 生成省份数据
  const provincesStr = provinces.map(p => {
    if (!p.hasTimeOfUsePricing) {
      return `  {
    name: '${p.name}',
    hasTimeOfUsePricing: false,
    note: ${p.note ? `'${p.note}'` : 'undefined'},
    months: {}
  }`;
    }
    
    // 有分时电价的省份
    const monthsStr = generateMonthsStr(p.months);
    return `  {
    name: '${p.name}',
    hasTimeOfUsePricing: true,
    note: ${p.note ? `'${p.note}'` : 'undefined'},
    months: {
${monthsStr}
    }
  }`;
  }).join(',\n');

  return header + provincesStr + footer;
}

function generateMonthsStr(months) {
  if (!months || Object.keys(months).length === 0) {
    return '';
  }
  
  const monthEntries = Object.entries(months);
  return monthEntries.map(([month, data]) => {
    const slots = data.timeSlots || [];
    const slotsStr = slots.map((slot, idx) => {
      return `          { type: '${slot.type}', startTime: '${slot.startTime}', endTime: '${slot.endTime}', description: '${slot.description}' }`;
    }).join(',\n');
    
    return `      ${month}: {
        monthName: '${month}月',
        timeSlots: [
${slotsStr}
        ]
      }`;
  }).join(',\n');
}
