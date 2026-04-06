<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <div v-if="loading" class="spinner mr-2"></div>
    <component
      v-if="icon && !loading"
      :is="icon"
      :class="iconClasses"
    />
    <slot v-if="!loading" />
    <span v-if="loading">{{ loadingText }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  loadingText?: string
  icon?: any
  fullWidth?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  loadingText: 'Đang tải...',
  fullWidth: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClasses = computed(() => {
  const baseClasses = 'inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2'
  
  const variantClasses = {
    primary: 'bg-gradient-to-r from-coffee-600 to-coffee-700 text-white hover:shadow-lg hover:scale-105 focus:ring-coffee-500',
    secondary: 'bg-coffee-100 text-coffee-700 hover:bg-coffee-200 focus:ring-coffee-500',
    outline: 'border-2 border-coffee-600 text-coffee-600 hover:bg-coffee-600 hover:text-white focus:ring-coffee-500',
    ghost: 'text-coffee-600 hover:bg-coffee-100 focus:ring-coffee-500',
    danger: 'bg-red-500 text-white hover:bg-red-600 focus:ring-red-500'
  }
  
  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  }
  
  const disabledClasses = props.disabled || props.loading ? 'opacity-50 cursor-not-allowed' : ''
  const fullWidthClasses = props.fullWidth ? 'w-full' : ''
  
  return [
    baseClasses,
    variantClasses[props.variant],
    sizeClasses[props.size],
    disabledClasses,
    fullWidthClasses
  ].join(' ')
})

const iconClasses = computed(() => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  }
  
  return sizeClasses[props.size]
})
</script>
