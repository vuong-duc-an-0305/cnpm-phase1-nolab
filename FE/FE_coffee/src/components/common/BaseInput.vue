<template>
  <div class="space-y-1">
    <label v-if="label" :for="inputId" class="block text-sm font-medium text-coffee-700">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    
    <div class="relative">
      <component
        v-if="leftIcon"
        :is="leftIcon"
        class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-coffee-400"
      />
      
      <input
        :id="inputId"
        v-model="inputValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      />
      
      <component
        v-if="rightIcon"
        :is="rightIcon"
        class="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-coffee-400"
      />
    </div>
    
    <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
    <p v-if="helpText && !error" class="text-sm text-coffee-500">{{ helpText }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

interface Props {
  modelValue: string | number
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url'
  label?: string
  placeholder?: string
  disabled?: boolean
  required?: boolean
  error?: string
  helpText?: string
  leftIcon?: any
  rightIcon?: any
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  required: false,
  size: 'md'
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
  input: [event: Event]
}>()

const inputId = ref(`input-${Math.random().toString(36).substr(2, 9)}`)
const inputValue = ref(props.modelValue)

watch(() => props.modelValue, (newValue) => {
  inputValue.value = newValue
})

const inputClasses = computed(() => {
  const baseClasses = 'w-full border rounded-xl focus:outline-none focus:ring-2 focus:ring-coffee-500 focus:border-transparent transition-all duration-200'
  
  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-3 text-sm',
    lg: 'px-6 py-4 text-base'
  }
  
  const stateClasses = props.error 
    ? 'border-red-300 bg-red-50' 
    : 'border-coffee-200 bg-coffee-50 hover:border-coffee-300'
  
  const disabledClasses = props.disabled ? 'opacity-50 cursor-not-allowed' : ''
  const iconClasses = props.leftIcon ? 'pl-10' : ''
  const rightIconClasses = props.rightIcon ? 'pr-10' : ''
  
  return [
    baseClasses,
    sizeClasses[props.size],
    stateClasses,
    disabledClasses,
    iconClasses,
    rightIconClasses
  ].join(' ')
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  inputValue.value = props.type === 'number' ? Number(target.value) : target.value
  emit('update:modelValue', inputValue.value)
  emit('input', event)
}

const handleBlur = (event: FocusEvent) => {
  emit('blur', event)
}

const handleFocus = (event: FocusEvent) => {
  emit('focus', event)
}
</script>
