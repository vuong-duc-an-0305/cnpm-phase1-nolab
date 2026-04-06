<template>
  <div class="space-y-8">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <div class="text-center">
        <Loader2 class="w-8 h-8 animate-spin mx-auto mb-4 text-coffee-600" />
        <p class="text-coffee-600">Đang tải dữ liệu...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
      <AlertCircle class="w-8 h-8 text-red-500 mx-auto mb-4" />
      <p class="text-red-600 mb-4">{{ error }}</p>
      <button 
        @click="loadDashboardData"
        class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
      >
        Thử lại
      </button>
    </div>

    <!-- Main Content -->
    <div v-else class="py-6">
      <!-- Welcome Section -->
      <div class="bg-gradient-to-r from-coffee-600 to-coffee-700 rounded-2xl p-6 text-white shadow-xl mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-2xl font-bold mb-2">Chào mừng trở lại, {{ user?.firstName }}! ☕</h2>
            <p class="text-coffee-100">
              Hôm nay có {{ todayStats.total_orders }} đơn hàng mới và doanh thu đạt 
              {{ formatCurrency(todayStats.total_revenue) }}
            </p>
          </div>
          <div class="text-6xl opacity-20">
            ☕
          </div>
        </div>
      </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
      <StatsCard
        title="Doanh thu hôm nay"
        :value="todayStats.total_revenue"
        format="currency"
        :change="todayStats.revenue_growth"
        change-type="increase"
        color="blue"
        :icon="DollarSign"
      />
      <StatsCard
        title="Đơn hàng hôm nay"
        :value="todayStats.total_orders"
        :change="todayStats.orders_growth"
        change-type="increase"
        color="green"
        :icon="ShoppingCart"
      />
      <StatsCard
        title="Tổng số khách hàng"
        :value="todayStats.total_customers"
        :change="todayStats.customers_growth"
        change-type="increase"
        color="purple"
        :icon="Users"
      />
      <StatsCard
        title="Sản phẩm"
        :value="todayStats.total_products"
        :change="todayStats.products_growth"
        change-type="increase"
        color="orange"
        :icon="Package"
      />
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <!-- Revenue Chart -->
      <div class="lg:col-span-2 card p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-bold text-coffee-800">Doanh thu theo thời gian</h3>
          <div class="flex gap-2">
            <button 
              @click="selectedPeriod = 'day'"
              :class="selectedPeriod === 'day' ? 'bg-coffee-600 text-white' : 'bg-coffee-100 text-coffee-700'"
              class="px-3 py-1 rounded-lg text-sm font-medium transition-colors"
            >
              Ngày
            </button>
            <button 
              @click="selectedPeriod = 'week'"
              :class="selectedPeriod === 'week' ? 'bg-coffee-600 text-white' : 'bg-coffee-100 text-coffee-700'"
              class="px-3 py-1 rounded-lg text-sm font-medium transition-colors"
            >
              Tuần
            </button>
            <button 
              @click="selectedPeriod = 'month'"
              :class="selectedPeriod === 'month' ? 'bg-coffee-600 text-white' : 'bg-coffee-100 text-coffee-700'"
              class="px-3 py-1 rounded-lg text-sm font-medium transition-colors"
            >
              Tháng
            </button>
            <button 
              @click="selectedPeriod = 'year'"
              :class="selectedPeriod === 'year' ? 'bg-coffee-600 text-white' : 'bg-coffee-100 text-coffee-700'"
              class="px-3 py-1 rounded-lg text-sm font-medium transition-colors"
            >
              Năm
            </button>
          </div>
        </div>
         <div class="h-80">
           <BarChart :key="`chart-${selectedPeriod}`" :data="chartData" :options="chartOptions" />
         </div>
      </div>

      <!-- Product Sales Chart -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-bold text-coffee-800">Sản phẩm bán chạy</h3>
          <div class="flex gap-2">
            <button 
              @click="selectedProductPeriod = 'day'"
              :class="selectedProductPeriod === 'day' ? 'bg-coffee-600 text-white' : 'bg-coffee-100 text-coffee-700'"
              class="px-3 py-1 rounded-lg text-sm font-medium transition-colors"
            >
              Ngày
            </button>
            <button 
              @click="selectedProductPeriod = 'week'"
              :class="selectedProductPeriod === 'week' ? 'bg-coffee-600 text-white' : 'bg-coffee-100 text-coffee-700'"
              class="px-3 py-1 rounded-lg text-sm font-medium transition-colors"
            >
              Tuần
            </button>
            <button 
              @click="selectedProductPeriod = 'month'"
              :class="selectedProductPeriod === 'month' ? 'bg-coffee-600 text-white' : 'bg-coffee-100 text-coffee-700'"
              class="px-3 py-1 rounded-lg text-sm font-medium transition-colors"
            >
              Tháng
            </button>
            <button 
              @click="selectedProductPeriod = 'year'"
              :class="selectedProductPeriod === 'year' ? 'bg-coffee-600 text-white' : 'bg-coffee-100 text-coffee-700'"
              class="px-3 py-1 rounded-lg text-sm font-medium transition-colors"
            >
              Năm
            </button>
          </div>
        </div>
        <div class="h-80">
          <DoughnutChart :key="`product-chart-${selectedProductPeriod}`" :data="productData" :options="doughnutOptions" />
        </div>
      </div>
    </div>

    <!-- Recent Orders & Alerts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
      <!-- Recent Orders -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-coffee-800">Đơn hàng gần đây</h3>
          <router-link
            to="/orders"
            class="text-sm text-coffee-600 hover:text-coffee-800 transition-colors"
          >
            Xem tất cả
          </router-link>
        </div>
        <div class="space-y-4">
          <div
            v-for="order in recentOrders"
            :key="order.OrderID"
            class="flex items-center justify-between p-4 bg-coffee-50 rounded-xl hover:bg-coffee-100 transition-colors"
          >
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-1">
                <span class="font-semibold text-coffee-800">#{{ order.OrderID }}</span>
                <span :class="getStatusClasses(order.Status)" class="px-2 py-1 text-xs rounded-lg">
                  {{ getStatusText(order.Status) }}
                </span>
              </div>
              <p class="text-sm text-coffee-600">{{ order.customer_name || 'Khách lẻ' }}</p>
              <p class="text-xs text-coffee-400">{{ formatTimeAgo(order.OrderDate) }}</p>
            </div>
            <span class="font-bold text-coffee-800">{{ formatCurrency(order.FinalAmount) }}</span>
          </div>
          <div v-if="recentOrders.length === 0" class="text-center py-8 text-coffee-400">
            <ShoppingCart class="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>Chưa có đơn hàng nào hôm nay</p>
          </div>
        </div>
      </div>

      <!-- Low Stock Alert -->
      <div class="card p-6">
        <h3 class="text-lg font-bold text-coffee-800 mb-4 flex items-center gap-2">
          <AlertCircle class="w-5 h-5 text-red-500" />
          Cảnh báo nguyên liệu
          <span class="text-sm font-normal text-coffee-600">
            ({{ lowStockItems.length }} mục)
          </span>
        </h3>
        <div class="space-y-4">
          <div
            v-for="item in lowStockItems"
            :key="item.IngredientID"
            :class="getStockAlertClasses(item)"
            class="p-4 rounded-xl"
          >
            <div class="flex items-start justify-between mb-2">
              <span class="font-semibold text-coffee-800">{{ item.IngredientName }}</span>
              <span :class="getStockBadgeClasses(item)" class="text-xs px-2 py-1 rounded-lg">
                {{ getStockStatusText(item) }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <div :class="getProgressBarClasses(item)" class="flex-1 h-2 rounded-full overflow-hidden">
                <div 
                  :class="getProgressFillClasses(item)"
                  class="h-full transition-all"
                  :style="{ width: `${getStockPercentage(item)}%` }"
                ></div>
              </div>
              <span class="text-sm text-coffee-600">
                {{ Number(item.QuantityInStock).toFixed(1) }}/{{ Number(item.MinQuantity).toFixed(1) }} {{ item.Unit || 'đơn vị' }}
              </span>
            </div>
          </div>
          <div v-if="lowStockItems.length === 0" class="text-center py-8 text-green-600">
            <Package class="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>Tất cả nguyên liệu đều đủ</p>
            <p class="text-sm text-green-500 mt-1">Không có nguyên liệu nào hết hàng hoặc gần hết</p>
          </div>
          <button 
            v-if="lowStockItems.length > 0"
            @click="$router.push('/inventory')"
            class="w-full py-3 bg-gradient-to-r from-coffee-500 to-coffee-600 text-white rounded-xl font-semibold hover:shadow-lg transition-shadow"
          >
            Nhập kho ngay
          </button>
        </div>
      </div>
    </div>

    <!-- Work Schedule Section -->
    <div class="card p-6 mb-8">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold text-coffee-800">Lịch làm việc</h3>
        <router-link
          to="/attendance"
          class="text-sm text-coffee-600 hover:text-coffee-800 transition-colors"
        >
          Quản lý chấm công
        </router-link>
      </div>
      <WorkScheduleCalendar
        :schedules="workSchedules"
        :employees="employees"
        :loading="loadingSchedules"
        :readonly="true"
        @period-change="handleSchedulePeriodChange"
      />
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onActivated, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  DollarSign,
  ShoppingCart,
  Users,
  Package,
  AlertCircle,
  Loader2
} from 'lucide-vue-next'
// @ts-ignore
import StatsCard from '../components/common/StatsCard.vue'
// @ts-ignore
import BarChart from '../components/charts/BarChart.vue'
// @ts-ignore
import DoughnutChart from '../components/charts/DoughnutChart.vue'
// @ts-ignore
import WorkScheduleCalendar from '../components/attendance/WorkScheduleCalendar.vue'
import { dashboardService } from '../services/dashboard'
import attendanceService from '../services/attendance'
import { userService } from '../services/users'
// import { useWebSocket } from '../services/websocket'  // ❌ Không dùng nữa
import type { DashboardStats, ChartData, Order, Ingredient } from '../types'
import type { ChartOptions } from 'chart.js'

const router = useRouter()
const selectedPeriod = ref<'day' | 'week' | 'month' | 'year'>('day')
const selectedProductPeriod = ref<'day' | 'week' | 'month' | 'year'>('day')

// Loading states
const isLoading = ref(true)
const error = ref<string | null>(null)
const isInitialized = ref(false) // Track if data has been loaded

// ========================================
// WebSocket Setup - VIẾT LẠI TỪ ĐẦU
// ========================================
let ws: WebSocket | null = null
let reconnectTimer: number | null = null
let reconnectAttempts = 0
const MAX_RECONNECT_ATTEMPTS = 5

const connectWebSocketDirect = () => {
  // HARDCODE production IP - ĐƠN GIẢN NHẤT
  const WS_URL = 'ws://16.171.13.43:8000/ws/dashboard/'
  
  console.log('[WebSocket] 🔄 Connecting to:', WS_URL)
  
  try {
    ws = new WebSocket(WS_URL)
    
    ws.onopen = () => {
      console.log('[WebSocket] ✅ Connected successfully!')
      reconnectAttempts = 0
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('[WebSocket] 📨 Received:', data.type)
        handleWebSocketMessage(data)
      } catch (e) {
        console.error('[WebSocket] Failed to parse message:', e)
      }
    }
    
    ws.onerror = (error) => {
      console.error('[WebSocket] ❌ Error:', error)
    }
    
    ws.onclose = () => {
      console.log('[WebSocket] 🔌 Disconnected')
      
      // Auto reconnect
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000)
        reconnectAttempts++
        console.log(`[WebSocket] ⏱️ Reconnecting in ${delay}ms... (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`)
        
        reconnectTimer = window.setTimeout(() => {
          connectWebSocketDirect()
        }, delay)
      }
    }
  } catch (error) {
    console.error('[WebSocket] Failed to create connection:', error)
  }
}

const disconnectWebSocketDirect = () => {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  
  if (ws) {
    ws.close()
    ws = null
  }
  console.log('[WebSocket] 🛑 Disconnected manually')
}

const handleWebSocketMessage = (data: any) => {
  console.log('[Dashboard] WebSocket received:', data.type, data)
  
  switch (data.type) {
    case 'connection_established':
      console.log('✅ Connected to real-time dashboard updates')
      break
      
    case 'stats_update':
      // Update stats real-time
      if (data.data) {
        todayStats.value.total_orders = data.data.total_orders || todayStats.value.total_orders
        todayStats.value.total_revenue = String(data.data.total_revenue || todayStats.value.total_revenue)
        console.log('📊 Dashboard stats updated:', data.data)
      }
      break
      
    case 'order_created':
      // New order notification - prepend to recent orders
      if (data.data) {
        const newOrder: Partial<Order> = {
          OrderID: data.data.order_id,
          CustomerID: { FullName: data.data.customer_name } as any,
          FinalAmount: String(data.data.total_amount),
          Status: data.data.status,
          OrderDate: data.data.order_date,
          EmployeeID: null as any,
          TotalAmount: String(data.data.total_amount),
          Discount: '0',
          PaymentMethod: 'CASH'
        }
        
        recentOrders.value.unshift(newOrder as Order)
        // Keep only top 10
        if (recentOrders.value.length > 10) {
          recentOrders.value = recentOrders.value.slice(0, 10)
        }
        
        console.log('🆕 New order added:', data.data.order_id)
      }
      break
      
    case 'order_updated':
      // Update existing order status
      if (data.data && data.data.order_id) {
        const index = recentOrders.value.findIndex((o: Order) => o.OrderID === data.data.order_id)
        if (index !== -1 && recentOrders.value[index]) {
          recentOrders.value[index]!.Status = data.data.new_status || data.data.status
          console.log('🔄 Order status updated:', data.data.order_id, data.data.new_status)
        }
      }
      break
      
    case 'pong':
      // Heartbeat response - ignore
      break
      
    default:
      console.log('Unknown message type:', data.type)
  }
}

// ❌ REMOVED: const { connect: connectWebSocket, disconnect: disconnectWebSocket } = useWebSocket(wsUrl, handleWebSocketMessage)
// ✅ NOW: Using connectWebSocketDirect() and disconnectWebSocketDirect()

// User data
const user = computed(() => ({
  firstName: 'Admin',
  lastName: 'User'
}))

// Dashboard data
const todayStats = ref<DashboardStats>({
  total_orders: 0,
  total_revenue: '0',
  total_customers: 0,
  total_products: 0,
  revenue_growth: 0,
  orders_growth: 0,
  customers_growth: 0,
  products_growth: 0
})

// Recent orders
const recentOrders = ref<Order[]>([])

// Low stock items
const lowStockItems = ref<Ingredient[]>([])

// Work schedules
const workSchedules = ref<any[]>([])
const employees = ref<any[]>([])
const loadingSchedules = ref(false)

// Chart data
const chartData = ref<ChartData>({
  labels: [],
  datasets: [
    {
      label: 'Doanh thu (₫)',
      data: [],
      backgroundColor: [
        '#D4AF37',
        '#B8860B', 
        '#CD853F',
        '#DAA520',
        '#F4A460',
        '#DEB887',
        '#C4A484'
      ],
      borderColor: '#8B4513',
      borderWidth: 2
    }
  ]
})

const productData = ref<ChartData>({
  labels: [],
  datasets: [
    {
      label: 'Sản phẩm',
      data: [],
      backgroundColor: [
        '#8B4513',
        '#D2691E',
        '#F4A460',
        '#DEB887',
        '#CD853F',
        '#D2B48C',
        '#BC9A6A'
      ],
      borderWidth: 0
    }
  ]
})

const chartOptions = ref<ChartOptions<'bar'>>({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: '#D4AF37',
      borderWidth: 1,
      callbacks: {
        label: function(context: any) {
          const value = context.parsed.y
          return `Doanh thu: ${new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
          }).format(value)}`
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: '#e2e8f0'
      },
      ticks: {
        color: '#64748b',
        callback: function(value: any) {
          return new Intl.NumberFormat('vi-VN', {
            notation: 'compact',
            compactDisplay: 'short'
          }).format(value) + ' ₫'
        }
      }
    },
    x: {
      grid: {
        color: '#e2e8f0'
      },
      ticks: {
        color: '#64748b',
        maxRotation: 45
      }
    }
  }
})

const doughnutOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'bottom' as const,
      labels: {
        usePointStyle: true,
        padding: 20,
        font: {
          size: 12,
          family: 'Inter, sans-serif'
        },
        color: '#64748b'
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: '#D4AF37',
      borderWidth: 1,
      callbacks: {
        label: function(context: any) {
          const label = context.label || ''
          const value = context.parsed
          const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0)
          const percentage = ((value / total) * 100).toFixed(1)
          return `${label}: ${value} (${percentage}%)`
        }
      }
    }
  },
  cutout: '60%'
})

// Methods
const formatCurrency = (value: string | number): string => {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND'
  }).format(Number(value))
}

const getStatusClasses = (status: string): string => {
  const classMap = {
    COMPLETED: 'bg-green-100 text-green-700',
    PREPARING: 'bg-yellow-100 text-yellow-700',
    PENDING: 'bg-blue-100 text-blue-700',
    CANCELLED: 'bg-red-100 text-red-700'
  }
  return classMap[status as keyof typeof classMap] || 'bg-coffee-100 text-coffee-700'
}

const getStatusText = (status: string): string => {
  const textMap = {
    COMPLETED: 'Hoàn thành',
    PREPARING: 'Đang chuẩn bị',
    PENDING: 'Chờ xác nhận',
    CANCELLED: 'Đã hủy'
  }
  return textMap[status as keyof typeof textMap] || status
}

const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 1) return 'Vừa xong'
  if (diffInMinutes < 60) return `${diffInMinutes} phút trước`
  
  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) return `${diffInHours} giờ trước`
  
  const diffInDays = Math.floor(diffInHours / 24)
  return `${diffInDays} ngày trước`
}

// Stock alert methods
const getStockStatusText = (item: Ingredient): string => {
  const quantity = Number(item.QuantityInStock)
  const minQuantity = Number(item.MinQuantity)
  
  if (quantity === 0) return 'Hết hàng'
  if (quantity < minQuantity) return 'Gần hết'
  return 'Sắp hết'
}

const getStockAlertClasses = (item: Ingredient): string => {
  const quantity = Number(item.QuantityInStock)
  const minQuantity = Number(item.MinQuantity)
  
  if (quantity === 0) {
    return 'bg-red-100 border border-red-300'
  } else if (quantity < minQuantity) {
    return 'bg-orange-50 border border-orange-200'
  } else {
    return 'bg-yellow-50 border border-yellow-200'
  }
}

const getStockBadgeClasses = (item: Ingredient): string => {
  const quantity = Number(item.QuantityInStock)
  const minQuantity = Number(item.MinQuantity)
  
  if (quantity === 0) {
    return 'bg-red-600 text-white'
  } else if (quantity < minQuantity) {
    return 'bg-orange-500 text-white'
  } else {
    return 'bg-yellow-500 text-white'
  }
}

const getProgressBarClasses = (item: Ingredient): string => {
  const quantity = Number(item.QuantityInStock)
  const minQuantity = Number(item.MinQuantity)
  
  if (quantity === 0) {
    return 'bg-red-200'
  } else if (quantity < minQuantity) {
    return 'bg-orange-200'
  } else {
    return 'bg-yellow-200'
  }
}

const getProgressFillClasses = (item: Ingredient): string => {
  const quantity = Number(item.QuantityInStock)
  const minQuantity = Number(item.MinQuantity)
  
  if (quantity === 0) {
    return 'bg-red-500'
  } else if (quantity < minQuantity) {
    return 'bg-orange-500'
  } else {
    return 'bg-yellow-500'
  }
}

const getStockPercentage = (item: Ingredient): number => {
  const quantity = Number(item.QuantityInStock)
  const minQuantity = Number(item.MinQuantity)
  
  if (quantity === 0) return 0
  if (quantity < minQuantity) {
    return Math.min((quantity / minQuantity) * 100, 100)
  } else {
    return Math.min((quantity / minQuantity) * 100, 100)
  }
}

const loadDashboardData = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    const data = await dashboardService.getDashboardData()
    
    todayStats.value = data.stats
    recentOrders.value = data.recentOrders
    lowStockItems.value = data.lowStockItems
    
    // Load chart data and schedules in parallel for better performance
    await Promise.all([
      updateChartData(),
      loadProductData(),
      loadEmployees(),
      loadWorkSchedules()
    ])
    
    isInitialized.value = true
    
  } catch (err) {
    console.error('Error loading dashboard data:', err)
    error.value = 'Không thể tải dữ liệu dashboard'
  } finally {
    isLoading.value = false
  }
}

const loadProductData = async () => {
  try {
    // Tính toán ngày dựa trên period được chọn (biểu đồ sử dụng today + 1)
    const today = new Date()
    today.setDate(today.getDate() + 1) // Thêm 1 ngày cho biểu đồ
    const endDate = new Date(today)
    const startDate = new Date(today)
    
    // Tính toán khoảng thời gian dựa trên period
    switch (selectedProductPeriod.value) {
      case 'day':
        startDate.setDate(today.getDate() - 6) // 7 ngày
        break
      case 'week':
        startDate.setDate(today.getDate() - (7 * 6)) // 7 tuần
        break
      case 'month':
        startDate.setMonth(today.getMonth() - 6) // 7 tháng
        break
      case 'year':
        startDate.setFullYear(today.getFullYear() - 6) // 7 năm
        break
      default:
        startDate.setDate(today.getDate() - 6)
    }
    
    const fromDateStr = startDate.toISOString().split('T')[0] as string
    const toDateStr = endDate.toISOString().split('T')[0] as string
    
    const period = selectedProductPeriod.value
    const bestSelling = await dashboardService.getBestSellingProductsByPeriod(
      fromDateStr, 
      toDateStr, 
      period, 
      5
    )
    
    
    if (bestSelling && bestSelling.length > 0) {
      const labels = bestSelling.map((item: any) => {
        const name = item.ProductID__ProductName || item.product_name || item.name || item.ProductName || 'Sản phẩm không tên'
        return String(name)
      })
      
      const data = bestSelling.map((item: any) => {
        const quantity = item.total_quantity || item.quantity || item.TotalQuantity || 0
        return quantity
      })
      
      productData.value = {
        labels: labels,
        datasets: [
          {
            label: 'Số lượng bán',
            data: data,
            backgroundColor: [
              '#8B4513',
              '#D2691E', 
              '#F4A460',
              '#DEB887',
              '#CD853F',
              '#D2B48C',
              '#BC9A6A'
            ],
            borderWidth: 0
          }
        ]
      }
    } else {
      // Không có dữ liệu
      productData.value = {
        labels: [],
        datasets: [
          {
            label: 'Số lượng bán',
            data: [],
            backgroundColor: [
              '#8B4513',
              '#D2691E', 
              '#F4A460',
              '#DEB887',
              '#CD853F'
            ],
            borderWidth: 0
          }
        ]
      }
    }
  } catch (error) {
    console.error('Error loading product data:', error)
    // Không có dữ liệu khi có lỗi
    productData.value = {
      labels: [],
      datasets: [
        {
          label: 'Số lượng bán',
          data: [],
          backgroundColor: [
            '#8B4513',
            '#D2691E', 
            '#F4A460',
            '#DEB887',
            '#CD853F'
          ],
          borderWidth: 0
        }
      ]
    }
  }
}

// Load work schedules
const loadWorkSchedules = async (startDate?: string, endDate?: string) => {
  try {
    loadingSchedules.value = true
    const response = await attendanceService.getWeeklySchedule(startDate, endDate)
    workSchedules.value = response.data?.schedules || response.data || []
  } catch (error) {
    console.error('Error loading work schedules:', error)
  } finally {
    loadingSchedules.value = false
  }
}

const loadEmployees = async () => {
  try {
    const response = await userService.getAll({ page_size: 100 })
    employees.value = response || []
  } catch (error) {
    console.error('Error loading employees:', error)
  }
}

const handleSchedulePeriodChange = (startDate: string, endDate: string) => {
  loadWorkSchedules(startDate, endDate)
}

const updateChartData = async () => {
  try {
    // Tính toán ngày chính xác - 7 điểm dữ liệu (biểu đồ sử dụng today + 1)
    const today = new Date()
    today.setDate(today.getDate() + 1) // Thêm 1 ngày cho biểu đồ
    const endDate = new Date(today)
    const startDate = new Date(today)
    
    // Tính toán khoảng thời gian dựa trên period
    switch (selectedPeriod.value) {
      case 'day':
        // 7 ngày: từ 6 ngày trước đến hôm nay + 1
        startDate.setDate(today.getDate() - 6)
        break
      case 'week':
        // 7 tuần: từ 6 tuần trước đến tuần này + 1
        startDate.setDate(today.getDate() - (7 * 6))
        break
      case 'month':
        // 7 tháng: từ 6 tháng trước đến tháng này + 1
        startDate.setMonth(today.getMonth() - 6)
        break
      case 'year':
        // 7 năm: từ 6 năm trước đến năm này + 1
        startDate.setFullYear(today.getFullYear() - 6)
        break
      default:
        startDate.setDate(today.getDate() - 6)
    }
    
    const fromDateStr = startDate.toISOString().split('T')[0] as string
    const toDateStr = endDate.toISOString().split('T')[0] as string
    
    // Gọi API
    const period = selectedPeriod.value
    const trend = await dashboardService.getRevenueTrendByPeriod(
      fromDateStr,
      toDateStr,
      period
    )
    
    // Đảm bảo có đúng 7 điểm dữ liệu
    const labels = (trend as any)?.labels || []
    const data = (trend as any)?.datasets?.[0]?.data || []
    
    // Nếu API trả về ít hơn 7 điểm, bổ sung bằng 0
    const paddedLabels = [...labels]
    const paddedData = [...data]
    
    while (paddedLabels.length < 7) {
      paddedLabels.push('')
      paddedData.push(0)
    }
    
    // Chỉ lấy 7 điểm đầu tiên  
    const finalLabels = paddedLabels.slice(0, 7).map(label => String(label))
    const finalData = paddedData.slice(0, 7)
    
    chartData.value = {
      labels: finalLabels,
      datasets: [
        {
          label: 'Doanh thu (₫)',
          data: finalData,
          backgroundColor: [
            '#D4AF37',
            '#B8860B', 
            '#CD853F',
            '#DAA520',
            '#F4A460',
            '#DEB887',
            '#C4A484'
          ],
          borderColor: '#8B4513',
          borderWidth: 2
        }
      ]
    }
    
  } catch (error) {
    console.error('Error loading chart data:', error)
    // Không có dữ liệu khi lỗi
    chartData.value = {
      labels: [],
      datasets: [
        {
          label: 'Doanh thu (₫)',
          data: [],
          backgroundColor: [
            '#D4AF37',
            '#B8860B', 
            '#CD853F',
            '#DAA520',
            '#F4A460',
            '#DEB887',
            '#C4A484'
          ],
          borderColor: '#8B4513',
          borderWidth: 2
        }
      ]
    }
  }
}


// Watch for period changes
watch(selectedPeriod, async () => {
  await updateChartData()
})

watch(selectedProductPeriod, async () => {
  await loadProductData()
})

onMounted(() => {
  if (!isInitialized.value) {
    loadDashboardData()
  }
  
  // Connect WebSocket with new direct implementation
  console.log('[Dashboard] 🚀 Mounting component, connecting WebSocket...')
  connectWebSocketDirect()
})

// Reload data when component is activated (returns from cache)
onActivated(() => {
  // Only refresh if returning to dashboard after significant time
  // Cache handles recent data, so we don't need to reload immediately
  if (isInitialized.value) {
    isLoading.value = false
  }
})

// Cleanup WebSocket on unmount
onUnmounted(() => {
  console.log('[Dashboard] 🧹 Unmounting component, cleaning up WebSocket...')
  disconnectWebSocketDirect()
})
</script>