<script setup>
/**
 * 省份选择器组件
 * 功能：下拉选择省份
 */
import { usePriceStore } from '../stores/priceStore'

const priceStore = usePriceStore()

// v-model绑定
const modelValue = defineModel()
</script>

<template>
  <div>
    <label class="block text-sm text-slate-400 mb-2">选择省份</label>
    <select 
      v-model="modelValue"
      class="input-field"
    >
      <option value="" disabled>请选择省份</option>
      <option 
        v-for="province in priceStore.getProvincesList" 
        :key="province"
        :value="province"
      >
        {{ province }}
      </option>
    </select>
  </div>
</template>

<style scoped>
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
</style>
