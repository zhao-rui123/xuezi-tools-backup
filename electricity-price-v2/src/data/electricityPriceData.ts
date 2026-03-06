// 全国各省分时电价数据
export interface TimeSlot {
  start: number;
  end: number;
  price: number;
  type: 'peak' | 'high' | 'normal' | 'low' | 'valley';
}

export interface ProvinceData {
  name: string;
  code: string;
  hasTimeOfUse: boolean;
  timeSlots: TimeSlot[];
  months: number[];
  note?: string;
}

export const provinceList = [
  { name: '北京', code: 'BJ' },
  { name: '天津', code: 'TJ' },
  { name: '河北', code: 'HE' },
  { name: '山西', code: 'SX' },
  { name: '内蒙古', code: 'NM' },
  { name: '辽宁', code: 'LN' },
  { name: '吉林', code: 'JL' },
  { name: '黑龙江', code: 'HL' },
  { name: '上海', code: 'SH' },
  { name: '江苏', code: 'JS' },
  { name: '浙江', code: 'ZJ' },
  { name: '安徽', code: 'AH' },
  { name: '福建', code: 'FJ' },
  { name: '江西', code: 'JX' },
  { name: '山东', code: 'SD' },
  { name: '河南', code: 'HA' },
  { name: '湖北', code: 'HB' },
  { name: '湖南', code: 'HN' },
  { name: '广东', code: 'GD' },
  { name: '广西', code: 'GX' },
  { name: '海南', code: 'HI' },
  { name: '重庆', code: 'CQ' },
  { name: '四川', code: 'SC' },
  { name: '贵州', code: 'GZ' },
  { name: '云南', code: 'YN' },
  { name: '西藏', code: 'XZ' },
  { name: '陕西', code: 'SN' },
  { name: '甘肃', code: 'GS' },
  { name: '青海', code: 'QH' },
  { name: '宁夏', code: 'NX' },
  { name: '新疆', code: 'XJ' },
];

// 电价类型颜色配置
export const priceTypeColors = {
  peak: { color: '#ff4d4f', label: '尖峰', bgColor: 'rgba(255, 77, 79, 0.15)' },
  high: { color: '#fa8c16', label: '高峰', bgColor: 'rgba(250, 140, 22, 0.15)' },
  normal: { color: '#52c41a', label: '平段', bgColor: 'rgba(82, 196, 26, 0.15)' },
  low: { color: '#1890ff', label: '低谷', bgColor: 'rgba(24, 144, 255, 0.15)' },
  valley: { color: '#722ed1', label: '深谷', bgColor: 'rgba(114, 46, 209, 0.15)' },
};

// 示例电价数据（以江苏为例，其他省份类似）
export const electricityPriceData: Record<string, ProvinceData> = {
  JS: {
    name: '江苏',
    code: 'JS',
    hasTimeOfUse: true,
    months: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    note: '江苏执行分时电价政策，大工业用电和一般工商业用电均实行分时电价。夏季(7-8月)和冬季(12-1月)执行季节性尖峰电价。',
    timeSlots: [
      { start: 0, end: 8, price: 0.3583, type: 'valley' },
      { start: 8, end: 9, price: 0.6167, type: 'normal' },
      { start: 9, end: 12, price: 1.0167, type: 'high' },
      { start: 12, end: 17, price: 0.6167, type: 'normal' },
      { start: 17, end: 21, price: 1.0167, type: 'high' },
      { start: 21, end: 22, price: 0.6167, type: 'normal' },
      { start: 22, end: 24, price: 0.3583, type: 'valley' },
    ],
  },
  GD: {
    name: '广东',
    code: 'GD',
    hasTimeOfUse: true,
    months: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    note: '广东珠三角地区执行分时电价，峰谷价差较大，适合储能项目开发。',
    timeSlots: [
      { start: 0, end: 8, price: 0.3125, type: 'valley' },
      { start: 8, end: 9, price: 0.6875, type: 'normal' },
      { start: 9, end: 12, price: 1.1250, type: 'high' },
      { start: 12, end: 14, price: 0.6875, type: 'normal' },
      { start: 14, end: 17, price: 1.1250, type: 'high' },
      { start: 17, end: 19, price: 1.2500, type: 'peak' },
      { start: 19, end: 21, price: 1.1250, type: 'high' },
      { start: 21, end: 22, price: 0.6875, type: 'normal' },
      { start: 22, end: 24, price: 0.3125, type: 'valley' },
    ],
  },
  ZJ: {
    name: '浙江',
    code: 'ZJ',
    hasTimeOfUse: true,
    months: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    note: '浙江分时电价政策完善，大工业用户必须执行分时电价，一般工商业用户可选择执行。',
    timeSlots: [
      { start: 0, end: 8, price: 0.3283, type: 'valley' },
      { start: 8, end: 9, price: 0.6583, type: 'normal' },
      { start: 9, end: 11, price: 1.0583, type: 'high' },
      { start: 11, end: 13, price: 0.8583, type: 'normal' },
      { start: 13, end: 17, price: 1.0583, type: 'high' },
      { start: 17, end: 19, price: 1.2583, type: 'peak' },
      { start: 19, end: 21, price: 1.0583, type: 'high' },
      { start: 21, end: 22, price: 0.6583, type: 'normal' },
      { start: 22, end: 24, price: 0.3283, type: 'valley' },
    ],
  },
  SH: {
    name: '上海',
    code: 'SH',
    hasTimeOfUse: true,
    months: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    note: '上海分时电价分为峰、平、谷三个时段，夏季(7-9月)和冬季(12-2月)执行季节性电价。',
    timeSlots: [
      { start: 0, end: 6, price: 0.2850, type: 'valley' },
      { start: 6, end: 8, price: 0.5850, type: 'normal' },
      { start: 8, end: 11, price: 0.9850, type: 'high' },
      { start: 11, end: 13, price: 0.5850, type: 'normal' },
      { start: 13, end: 15, price: 0.9850, type: 'high' },
      { start: 15, end: 18, price: 0.5850, type: 'normal' },
      { start: 18, end: 21, price: 0.9850, type: 'high' },
      { start: 21, end: 22, price: 0.5850, type: 'normal' },
      { start: 22, end: 24, price: 0.2850, type: 'valley' },
    ],
  },
  SD: {
    name: '山东',
    code: 'SD',
    hasTimeOfUse: true,
    months: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    note: '山东执行分时电价，并试点深谷电价机制，中午时段(11-14点)执行深谷电价。',
    timeSlots: [
      { start: 0, end: 2, price: 0.2850, type: 'valley' },
      { start: 2, end: 6, price: 0.2450, type: 'low' },
      { start: 6, end: 8, price: 0.5850, type: 'normal' },
      { start: 8, end: 11, price: 0.9850, type: 'high' },
      { start: 11, end: 14, price: 0.1850, type: 'valley' },
      { start: 14, end: 15, price: 0.5850, type: 'normal' },
      { start: 15, end: 17, price: 0.9850, type: 'high' },
      { start: 17, end: 19, price: 1.1850, type: 'peak' },
      { start: 19, end: 21, price: 0.9850, type: 'high' },
      { start: 21, end: 22, price: 0.5850, type: 'normal' },
      { start: 22, end: 24, price: 0.2850, type: 'valley' },
    ],
  },
  // 更多省份数据...
  BJ: {
    name: '北京',
    code: 'BJ',
    hasTimeOfUse: true,
    months: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    note: '北京执行分时电价政策，大工业用电和一般工商业用电均实行分时电价。',
    timeSlots: [
      { start: 0, end: 7, price: 0.3150, type: 'valley' },
      { start: 7, end: 10, price: 0.6850, type: 'high' },
      { start: 10, end: 15, price: 0.4850, type: 'normal' },
      { start: 15, end: 18, price: 0.6850, type: 'high' },
      { start: 18, end: 21, price: 0.9850, type: 'peak' },
      { start: 21, end: 24, price: 0.3150, type: 'valley' },
    ],
  },
  // 无分时电价的省份示例
  XZ: {
    name: '西藏',
    code: 'XZ',
    hasTimeOfUse: false,
    months: [],
    note: '西藏暂不执行分时电价政策。',
    timeSlots: [],
  },
};

// 获取省份数据
export const getProvinceData = (code: string): ProvinceData | undefined => {
  return electricityPriceData[code];
};

// 获取某小时对应的电价
export const getPriceForHour = (provinceCode: string, hour: number): TimeSlot | undefined => {
  const province = getProvinceData(provinceCode);
  if (!province || !province.hasTimeOfUse) return undefined;
  
  return province.timeSlots.find(slot => hour >= slot.start && hour < slot.end);
};

// 生成24小时电价数据（用于图表）
export const generate24HourData = (provinceCode: string): { hour: string; price: number; type: string }[] => {
  const data: { hour: string; price: number; type: string }[] = [];
  
  for (let i = 0; i < 24; i++) {
    const slot = getPriceForHour(provinceCode, i);
    data.push({
      hour: `${i}:00`,
      price: slot ? slot.price : 0,
      type: slot ? slot.type : 'normal',
    });
  }
  
  return data;
};
