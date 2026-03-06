<script setup>
/**
 * 时段明细表组件
 * 展示24小时各时段的详细信息
 */
const props = defineProps({
  /** 24小时时段安排 */
  schedule: {
    type: Array,
    required: true
  }
})

/**
 * 获取时段样式类名
 * @param {string} period - 时段类型
 * @returns {string} CSS类名
 */
function getPeriodClass(period) {
  const classes = {
    deepValley: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    valley: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    flat: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
    high: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    peak: 'bg-red-500/20 text-red-400 border-red-500/30'
  }
  return classes[period] || classes.flat
}

/**
 * 获取建议操作文本
 * @param {string} action - 操作类型
 * @returns {string} 中文文本
 */
function getActionText(action) {
  const texts = {
    charge: '🔋 充电',
    discharge: '⚡ 放电',
    idle: '⏸️ 待机'
  }
  return texts[action] || '待机'
}
</script>

<template>
  <div class="glass-card">
    <h3 class="text-lg font-semibold mb-4">时段明细</h3>
    
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b border-white/10">
            <th class="text-left py-3 px-4 text-slate-400">时间</th>
            <th class="text-left py-3 px-4 text-slate-400">时段类型</th>
            <th class="text-left py-3 px-4 text-slate-400">电价</th>
            <th class="text-left py-3 px-4 text-slate-400">建议操作</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="hour in schedule" 
            :key="hour.hour"
            class="border-b border-white/5 hover:bg-white/5 transition-colors"
          >
            <td class="py-3 px-4">{{ hour.hour }}:00 - {{ hour.hour + 1 }}:00</td>
            <td class="py-3 px-4">
              <span 
                class="px-3 py-1 rounded-full text-sm border"
                :class="getPeriodClass(hour.period)"
              >
                {{ hour.periodName }}
              </span>
            </td>
            <td class="py-3 px-4 font-mono">{{ hour.price.toFixed(4) }}</td>
            <td class="py-3 px-4">{{ getActionText(hour.action) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
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
</style>
