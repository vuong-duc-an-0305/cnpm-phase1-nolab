<template>
  <div class="skeleton-loader animate-pulse">
    <div v-if="type === 'stats-card'" class="space-y-3">
      <div class="h-4 bg-gray-200 rounded w-3/4"></div>
      <div class="h-8 bg-gray-200 rounded w-1/2"></div>
      <div class="h-3 bg-gray-200 rounded w-1/3"></div>
    </div>

    <div v-else-if="type === 'chart'" class="space-y-4">
      <div class="h-6 bg-gray-200 rounded w-1/3"></div>
      <div class="h-64 bg-gray-200 rounded"></div>
    </div>

    <div v-else-if="type === 'table'" class="space-y-3">
      <div class="h-4 bg-gray-200 rounded w-full"></div>
      <div class="h-4 bg-gray-200 rounded w-full"></div>
      <div class="h-4 bg-gray-200 rounded w-5/6"></div>
      <div class="h-4 bg-gray-200 rounded w-4/5"></div>
    </div>

    <div v-else-if="type === 'calendar'" class="space-y-3">
      <div class="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
      <div class="grid grid-cols-7 gap-2">
        <div v-for="i in 35" :key="i" class="h-20 bg-gray-200 rounded"></div>
      </div>
    </div>

    <div v-else class="h-32 bg-gray-200 rounded"></div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  type?: 'stats-card' | 'chart' | 'table' | 'calendar' | 'default'
}

withDefaults(defineProps<Props>(), {
  type: 'default'
})
</script>

<style scoped>
.skeleton-loader {
  @apply w-full;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
