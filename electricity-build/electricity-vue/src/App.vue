<script setup>
/**
 * 分时电价查询系统 - 主应用组件
 * 功能：省份选择、电价展示、时段分析
 */
import { ref, computed, onMounted } from 'vue'
import { usePriceStore } from './stores/priceStore'
import ProvinceSelector from './components/ProvinceSelector.vue'
import PriceChart from './components/PriceChart.vue'
import TimeTable from './components/TimeTable.vue'
import CycleInfo from './components/CycleInfo.vue'

// 状态管理
const priceStore = usePriceStore()

// 本地状态
const selectedYear = ref(2026)
const selectedMonth = ref(2)
const loading = ref(false)

// 计算属性：当前电价数据
const currentPriceData = computed(() => {
  return priceStore.getPriceData(
    priceStore.selectedProvince,
    selectedYear.value,
    selectedMonth.value
  )
})

// 计算属性：24小时时段安排
const hourlySchedule = computed(() => {
  if (!currentPriceData.value) return []
  return priceStore.getHourlySchedule(currentPriceData.value)
})

// 月份选项
const months = [
  { value: 1, label: '1月' },
  { value: 2, label: '2月' },
  { value: 3, label: '3月' },
  { value: 4, label: '4月' },
  { value: 5, label: '5月' },
  { value: 6, label: '6月' },
  { value: 7, label: '7月' },
  { value: 8, label: '8月' },
  { value: 9, label: '9月' },
  { value: 10, label: '10月' },
  { value: 11, label: '11月' },
  { value: 12, label: '12月' }
]

// 初始化
onMounted(() => {
  priceStore.initProvinces()
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white">
    <!-- 头部 -->
    <header class="bg-slate-800/50 backdrop-blur-lg border-b border-white/10">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          分时电价查询系统
        </h1>
        <p class="text-slate-400 mt-2">全国31省份工商业分时电价数据查询</p>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="max-w-7xl mx-auto px-4 py-8">
      <!-- 控制面板 -->
      <div class="glass-card mb-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- 省份选择 -->
          <ProvinceSelector v-model="priceStore.selectedProvince" /&gt;

          <!-- 年份选择 -->
          <div>
            <label class="block text-sm text-slate-400 mb-2">年份</label>
            <select v-model="selectedYear" class="input-field">
              <option :value="2026">2026年</option>
            </select>
          </div>

          <!-- 月份选择 -->
          <div>
            <label class="block text-sm text-slate-400 mb-2">月份</label>
            <select v-model="selectedMonth" class="input-field">
              <option v-for="m in months" :key="m.value" :value="m.value">
                {{ m.label }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
        <p class="text-slate-400 mt-4">加载中...</p>
      </div>

      <!-- 数据展示 -->
      <template v-else-if="currentPriceData">
        <!-- 电价概览卡片 -->
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <div v-for="(period, key) in {
            deepValley: { name: '深谷', color: 'from-emerald-500 to-teal-500' },
            valley: { name: '低谷', color: 'from-blue-500 to-cyan-500' },
            flat: { name: '平段', color: 'from-slate-500 to-gray-500' },
            high: { name: '高峰', color: 'from-orange-500 to-amber-500' },
            peak: { name: '尖峰', color: 'from-red-500 to-rose-500' }
          }" :key="key"
               class="price-card">
            <div :class="`bg-gradient-to-br ${period.color} rounded-lg p-4 text-center`">
              <div class="text-sm opacity-90">{{ period.name }}</div>
              <div class="text-2xl font-bold mt-1">
                {{ currentPriceData[key]?.price?.toFixed(4) || '--' }}
              </div>
              <div class="text-xs opacity-75 mt-1">元/kWh</div>
            </div>
          </div>
        </div>

        <!-- 循环次数信息 -->
        <CycleInfo :cycles="currentPriceData.cycles" /&gt;

        <!-- 24小时电价图表 -->
        <PriceChart :schedule="hourlySchedule" /&gt;

        <!-- 时段明细表 -->
        <TimeTable :schedule="hourlySchedule" /&gt;
      </template>

      <!-- 无数据 -->
      <div v-else class="text-center py-12 text-slate-400">
        <p>请选择省份查看电价数据</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.glass-card {
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 24px;
}

.input-field {
  width: 100%;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 8px;
  padding: 10px 14px;
  color: white;
  transition: all 0.3s;
}

.input-field:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.price-card {
  transition: transform 0.3s;
}

.price-card:hover {
  transform: translateY(-4px);
}
</style>
