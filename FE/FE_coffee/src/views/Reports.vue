<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-coffee-800">Báo cáo doanh thu</h2>
        <p class="text-coffee-600 mt-1">Phân tích chi tiết hiệu quả kinh doanh</p>
      </div>
      <div class="flex gap-3">
        <select 
          v-model="selectedPeriod"
          class="px-4 py-2 bg-white border border-coffee-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-coffee-500"
        >
          <option value="today">Hôm nay</option>
          <option value="week">Tuần này</option>
          <option value="month">Tháng này</option>
          <option value="year">Năm nay</option>
        </select>
        <button class="btn-secondary inline-flex items-center" @click="openExportModal"><Download class="w-4 h-4 mr-2" />Xuất báo cáo</button>
      </div>
    </div>

    <!-- Revenue Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="card p-6"><h3 class="text-coffee-600 text-sm mb-1 font-medium">Tổng doanh thu</h3><p class="text-2xl font-bold text-coffee-700">{{ formatCurrency(revenueStats.total_revenue) }}</p></div>
      <div class="card p-6"><h3 class="text-coffee-600 text-sm mb-1 font-medium">Đơn hàng</h3><p class="text-2xl font-bold text-coffee-700">{{ revenueStats.total_orders }}</p></div>
      <div class="card p-6"><h3 class="text-coffee-600 text-sm mb-1 font-medium">Giá trị TB</h3><p class="text-2xl font-bold text-coffee-700">{{ formatCurrency(revenueStats.average_order_value) }}</p></div>
      <div class="card p-6"><h3 class="text-coffee-600 text-sm mb-1 font-medium">Lợi nhuận</h3><p class="text-2xl font-bold text-coffee-700">—</p></div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Revenue Chart -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-bold text-coffee-800">Doanh thu theo thời gian</h3>
          <select 
            v-model="chartPeriod"
            class="px-3 py-1 bg-coffee-50 border border-coffee-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coffee-500"
          >
            <option value="7">7 ngày</option>
            <option value="30">30 ngày</option>
            <option value="90">90 ngày</option>
          </select>
        </div>
        <div class="h-80">
          <LineChart
            v-if="chartData && chartData.labels.length > 0"
            :data="chartData"
            :options="chartOptions"
          />
          <div v-else class="flex items-center justify-center h-full text-coffee-500">
            <div class="text-center">
              <TrendingUp class="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p class="text-sm">Không có dữ liệu doanh thu trong khoảng thời gian này</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Category Distribution -->
      <div class="card p-6">
        <h3 class="text-lg font-bold text-coffee-800 mb-6">Doanh thu theo danh mục</h3>
        <div class="h-80">
          <DoughnutChart
            v-if="categoryData && categoryData.labels.length > 0"
            :data="categoryData"
            :options="doughnutOptions"
          />
          <div v-else class="flex items-center justify-center h-full text-coffee-500">
            <div class="text-center">
              <Activity class="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p class="text-sm">Không có dữ liệu doanh thu theo danh mục</p>
            </div>
          </div>
        </div>
        <div v-if="categoryData && categoryData.labels.length > 0" class="space-y-2 mt-4">
          <div
            v-for="(item, index) in categoryData.datasets[0].data"
            :key="index"
            class="flex items-center justify-between"
          >
            <div class="flex items-center gap-2">
              <div 
                class="w-3 h-3 rounded-full"
                :style="{ backgroundColor: categoryData.datasets[0].backgroundColor[index] }"
              ></div>
              <span class="text-sm text-coffee-600">{{ categoryData.labels[index] }}</span>
            </div>
            <span class="text-sm font-semibold text-coffee-800">{{ formatCurrency(item) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Best Selling Products -->
    <div class="card p-6">
      <h3 class="text-lg font-bold text-coffee-800 mb-6">Top sản phẩm bán chạy</h3>
      <div class="space-y-3">
        <div
          v-for="(product, index) in bestSellingProducts"
          :key="index"
          class="flex items-center justify-between p-4 bg-coffee-50 rounded-xl hover:bg-coffee-100 transition-colors"
        >
          <div class="flex items-center gap-3">
            <div :class="getRankClasses(index)" class="w-10 h-10 rounded-lg flex items-center justify-center font-bold text-white">
              {{ index + 1 }}
            </div>
            <div>
              <p class="font-semibold text-coffee-800">{{ product.name }}</p>
              <p class="text-sm text-coffee-600">Đã bán: {{ product.sold }}</p>
            </div>
          </div>
          <div class="text-right">
            <p class="font-bold text-green-600">{{ formatCurrency(product.revenue) }}</p>
            <span :class="product.trend === 'up' ? 'text-green-600' : 'text-red-600'" class="text-xs flex items-center gap-1">
              <component :is="product.trend === 'up' ? ArrowUp : ArrowDown" class="w-3 h-3" />
              {{ product.trend === 'up' ? 'Tăng' : 'Giảm' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Coming Soon Notice -->
    <div class="card p-6 bg-gradient-to-r from-coffee-100 to-coffee-200">
      <div class="text-center">
        <TrendingUp class="w-16 h-16 text-coffee-500 mx-auto mb-4" />
        <h3 class="text-xl font-bold text-coffee-800 mb-2">Nhiều báo cáo hơn đang được phát triển</h3>
        <p class="text-coffee-600 mb-4">
          Chúng tôi đang làm việc để mang đến cho bạn nhiều loại báo cáo chi tiết hơn
        </p>
        <div class="flex flex-wrap justify-center gap-2">
          <span class="px-3 py-1 bg-white rounded-lg text-sm text-coffee-700">Báo cáo khách hàng</span>
          <span class="px-3 py-1 bg-white rounded-lg text-sm text-coffee-700">Báo cáo nhân viên</span>
          <span class="px-3 py-1 bg-white rounded-lg text-sm text-coffee-700">Báo cáo kho</span>
          <span class="px-3 py-1 bg-white rounded-lg text-sm text-coffee-700">So sánh theo kỳ</span>
        </div>
      </div>
    </div>

    <!-- Export modal -->
    <div v-if="showExport" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-coffee-800 mb-4">Xuất báo cáo</h3>
        <label class="block text-sm text-coffee-600 mb-1">Chọn khoảng thời gian</label>
        <select
          v-model="exportPeriod"
          class="w-full px-3 py-2 bg-white border border-coffee-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-coffee-500"
        >
          <option value="today">Hôm nay</option>
          <option value="week">Tuần này</option>
          <option value="month">Tháng này</option>
          <option value="year">Năm nay</option>
        </select>
        <div class="flex justify-end gap-3 mt-4">
          <button class="btn-secondary" @click="closeExportModal">Hủy</button>
          <button class="btn-primary" @click="() => { closeExportModal(); exportExcel(); }">Xuất</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useToast } from 'vue-toastification'
import {
  DollarSign,
  ShoppingCart,
  TrendingUp,
  Activity,
  Download,
  ArrowUp,
  ArrowDown
} from 'lucide-vue-next'
import { defineAsyncComponent } from 'vue'
const LineChart = defineAsyncComponent(() => import('../components/charts/LineChart.vue'))
const DoughnutChart = defineAsyncComponent(() => import('../components/charts/DoughnutChart.vue'))
// Types are available via chart.js runtime; fallback to any to avoid TS error if missing types
type CJChartData<TType extends string> = any

const toast = useToast()
const selectedPeriod = ref('month')
const exportPeriod = ref('month')
const chartPeriod = ref('7')

// Helpers to build date range
function formatDate(d: Date) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function getRange(period: string) {
  const to = new Date()
  const from = new Date()
  if (period === 'today') {
    // no change
  } else if (period === 'week') {
    from.setDate(to.getDate() - 6)
  } else if (period === 'month') {
    from.setMonth(to.getMonth() - 1)
  } else if (period === 'year') {
    from.setFullYear(to.getFullYear() - 1)
  }
  return { from_date: formatDate(from), to_date: formatDate(to) }
}

const revenueStats = ref({
  total_revenue: '0',
  total_orders: 0,
  average_order_value: '0',
})

const bestSellingProducts = ref<Array<{ name: string; sold: number; revenue: number; trend: 'up'|'down' }>>([])

// Chart data (runtime) - Khởi tạo với dữ liệu rỗng, sẽ được load từ API
const chartData = ref<CJChartData<'line'>>({
  labels: [],
  datasets: [
    {
      label: 'Doanh thu',
      data: [],
      borderColor: '#D4AF37',
      backgroundColor: 'rgba(212, 175, 55, 0.1)',
      borderWidth: 3,
      fill: true,
      tension: 0.4
    }
  ]
})

const categoryData = ref<CJChartData<'doughnut'>>({ 
  labels: [], 
  datasets: [{ 
    label: 'Doanh thu theo danh mục', 
    data: [], 
    backgroundColor: ['#8B4513','#D2691E','#F4A460','#DEB887','#C4A484','#A0522D','#CD853F','#D2B48C','#BC9A6A','#8B7355'] 
  }] 
})

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: '#e2e8f0'
      },
      ticks: {
        color: '#64748b'
      }
    },
    x: {
      grid: {
        color: '#e2e8f0'
      },
      ticks: {
        color: '#64748b'
      }
    }
  }
})

const doughnutOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  cutout: '60%'
})

const formatCurrency = (value: string | number): string => {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND'
  }).format(Number(value))
}

const getRankClasses = (index: number): string => {
  if (index === 0) return 'bg-coffee-500'
  if (index === 1) return 'bg-gray-400'
  if (index === 2) return 'bg-orange-500'
  return 'bg-gray-300'
}

import { orderService } from '../services/orders'
import { apiService } from '../services/api'

async function loadAll() {
  const { from_date, to_date } = getRange(selectedPeriod.value)

  // Stats
  try {
    const stats = await orderService.getRevenueStats(from_date, to_date)
    const sum = (stats as any)?.summary || {}
    revenueStats.value = {
      total_revenue: String(sum.total_revenue || '0'),
      total_orders: Number(sum.total_orders || 0),
      average_order_value: String(sum.average_order_value || '0'),
    }
  } catch (err: any) {
    // eslint-disable-next-line no-console
    console.error('Revenue stats error:', err?.response?.data || err)
    toast.error('Không tải được tổng quan doanh thu')
  }

  // Trend
  try {
    const trend = await orderService.getRevenueTrend(from_date, to_date, 'day')
    const trendData = (trend as any)?.datasets?.[0]?.data || []
    const trendLabels = (trend as any)?.labels || []
    
    chartData.value = {
      labels: trendLabels,
      datasets: [
        {
          label: 'Doanh thu',
          data: trendData,
          borderColor: '#D4AF37',
          backgroundColor: 'rgba(212, 175, 55, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4
        }
      ]
    }
  } catch (err: any) {
    // eslint-disable-next-line no-console
    console.error('Revenue trend error:', err?.response?.data || err)
    toast.warning('Không tải được biểu đồ doanh thu theo thời gian')
    // Reset về dữ liệu rỗng
    chartData.value = {
      labels: [],
      datasets: [
        {
          label: 'Doanh thu',
          data: [],
          borderColor: '#D4AF37',
          backgroundColor: 'rgba(212, 175, 55, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4
        }
      ]
    }
  }

  // By Category (tùy chọn)
  try {
    const byCat = await orderService.getRevenueByCategory(from_date, to_date)
    const catLabels = (byCat as any)?.labels || []
    const catData = ((byCat as any)?.datasets?.[0]?.data) || []
    
    // Tạo màu sắc động dựa trên số lượng danh mục
    const colors = ['#8B4513','#D2691E','#F4A460','#DEB887','#C4A484','#A0522D','#CD853F','#D2B48C','#BC9A6A','#8B7355']
    const backgroundColor = catLabels.map((_: any, index: number) => colors[index % colors.length])
    
    categoryData.value = {
      labels: catLabels,
      datasets: [
        {
          label: 'Doanh thu theo danh mục',
          data: catData,
          backgroundColor: backgroundColor,
          borderWidth: 0,
        },
      ],
    }
  } catch (err: any) {
    // eslint-disable-next-line no-console
    console.error('Revenue by category error:', err?.response?.data || err)
    // Không chặn trang: để rỗng và hiển thị phần còn lại
    categoryData.value = { 
      labels: [], 
      datasets: [{ 
        label: 'Doanh thu theo danh mục', 
        data: [], 
        backgroundColor: ['#8B4513','#D2691E','#F4A460','#DEB887','#C4A484','#A0522D','#CD853F','#D2B48C','#BC9A6A','#8B7355'], 
        borderWidth: 0 
      }] 
    }
  }

  // Best selling (tùy chọn)
  try {
    const best = await orderService.getBestSelling(from_date, to_date, 5)
    const list = (best as any)?.best_selling_products || []
    bestSellingProducts.value = list.map((x: any) => ({
      name: x.ProductID__ProductName || `SP #${x.ProductID}`,
      sold: Number(x.total_quantity || 0),
      revenue: Number(x.total_revenue || 0),
      trend: 'up',
    }))
  } catch (err: any) {
    // eslint-disable-next-line no-console
    console.error('Best selling error:', err?.response?.data || err)
    bestSellingProducts.value = []
  }
}

// Watch for period changes to reload data
watch([selectedPeriod, chartPeriod], () => {
  loadAll()
}, { deep: true })

onMounted(() => {
  loadAll()
  const handler = () => loadAll()
  window.addEventListener('reports:refresh', handler)
  ;(window as any).__reportsRefreshHandler = handler
})

onBeforeUnmount(() => {
  const handler = (window as any).__reportsRefreshHandler
  if (handler) window.removeEventListener('reports:refresh', handler)
})

async function exportExcel() {
  try {
    const { from_date, to_date } = getRange(exportPeriod.value)
    const blob = await apiService.download('/reports/export.xlsx', { from_date, to_date, type: 'revenue' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `bao_cao_${from_date}_${to_date}.xlsx`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
  } catch (err: any) {
    // eslint-disable-next-line no-console
    console.error('Export excel error:', err?.response?.data || err)
    toast.error('Xuất báo cáo thất bại')
  }
}

// Export modal state
const showExport = ref(false)
function openExportModal() { showExport.value = true }
function closeExportModal() { showExport.value = false }
</script>
