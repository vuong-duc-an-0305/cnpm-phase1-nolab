<template>
  <div class="card p-6 hover:scale-105 transition-all duration-300">
    <div class="flex items-start justify-between mb-4">
      <div :class="iconBgClasses" class="p-3 rounded-xl shadow-lg">
        <component :is="icon" class="w-6 h-6 text-white" />
      </div>
      <div v-if="change !== undefined" :class="changeClasses" class="flex items-center gap-1 text-sm font-semibold px-2 py-1 rounded-lg">
        <component :is="changeIcon" class="w-4 h-4" />
        <span>{{ changeText }}</span>
      </div>
    </div>
    
    <h3 class="text-coffee-600 text-sm mb-1 font-medium">{{ title }}</h3>
    <p class="text-2xl font-bold text-coffee-700 mb-2">{{ formattedValue }}</p>
    
    <div v-if="subtitle" class="text-xs text-coffee-500">{{ subtitle }}</div>
    
    <!-- Progress bar for percentage values -->
    <div v-if="showProgress && progressValue !== undefined" class="mt-3">
      <div class="flex justify-between text-xs text-coffee-600 mb-1">
        <span>{{ progressLabel }}</span>
        <span>{{ progressValue }}%</span>
      </div>
      <div class="w-full bg-coffee-200 h-2 rounded-full overflow-hidden">
        <div 
          :class="progressColorClasses"
          class="h-full transition-all duration-500 ease-out"
          :style="{ width: `${Math.min(progressValue, 100)}%` }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent } from 'vue'

interface Props {
  title: string
  value: string | number
  subtitle?: string
  icon: any
  change?: number
  changeType?: 'increase' | 'decrease' | 'neutral'
  color?: 'blue' | 'green' | 'purple' | 'orange' | 'red' | 'yellow'
  showProgress?: boolean
  progressValue?: number
  progressLabel?: string
  format?: 'number' | 'currency' | 'percentage'
}

const props = withDefaults(defineProps<Props>(), {
  changeType: 'neutral',
  color: 'blue',
  showProgress: false,
  format: 'number'
})

const iconBgClasses = computed(() => {
  const colorMap = {
    blue: 'bg-gradient-to-br from-blue-500 to-blue-600',
    green: 'bg-gradient-to-br from-green-500 to-green-600',
    purple: 'bg-gradient-to-br from-purple-500 to-purple-600',
    orange: 'bg-gradient-to-br from-orange-500 to-orange-600',
    red: 'bg-gradient-to-br from-red-500 to-red-600',
    yellow: 'bg-gradient-to-br from-yellow-500 to-yellow-600'
  }
  return colorMap[props.color]
})

const changeClasses = computed(() => {
  if (props.changeType === 'increase') {
    return 'bg-green-50 text-green-600'
  } else if (props.changeType === 'decrease') {
    return 'bg-red-50 text-red-600'
  }
  return 'bg-coffee-50 text-coffee-600'
})

const changeIcon = computed(() => {
  if (props.changeType === 'increase') {
    return 'ArrowUp'
  } else if (props.changeType === 'decrease') {
    return 'ArrowDown'
  }
  return 'Minus'
})

const changeText = computed(() => {
  if (props.change === undefined) return ''
  const sign = props.change > 0 ? '+' : ''
  return `${sign}${props.change}%`
})

const formattedValue = computed(() => {
  if (props.format === 'currency') {
    return typeof props.value === 'number' 
      ? props.value.toLocaleString('vi-VN', { style: 'currency', currency: 'VND' })
      : props.value
  } else if (props.format === 'percentage') {
    return `${props.value}%`
  } else if (props.format === 'number') {
    return typeof props.value === 'number' 
      ? props.value.toLocaleString('vi-VN')
      : props.value
  }
  return props.value
})

const progressColorClasses = computed(() => {
  if (props.progressValue === undefined) return 'bg-coffee-500'
  
  if (props.progressValue >= 80) return 'bg-green-500'
  if (props.progressValue >= 60) return 'bg-yellow-500'
  if (props.progressValue >= 40) return 'bg-orange-500'
  return 'bg-red-500'
})
</script>
