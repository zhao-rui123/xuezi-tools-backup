<script setup>
/**
 * 循环次数信息组件
 * 显示该省份的日循环次数（1次或2次）
 */
const props = defineProps({
  /** 循环次数 */
  cycles: {
    type: Number,
    default: 1
  }
})
</script>

<template>
  <div class="glass-card mb-8">
    <div class="flex items-center gap-4">
      <div class="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
        <span class="text-xl font-bold">{{ cycles }}</span>
      </div>
      <div>
        <div class="text-lg font-semibold">日循环次数</div>
        <div class="text-sm text-slate-400">
          {{ cycles === 2 ? '两充两放模式' : '一充一放模式' }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.glass-card {
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
}
</style>
