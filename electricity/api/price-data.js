/**
 * 电价数据服务 - 从独立JSON文件加载数据
 * 数据文件: prices.json
 * 更新：2026年3月电价数据
 * 
 * 维护说明：
 * - 修改电价数据只需编辑 prices.json
 * - 无需修改此文件
 */

let PROVINCE_PRICE_DATA = null;

/**
 * 加载电价数据
 */
async function loadPriceData() {
  if (PROVINCE_PRICE_DATA) return PROVINCE_PRICE_DATA;
  
  try {
    const response = await fetch('./api/prices.json');
    PROVINCE_PRICE_DATA = await response.json();
    return PROVINCE_PRICE_DATA;
  } catch (error) {
    console.error('加载电价数据失败:', error);
    // 降级到默认配置
    return DEFAULT_PRICE_CONFIG;
  }
}

// 默认配置（数据加载失败时使用）
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
  
  if (!PROVINCE_PRICE_DATA) {
    // 数据未加载，同步加载
    const xhr = new XMLHttpRequest();
    xhr.open('GET', './api/prices.json', false);
    xhr.send();
    if (xhr.status === 200) {
      PROVINCE_PRICE_DATA = JSON.parse(xhr.responseText);
    }
  }
  
  if (PROVINCE_PRICE_DATA && 
      PROVINCE_PRICE_DATA[province] && 
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
  if (!PROVINCE_PRICE_DATA) {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', './api/prices.json', false);
    xhr.send();
    if (xhr.status === 200) {
      PROVINCE_PRICE_DATA = JSON.parse(xhr.responseText);
    }
  }
  return PROVINCE_PRICE_DATA ? Object.keys(PROVINCE_PRICE_DATA) : [];
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
    loadPriceData
  };
}
