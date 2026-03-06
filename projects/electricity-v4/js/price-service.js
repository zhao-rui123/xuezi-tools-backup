/**
 * 电价数据API服务
 * 提供数据获取、处理和转换功能
 */

class PriceDataService {
  constructor() {
    this.data = PRICE_DATA;
    this.notes = PROVINCE_NOTES;
    this.colors = PRICE_COLORS;
    this.typeNames = PRICE_TYPE_NAMES;
    this.typeWeights = PRICE_TYPE_WEIGHTS;
  }

  /**
   * 获取所有省份列表
   * @returns {Array} 省份名称列表
   */
  getProvinces() {
    return Object.keys(this.data).sort();
  }

  /**
   * 获取省份备注信息
   * @param {string} province - 省份名称
   * @returns {string|null} 备注信息
   */
  getProvinceNote(province) {
    return this.notes[province] || null;
  }

  /**
   * 获取省份指定年月的数据
   * @param {string} province - 省份名称
   * @param {number} year - 年份
   * @param {number} month - 月份
   * @returns {Object|null} 电价数据
   */
  getPriceData(province, year, month) {
    const yearStr = String(year);
    const monthStr = String(month);
    
    if (this.data[province] && 
        this.data[province][yearStr] && 
        this.data[province][yearStr][monthStr]) {
      return this.data[province][yearStr][monthStr];
    }
    
    return null;
  }

  /**
   * 获取省份有数据的月份列表
   * @param {string} province - 省份名称
   * @param {number} year - 年份
   * @returns {Array} 月份列表
   */
  getAvailableMonths(province, year) {
    const yearStr = String(year);
    
    if (!this.data[province] || !this.data[province][yearStr]) {
      return [];
    }
    
    return Object.keys(this.data[province][yearStr])
      .map(m => parseInt(m))
      .sort((a, b) => a - b);
  }

  /**
   * 获取24小时电价数据（用于图表）
   * @param {string} province - 省份名称
   * @param {number} year - 年份
   * @param {number} month - 月份
   * @returns {Array} 24小时电价数据
   */
  get24HourData(province, year, month) {
    const priceData = this.getPriceData(province, year, month);
    
    if (!priceData) {
      return null;
    }

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
        color: period ? this.colors[period] : '#ccc'
      });
    }
    
    return hourlyData;
  }

  /**
   * 获取时段汇总数据（用于表格）
   * @param {string} province - 省份名称
   * @param {number} year - 年份
   * @param {number} month - 月份
   * @returns {Array} 时段汇总数据
   */
  getTimeSlots(province, year, month) {
    const priceData = this.getPriceData(province, year, month);
    
    if (!priceData) {
      return [];
    }

    const slots = [];
    const periods = ['peak', 'high', 'flat', 'valley', 'deepValley'];
    
    for (const period of periods) {
      if (priceData[period] && priceData[period].hours && priceData[period].hours.length > 0) {
        const hours = priceData[period].hours;
        const ranges = this._hoursToRanges(hours);
        
        slots.push({
          type: period,
          typeName: priceData[period].name,
          price: priceData[period].price,
          hours: hours,
          ranges: ranges,
          hourCount: hours.length,
          color: this.colors[period]
        });
      }
    }
    
    // 按电价从高到低排序
    return slots.sort((a, b) => b.price - a.price);
  }

  /**
   * 获取循环次数
   * @param {string} province - 省份名称
   * @param {number} year - 年份
   * @param {number} month - 月份
   * @returns {number} 循环次数
   */
  getCycles(province, year, month) {
    const priceData = this.getPriceData(province, year, month);
    return priceData ? (priceData.cycles || 1) : 0;
  }

  /**
   * 获取电价统计信息
   * @param {string} province - 省份名称
   * @param {number} year - 年份
   * @param {number} month - 月份
   * @returns {Object} 统计信息
   */
  getStatistics(province, year, month) {
    const priceData = this.getPriceData(province, year, month);
    
    if (!priceData) {
      return null;
    }

    const hourlyData = this.get24HourData(province, year, month);
    const prices = hourlyData.map(h => h.price);
    
    return {
      maxPrice: Math.max(...prices),
      minPrice: Math.min(...prices),
      avgPrice: (prices.reduce((a, b) => a + b, 0) / prices.length).toFixed(4),
      peakPrice: priceData.peak ? priceData.peak.price : 0,
      valleyPrice: priceData.deepValley ? priceData.deepValley.price : (priceData.valley ? priceData.valley.price : 0),
      priceDiff: (Math.max(...prices) - Math.min(...prices)).toFixed(4)
    };
  }

  /**
   * 将小时列表转换为时间范围字符串
   * @private
   */
  _hoursToRanges(hours) {
    if (!hours || hours.length === 0) return [];
    
    const sorted = [...hours].sort((a, b) => a - b);
    const ranges = [];
    let start = sorted[0];
    let end = sorted[0];
    
    for (let i = 1; i < sorted.length; i++) {
      if (sorted[i] === end + 1) {
        end = sorted[i];
      } else {
        ranges.push(this._formatRange(start, end));
        start = sorted[i];
        end = sorted[i];
      }
    }
    
    ranges.push(this._formatRange(start, end));
    return ranges;
  }

  /**
   * 格式化时间范围
   * @private
   */
  _formatRange(start, end) {
    const startStr = `${start.toString().padStart(2, '0')}:00`;
    const endStr = end === 23 ? '24:00' : `${(end + 1).toString().padStart(2, '0')}:00`;
    return `${startStr}-${endStr}`;
  }
}

// 创建全局实例
const priceService = new PriceDataService();

// 导出（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { PriceDataService, priceService };
}
