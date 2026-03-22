<template>
  <div class="app-container">
    <!-- Header -->
    <header>
      <h1>分时电价查询系统</h1>
      <p>各省份分时电价数据查询与计算</p>
    </header>

    <!-- Selectors -->
    <div class="selectors">
      <div class="selector-group">
        <label>选择省份</label>
        <select v-model="selectedProvince">
          <option v-for="province in provinces" :key="province" :value="province">{{ province }}</option>
        </select>
      </div>
      <div class="selector-group">
        <label>选择年份</label>
        <select v-model="selectedYear" class="year">
          <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
        </select>
      </div>
      <div class="selector-group">
        <label>选择月份</label>
        <select v-model="selectedMonth" class="month">
          <option v-for="month in months" :key="month" :value="month">{{ month }}月</option>
        </select>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Left Column -->
      <div class="left-column">
        <!-- Price Table -->
        <div class="card">
          <h2>
            <svg class="icon-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
            </svg>
            {{ selectedProvince }} - {{ selectedYear }}年{{ selectedMonth }}月电价
          </h2>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>时段类型</th>
                  <th>电价(元/kWh)</th>
                  <th>时间段</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="period in pricePeriods" :key="period.name">
                  <td>
                    <span :class="['badge', period.badgeClass]">{{ period.name }}</span>
                  </td>
                  <td>{{ period.price.toFixed(4) }}</td>
                  <td class="text-gray">{{ period.hoursText }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="card-footer">
            <span class="cycles-label">日循环次数:</span>
            <span class="cycles-value">{{ cycles }} 次</span>
          </div>
        </div>

        <!-- 24h Chart -->
        <div class="card">
          <h2>
            <svg class="icon-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
            </svg>
            24小时电价分布
          </h2>
          <div ref="chartRef" class="chart-container"></div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="right-column">
        <!-- Calculator -->
        <div class="card">
          <h2>
            <svg class="icon-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
            </svg>
            电费计算器
          </h2>
          <div class="space-y-4">
            <div class="input-group">
              <label>用电量 (kWh)</label>
              <input 
                v-model.number="calcUsage" 
                type="number" 
                placeholder="请输入用电量"
              />
            </div>
            <div class="input-group">
              <label>用电时段分布</label>
              <div class="distribution-grid">
                <div class="distribution-item">
                  <span class="text-gray">尖峰时段:</span>
                  <span>{{ calcPeakHours }}h</span>
                </div>
                <div class="distribution-item">
                  <span class="text-gray">高峰时段:</span>
                  <span>{{ calcHighHours }}h</span>
                </div>
                <div class="distribution-item">
                  <span class="text-gray">平段时段:</span>
                  <span>{{ calcFlatHours }}h</span>
                </div>
                <div class="distribution-item">
                  <span class="text-gray">低谷时段:</span>
                  <span>{{ calcValleyHours }}h</span>
                </div>
                <div v-if="currentData?.deepValley?.hours?.length" class="distribution-item">
                  <span class="text-gray">深谷时段:</span>
                  <span>{{ calcDeepValleyHours }}h</span>
                </div>
              </div>
            </div>
            <button @click="calculateBill" class="btn btn-primary">
              计算电费
            </button>
            <div v-if="billResult" class="result-section">
              <div class="result-grid">
                <div class="result-box">
                  <div class="result-box-label">总电费</div>
                  <div class="result-box-value green">¥{{ billResult.total.toFixed(2) }}</div>
                </div>
                <div class="result-box">
                  <div class="result-box-label">平均电价</div>
                  <div class="result-box-value blue">¥{{ billResult.avgPrice.toFixed(4) }}/kWh</div>
                </div>
              </div>
              <div class="detail-grid">
                <div class="detail-item">
                  <span class="text-gray">尖峰电费:</span>
                  <span class="red">¥{{ billResult.peak.toFixed(2) }}</span>
                </div>
                <div class="detail-item">
                  <span class="text-gray">高峰电费:</span>
                  <span class="orange">¥{{ billResult.high.toFixed(2) }}</span>
                </div>
                <div class="detail-item">
                  <span class="text-gray">平段电费:</span>
                  <span class="gray">¥{{ billResult.flat.toFixed(2) }}</span>
                </div>
                <div class="detail-item">
                  <span class="text-gray">低谷电费:</span>
                  <span class="green">¥{{ billResult.valley.toFixed(2) }}</span>
                </div>
                <div v-if="billResult.deepValley" class="detail-item col-span-2">
                  <span class="text-gray">深谷电费:</span>
                  <span class="purple">¥{{ billResult.deepValley.toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Charge/Discharge Optimization -->
        <div class="card">
          <h2>
            <svg class="icon-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            充放电优化策略
          </h2>
          <div class="space-y-4">
            <div class="input-group">
              <label>储能系统容量 (kWh)</label>
              <input 
                v-model.number="storageCapacity" 
                type="number" 
                placeholder="如: 1000"
              />
            </div>
            <div class="input-group">
              <label>充放电效率 (%)</label>
              <input 
                v-model.number="efficiency" 
                type="number" 
                placeholder="如: 85"
              />
            </div>
            <button @click="calculateOptimization" class="btn btn-purple">
              计算优化策略
            </button>
            <div v-if="optimizationResult" class="result-section">
              <div class="result-box" style="margin-bottom: 1rem;">
                <div class="result-box-label">每日收益估算</div>
                <div class="result-box-value green">¥{{ optimizationResult.dailyProfit.toFixed(2) }}</div>
              </div>
              <div class="space-y-4">
                <div class="result-box">
                  <div class="badge badge-valley" style="margin-bottom: 0.5rem; display: inline-block;">充电时段 (低价)</div>
                  <div class="text-gray" style="font-size: 0.875rem;">
                    <p>建议在以下时段充电:</p>
                    <p style="color: white; margin-top: 0.25rem;">{{ optimizationResult.chargeHours }}</p>
                  </div>
                </div>
                <div class="result-box">
                  <div class="badge badge-peak" style="margin-bottom: 0.5rem; display: inline-block;">放电时段 (高价)</div>
                  <div class="text-gray" style="font-size: 0.875rem;">
                    <p>建议在以下时段放电:</p>
                    <p style="color: white; margin-top: 0.25rem;">{{ optimizationResult.dischargeHours }}</p>
                  </div>
                </div>
                <div class="detail-grid">
                  <div class="detail-item">
                    <span class="text-gray">充电成本</span>
                    <span class="green">¥{{ optimizationResult.chargeCost.toFixed(2) }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="text-gray">放电收益</span>
                    <span class="red">¥{{ optimizationResult.dischargeRevenue.toFixed(2) }}</span>
                  </div>
                </div>
                <div class="detail-item" style="margin-top: 0.5rem;">
                  <span class="text-gray">{{ selectedMonth }}月收益估算</span>
                  <span class="result-box-value yellow" style="font-size: 1.25rem;">¥{{ optimizationResult.monthlyProfit.toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer>
      <p>数据来源: 各省发改委电价文件 | 更新时间: 2026年3月</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'

// Data
const priceData = ref({})
const provinces = ref([])
const years = ref([])
const months = ref([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

// Selections
const selectedProvince = ref('')
const selectedYear = ref('')
const selectedMonth = ref(3)

// Calculator
const calcUsage = ref(1000)
const billResult = ref(null)

// Optimization
const storageCapacity = ref(1000)
const efficiency = ref(85)
const optimizationResult = ref(null)

// Chart ref
const chartRef = ref(null)
let chartInstance = null

// Computed
const currentData = computed(() => {
  if (!priceData.value[selectedProvince.value]) return null
  if (!priceData.value[selectedProvince.value][selectedYear.value]) return null
  return priceData.value[selectedProvince.value][selectedYear.value][selectedMonth.value]
})

const cycles = computed(() => {
  return currentData.value?.cycles || 0
})

const pricePeriods = computed(() => {
  if (!currentData.value) return []
  const data = currentData.value
  const periods = []
  
  // 尖峰
  if (data.peak?.hours?.length) {
    periods.push({
      name: data.peak.name || '尖峰',
      price: data.peak.price || 0,
      hours: data.peak.hours,
      hoursText: formatHours(data.peak.hours),
      badgeClass: 'badge-peak'
    })
  }
  
  // 高峰
  if (data.high?.hours?.length) {
    periods.push({
      name: data.high.name || '高峰',
      price: data.high.price || 0,
      hours: data.high.hours,
      hoursText: formatHours(data.high.hours),
      badgeClass: 'badge-high'
    })
  }
  
  // 平段
  if (data.flat?.hours?.length) {
    periods.push({
      name: data.flat.name || '平段',
      price: data.flat.price || 0,
      hours: data.flat.hours,
      hoursText: formatHours(data.flat.hours),
      badgeClass: 'badge-flat'
    })
  }
  
  // 低谷
  if (data.valley?.hours?.length) {
    periods.push({
      name: data.valley.name || '低谷',
      price: data.valley.price || 0,
      hours: data.valley.hours,
      hoursText: formatHours(data.valley.hours),
      badgeClass: 'badge-valley'
    })
  }
  
  // 深谷
  if (data.deepValley?.hours?.length) {
    periods.push({
      name: data.deepValley.name || '深谷',
      price: data.deepValley.price || 0,
      hours: data.deepValley.hours,
      hoursText: formatHours(data.deepValley.hours),
      badgeClass: 'badge-deep'
    })
  }
  
  return periods
})

// Calculator computed
const calcPeakHours = computed(() => currentData.value?.peak?.hours?.length || 0)
const calcHighHours = computed(() => currentData.value?.high?.hours?.length || 0)
const calcFlatHours = computed(() => currentData.value?.flat?.hours?.length || 0)
const calcValleyHours = computed(() => currentData.value?.valley?.hours?.length || 0)
const calcDeepValleyHours = computed(() => currentData.value?.deepValley?.hours?.length || 0)

// Functions
function formatHours(hours) {
  if (!hours || hours.length === 0) return '-'
  const sorted = [...hours].sort((a, b) => a - b)
  return sorted.map(h => `${h}:00`).join(', ')
}

function loadPriceData() {
  fetch('./prices.json')
    .then(res => res.json())
    .then(data => {
      priceData.value = data
      provinces.value = Object.keys(data)
      if (provinces.value.length > 0) {
        selectedProvince.value = provinces.value[0]
        const firstProvinceYears = Object.keys(data[provinces.value[0]])
        years.value = firstProvinceYears
        if (firstProvinceYears.length > 0) {
          selectedYear.value = firstProvinceYears[firstProvinceYears.length - 1]
        }
      }
    })
    .catch(err => console.error('Failed to load price data:', err))
}

function initChart() {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  updateChart()
}

function updateChart() {
  if (!chartInstance || !currentData.value) return
  
  const data = currentData.value
  const hours = Array.from({ length: 24 }, (_, i) => i)
  const prices = hours.map(hour => {
    if (data.peak?.hours?.includes(hour)) return { value: data.peak.price, name: '尖峰' }
    if (data.high?.hours?.includes(hour)) return { value: data.high.price, name: '高峰' }
    if (data.flat?.hours?.includes(hour)) return { value: data.flat.price, name: '平段' }
    if (data.valley?.hours?.includes(hour)) return { value: data.valley.price, name: '低谷' }
    if (data.deepValley?.hours?.includes(hour)) return { value: data.deepValley.price, name: '深谷' }
    return { value: 0, name: '-' }
  })
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1e293b',
      borderColor: '#475569',
      textStyle: { color: '#f1f5f9' },
      formatter: (params) => {
        const p = params[0]
        return `${p.name}:00<br/>电价: ¥${p.value.toFixed(4)}/kWh`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: hours.map(h => `${h}:00`),
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#94a3b8', interval: 2 },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '电价(元/kWh)',
      nameTextStyle: { color: '#94a3b8' },
      axisLine: { show: false },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#334155', type: 'dashed' } }
    },
    series: [{
      data: prices.map(p => ({
        value: p.value,
        itemStyle: {
          color: p.name === '尖峰' ? '#ef4444' :
                 p.name === '高峰' ? '#f97316' :
                 p.name === '平段' ? '#94a3b8' :
                 p.name === '低谷' ? '#22c55e' :
                 p.name === '深谷' ? '#a855f7' : '#475569'
        }
      })),
      type: 'bar',
      barWidth: '60%'
    }]
  }
  
  chartInstance.setOption(option)
}

function calculateBill() {
  if (!calcUsage.value || !currentData.value) return
  
  const data = currentData.value
  const totalHours = 24
  const usagePerHour = calcUsage.value / totalHours
  
  const peakHours = data.peak?.hours?.length || 0
  const highHours = data.high?.hours?.length || 0
  const flatHours = data.flat?.hours?.length || 0
  const valleyHours = data.valley?.hours?.length || 0
  const deepValleyHours = data.deepValley?.hours?.length || 0
  
  const peakCost = (data.peak?.price || 0) * usagePerHour * peakHours
  const highCost = (data.high?.price || 0) * usagePerHour * highHours
  const flatCost = (data.flat?.price || 0) * usagePerHour * flatHours
  const valleyCost = (data.valley?.price || 0) * usagePerHour * valleyHours
  const deepValleyCost = (data.deepValley?.price || 0) * usagePerHour * deepValleyHours
  
  const total = peakCost + highCost + flatCost + valleyCost + deepValleyCost
  
  billResult.value = {
    total,
    avgPrice: calcUsage.value > 0 ? total / calcUsage.value : 0,
    peak: peakCost,
    high: highCost,
    flat: flatCost,
    valley: valleyCost,
    deepValley: deepValleyCost
  }
}

function calculateOptimization() {
  if (!storageCapacity.value || !currentData.value) return
  
  const data = currentData.value
  
  // Find best charge hours (lowest price)
  const chargePrices = []
  const dischargePrices = []
  
  for (let h = 0; h < 24; h++) {
    let price = 0
    let name = ''
    if (data.deepValley?.hours?.includes(h)) {
      price = data.deepValley.price
      name = '深谷'
    } else if (data.valley?.hours?.includes(h)) {
      price = data.valley.price
      name = '低谷'
    } else if (data.flat?.hours?.includes(h)) {
      price = data.flat.price
      name = '平段'
    } else if (data.high?.hours?.includes(h)) {
      price = data.high.price
      name = '高峰'
    } else if (data.peak?.hours?.includes(h)) {
      price = data.peak.price
      name = '尖峰'
    }
    
    if (price > 0) {
      chargePrices.push({ hour: h, price, name })
    }
  }
  
  for (let h = 0; h < 24; h++) {
    let price = 0
    let name = ''
    if (data.peak?.hours?.includes(h)) {
      price = data.peak.price
      name = '尖峰'
    } else if (data.high?.hours?.includes(h)) {
      price = data.high.price
      name = '高峰'
    } else if (data.flat?.hours?.includes(h)) {
      price = data.flat.price
      name = '平段'
    } else if (data.valley?.hours?.includes(h)) {
      price = data.valley.price
      name = '低谷'
    } else if (data.deepValley?.hours?.includes(h)) {
      price = data.deepValley.price
      name = '深谷'
    }
    
    if (price > 0) {
      dischargePrices.push({ hour: h, price, name })
    }
  }
  
  // Get top 6 discharge hours (highest price)
  dischargePrices.sort((a, b) => b.price - a.price)
  const bestDischarge = dischargePrices.slice(0, 6)
  
  // Get bottom 6 charge hours (lowest price)
  chargePrices.sort((a, b) => a.price - b.price)
  const bestCharge = chargePrices.slice(0, 6)
  
  const eff = efficiency.value / 100
  const capacity = storageCapacity.value
  
  // Calculate daily profit
  const chargeCost = bestCharge.reduce((sum, p) => sum + p.price * capacity / 6, 0)
  const dischargeRevenue = bestDischarge.reduce((sum, p) => sum + p.price * capacity / 6 * eff, 0)
  const dailyProfit = dischargeRevenue - chargeCost
  
  // Get month days
  const monthDays = new Date(selectedYear.value, selectedMonth.value, 0).getDate()
  const monthlyProfit = dailyProfit * monthDays
  
  optimizationResult.value = {
    dailyProfit,
    monthlyProfit,
    chargeHours: bestCharge.map(p => `${p.hour}:00`).join(', '),
    dischargeHours: bestDischarge.map(p => `${p.hour}:00`).join(', '),
    chargeCost,
    dischargeRevenue
  }
}

// Watchers
watch([selectedProvince], () => {
  if (selectedProvince.value && priceData.value[selectedProvince.value]) {
    years.value = Object.keys(priceData.value[selectedProvince.value])
    if (years.value.length > 0) {
      selectedYear.value = years.value[years.value.length - 1]
    }
  }
  billResult.value = null
  optimizationResult.value = null
})

watch([selectedYear], () => {
  billResult.value = null
  optimizationResult.value = null
})

watch([selectedMonth], () => {
  billResult.value = null
  optimizationResult.value = null
})

watch(currentData, () => {
  nextTick(() => {
    initChart()
  })
})

onMounted(() => {
  loadPriceData()
  window.addEventListener('resize', () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  })
})
</script>

<style>
.app-container {
  min-height: 100vh;
  background-color: var(--bg-primary);
}

.left-column, .right-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.text-gray {
  color: var(--text-secondary);
}

.icon-blue {
  color: var(--accent-blue);
}

.icon-green {
  color: var(--accent-green);
}

.icon-yellow {
  color: var(--accent-yellow);
}

.icon-purple {
  color: var(--accent-purple);
}
</style>
