/**
 * 电价查询系统配置文件
 * 集中管理应用配置项
 */

const APP_CONFIG = {
  // 应用信息
  app: {
    name: '电价查询系统',
    version: '4.0.0',
    description: '全国31省份工商业电价查询'
  },

  // 默认设置
  defaults: {
    province: '山东',
    year: 2026,
    month: 2
  },

  // 图表配置
  chart: {
    type: 'bar',
    responsive: true,
    maintainAspectRatio: false,
    borderRadius: 4,
    borderSkipped: false
  },

  // 颜色配置
  colors: {
    peak: '#ef4444',      // 尖峰 - 红色
    high: '#f97316',      // 高峰 - 橙色
    flat: '#22c55e',      // 平段 - 绿色
    valley: '#6366f1',    // 低谷 - 紫色
    deepValley: '#3b82f6' // 深谷 - 蓝色
  },

  // 时段类型名称
  typeNames: {
    peak: '尖峰',
    high: '高峰',
    flat: '平段',
    valley: '低谷',
    deepValley: '深谷'
  },

  // 时段优先级（用于排序）
  typePriority: ['peak', 'high', 'flat', 'valley', 'deepValley'],

  // 数据文件路径
  dataPath: './data/price-data.js',

  // API接口路径
  apiPath: './api/price-data.js'
};

// 导出配置（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { APP_CONFIG };
}
