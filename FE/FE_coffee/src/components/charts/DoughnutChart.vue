<template>
  <div class="relative h-full w-full">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import type { ChartData, ChartOptions } from 'chart.js'

interface Props {
  data: ChartData<'doughnut'>
  options?: ChartOptions<'doughnut'>
}

const props = withDefaults(defineProps<Props>(), {
  options: () => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    cutout: '60%'
  })
})

const chartRef = ref<HTMLCanvasElement>()
let chart: Chart<'doughnut'> | null = null

const createChart = async () => {
  if (!chartRef.value) return

  await nextTick()

  if (chart) {
    chart.destroy()
  }

  chart = new Chart(chartRef.value, {
    type: 'doughnut',
    data: props.data,
    options: props.options
  })
}

const updateChart = () => {
  if (chart) {
    chart.data = props.data
    chart.update()
  }
}

watch(() => props.data, updateChart, { deep: true })

onMounted(() => {
  createChart()
})

onUnmounted(() => {
  if (chart) {
    chart.destroy()
  }
})
</script>
