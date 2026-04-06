<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-coffee-800">Quản lý khách hàng</h2>
        <p class="text-coffee-600 mt-1">Tổng cộng {{ customers.length }} khách hàng</p>
      </div>
      <BaseButton variant="primary" @click="showCreateModal = true">
        <Plus class="w-4 h-4 mr-2" />
        Thêm khách hàng
      </BaseButton>
    </div>

    <!-- Search and Filter -->
    <div class="flex flex-col sm:flex-row gap-4">
      <div class="flex-1">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 text-coffee-400 w-4 h-4" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Tìm kiếm theo tên hoặc số điện thoại..."
            class="w-full pl-10 pr-4 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500 focus:border-transparent"
            @input="debouncedSearch"
          />
        </div>
      </div>
      <div class="flex gap-2">
        <select
          v-model="selectedMembershipLevel"
          @change="debouncedFilter"
          class="px-4 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500 focus:border-transparent"
        >
          <option value="">Tất cả cấp độ</option>
          <option value="Bronze">Bronze</option>
          <option value="Silver">Silver</option>
          <option value="Gold">Gold</option>
          <option value="VIP">VIP</option>
        </select>
        <BaseButton
          @click="selectedMembershipLevel = 'VIP'"
          variant="secondary"
          size="sm"
        >
          <Award class="w-4 h-4 mr-1" />
          VIP
        </BaseButton>
        <BaseButton
          @click="selectedMembershipLevel = ''"
          variant="ghost"
          size="sm"
        >
          <RefreshCw class="w-4 h-4 mr-1" />
          Tất cả
        </BaseButton>
        <!-- Removed Refresh button - not needed -->
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <StatsCard
        title="Tổng khách hàng"
        :value="customers.length"
        color="blue"
        :icon="Users"
      />
      <StatsCard
        title="Khách VIP"
        :value="vipCustomers"
        color="purple"
        :icon="Award"
      />
      <StatsCard
        title="Khách thường"
        :value="regularCustomers"
        color="green"
        :icon="User"
      />
      <StatsCard
        title="Khách mới"
        :value="newCustomers"
        color="orange"
        :icon="UserPlus"
      />
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <Loader2 class="w-8 h-8 animate-spin text-coffee-500" />
      <span class="ml-2 text-coffee-600">Đang tải...</span>
    </div>

    <!-- Customers Grid -->
    <div v-else-if="Array.isArray(customers) && customers.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="customer in customers"
        :key="customer.CustomerID"
        class="card p-6 hover:shadow-lg transition-all duration-300 border border-coffee-200"
      >
        <!-- Customer Info Header -->
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
        <h3 class="text-lg font-bold text-coffee-800 mb-1">{{ customer.FullName }}</h3>
            <p class="text-sm text-coffee-500 mb-1">{{ customer.PhoneNumber }}</p>
            <p v-if="customer.Email" class="text-xs text-coffee-400">{{ customer.Email }}</p>
          </div>
          <span :class="getMembershipClasses(customer.membership_level)" class="px-2 py-1 text-xs rounded-lg font-medium">
            {{ getMembershipText(customer.membership_level) }}
          </span>
        </div>
        
        <!-- Customer Stats -->
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div class="text-center p-3 bg-coffee-50 rounded-lg">
            <div class="text-lg font-bold text-coffee-800">{{ customer.LoyaltyPoints }}</div>
            <div class="text-xs text-coffee-500">Điểm tích lũy</div>
          </div>
          <div class="text-center p-3 bg-coffee-50 rounded-lg">
            <div class="text-lg font-bold text-coffee-800">{{ customer.total_orders || 0 }}</div>
            <div class="text-xs text-coffee-500">Đơn hàng</div>
          </div>
        </div>

        <!-- Total Spent -->
        <div v-if="customer.total_spent" class="mb-4 p-3 bg-green-50 rounded-lg">
          <div class="text-center">
            <div class="text-sm text-green-600 font-medium">Tổng chi tiêu</div>
            <div class="text-lg font-bold text-green-700">{{ formatCurrency(customer.total_spent) }}</div>
          </div>
        </div>

        <!-- Register Date -->
        <div v-if="customer.RegisterDate" class="mb-4 text-xs text-coffee-500">
          <div class="flex items-center">
            <Calendar class="w-3 h-3 mr-1" />
            Đăng ký: {{ formatDate(customer.RegisterDate) }}
          </div>
        </div>
        
        <!-- Actions -->
        <div class="flex gap-2">
          <BaseButton
            @click="viewCustomer(customer.CustomerID)"
            variant="ghost"
            size="sm"
            class="flex-1"
          >
            <Eye class="w-4 h-4 mr-1" />
            Xem
          </BaseButton>
          <BaseButton
            @click="editCustomer(customer)"
            variant="secondary"
            size="sm"
            class="flex-1"
          >
            <Edit class="w-4 h-4 mr-1" />
            Sửa
          </BaseButton>
          <BaseButton
            @click="confirmDelete(customer)"
            variant="danger"
            size="sm"
          >
            <Trash2 class="w-4 h-4" />
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && (!Array.isArray(customers) || customers.length === 0)" class="text-center py-12">
      <Users class="w-16 h-16 text-coffee-300 mx-auto mb-4" />
      <h3 class="text-lg font-semibold text-coffee-600 mb-2">Chưa có khách hàng nào</h3>
      <p class="text-coffee-500 mb-4">Hãy thêm khách hàng đầu tiên để bắt đầu</p>
      <BaseButton variant="primary" @click="showCreateModal = true">
        <Plus class="w-4 h-4 mr-2" />
        Thêm khách hàng
      </BaseButton>
    </div>

    <!-- Customer Modal -->
    <CustomerModal
      v-if="showCreateModal"
      :customer="editingCustomer"
      @close="showCreateModal = false"
      @saved="handleCustomerSaved"
    />

    <!-- Delete confirm (giống Products) -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-coffee-800 mb-2">Xác nhận xóa</h3>
        <p class="text-coffee-700">Bạn có chắc muốn xóa khách hàng <span class="font-semibold">{{ showDeleteConfirm?.FullName }}</span>?</p>
        <div class="flex justify-end gap-3 mt-6">
          <button class="btn-secondary" :disabled="deleting" @click="closeDelete">Hủy</button>
          <button class="btn-danger" :disabled="deleting" @click="doDelete">{{ deleting ? 'Đang xóa...' : 'Xóa' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import {
  Plus,
  Users,
  Award,
  User,
  UserPlus,
  Eye,
  Edit,
  Trash2,
  Search,
  Loader2,
  Calendar,
  RefreshCw
} from 'lucide-vue-next'
// @ts-ignore
import StatsCard from '../components/common/StatsCard.vue'
// @ts-ignore
import BaseButton from '../components/common/BaseButton.vue'
// @ts-ignore
import CustomerModal from '../components/customers/CustomerModal.vue'
import { customerService } from '../services/customers'
import type { Customer, CustomerForm } from '../types'

const router = useRouter()
const toast = useToast()

// State
const customers = ref<Customer[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedMembershipLevel = ref('')
const showCreateModal = ref(false)
const editingCustomer = ref<Customer | null>(null)

// Computed
const vipCustomers = computed(() => {
  if (!Array.isArray(customers.value)) return 0
  return customers.value.filter(c => c.membership_level === 'VIP' || c.membership_level === 'Gold').length
})

const regularCustomers = computed(() => {
  if (!Array.isArray(customers.value)) return 0
  return customers.value.filter(c => c.membership_level === 'Silver' || c.membership_level === 'Bronze').length
})

const newCustomers = computed(() => {
  if (!Array.isArray(customers.value)) return 0
  return customers.value.filter(c => (c.LoyaltyPoints || 0) < 100).length
})

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
    day: '2-digit'
  })
}

// Removed showConfirmDialog - using modal instead

const loadCustomers = async () => {
  try {
    loading.value = true
    const filters: any = {}
    
    if (searchQuery.value) {
      filters.search = searchQuery.value
    }
    
    // Server-side filtering for membership level
    if (selectedMembershipLevel.value) {
      filters.membership_level = selectedMembershipLevel.value
    }
    
    const response = await customerService.getAll(filters)
    
    // Handle paginated response
    if (response && typeof response === 'object' && 'results' in response) {
      customers.value = response.results as Customer[]
    } else if (Array.isArray(response)) {
      customers.value = response as Customer[]
    } else {
      console.warn('⚠️ Unexpected response format:', response)
      customers.value = []
    }
  } catch (error: any) {
    console.error('Error loading customers:', error)
    toast.error('Không thể tải danh sách khách hàng')
    customers.value = []
  } finally {
    loading.value = false
  }
}

// Debounced search to prevent too many API calls
let searchTimeout: ReturnType<typeof setTimeout> | undefined
const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadCustomers()
  }, 500)
}

// Debounced filter to prevent too many API calls
let filterTimeout: ReturnType<typeof setTimeout> | undefined
const debouncedFilter = () => {
  if (filterTimeout) clearTimeout(filterTimeout)
  filterTimeout = setTimeout(() => {
    loadCustomers()
  }, 300)
}

// Removed handleFilter - using debouncedFilter instead

// Removed loadVIPCustomers and resetFilters - not needed

// Removed forceRefreshCustomers - not needed

const viewCustomer = (id: number) => {
  router.push(`/customers/${id}`)
}

const editCustomer = (customer: Customer) => {
  editingCustomer.value = customer
  showCreateModal.value = true
}

// Delete (giống hệt Products)
const showDeleteConfirm = ref<null | Customer>(null)
const deleting = ref(false)
function confirmDelete(c: Customer) { showDeleteConfirm.value = c }
function closeDelete() { showDeleteConfirm.value = null }
async function doDelete() {
  if (!showDeleteConfirm.value) return
  try {
    deleting.value = true
    const id = showDeleteConfirm.value.CustomerID
    closeDelete()
    // optimistic update
    customers.value = customers.value.filter(x => x.CustomerID !== id)
    await customerService.delete(id)
    await loadCustomers().catch(() => {})
  } catch (err: any) {
    toast.error(err?.response?.data?.error || err?.response?.data?.detail || 'Không thể xóa khách hàng')
    console.error('Delete customer error:', err?.response?.data || err)
    await loadCustomers().catch(() => {})
  } finally {
    deleting.value = false
    closeDelete()
  }
}

const handleCustomerSaved = () => {
  showCreateModal.value = false
  editingCustomer.value = null
  
  // 🔄 Sync with API to get latest data (needed for create/edit)
  loadCustomers()
}

// Watchers - Removed to prevent unnecessary API calls

// Lifecycle
onMounted(() => {
  loadCustomers()
})
</script>
