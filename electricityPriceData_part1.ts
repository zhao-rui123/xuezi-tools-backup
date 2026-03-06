export interface TimeSlot {
  type: '尖峰' | '高峰' | '平段' | '低谷' | '深谷';
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

// 河南省时段配置
const hy = {
  winter: [
    { type: "高峰" as const, startTime: "16:00", endTime: "17:00", description: "高峰时段" },
    { type: "尖峰" as const, startTime: "17:00", endTime: "19:00", description: "尖峰时段" },
    { type: "高峰" as const, startTime: "19:00", endTime: "24:00", description: "高峰时段" },
    { type: "低谷" as const, startTime: "00:00", endTime: "07:00", description: "低谷时段" },
    { type: "平段" as const, startTime: "07:00", endTime: "16:00", description: "平段" }
  ],
  springAutumn: [
    { type: "高峰" as const, startTime: "16:00", endTime: "24:00", description: "高峰时段" },
    { type: "低谷" as const, startTime: "00:00", endTime: "06:00", description: "低谷凌晨" },
    { type: "低谷" as const, startTime: "11:00", endTime: "14:00", description: "低谷中午" },
    { type: "平段" as const, startTime: "06:00", endTime: "11:00", description: "平段上午" },
    { type: "平段" as const, startTime: "14:00", endTime: "16:00", description: "平段下午" }
  ],
  summer: [
    { type: "高峰" as const, startTime: "16:00", endTime: "20:00", description: "高峰时段" },
    { type: "尖峰" as const, startTime: "20:00", endTime: "23:00", description: "尖峰时段" },
    { type: "高峰" as const, startTime: "23:00", endTime: "24:00", description: "高峰时段" },
    { type: "低谷" as const, startTime: "00:00", endTime: "07:00", description: "低谷时段" },
    { type: "平段" as const, startTime: "07:00", endTime: "16:00", description: "平段" }
  ]
};

// 云南省时段配置
const cL = [
  { type: "高峰" as const, startTime: "07:00", endTime: "09:00", description: "高峰上午" },
  { type: "高峰" as const, startTime: "18:00", endTime: "24:00", description: "高峰晚间" },
  { type: "平段" as const, startTime: "00:00", endTime: "02:00", description: "平段凌晨" },
  { type: "平段" as const, startTime: "06:00", endTime: "07:00", description: "平段早晨" },
  { type: "平段" as const, startTime: "09:00", endTime: "12:00", description: "平段上午" },
  { type: "平段" as const, startTime: "16:00", endTime: "18:00", description: "平段下午" },
  { type: "低谷" as const, startTime: "02:00", endTime: "06:00", description: "低谷凌晨" },
  { type: "低谷" as const, startTime: "12:00", endTime: "16:00", description: "低谷中午" }
];

// 江苏省时段配置
const e_ = {
  summerWinter: [
    { type: "高峰" as const, startTime: "14:00", endTime: "22:00", description: "高峰时段" },
    { type: "平段" as const, startTime: "06:00", endTime: "11:00", description: "平段上午" },
    { type: "平段" as const, startTime: "13:00", endTime: "14:00", description: "平段下午" },
    { type: "平段" as const, startTime: "22:00", endTime: "24:00", description: "平段深夜" },
    { type: "低谷" as const, startTime: "00:00", endTime: "06:00", description: "低谷凌晨" },
    { type: "低谷" as const, startTime: "11:00", endTime: "13:00", description: "低谷中午" }
  ],
  springAutumn: [
    { type: "高峰" as const, startTime: "15:00", endTime: "22:00", description: "高峰时段" },
    { type: "平段" as const, startTime: "06:00", endTime: "10:00", description: "平段上午" },
    { type: "平段" as const, startTime: "14:00", endTime: "15:00", description: "平段下午" },
    { type: "平段" as const, startTime: "22:00", endTime: "02:00", description: "平段深夜" },
    { type: "低谷" as const, startTime: "02:00", endTime: "06:00", description: "低谷凌晨" },
    { type: "低谷" as const, startTime: "10:00", endTime: "14:00", description: "低谷中午" }
  ]
};

// 安徽省时段配置
const t_ = {
  special: [
    { type: "高峰" as const, startTime: "16:00", endTime: "24:00", description: "高峰时段" },
    { type: "平段" as const, startTime: "09:00", endTime: "11:00", description: "平段上午" },
    { type: "平段" as const, startTime: "13:00", endTime: "16:00", description: "平段下午" },
    { type: "低谷" as const, startTime: "02:00", endTime: "09:00", description: "低谷凌晨" },
    { type: "低谷" as const, startTime: "11:00", endTime: "13:00", description: "低谷中午" }
  ],
  other: [
    { type: "高峰" as const, startTime: "06:00", endTime: "08:00", description: "高峰早晨" },
    { type: "高峰" as const, startTime: "16:00", endTime: "22:00", description: "高峰晚间" },
    { type: "平段" as const, startTime: "08:00", endTime: "11:00", description: "平段上午" },
    { type: "平段" as const, startTime: "14:00", endTime: "16:00", description: "平段下午" },
    { type: "平段" as const, startTime: "22:00", endTime: "23:00", description: "平段深夜" },
    { type: "低谷" as const, startTime: "11:00", endTime: "14:00", description: "低谷中午" },
    { type: "低谷" as const, startTime: "23:00", endTime: "06:00", description: "低谷凌晨" }
  ]
};

// 广东省（珠三角五市）时段配置
const n_ = {
  summer: [
    { type: "尖峰" as const, startTime: "11:00", endTime: "12:00", description: "尖峰时段1" },
    { type: "尖峰" as const, startTime: "15:00", endTime: "17:00", description: "尖峰时段2" },
    { type: "高峰" as const, startTime: "10:00", endTime: "11:00", description: "高峰上午" },
    { type: "高峰" as const, startTime: "12:00", endTime: "14:00", description: "高峰中午" },
    { type: "高峰" as const, startTime: "17:00", endTime: "19:00", description: "高峰下午" },
    { type: "平段" as const, startTime: "08:00", endTime: "10:00", description: "平段上午" },
    { type: "平段" as const, startTime: "14:00", endTime: "15:00", description: "平段下午1" },
    { type: "平段" as const, startTime: "19:00", endTime: "24:00", description: "平段晚间" },
    { type: "低谷" as const, startTime: "00:00", endTime: "08:00", description: "低谷时段" }
  ],
  other: [
    { type: "高峰" as const, startTime: "10:00", endTime: "12:00", description: "高峰上午" },
    { type: "高峰" as const, startTime: "14:00", endTime: "19:00", description: "高峰下午" },
    { type: "平段" as const, startTime: "08:00", endTime: "10:00", description: "平段上午" },
    { type: "平段" as const, startTime: "12:00", endTime: "14:00", description: "平段中午" },
    { type: "平段" as const, startTime: "19:00", endTime: "24:00", description: "平段晚间" },
    { type: "低谷" as const, startTime: "00:00", endTime: "08:00", description: "低谷时段" }
  ]
};

// 山东省时段配置
const Sf = {
  winter: [
    { type: "尖峰" as const, startTime: "16:00", endTime: "19:00", description: "尖峰时段" },
    { type: "高峰" as const, startTime: "19:00", endTime: "21:00", description: "高峰时段" },
    { type: "平段" as const, startTime: "07:00", endTime: "11:00", description: "平段上午" },
    { type: "平段" as const, startTime: "14:00", endTime: "16:00", description: "平段下午" },
    { type: "平段" as const, startTime: "21:00", endTime: "23:00", description: "平段晚间" },
    { type: "深谷" as const, startTime: "11:00", endTime: "14:00", description: "深谷时段" },
    { type: "低谷" as const, startTime: "02:00", endTime: "07:00", description: "低谷凌晨" },
    { type: "平段" as const, startTime: "23:00", endTime: "02:00", description: "平段深夜" }
  ],
  summer: [
    { type: "尖峰" as const, startTime: "17:00", endTime: "22:00", description: "尖峰时段" },
    { type: "平段" as const, startTime: "07:00", endTime: "09:00", description: "平段上午" },
    { type: "平段" as const, startTime: "16:00", endTime: "17:00", description: "平段下午" },
    { type: "平段" as const, startTime: "22:00", endTime: "23:00", description: "平段深夜" },
    { type: "低谷" as const, startTime: "01:00", endTime: "06:00", description: "低谷凌晨" },
    { type: "平段" as const, startTime: "23:00", endTime: "01:00", description: "平段深夜" }
  ],
  springAutumn: [
    { type: "尖峰" as const, startTime: "17:00", endTime: "20:00", description: "尖峰时段" },
    { type: "高峰" as const, startTime: "20:00", endTime: "21:00", description: "高峰时段" },
    { type: "平段" as const, startTime: "07:00", endTime: "11:00", description: "平段上午" },
    { type: "平段" as const, startTime: "14:00", endTime: "17:00", description: "平段下午" },
    { type: "平段" as const, startTime: "21:00", endTime: "23:00", description: "平段晚间" },
    { type: "深谷" as const, startTime: "11:00", endTime: "14:00", description: "深谷时段" },
    { type: "低谷" as const, startTime: "02:00", endTime: "07:00", description: "低谷凌晨" },
    { type: "平段" as const, startTime: "23:00", endTime: "02:00", description: "平段深夜" }
  ],
  june: [
    { type: "尖峰" as const, startTime: "17:00", endTime: "22:00", description: "尖峰时段" },
    { type: "平段" as const, startTime: "07:00", endTime: "09:00", description: "平段上午" },
    { type: "平段" as const, startTime: "16:00", endTime: "17:00", description: "平段下午" },
    { type: "平段" as const, startTime: "22:00", endTime: "23:00", description: "平段深夜" },
    { type: "低谷" as const, startTime: "02:00", endTime: "07:00", description: "低谷凌晨" },
    { type: "低谷" as const, startTime: "09:00", endTime: "16:00", description: "低谷白天" },
    { type: "平段" as const, startTime: "23:00", endTime: "02:00", description: "平段深夜" }
  ]
};

// 山西省时段配置
const my = {
  summer: [
    { type: "高峰" as const, startTime: "08:00", endTime: "11:00", description: "高峰上午" },
    { type: "高峰" as const, startTime: "17:00", endTime: "23:00", description: "高峰晚间" },
    { type: "平段" as const, startTime: "07:00", endTime: "08:00", description: "平段早晨" },
    { type: "平段" as const, startTime: "13:00", endTime: "17:00", description: "平段下午" },
    { type: "平段" as const, startTime: "23:00", endTime: "24:00", description: "平段深夜" },
    { type: "低谷" as const, startTime: "00:00", endTime: "07:00", description: "低谷凌晨" },
    { type: "低谷" as const, startTime: "11:00", endTime: "13:00", description: "低谷中午" }
  ],
  winter: [
    { type: "高峰" as const, startTime: "17:00", endTime: "23:00", description: "高峰时段" },
    { type: "平段" as const, startTime: "07:00", endTime: "08:00", description: "平段早晨" },
    { type: "平段" as const, startTime: "13:00", endTime: "17:00", description: "平段下午" },
    { type: "平段" as const, startTime: "23:00", endTime: "24:00", description: "平段深夜" },
    { type: "低谷" as const, startTime: "00:00", endTime: "07:00", description: "低谷凌晨" },
    { type: "低谷" as const, startTime: "11:00", endTime: "13:00", description: "低谷中午" }
  ],
  other: [
    { type: "高峰" as const, startTime: "08:00", endTime: "11:00", description: "高峰上午" },
    { type: "高峰" as const, startTime: "17:00", endTime: "23:00", description: "高峰晚间" },
    { type: "平段" as const, startTime: "07:00", endTime: "08:00", description: "平段早晨" },
    { type: "平段" as const, startTime: "13:00", endTime: "17:00", description: "平段下午" },
    { type: "平段" as const, startTime: "23:00", endTime: "24:00", description: "平段深夜" },
    { type: "低谷" as const, startTime: "00:00", endTime: "07:00", description: "低谷凌晨" },
    { type: "低谷" as const, startTime: "11:00", endTime: "13:00", description: "低谷中午" }
  ]
};

// 北京市时段配置
const yy = {
  summer: [
    { type: "尖峰" as const, startTime: "11:00", endTime: "13:00", description: "尖峰时段1" },
    { type: "尖峰" as const, startTime: "16:00", endTime: "17:00", description: "尖峰时段2" },
    { type: "高峰" as const, startTime: "10:00", endTime: "11:00", description: "高峰上午1" },
    { type: "高峰" as const, startTime: "13:00", endTime: "16:00", description: "高峰下午" },
    { type: "高峰" as const, startTime: "17:00", endTime: "22:00", description: "高峰晚间" },
    { type: "平段" as const, startTime: "07:00", endTime: "10:00", description: "平段上午" },
    { type: "平段" as const, startTime: "22:00", endTime: "23:00", description: "平段深夜" },
    { type: "低谷" as const, startTime: "23:00", endTime: "07:00", description: "低谷时段" }
  ],
  winter: [
    { type: "尖峰" as const, startTime: "18:00", endTime: "21:00", description: "尖峰时段" },
    { type: "高峰" as const, startTime: "10:00", endTime: "13:00", description: "高峰上午" },
    { type: "高峰" as const, startTime: "17:00", endTime: "18:00", description: "高峰下午1" },
    { type: "高峰" as const, startTime: "21:00", endTime: "22:00", description: "高峰晚间" },
    { type: "平段" as const, startTime: "07:00", endTime: "10:00", description: "平段上午" },
    { type: "平段" as const, startTime: "13:00", endTime: "17:00", description: "平段下午" },
    { type: "平段" as const, startTime: "22:00", endTime: "23:00", description: "平段深夜" },
    { type: "低谷" as const, startTime: "23:00", endTime: "07:00", description: "低谷时段" }
  ],
  other: [
    { type: "高峰" as const, startTime: "10:00", endTime: "13:00", description: "高峰上午" },
    { type: "高峰" as const, startTime: "17:00", endTime: "22:00", description: "高峰晚间" },
    { type: "平段" as const, startTime: "07:00", endTime: "10:00", description: "平段上午" },
    { type: "平段" as const, startTime: "13:00", endTime: "17:00", description: "平段下午" },
    { type: "平段" as const, startTime: "22:00", endTime: "23:00", description: "平段深夜" },
    { type: "低谷" as const, startTime: "23:00", endTime: "07:00", description: "低谷时段" }
  ]
};

// 河北省（南网）时段配置
const wf = {
  spring: [
    { type: "深谷" as const, startTime: "12:00", endTime: "15:00", description: "深谷时段" },
    { type: "低谷" as const, startTime: "03:00", endTime: "07:00", description: "低谷凌晨" },
    { type: "低谷" as const, startTime: "11:00", endTime: "12:00", description: "低谷中午" },
    { type: "平段" as const, startTime: "00:00", endTime: "03:00", description: "平段深夜" },
    { type: "平段" as const, startTime: "07:00", endTime: "11:00", description: "平段上午" },
    { type: "平段" as const, startTime: "15:00", endTime: "16:00", description: "平段下午" },
    { type: "高峰" as const, startTime: "16:00", endTime: "24:00", description: "高峰时段" }
  ],
  summer: [
    { type: "尖峰" as const, startTime: "19:00", endTime: "22:00", description: "尖峰时段" },
    { type: "高峰" as const, startTime: "16:00", endTime: "19:00", description: "高峰下午" },
    { type: "高峰" as const, startTime: "22:00", endTime: "24:00", description: "高峰深夜" },
    { type: "平段" as const, startTime: "00:00", endTime: "01:00", description: "平段深夜" },
    { type: "平段" as const, startTime: "07:00", endTime: "12:00", description: "平段上午" },
    { type: "平段" as const, startTime: "14:00", endTime: "16:00", description: "平段下午" },
    { type: "低谷" as const, startTime: "01:00", endTime: "07:00", description: "低谷凌晨" },
    { type: "低谷" as const, startTime: "12:00", endTime: "14:00", description: "低谷中午" }
  ],
  autumn: [
    { type: "深谷" as const, startTime: "12:00", endTime: "14:00", description: "深谷时段" },
    { type: "低谷" as const, startTime: "02:00", endTime: "06:00", description: "低谷凌晨" },
    { type: "低谷" as const, startTime: "11:00", endTime: "12:00", description: "低谷中午1" },
    { type: "低谷" as const, startTime: "14:00", endTime: "15:00", description: "低谷中午2" },
    { type: "平段" as const, startTime: "00:00", endTime: "02:00", description: "平段深夜" },
    { type: "平段" as const, startTime: "06:00", endTime: "11:00", description: "平段上午" },
    { type: "平段" as const, startTime: "15:00", endTime: "16:00", description: "平段下午" },
    { type: "高峰" as const, startTime: "16:00", endTime: "24:00", description: "高峰时段" }
  ],
  winter: [
    { type: "尖峰" as const, startTime: "17:00", endTime: "19:00", description: "尖峰时段" },
    { type: "高峰" as const, startTime: "07:00", endTime: "09:00", description: "高峰上午" },
    { type: "高峰" as const, startTime: "19:00", endTime: "23:00", description: "高峰晚间" },
    { type: "平段" as const, startTime: "00:00", endTime: "02:00", description: "平段深夜" },
    { type: "平段" as const, startTime: "06:00", endTime: "07:00", description: "平段早晨" },
    { type: "平段" as const, startTime: "09:00", endTime: "11:00", description: "平段上午" },
    { type: "平段" as const, startTime: "15:00", endTime: "17:00", description: "平段下午" },
    { type: "平段" as const, startTime: "23:00", endTime: "24:00", description: "平段深夜2" },
    { type: "低谷" as const, startTime: "02:00", endTime: "06:00", description: "低谷凌晨" },
    { type: "低谷" as const, startTime: "11:00", endTime: "15:00", description: "低谷中午" }
  ]
};

// 辅助函数：生成月份数据
function ft(slots: { months: number[]; slots: TimeSlot[] }[]): Record<number, MonthData> {
  const result: Record<number, MonthData> = {};
  for (let n = 1; n <= 12; n++) {
    const r = slots.find(o => o.months.includes(n));
    if (r) {
      result[n] = {
        monthName: `${n}月`,
        timeSlots: JSON.parse(JSON.stringify(r.slots))
      };
    }
  }
  return result;
}

export const provinceData: ProvinceData[] = [
  {
    name: "河南省",
    hasTimeOfUsePricing: true,
    months: {
      1: { monthName: "1月", timeSlots: hy.winter },
      2: { monthName: "2月", timeSlots: hy.winter },
      3: { monthName: "3月", timeSlots: hy.springAutumn },
      4: { monthName: "4月", timeSlots: hy.springAutumn },
      5: { monthName: "5月", timeSlots: hy.springAutumn },
      6: { monthName: "6月", timeSlots: hy.summer },
      7: { monthName: "7月", timeSlots: hy.summer },
      8: { monthName: "8月", timeSlots: hy.summer },
      9: { monthName: "9月", timeSlots: hy.springAutumn },
      10: { monthName: "10月", timeSlots: hy.springAutumn },
      11: { monthName: "11月", timeSlots: hy.springAutumn },
      12: { monthName: "12月", timeSlots: hy.winter }
    }
  },
  {
    name: "云南省",
    hasTimeOfUsePricing: true,
    note: "尖峰暂缓执行",
    months: Object.fromEntries(
      Array.from({ length: 12 }, (_, t) => [
        t + 1,
        {
          monthName: `${t + 1}月`,
          timeSlots: JSON.parse(JSON.stringify(cL))
        }
      ])
    )
  },
  {
    name: "江苏省",
    hasTimeOfUsePricing: true,
    months: {
      1: { monthName: "1月", timeSlots: e_.summerWinter },
      2: { monthName: "2月", timeSlots: e_.summerWinter },
      3: { monthName: "3月", timeSlots: e_.springAutumn },
      4: { monthName: "4月", timeSlots: e_.springAutumn },
      5: { monthName: "5月", timeSlots: e_.springAutumn },
      6: { monthName: "6月", timeSlots: e_.summerWinter },
      7: { monthName: "7月", timeSlots: e_.summerWinter },
      8: { monthName: "8月", timeSlots: e_.summerWinter },
      9: { monthName: "9月", timeSlots: e_.springAutumn },
      10: { monthName: "10月", timeSlots: e_.springAutumn },
      11: { monthName: "11月", timeSlots: e_.springAutumn },
      12: { monthName: "12月", timeSlots: e_.summerWinter }
    }
  },
  {
    name: "安徽省",
    hasTimeOfUsePricing: true,
    months: {
      1: { monthName: "1月", timeSlots: t_.special },
      2: { monthName: "2月", timeSlots: t_.other },
      3: { monthName: "3月", timeSlots: t_.other },
      4: { monthName: "4月", timeSlots: t_.other },
      5: { monthName: "5月", timeSlots: t_.other },
      6: { monthName: "6月", timeSlots: t_.other },
      7: { monthName: "7月", timeSlots: t_.special },
      8: { monthName: "8月", timeSlots: t_.special },
      9: { monthName: "9月", timeSlots: t_.special },
      10: { monthName: "10月", timeSlots: t_.other },
      11: { monthName: "11月", timeSlots: t_.other },
      12: { monthName: "12月", timeSlots: t_.special }
    }
  },
  {
    name: "广东省（珠三角五市）",
    hasTimeOfUsePricing: true,
    months: {
      1: { monthName: "1月", timeSlots: n_.other },
      2: { monthName: "2月", timeSlots: n_.other },
      3: { monthName: "3月", timeSlots: n_.other },
      4: { monthName: "4月", timeSlots: n_.other },
      5: { monthName: "5月", timeSlots: n_.other },
      6: { monthName: "6月", timeSlots: n_.other },
      7: { monthName: "7月", timeSlots: n_.summer },
      8: { monthName: "8月", timeSlots: n_.summer },
      9: { monthName: "9月", timeSlots: n_.summer },
      10: { monthName: "10月", timeSlots: n_.other },
      11: { monthName: "11月", timeSlots: n_.other },
      12: { monthName: "12月", timeSlots: n_.other }
    }
  },
  {
    name: "山东省",
    hasTimeOfUsePricing: true,
    months: {
      1: { monthName: "1月", timeSlots: Sf.winter },
      2: { monthName: "2月", timeSlots: Sf.winter },
      3: { monthName: "3月", timeSlots: Sf.springAutumn },
      4: { monthName: "4月", timeSlots: Sf.springAutumn },
      5: { monthName: "5月", timeSlots: Sf.springAutumn },
      6: { monthName: "6月", timeSlots: Sf.june },
      7: { monthName: "7月", timeSlots: Sf.summer },
      8: { monthName: "8月", timeSlots: Sf.summer },
      9: { monthName: "9月", timeSlots: Sf.springAutumn },
      10: { monthName: "10月", timeSlots: Sf.springAutumn },
      11: { monthName: "11月", timeSlots: Sf.springAutumn },
      12: { monthName: "12月", timeSlots: Sf.winter }
    }
  },
  {
    name: "山西省",
    hasTimeOfUsePricing: true,
    months: {
      1: { monthName: "1月", timeSlots: my.winter },
      2: { monthName: "2月", timeSlots: my.other },
      3: { monthName: "3月", timeSlots: my.other },
      4: { monthName: "4月", timeSlots: my.other },
      5: { monthName: "5月", timeSlots: my.other },
      6: { monthName: "6月", timeSlots: my.other },
      7: { monthName: "7月", timeSlots: my.summer },
      8: { monthName: "8月", timeSlots: my.summer },
      9: { monthName: "9月", timeSlots: my.other },
      10: { monthName: "10月", timeSlots: my.other },
      11: { monthName: "11月", timeSlots: my.other },
      12: { monthName: "12月", timeSlots: my.winter }
    }
  },
  {
    name: "北京市",
    hasTimeOfUsePricing: true,
    months: {
      1: { monthName: "1月", timeSlots: yy.winter },
      2: { monthName: "2月", timeSlots: yy.other },
      3: { monthName: "3月", timeSlots: yy.other },
      4: { monthName: "4月", timeSlots: yy.other },
      5: { monthName: "5月", timeSlots: yy.other },
      6: { monthName: "6月", timeSlots: yy.other },
      7: { monthName: "7月", timeSlots: yy.summer },
      8: { monthName: "8月", timeSlots: yy.summer },
      9: { monthName: "9月", timeSlots: yy.other },
      10: { monthName: "10月", timeSlots: yy.other },
      11: { monthName: "11月", timeSlots: yy.other },
      12: { monthName: "12月", timeSlots: yy.winter }
    }
  },
  {
    name: "河北省（北网）",
    hasTimeOfUsePricing: true,
    note: "冀北地区，与冀北地区数据一致",
    months: ft([
      { months: [6, 7, 8], slots: [
        { type: "尖峰", startTime: "18:00", endTime: "21:00", description: "尖峰时段" },
        { type: "高峰", startTime: "10:00", endTime: "12:00", description: "高峰上午" },
        { type: "高峰", startTime: "16:00", endTime: "18:00", description: "高峰下午" },
        { type: "高峰", startTime: "21:00", endTime: "22:00", description: "高峰晚间" },
        { type: "平段", startTime: "07:00", endTime: "10:00", description: "平段上午" },
        { type: "平段", startTime: "12:00", endTime: "16:00", description: "平段中午" },
        { type: "平段", startTime: "22:00", endTime: "23:00", description: "平段晚间" },
        { type: "低谷", startTime: "00:00", endTime: "07:00", description: "低谷凌晨" },
        { type: "低谷", startTime: "23:00", endTime: "24:00", description: "低谷深夜" }
      ]},
      { months: [1, 11, 12], slots: [
        { type: "尖峰", startTime: "17:00", endTime: "19:00", description: "尖峰时段" },
        { type: "高峰", startTime: "07:00", endTime: "09:00", description: "高峰上午" },
        { type: "高峰", startTime: "16:00", endTime: "17:00", description: "高峰下午1" },
        { type: "高峰", startTime: "19:00", endTime: "22:00", description: "高峰晚间" },
        { type: "深谷", startTime: "12:00", endTime: "15:00", description: "深谷时段" },
        { type: "平段", startTime: "00:00", endTime: "01:00", description: "平段深夜1" },
        { type: "平段", startTime: "06:00", endTime: "07:00", description: "平段早晨" },
        { type: "平段", startTime: "09:00", endTime: "12:00", description: "平段上午" },
        { type: "平段", startTime: "15:00", endTime: "16:00", description: "平段下午" },
        { type: "平段", startTime: "22:00", endTime: "24:00", description: "平段深夜2" },
        { type: "低谷", startTime: "01:00", endTime: "06:00", description: "低谷凌晨" }
      ]},
      { months: [2], slots: [
        { type: "高峰", startTime: "16:00", endTime: "22:00", description: "高峰时段" },
        { type: "深谷", startTime: "12:00", endTime: "15:00", description: "深谷时段" },
        { type: "平段", startTime: "00:00", endTime: "01:00", description: "平段深夜1" },
        { type: "平段", startTime: "06:00", endTime: "12:00", description: "平段上午" },
        { type: "平段", startTime: "15:00", endTime: "16:00", description: "平段下午" },
        { type: "平段", startTime: "22:00", endTime: "24:00", description: "平段深夜2" },
        { type: "低谷", startTime: "01:00", endTime: "06:00", description: "低谷凌晨" }
      ]},
      { months: [3, 4, 5, 9, 10], slots: [
        { type: "高峰", startTime: "16:00", endTime: "22:00", description: "高峰时段" },
        { type: "平段", startTime: "00:00", endTime: "01:00", description: "平段深夜1" },
        { type: "平段", startTime: "06:00", endTime: "12:00", description: "平段上午" },
        { type: "平段", startTime: "15:00", endTime: "16:00", description: "平段下午" },
        { type: "平段", startTime: "22:00", endTime: "24:00", description: "平段深夜2" },
        { type: "低谷", startTime: "01:00", endTime: "06:00", description: "低谷凌晨" },
        { type: "低谷", startTime: "12:00", endTime: "15:00", description: "低谷中午" }
      ]}
    ])
  },
  {
    name: "河北省（南网）",
    hasTimeOfUsePricing: true,
    months: {
      1: { monthName: "1月", timeSlots: wf.winter },
      2: { monthName: "2月", timeSlots: wf.winter },
      3: { monthName: "3月", timeSlots: wf.spring },
      4: { monthName: "4月", timeSlots: wf.spring },
      5: { monthName: "5月", timeSlots: wf.spring },
      6: { monthName: "6月", timeSlots: wf.summer },
      7: { monthName: "7月", timeSlots: wf.summer },
      8: { monthName: "8月", timeSlots: wf.summer },
      9: { monthName: "9月", timeSlots: wf.autumn },
      10: { monthName: "10月", timeSlots: wf.autumn },
      11: { monthName: "11月", timeSlots: wf.autumn },
      12: { monthName: "12月", timeSlots: wf.winter }
    }
  }
];

export default provinceData;
