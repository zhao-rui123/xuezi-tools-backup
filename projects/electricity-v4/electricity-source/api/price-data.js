/**
 * 电价数据服务 - 从主站提取数据供电费清单处理器使用
 * 部署地址：/electricity/api/price-data.js
 */

// 31省份电价数据（2026年2月版本）
const PROVINCE_PRICE_DATA = {
  "山东": {
    "2026": {
      "2": {
        "deepValley": { price: 0.2401, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4802, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7064, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0693, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.2246, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "河南": {
    "2026": {
      "2": {
        "deepValley": { price: 0.2804, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.5608, hours: [11,12,13,14], name: "低谷" },
        "flat": { price: 0.7842, hours: [6,7,8,9,10,15,16,17,22,23], name: "平段" },
        "high": { price: 1.1203, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.2323, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "浙江": {
    "2026": {
      "2": {
        "deepValley": { price: 0.1829, hours: [11,12,13], name: "深谷" },
        "valley": { price: 0.3658, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.7308, hours: [8,9,10,14,15,16,17,22,23], name: "平段" },
        "high": { price: 1.0962, hours: [19,20,21], name: "高峰" },
        "peak": { price: 1.2058, hours: [18], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "广东": {
    "2026": {
      "2": {
        "deepValley": { price: 0.2205, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4410, hours: [8,9,10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7203, hours: [16,17,22,23], name: "平段" },
        "high": { price: 1.0805, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1886, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "江苏": {
    "2026": {
      "2": {
        "deepValley": { price: 0.2408, hours: [11,12,13], name: "深谷" },
        "valley": { price: 0.4816, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.7224, hours: [8,9,10,14,15,16,17,22,23], name: "平段" },
        "high": { price: 1.0836, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1920, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "河北": {
    "2026": {
      "2": {
        "deepValley": { price: 0.2602, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.5204, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7806, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0408, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1449, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "四川": {
    "2026": {
      "1": {
        "deepValley": { price: 0.4010, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4010, hours: [], name: "低谷" },
        "flat": { price: 0.8023, hours: [8,12,13,14,21,22,23], name: "平段" },
        "high": { price: 1.2037, hours: [9,10,11,15,16,17,18,19,20], name: "高峰" },
        "peak": { price: 1.2037, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "2": {
        "deepValley": { price: 0.4010, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4010, hours: [], name: "低谷" },
        "flat": { price: 0.8023, hours: [8,12,13,14,21,22,23], name: "平段" },
        "high": { price: 1.2037, hours: [9,10,11,15,16,17,18,19,20], name: "高峰" },
        "peak": { price: 1.2037, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  }
};

// 默认配置（其他省份使用）
const DEFAULT_PRICE_CONFIG = {
  "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
  "valley": { price: 0.50, hours: [10,11,12,13,14,15], name: "低谷" },
  "flat": { price: 0.75, hours: [6,7,8,9,16,17,22,23], name: "平段" },
  "high": { price: 1.10, hours: [18,19,20,21], name: "高峰" },
  "peak": { price: 1.25, hours: [], name: "尖峰" },
  "cycles": 1
};

/**
 * 获取省份电价数据
 * @param {string} province - 省份名称
 * @param {number} year - 年份
 * @param {number} month - 月份
 * @returns {Object} 电价数据
 */
function getProvincePriceData(province, year, month) {
  const yearStr = String(year);
  const monthStr = String(month);
  
  if (PROVINCE_PRICE_DATA[province] && 
      PROVINCE_PRICE_DATA[province][yearStr] && 
      PROVINCE_PRICE_DATA[province][yearStr][monthStr]) {
    return PROVINCE_PRICE_DATA[province][yearStr][monthStr];
  }
  
  // 返回默认配置
  return DEFAULT_PRICE_CONFIG;
}

/**
 * 获取省份列表
 * @returns {Array} 省份名称列表
 */
function getProvincesList() {
  return Object.keys(PROVINCE_PRICE_DATA);
}

/**
 * 获取充放电时段配置
 * @param {Object} priceData - 电价数据
 * @returns {Array} 24小时充放电状态
 */
function getChargeDischargeSchedule(priceData) {
  const schedule = [];
  
  for (let hour = 0; hour < 24; hour++) {
    let period = 'flat';
    let action = 'idle';
    
    // 判断时段
    if (priceData.deepValley && priceData.deepValley.hours.includes(hour)) {
      period = 'deepValley';
      action = 'charge';
    } else if (priceData.valley && priceData.valley.hours.includes(hour)) {
      period = 'valley';
      action = 'charge';
    } else if (priceData.flat && priceData.flat.hours.includes(hour)) {
      period = 'flat';
      action = 'idle';
    } else if (priceData.high && priceData.high.hours.includes(hour)) {
      period = 'high';
      action = 'discharge';
    } else if (priceData.peak && priceData.peak.hours.includes(hour)) {
      period = 'peak';
      action = 'discharge';
    }
    
    schedule.push({
      hour,
      period,
      action,
      price: priceData[period] ? priceData[period].price : 0
    });
  }
  
  return schedule;
}

/**
 * 获取循环次数
 * @param {string} province - 省份名称
 * @param {number} month - 月份
 * @returns {number} 循环次数（1或2）
 */
function getCycleCount(province, month) {
  const priceData = getProvincePriceData(province, 2026, month);
  return priceData.cycles || 1;
}

// 导出（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    getProvincePriceData,
    getProvincesList,
    getChargeDischargeSchedule,
    getCycleCount,
    PROVINCE_PRICE_DATA
  };
}