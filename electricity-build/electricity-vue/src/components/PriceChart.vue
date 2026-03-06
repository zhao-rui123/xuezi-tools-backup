<script setup>
/**
 * 电价图表组件
 * 使用Chart.js展示24小时电价曲线
 */
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  /** 24小时时段安排 */
  schedule: {
    type: Array,
    required: true
  }
})

// 图表数据
const chartData = computed(() => ({
  labels: props.schedule.map(s => `${s.hour}:00`),
  datasets: [{
    label: '电价 (元/kWh)',
    data: props.schedule.map(s => s.price),
    borderColor: '#6366f1',
    backgroundColor: 'rgba(99, 102, 241, 0.1)',
    borderWidth: 2,
    fill: true,
    tension: 0.4,
    pointRadius: 4,
    pointBackgroundColor: props.schedule.map(s => {
      // 根据时段类型设置不同颜色
      const colors = {
        deepValley: '#10b981',
        valley: '#3b82f6',
        flat: '#6b7280',
        high: '#f59e0b',
        peak: '#ef4444'
      }
      return colors[s.period] || '#6366f1'
    })
  }]
}))

// 图表选项
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          const hour = props.schedule[context.dataIndex]
          return `${hour.periodName}: ${context.parsed.y.toFixed(4)} 元/kWh`
        }
      }
    }
  },
  scales: {
    x: {
      grid: {
        color: 'rgba(255, 255, 255, 0.05)'
      },
      ticks: {
        color: '#94a3b8'
      }
    },
    y: {
      grid: {
        color: 'rgba(255, 255, 255, 0.05)'
      },
      ticks: {
        color: '#94a3b8',
        callback: (value) => value.toFixed(2)
      },
      title: {
        display: true,
        text: '电价 (元/kWh)',
        color: '#94a3b8'
      }
    }
  }
}
</script>

<template>
  <div class="glass-card mb-8">
    <h3 class="text-lg font-semibold mb-4">24小时电价曲线</h3>
    <div class="h-80">
      <Line :data="chartData" :options="chartOptions" />
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
