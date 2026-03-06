/**
 * Pinia Store - 电价数据管理
 * 功能：管理省份列表、电价数据、计算时段安排
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { PRICE_DATA } from '../api/priceData'

export const usePriceStore = defineStore('price', () => {
  // ============ State ============
  /** 当前选中的省份 */
  const selectedProvince = ref('')
  
  /** 省份列表 */
  const provinces = ref([])
  
  // ============ Getters ============
  
  /**
   * 获取指定省份的电价数据
   * @param {string} province - 省份名称
   * @param {number} year - 年份
   * @param {number} month - 月份
   * @returns {Object|null} 电价数据对象
   */
  const getPriceData = computed(() => (province, year, month) => {
    const yearData = PRICE_DATA[province]
    if (!yearData) return null
    
    const monthData = yearData[year]?.[month]
    return monthData || null
  })
  
  /**
   * 获取省份列表
   * @returns {string[]} 省份名称数组
   */
  const getProvincesList = computed(() => {
    return Object.keys(PRICE_DATA).sort()
  })
  
  // ============ Actions ============
  
  /**
   * 初始化省份列表
   * 默认选中第一个省份
   */
  function initProvinces() {
    provinces.value = getProvincesList.value
    if (provinces.value.length > 0 && !selectedProvince.value) {
      selectedProvince.value = provinces.value[0]
    }
  }
  
  /**
   * 设置选中省份
   * @param {string} province - 省份名称
   */
  function setProvince(province) {
    selectedProvince.value = province
  }
  
  /**
   * 获取24小时时段安排
   * @param {Object} priceData - 电价数据
   * @returns {Array} 24小时时段数组
   */
  function getHourlySchedule(priceData) {
    const schedule = []
    
    for (let hour = 0; hour < 24; hour++) {
      let period = 'flat'
      let action = 'idle'
      let price = 0
      
      // 判断时段类型
      if (priceData.deepValley?.hours?.includes(hour)) {
        period = 'deepValley'
        action = 'charge'
        price = priceData.deepValley.price
      } else if (priceData.valley?.hours?.includes(hour)) {
        period = 'valley'
        action = 'charge'
        price = priceData.valley.price
      } else if (priceData.flat?.hours?.includes(hour)) {
        period = 'flat'
        action = 'idle'
        price = priceData.flat.price
      } else if (priceData.high?.hours?.includes(hour)) {
        period = 'high'
        action = 'discharge'
        price = priceData.high.price
      } else if (priceData.peak?.hours?.includes(hour)) {
        period = 'peak'
        action = 'discharge'
        price = priceData.peak.price
      }
      
      schedule.push({
        hour,
        period,
        action,
        price,
        periodName: getPeriodName(period)
      })
    }
    
    return schedule
  }
  
  /**
   * 获取时段中文名称
   * @param {string} period - 时段代码
   * @returns {string} 中文名称
   */
  function getPeriodName(period) {
    const names = {
      deepValley: '深谷',
      valley: '低谷',
      flat: '平段',
      high: '高峰',
      peak: '尖峰'
    }
    return names[period] || '平段'
  }
  
  return {
    // State
    selectedProvince,
    provinces,
    
    // Getters
    getPriceData,
    getProvincesList,
    
    // Actions
    initProvinces,
    setProvince,
    getHourlySchedule
  }
})
