<template>
  <div v-if="show && user" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto py-8" @click.self="$emit('close')">
    <div class="bg-white rounded-xl p-6 w-full max-w-2xl shadow-xl m-4 max-h-[90vh] overflow-y-auto">
      <h3 class="text-xl font-bold text-coffee-800 mb-6">
        Thông tin chi tiết nhân viên - {{ user.full_name || user.username }}
      </h3>

      <!-- Loading State -->
      <div v-if="loading" class="py-12 text-center text-coffee-600">Đang tải...</div>

      <!-- Form -->
      <div v-else class="space-y-6">
        <!-- Ảnh đại diện -->
        <div class="card p-4">
          <h4 class="text-sm font-semibold text-coffee-800 mb-3">Ảnh đại diện</h4>
          <div class="flex items-center gap-4">
            <div v-if="form.avatar" class="w-24 h-24 rounded-full overflow-hidden bg-coffee-100">
              <img :src="form.avatar" alt="Avatar" class="w-full h-full object-cover" />
            </div>
            <div v-else class="w-24 h-24 rounded-full bg-coffee-200 flex items-center justify-center text-coffee-600 text-2xl font-bold">
              {{ (user.full_name?.[0] || user.username[0] || '?').toUpperCase() }}
            </div>
            <div class="flex-1">
              <input v-model="form.avatar" type="url" class="input-field" placeholder="URL ảnh đại diện" />
              <p class="text-xs text-coffee-500 mt-1">Nhập URL ảnh (https://...)</p>
            </div>
          </div>
        </div>

        <!-- Thông tin cá nhân -->
        <div class="card p-4">
          <h4 class="text-sm font-semibold text-coffee-800 mb-3">Thông tin cá nhân</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-coffee-600 mb-1">Số điện thoại</label>
              <input v-model="form.phone_number" type="tel" class="input-field" placeholder="0987654321" />
            </div>
            <div>
              <label class="block text-sm text-coffee-600 mb-1">CCCD/CMND</label>
              <input v-model="form.citizen_id" class="input-field" placeholder="001234567890" />
            </div>
            <div>
              <label class="block text-sm text-coffee-600 mb-1">Giới tính</label>
              <select v-model="form.gender" class="input-field">
                <option value="MALE">Nam</option>
                <option value="FEMALE">Nữ</option>
                <option value="OTHER">Khác</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-coffee-600 mb-1">Ngày sinh</label>
              <input v-model="form.date_of_birth" type="date" class="input-field" />
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm text-coffee-600 mb-1">Địa chỉ</label>
              <textarea v-model="form.address" class="input-field" rows="2" placeholder="Số nhà, đường, phường/xã, quận/huyện, tỉnh/thành"></textarea>
            </div>
          </div>
        </div>

        <!-- Thông tin công việc -->
        <div class="card p-4">
          <h4 class="text-sm font-semibold text-coffee-800 mb-3">Thông tin công việc</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-coffee-600 mb-1">Vị trí công việc *</label>
              <select v-model="userRole" class="input-field">
                <option value="cashier">Thu ngân</option>
                <option value="waiter">Bồi bàn</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-coffee-600 mb-1">Lương cơ bản (VNĐ)</label>
              <input v-model.number="form.salary" type="number" class="input-field" placeholder="5000000" />
            </div>
            <div>
              <label class="block text-sm text-coffee-600 mb-1">Ngày vào làm</label>
              <input :value="formatDate(form.hire_date)" class="input-field" disabled />
            </div>
          </div>
        </div>

        <!-- Ghi chú -->
        <div class="card p-4">
          <h4 class="text-sm font-semibold text-coffee-800 mb-3">Ghi chú</h4>
          <textarea v-model="form.notes" class="input-field" rows="3" placeholder="Ghi chú về nhân viên..."></textarea>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
          {{ error }}
        </div>

        <!-- Actions -->
        <div class="flex gap-3 pt-2">
          <button @click="$emit('close')" class="btn-secondary flex-1">Đóng</button>
          <button @click="save" :disabled="saving" class="btn-primary flex-1">
            {{ saving ? 'Đang lưu...' : 'Lưu thay đổi' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { userService, type User, type EmployeeDetail } from '../services/users'

interface Props {
  show: boolean
  user: User | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  updated: []
}>()

const toast = useToast()
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const userRole = ref<'cashier' | 'waiter'>('waiter')

const form = ref<Partial<EmployeeDetail>>({
  avatar: '',
  phone_number: '',
  citizen_id: '',
  gender: 'OTHER',
  date_of_birth: '',
  address: '',
  salary: undefined,
  notes: ''
})

// Load employee detail khi modal mở
watch(() => props.show, async (newVal) => {
  if (newVal && props.user?.id) {
    await loadDetail()
  }
})

const loadDetail = async () => {
  if (!props.user) return
  
  try {
    loading.value = true
    error.value = ''
    const detail = await userService.getEmployeeDetail(props.user.id)
    
    // Load user role
    userRole.value = (props.user.role === 'cashier' || props.user.role === 'waiter') ? props.user.role : 'waiter'
    
    // Populate form
    form.value = {
      avatar: detail.avatar || '',
      phone_number: detail.phone_number || '',
      citizen_id: detail.citizen_id || '',
      gender: detail.gender || 'OTHER',
      date_of_birth: detail.date_of_birth || '',
      address: detail.address || '',
      hire_date: detail.hire_date,
      salary: detail.salary,
      notes: detail.notes || ''
    }
  } catch (err: any) {
    error.value = err.message || 'Không thể tải thông tin chi tiết'
  } finally {
    loading.value = false
  }
}

const save = async () => {
  if (!props.user) return
  
  try {
    saving.value = true
    error.value = ''
    
    // Cập nhật role trước
    if (userRole.value !== props.user.role) {
      await userService.update(props.user.id, { role: userRole.value })
    }
    
    // Chuẩn bị data (loại bỏ các field empty string)
    const data: any = {}
    Object.entries(form.value).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined && key !== 'hire_date') {
        data[key] = value
      }
    })
    
    await userService.updateEmployeeDetail(props.user.id, data)
    toast.success('Cập nhật thông tin chi tiết thành công')
    emit('updated')
    emit('close')
  } catch (err: any) {
    error.value = err.message || 'Không thể cập nhật thông tin'
    toast.error('Cập nhật thất bại')
  } finally {
    saving.value = false
  }
}

const formatDate = (date?: string) => {
  if (!date) return 'Chưa có'
  return new Date(date).toLocaleDateString('vi-VN')
}
</script>
