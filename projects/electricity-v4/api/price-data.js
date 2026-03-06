/**
 * API接口 - 电价数据服务
 * 提供电价数据的API访问接口
 */

// 引入数据文件（在Node.js环境中）
if (typeof require !== 'undefined') {
  try {
    const data = require('../data/price-data.js');
    Object.assign(global, data);
  } catch (e) {
    console.log('Running in browser environment');
  }
}

/**
 * API响应格式
 * @param {boolean} success - 是否成功
 * @param {*} data - 响应数据
 * @param {string} message - 消息
 */
function apiResponse(success, data, message = '') {
  return {
    success,
    data,
    message,
    timestamp: new Date().toISOString()
  };
}

/**
 * 获取所有省份列表
 * @returns {Array} 省份列表
 */
function getProvinces() {
  if (typeof PRICE_DATA === 'undefined') {
    return apiResponse(false, null, '数据未加载');
  }
  return apiResponse(true, Object.keys(PRICE_DATA).sort());
}

/**
 * 获取指定省份的电价数据
 * @param {string} province - 省份名称
 * @param {number} year - 年份
 * @param {number} month - 月份
 * @returns {Object} 电价数据
 */
function getPriceData(province, year, month) {
  if (typeof PRICE_DATA === 'undefined') {
    return apiResponse(false, null, '数据未加载');
  }
  
  const yearStr = String(year);
  const monthStr = String(month);
  
  if (PRICE_DATA[province] && 
      PRICE_DATA[province][yearStr] && 
      PRICE_DATA[province][yearStr][monthStr]) {
    return apiResponse(true, PRICE_DATA[province][yearStr][monthStr]);
  }
  
  return apiResponse(false, null, '未找到该省份指定时间的电价数据');
}

/**
 * 获取省份可用的月份列表
 * @param {string} province - 省份名称
 * @param {number} year - 年份
 * @returns {Array} 月份列表
 */
function getAvailableMonths(province, year) {
  if (typeof PRICE_DATA === 'undefined') {
    return apiResponse(false, null, '数据未加载');
  }
  
  const yearStr = String(year);
  
  if (!PRICE_DATA[province] || !PRICE_DATA[province][yearStr]) {
    return apiResponse(true, []);
  }
  
  const months = Object.keys(PRICE_DATA[province][yearStr])
    .map(m => parseInt(m))
    .sort((a, b) => a - b);
  
  return apiResponse(true, months);
}

/**
 * 获取省份备注信息
 * @param {string} province - 省份名称
 * @returns {string} 备注信息
 */
function getProvinceNote(province) {
  if (typeof PROVINCE_NOTES === 'undefined') {
    return apiResponse(false, null, '备注数据未加载');
  }
  
  return apiResponse(true, PROVINCE_NOTES[province] || null);
}

/**
 * 获取24小时电价数据（用于图表）
 * @param {string} province - 省份名称
 * @param {number} year - 年份
 * @param {number} month - 月份
 * @returns {Array} 24小时电价数据
 */
function get24HourData(province, year, month) {
  if (typeof PRICE_DATA === 'undefined' || typeof PRICE_COLORS === 'undefined') {
    return apiResponse(false, null, '数据未加载');
  }
  
  const yearStr = String(year);
  const monthStr = String(month);
  
  if (!PRICE_DATA[province] || 
      !PRICE_DATA[province][yearStr] || 
      !PRICE_DATA[province][yearStr][monthStr]) {
    return apiResponse(false, null, '未找到数据');
  }
  
  const priceData = PRICE_DATA[province][yearStr][monthStr];
  const hourlyData = [];
  
  for (let hour = 0; hour < 24; hour++) {
    let period = null;
    let price = 0;
    let typeName = "";
    
    // 按优先级查找时段（尖峰 > 高峰 > 平段 > 低谷 > 深谷）
    const periods = ['peak', 'high', 'flat', 'valley', 'deepValley'];
    
    for (const p of periods) {
      if (priceData[p] && priceData[p].hours && priceData[p].hours.includes(hour)) {
        period = p;
        price = priceData[p].price;
        typeName = priceData[p].name;
        break;
      }
    }
    
    hourlyData.push({
      hour: hour,
      hourLabel: `${hour.toString().padStart(2, '0')}:00`,
      period: period,
      price: price,
      typeName: typeName,
      color: period ? PRICE_COLORS[period] : '#ccc'
    });
  }
  
  return apiResponse(true, hourlyData);
}

/**
 * 获取时段汇总数据
 * @param {string} province - 省份名称
 * @param {number} year - 年份
 * @param {number} month - 月份
 * @returns {Array} 时段汇总数据
 */
function getTimeSlots(province, year, month) {
  if (typeof PRICE_DATA === 'undefined' || typeof PRICE_COLORS === 'undefined') {
    return apiResponse(false, null, '数据未加载');
  }
  
  const yearStr = String(year);
  const monthStr = String(month);
  
  if (!PRICE_DATA[province] || 
      !PRICE_DATA[province][yearStr] || 
      !PRICE_DATA[province][yearStr][monthStr]) {
    return apiResponse(false, null, '未找到数据');
  }
  
  const priceData = PRICE_DATA[province][yearStr][monthStr];
  const slots = [];
  const periods = ['peak', 'high', 'flat', 'valley', 'deepValley'];
  
  for (const period of periods) {
    if (priceData[period] && priceData[period].hours && priceData[period].hours.length > 0) {
      const hours = priceData[period].hours;
      const ranges = hoursToRanges(hours);
      
      slots.push({
        type: period,
        typeName: priceData[period].name,
        price: priceData[period].price,
        hours: hours,
        ranges: ranges,
        hourCount: hours.length,
        color: PRICE_COLORS[period]
      });
    }
  }
  
  // 按电价从高到低排序
  slots.sort((a, b) => b.price - a.price);
  
  return apiResponse(true, slots);
}

/**
 * 将小时列表转换为时间范围字符串
 * @param {Array} hours - 小时列表
 * @returns {Array} 时间范围列表
 */
function hoursToRanges(hours) {
  if (!hours || hours.length === 0) return [];
  
  const sorted = [...hours].sort((a, b) => a - b);
  const ranges = [];
  let start = sorted[0];
  let end = sorted[0];
  
  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i] === end + 1) {
      end = sorted[i];
    } else {
      ranges.push(formatRange(start, end));
      start = sorted[i];
      end = sorted[i];
    }
  }
  
  ranges.push(formatRange(start, end));
  return ranges;
}

/**
 * 格式化时间范围
 * @param {number} start - 开始小时
 * @param {number} end - 结束小时
 * @returns {string} 格式化后的时间范围
 */
function formatRange(start, end) {
  const startStr = `${start.toString().padStart(2, '0')}:00`;
  const endStr = end === 23 ? '24:00' : `${(end + 1).toString().padStart(2, '0')}:00`;
  return `${startStr}-${endStr}`;
}

/**
 * 获取循环次数
 * @param {string} province - 省份名称
 * @param {number} year - 年份
 * @param {number} month - 月份
 * @returns {number} 循环次数
 */
function getCycles(province, year, month) {
  if (typeof PRICE_DATA === 'undefined') {
    return apiResponse(false, null, '数据未加载');
  }
  
  const yearStr = String(year);
  const monthStr = String(month);
  
  if (PRICE_DATA[province] && 
      PRICE_DATA[province][yearStr] && 
      PRICE_DATA[province][yearStr][monthStr]) {
    return apiResponse(true, PRICE_DATA[province][yearStr][monthStr].cycles || 1);
  }
  
  return apiResponse(false, null, '未找到数据');
}

/**
 * 获取电价统计信息
 * @param {string} province - 省份名称
 * @param {number} year - 年份
 * @param {number} month - 月份
 * @returns {Object} 统计信息
 */
function getStatistics(province, year, month) {
  const hourlyResult = get24HourData(province, year, month);
  
  if (!hourlyResult.success) {
    return hourlyResult;
  }
  
  const hourlyData = hourlyResult.data;
  const prices = hourlyData.map(h => h.price);
  
  const stats = {
    maxPrice: Math.max(...prices),
    minPrice: Math.min(...prices),
    avgPrice: (prices.reduce((a, b) => a + b, 0) / prices.length).toFixed(4),
    priceDiff: (Math.max(...prices) - Math.min(...prices)).toFixed(4)
  };
  
  return apiResponse(true, stats);
}

// 导出API函数（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    apiResponse,
    getProvinces,
    getPriceData,
    getAvailableMonths,
    getProvinceNote,
    get24HourData,
    getTimeSlots,
    getCycles,
    getStatistics
  };
}
