<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-coffee-800">Quản lý nhân viên</h2>
        <p class="text-coffee-600 mt-1">Tổng cộng {{ employees.length }} nhân viên</p>
      </div>
      <button class="btn-primary inline-flex items-center" @click="showCreate = true">
        <Plus class="w-4 h-4 mr-2" />
        Thêm nhân viên
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="card p-6">
        <h3 class="text-coffee-600 text-sm mb-1 font-medium">Tổng nhân viên</h3>
        <p class="text-2xl font-bold text-coffee-700">{{ employees.length }}</p>
      </div>
      <div class="card p-6">
        <h3 class="text-coffee-600 text-sm mb-1 font-medium">Thu ngân</h3>
        <p class="text-2xl font-bold text-coffee-700">{{ cashiers }}</p>
      </div>
      <div class="card p-6">
        <h3 class="text-coffee-600 text-sm mb-1 font-medium">Phục vụ</h3>
        <p class="text-2xl font-bold text-coffee-700">{{ waiters }}</p>
      </div>
    </div>

    <!-- Search -->
    <div class="bg-white rounded-xl p-4 shadow-md">
      <div class="flex gap-3">
        <input v-model="searchQuery" @input="onSearchInput" class="input-field" placeholder="Tìm tên/email/username" />
      </div>
    </div>

    <!-- Employee Table -->
    <div class="card overflow-hidden">
      <div v-if="isLoading" class="p-8 text-center text-coffee-600">Đang tải...</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-coffee-100">
            <tr>
              <th class="px-6 py-3 text-left text-sm font-semibold text-coffee-800">Username</th>
              <th class="px-6 py-3 text-left text-sm font-semibold text-coffee-800">Họ tên</th>
              <th class="px-6 py-3 text-left text-sm font-semibold text-coffee-800">Email</th>
              <th class="px-6 py-3 text-left text-sm font-semibold text-coffee-800">Vai trò</th>
              <th class="px-6 py-3 text-center text-sm font-semibold text-coffee-800">Trạng thái</th>
              <th class="px-6 py-3 text-center text-sm font-semibold text-coffee-800">Thao tác</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-coffee-100">
            <tr v-for="emp in filteredEmployees" :key="emp.id" class="hover:bg-coffee-50 transition-colors">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div v-if="emp.employee_detail?.avatar" class="w-10 h-10 rounded-full overflow-hidden bg-coffee-100 flex-shrink-0">
                    <img :src="emp.employee_detail.avatar" :alt="emp.full_name" class="w-full h-full object-cover" />
                  </div>
                  <div v-else class="w-10 h-10 rounded-full bg-coffee-200 flex items-center justify-center text-coffee-600 font-semibold flex-shrink-0">
                    {{ (emp.full_name?.[0] || emp.username[0] || '?').toUpperCase() }}
                  </div>
                  <span class="text-coffee-800 font-medium">{{ emp.username }}</span>
                </div>
              </td>
              <td class="px-6 py-4 text-coffee-700">{{ emp.full_name || `${emp.first_name} ${emp.last_name}`.trim() }}</td>
              <td class="px-6 py-4 text-coffee-600">{{ emp.email }}</td>
              <td class="px-6 py-4">
                <span :class="getRoleBadgeClass(emp.role)">{{ getRoleLabel(emp.role) }}</span>
              </td>
              <td class="px-6 py-4 text-center">
                <span :class="emp.is_active ? 'text-green-600' : 'text-red-600'">
                  {{ emp.is_active ? 'Hoạt động' : 'Ngưng' }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center justify-center gap-2">
                  <button @click="showDetail(emp)" class="p-2 hover:bg-blue-50 rounded-lg transition-colors" title="Chi tiết & Chỉnh sửa">
                    <UserIcon class="w-4 h-4 text-blue-600" />
                  </button>
                  <button @click="openScheduleModal(emp)" class="p-2 hover:bg-green-50 rounded-lg transition-colors" title="Đặt lịch làm việc">
                    <Calendar class="w-4 h-4 text-green-600" />
                  </button>
                  <button @click="confirmDelete(emp)" class="p-2 hover:bg-red-50 rounded-lg transition-colors" title="Xóa">
                    <Trash2 class="w-4 h-4 text-red-600" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreate" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showCreate = false">
      <div class="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
        <h3 class="text-xl font-bold text-coffee-800 mb-4">Thêm nhân viên mới</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm text-coffee-600 mb-1">Username *</label>
            <input v-model="createForm.username" class="input-field" placeholder="Tên đăng nhập" />
          </div>
          <div>
            <label class="block text-sm text-coffee-600 mb-1">Mật khẩu *</label>
            <input v-model="createForm.password" type="password" class="input-field" placeholder="Mật khẩu" />
          </div>
          <div>
            <label class="block text-sm text-coffee-600 mb-1">Họ *</label>
            <input v-model="createForm.first_name" class="input-field" placeholder="Nguyễn" />
          </div>
          <div>
            <label class="block text-sm text-coffee-600 mb-1">Tên *</label>
            <input v-model="createForm.last_name" class="input-field" placeholder="Văn A" />
          </div>
          <div>
            <label class="block text-sm text-coffee-600 mb-1">Email *</label>
            <input v-model="createForm.email" type="email" class="input-field" placeholder="email@example.com" />
          </div>
          <div>
            <label class="block text-sm text-coffee-600 mb-1">Vai trò *</label>
            <select v-model="createForm.role" class="input-field">
              <option value="cashier">Thu ngân</option>
              <option value="waiter">Phục vụ</option>
            </select>
          </div>
          <div v-if="createError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {{ createError }}
          </div>
          <div class="flex gap-3 pt-2">
            <button @click="showCreate = false" class="btn-secondary flex-1">Hủy</button>
            <button @click="submitCreate" :disabled="submitting || !isValidCreate" class="btn-primary flex-1">
              {{ submitting ? 'Đang tạo...' : 'Tạo' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirm Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showDeleteConfirm = null">
      <div class="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
        <h3 class="text-xl font-bold text-red-600 mb-4">Xác nhận xóa</h3>
        <p class="text-coffee-700 mb-6">
          Bạn có chắc chắn muốn xóa nhân viên <strong>{{ showDeleteConfirm.full_name || showDeleteConfirm.username }}</strong>?
        </p>
        <div class="flex gap-3">
          <button @click="showDeleteConfirm = null" class="btn-secondary flex-1">Hủy</button>
          <button @click="doDelete" :disabled="deleting" class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 flex-1">
            {{ deleting ? 'Đang xóa...' : 'Xóa' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Employee Detail Modal -->
    <EmployeeDetailModal :show="showDetailModal" :user="selectedUser" @close="showDetailModal = false" @updated="fetchEmployees" />

    <!-- Set Schedule Modal -->
    <SetScheduleModal 
      :show="showScheduleModal" 
      :employee-id="scheduleEmployeeId" 
      :employee-name="scheduleEmployeeName"
      @close="showScheduleModal = false" 
      @success="handleScheduleSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { Plus, Trash2, User as UserIcon, Calendar } from 'lucide-vue-next'
import { userService, type User } from '../services/users'
import EmployeeDetailModal from '../components/EmployeeDetailModal.vue'
import SetScheduleModal from '../components/employees/SetScheduleModal.vue'

const toast = useToast()
const employees = ref<User[]>([])
const isLoading = ref(false)
const searchQuery = ref('')

// Computed stats
const cashiers = computed(() => employees.value.filter(e => e.role === 'cashier').length)
const waiters = computed(() => employees.value.filter(e => e.role === 'waiter').length)

const filteredEmployees = computed(() => {
  if (!searchQuery.value.trim()) return employees.value
  const query = searchQuery.value.toLowerCase()
  return employees.value.filter(emp =>
    emp.username.toLowerCase().includes(query) ||
    emp.email?.toLowerCase().includes(query) ||
    emp.first_name?.toLowerCase().includes(query) ||
    emp.last_name?.toLowerCase().includes(query) ||
    emp.full_name?.toLowerCase().includes(query)
  )
})

// Create state
const showCreate = ref(false)
const submitting = ref(false)
const createError = ref('')
const createForm = ref({
  username: '',
  password: '',
  first_name: '',
  last_name: '',
  email: '',
  role: 'waiter' as 'cashier' | 'waiter'
})

const isValidCreate = computed(() => {
  return (
    createForm.value.username.trim().length > 0 &&
    createForm.value.password.trim().length >= 6 &&
    createForm.value.first_name.trim().length > 0 &&
    createForm.value.last_name.trim().length > 0 &&
    createForm.value.email.trim().length > 0
  )
})

// Delete state
const showDeleteConfirm = ref<User | null>(null)
const deleting = ref(false)

// Detail modal state
const showDetailModal = ref(false)
const selectedUser = ref<User | null>(null)

// Schedule modal state
const showScheduleModal = ref(false)
const scheduleEmployeeId = ref(0)
const scheduleEmployeeName = ref('')

// Show detail modal
function showDetail(user: User) {
  selectedUser.value = user
  showDetailModal.value = true
}

// Open schedule modal
function openScheduleModal(user: User) {
  scheduleEmployeeId.value = user.id
  scheduleEmployeeName.value = user.full_name || `${user.first_name} ${user.last_name}`.trim()
  showScheduleModal.value = true
}

// Handle schedule success
function handleScheduleSuccess() {
  toast.success('Đã đặt lịch làm việc thành công!')
  showScheduleModal.value = false
}

// Fetch employees
async function fetchEmployees() {
  try {
    isLoading.value = true
    console.log('🔍 Fetching employees from /api/users/')
    const res: any = await userService.getAll({ page_size: 100 })
    console.log('✅ Employees response:', res)
    employees.value = Array.isArray(res) ? res : (res.results || [])
    console.log(`👥 Loaded ${employees.value.length} employees`)
  } catch (err: any) {
    console.error('❌ Employees fetch error:', err)
    console.error('Error response:', err?.response)
    console.error('Error data:', err?.response?.data)
    console.error('Error status:', err?.response?.status)
    toast.error('Không tải được danh sách nhân viên')
  } finally {
    isLoading.value = false
  }
}

let searchTimer: number | undefined
function onSearchInput() {
  if (searchTimer) window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => fetchEmployees(), 500)
}

// Create
async function submitCreate() {
  if (!isValidCreate.value) return
  try {
    submitting.value = true
    createError.value = ''
    await userService.create({
      username: createForm.value.username.trim(),
      password: createForm.value.password,
      first_name: createForm.value.first_name.trim(),
      last_name: createForm.value.last_name.trim(),
      email: createForm.value.email.trim(),
      role: createForm.value.role
    })
    await fetchEmployees()
    showCreate.value = false
    createForm.value = { username: '', password: '', first_name: '', last_name: '', email: '', role: 'waiter' }
    toast.success('Thêm nhân viên thành công')
  } catch (err: any) {
    createError.value = err?.response?.data?.message || err?.response?.data?.detail || 'Không thể tạo nhân viên'
    console.error('Create employee error:', err?.response?.data || err)
  } finally {
    submitting.value = false
  }
}

// Delete
function confirmDelete(emp: User) {
  showDeleteConfirm.value = emp
}

async function doDelete() {
  if (!showDeleteConfirm.value) return
  try {
    deleting.value = true
    const id = showDeleteConfirm.value.id
    await userService.delete(id)
    await fetchEmployees()
    showDeleteConfirm.value = null
    toast.success('Xóa nhân viên thành công')
  } catch (err: any) {
    toast.error(err?.response?.data?.message || err?.response?.data?.detail || 'Không thể xóa nhân viên')
    console.error('Delete employee error:', err?.response?.data || err)
  } finally {
    deleting.value = false
    showDeleteConfirm.value = null
  }
}

// Helper functions
function getRoleLabel(role: string): string {
  const roleMap: Record<string, string> = {
    admin: 'Admin',
    manager: 'Quản lý',
    cashier: 'Thu ngân',
    waiter: 'Phục vụ'
  }
  return roleMap[role] || role
}

function getRoleBadgeClass(role: string): string {
  const classMap: Record<string, string> = {
    admin: 'px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-semibold',
    manager: 'px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-semibold',
    cashier: 'px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-semibold',
    waiter: 'px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold'
  }
  return classMap[role] || 'px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-semibold'
}

onMounted(() => fetchEmployees())
</script>
