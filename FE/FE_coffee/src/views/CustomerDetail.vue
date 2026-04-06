<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <BaseButton @click="$router.push('/customers')" variant="ghost" size="sm">
          <ArrowLeft class="w-4 h-4 mr-2" />
          Quay lại
        </BaseButton>
        <div>
          <h2 class="text-2xl font-bold text-coffee-800">Chi tiết khách hàng</h2>
          <p class="text-coffee-600">Thông tin chi tiết và lịch sử giao dịch</p>
        </div>
      </div>
      <div class="flex gap-2">
        <BaseButton @click="editCustomer" variant="secondary" size="sm">
          <Edit class="w-4 h-4 mr-2" />
          Chỉnh sửa
        </BaseButton>
        <BaseButton @click="showPointsModal = true" variant="primary" size="sm">
          <Award class="w-4 h-4 mr-2" />
          Quản lý điểm
        </BaseButton>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <Loader2 class="w-8 h-8 animate-spin text-coffee-500" />
      <span class="ml-2 text-coffee-600">Đang tải...</span>
    </div>

    <!-- Customer Info -->
    <div v-else-if="customer" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Customer Details -->
      <div class="lg:col-span-1">
        <div class="card p-6">
          <div class="text-center mb-6">
            <div class="text-6xl mb-4">👤</div>
            <h3 class="text-xl font-bold text-coffee-800">{{ customer.FullName }}</h3>
            <p class="text-coffee-500">{{ customer.PhoneNumber }}</p>
            <p v-if="customer.Email" class="text-coffee-400 text-sm">{{ customer.Email }}</p>
          </div>

          <!-- Membership Info -->
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-coffee-600">Cấp độ thành viên:</span>
              <span :class="getMembershipClasses(customer.membership_level)" class="px-2 py-1 text-xs rounded-lg font-medium">
                {{ getMembershipText(customer.membership_level) }}
              </span>
            </div>

            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-coffee-600">Điểm tích lũy:</span>
              <span class="text-lg font-bold text-coffee-800">{{ customer.LoyaltyPoints }}</span>
            </div>

            <div v-if="customer.RegisterDate" class="flex items-center justify-between">
              <span class="text-sm font-medium text-coffee-600">Ngày đăng ký:</span>
              <span class="text-sm text-coffee-500">{{ formatDate(customer.RegisterDate) }}</span>
            </div>

            <div v-if="customer.total_orders" class="flex items-center justify-between">
              <span class="text-sm font-medium text-coffee-600">Tổng đơn hàng:</span>
              <span class="text-sm text-coffee-500">{{ customer.total_orders }}</span>
            </div>

            <div v-if="customer.total_spent" class="flex items-center justify-between">
              <span class="text-sm font-medium text-coffee-600">Tổng chi tiêu:</span>
              <span class="text-sm text-coffee-500">{{ formatCurrency(customer.total_spent) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Order History -->
      <div class="lg:col-span-2">
        <div class="card p-6" ref="orderHistorySection">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-coffee-800">Lịch sử đơn hàng</h3>
            <BaseButton @click="loadOrderHistory" variant="ghost" size="sm" :disabled="loadingOrders">
              <RefreshCw class="w-4 h-4 mr-2" :class="{ 'animate-spin': loadingOrders }" />
              Làm mới
            </BaseButton>
          </div>

          <!-- Order History List -->
          <div v-if="loadingOrders" class="flex justify-center py-8">
            <Loader2 class="w-6 h-6 animate-spin text-coffee-500" />
          </div>

          <div v-else-if="orderHistory.length === 0" class="text-center py-8">
            <ShoppingBag class="w-12 h-12 text-coffee-300 mx-auto mb-3" />
            <p class="text-coffee-500">Khách hàng chưa có đơn hàng nào</p>
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="order in orderHistory"
              :key="order.OrderID"
              class="border border-coffee-200 rounded-lg p-4 hover:bg-coffee-50 transition-colors"
            >
              <div class="flex items-center justify-between">
                <div>
                  <h4 class="font-medium text-coffee-800">Đơn hàng #{{ order.OrderID }}</h4>
                  <p class="text-sm text-coffee-500">{{ formatDate(order.OrderDate) }}</p>
                </div>
                <div class="text-right">
                  <p class="font-semibold text-coffee-800">{{ formatCurrency(order.TotalAmount) }}</p>
                  <span :class="getStatusClasses(order.Status)" class="text-xs px-2 py-1 rounded-full">
                    {{ order.status_display || order.Status }}
                  </span>
                </div>
              </div>
              <div v-if="order.items_count" class="mt-2 text-sm text-coffee-500">
                {{ order.items_count }} sản phẩm
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else class="text-center py-12">
      <Users class="w-16 h-16 text-coffee-300 mx-auto mb-4" />
      <h3 class="text-lg font-semibold text-coffee-600 mb-2">Không tìm thấy khách hàng</h3>
      <p class="text-coffee-500 mb-4">Khách hàng có thể đã bị xóa hoặc không tồn tại</p>
      <BaseButton @click="$router.push('/customers')" variant="primary">
        <ArrowLeft class="w-4 h-4 mr-2" />
        Quay lại danh sách
      </BaseButton>
    </div>

    <!-- Customer Modal -->
    <CustomerModal
      v-if="showEditModal"
      :customer="customer"
      @close="showEditModal = false"
      @saved="handleCustomerSaved"
    />

    <!-- Points Management Modal -->
    <PointsModal
      v-if="showPointsModal"
      :customer="customer"
      @close="showPointsModal = false"
      @saved="handlePointsSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import {
  ArrowLeft,
  Edit,
  Award,
  Loader2,
  RefreshCw,
  ShoppingBag,
  Users
} from 'lucide-vue-next'
// @ts-ignore
import BaseButton from '../components/common/BaseButton.vue'
// @ts-ignore
import CustomerModal from '../components/customers/CustomerModal.vue'
// @ts-ignore
import PointsModal from '../components/customers/PointsModal.vue'
import { customerService } from '../services/customers'
import type { Customer, CustomerOrderHistory } from '../types'

const route = useRoute()
const router = useRouter()
const toast = useToast()

// State
const customer = ref<Customer | null>(null)
const orderHistory = ref<CustomerOrderHistory[]>([])
const loading = ref(false)
const loadingOrders = ref(false)
const hasLoadedOrders = ref(false)
const orderHistorySection = ref<HTMLElement | null>(null)
const showEditModal = ref(false)
const showPointsModal = ref(false)

// Computed
const customerId = computed(() => parseInt(route.params.id as string))

// Methods
const getMembershipClasses = (level?: string): string => {
  const classMap = {
    'VIP': 'bg-purple-100 text-purple-700',
    'Gold': 'bg-yellow-100 text-yellow-700',
    'Silver': 'bg-gray-100 text-gray-700',
    'Bronze': 'bg-orange-100 text-orange-700'
  }
  return classMap[level as keyof typeof classMap] || 'bg-coffee-100 text-coffee-700'
}

const getMembershipText = (level?: string): string => {
  return level || 'Thường'
}

const getStatusClasses = (status: string): string => {
  const classMap = {
    'PENDING': 'bg-yellow-100 text-yellow-700',
    'PREPARING': 'bg-blue-100 text-blue-700',
    'COMPLETED': 'bg-green-100 text-green-700',
    'CANCELLED': 'bg-red-100 text-red-700'
  }
  return classMap[status as keyof typeof classMap] || 'bg-gray-100 text-gray-700'
}

const formatCurrency = (amount: string | number): string => {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND'
  }).format(num)
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadCustomer = async () => {
  try {
    loading.value = true
    customer.value = await customerService.getById(customerId.value)
  } catch (error: any) {
    console.error('Error loading customer:', error)
    if (error.response?.status === 404) {
      toast.error('Không tìm thấy khách hàng')
    } else {
      toast.error('Không thể tải thông tin khách hàng')
    }
  } finally {
    loading.value = false
  }
}

const loadOrderHistory = async () => {
  if (!customer.value) return

  try {
    hasLoadedOrders.value = true
    loadingOrders.value = true
    orderHistory.value = await customerService.getOrderHistory(customer.value.CustomerID)
  } catch (error: any) {
    console.error('Error loading order history:', error)
    toast.error('Không thể tải lịch sử đơn hàng')
  } finally {
    loadingOrders.value = false
  }
}

const editCustomer = () => {
  showEditModal.value = true
}

const handleCustomerSaved = () => {
  showEditModal.value = false
  loadCustomer()
}

const handlePointsSaved = () => {
  showPointsModal.value = false
  loadCustomer()
}

// Lifecycle
let orderHistoryObserver: IntersectionObserver | null = null

onMounted(async () => {
  await loadCustomer()
  // Tải lịch sử ngay khi đã có thông tin khách hàng
  if (customer.value && !hasLoadedOrders.value) {
    loadOrderHistory()
  }

  if ('IntersectionObserver' in window) {
    orderHistoryObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && !hasLoadedOrders.value && !loadingOrders.value && customer.value) {
          loadOrderHistory()
        }
      })
    }, { threshold: 0.15 })

    if (orderHistorySection.value) {
      orderHistoryObserver.observe(orderHistorySection.value)
    }
  }
})

onBeforeUnmount(() => {
  if (orderHistoryObserver) {
    orderHistoryObserver.disconnect()
    orderHistoryObserver = null
  }
})
</script>
