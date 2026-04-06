<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-coffee-800">Chi tiết đơn hàng #{{ orderId }}</h2>
        <p v-if="order" class="text-coffee-600 mt-1">
          Khách: <span class="font-medium">{{ order.customer_name || order.customer?.FullName || '-' }}</span> ·
          Nhân viên: <span class="font-medium">{{ order.employee_name || order.employee?.FullName || '-' }}</span> ·
          Ngày đặt: <span class="font-medium">{{ formatDate(order.OrderDate) }}</span>
        </p>
      </div>
      <div class="flex gap-3">
        <button class="btn-secondary inline-flex items-center" @click="goBack">
          <ArrowLeft class="w-4 h-4 mr-2" />
          Quay lại
        </button>
      </div>
    </div>

    <!-- Loading / Error -->
    <div v-if="isLoading" class="card p-6 text-center text-coffee-600">Đang tải chi tiết đơn hàng...</div>
    <div v-else-if="errorMessage" class="card p-6 text-center text-red-600">{{ errorMessage }}</div>

    <!-- Summary Cards -->
    <div v-else-if="order" class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="card p-6">
        <h3 class="text-coffee-600 text-sm mb-1 font-medium">Mã đơn</h3>
        <p class="text-2xl font-bold text-coffee-700">#{{ order.OrderID }}</p>
      </div>
      <div class="card p-6">
        <h3 class="text-coffee-600 text-sm mb-1 font-medium">Trạng thái</h3>
        <p>
          <span :class="getStatusClasses(order.Status)" class="px-3 py-1 rounded-lg text-xs font-medium">
            {{ getStatusText(order.Status) }}
          </span>
        </p>
      </div>
      <div class="card p-6">
        <h3 class="text-coffee-600 text-sm mb-1 font-medium">Tổng tiền</h3>
        <p class="text-2xl font-bold text-coffee-700">{{ formatCurrency(order.TotalAmount) }}</p>
      </div>
      <div class="card p-6">
        <h3 class="text-coffee-600 text-sm mb-1 font-medium">Thanh toán</h3>
        <p class="text-coffee-700 font-medium">{{ order.payment_method_display || order.PaymentMethod || '-' }}</p>
      </div>
    </div>

    <!-- Items Table -->
    <div v-if="order && items.length" class="card overflow-hidden">
      <div class="px-6 py-4 border-b border-coffee-200">
        <h3 class="text-lg font-bold text-coffee-800">Sản phẩm trong đơn</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-coffee-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-coffee-700 uppercase">Sản phẩm</th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-coffee-700 uppercase">Số lượng</th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-coffee-700 uppercase">Đơn giá</th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-coffee-700 uppercase">Thành tiền</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-coffee-200">
            <tr v-for="row in items" :key="row.OrderDetailID" class="hover:bg-coffee-50">
              <td class="px-6 py-4">{{ row.product_name || row.product?.ProductName || ('SP #' + row.ProductID) }}</td>
              <td class="px-6 py-4 text-right">{{ row.Quantity }}</td>
              <td class="px-6 py-4 text-right">{{ formatCurrency(row.UnitPrice) }}</td>
              <td class="px-6 py-4 text-right">{{ formatCurrency(row.Subtotal || (Number(row.UnitPrice) * Number(row.Quantity))) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty state for items -->
    <div v-if="order && !items.length" class="card p-6 text-center text-coffee-600">
      Đơn hàng không có sản phẩm nào.
    </div>
  </div>
  </template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from 'lucide-vue-next'
import { orderService } from '../services/orders'

type AnyObject = Record<string, any>

const route = useRoute()
const router = useRouter()
const orderId = computed(() => Number(route.params.id))

const isLoading = ref(false)
const errorMessage = ref('')
const order = ref<AnyObject | null>(null)
const items = ref<AnyObject[]>([])

const goBack = () => router.push('/orders')

const formatCurrency = (value: string | number): string => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(Number(value))
}

const formatDate = (value: string): string => {
  return new Date(value).toLocaleDateString('vi-VN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const getStatusClasses = (status: string): string => {
  const classMap: AnyObject = {
    'COMPLETED': 'bg-green-100 text-green-700',
    'PREPARING': 'bg-yellow-100 text-yellow-700',
    'PENDING': 'bg-blue-100 text-blue-700',
    'CANCELLED': 'bg-red-100 text-red-700',
  }
  return classMap[status] || 'bg-coffee-100 text-coffee-700'
}

const getStatusText = (status: string): string => {
  const textMap: AnyObject = {
    'COMPLETED': 'Hoàn thành',
    'PREPARING': 'Đang chuẩn bị',
    'PENDING': 'Chờ xác nhận',
    'CANCELLED': 'Đã hủy',
  }
  return textMap[status] || status
}

const loadData = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    const id = orderId.value
    if (!id || Number.isNaN(id)) {
      throw new Error('Mã đơn hàng không hợp lệ')
    }
    const orderRes = await orderService.getById(id)
    order.value = orderRes as AnyObject
    // BE trả về field order_details nằm trong object order
    const details = (order.value as any)?.order_details
    items.value = Array.isArray(details) ? details : []
  } catch (err: any) {
    errorMessage.value = err?.response?.data?.message || err?.response?.data?.detail || err?.message || 'Không tải được chi tiết đơn hàng'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadData)
</script>
