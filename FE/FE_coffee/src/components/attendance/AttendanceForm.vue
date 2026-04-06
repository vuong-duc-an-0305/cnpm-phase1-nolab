<template>
  <div class="attendance-form bg-white rounded-lg shadow p-6">
    <h3 class="text-lg font-semibold mb-4">
      {{ mode === 'check-in' ? 'Chấm công vào ca' : 'Chấm công ra ca' }}
    </h3>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- Employee selection (admin only) -->
      <div v-if="showEmployeeSelect">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Nhân viên <span class="text-red-500">*</span>
        </label>
        <select
          v-model="formData.employee"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">-- Chọn nhân viên --</option>
          <option v-for="emp in employees" :key="emp.id" :value="emp.id">
            {{ emp.username }} - {{ emp.first_name }} {{ emp.last_name }}
          </option>
        </select>
      </div>

      <!-- Date -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Ngày <span class="text-red-500">*</span>
        </label>
        <input
          v-model="formData.date"
          type="date"
          required
          :max="today"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <!-- Check-in time -->
      <div v-if="mode === 'check-in'">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Giờ vào <span class="text-red-500">*</span>
        </label>
        <input
          v-model="formData.check_in_time"
          type="time"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <!-- Check-out time -->
      <div v-if="mode === 'check-out'">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Giờ ra <span class="text-red-500">*</span>
        </label>
        <input
          v-model="formData.check_out_time"
          type="time"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        />
        
        <!-- Show calculated work hours -->
        <div v-if="calculatedHours !== null" class="mt-2 text-sm">
          <span class="text-gray-600">Số công ước tính: </span>
          <span :class="calculatedHours > 16 ? 'text-red-600 font-bold' : 'text-green-600 font-semibold'">
            {{ calculatedHours.toFixed(2) }} công
          </span>
          <span v-if="calculatedHours > 16" class="text-red-600 ml-2">
            (Vượt quá giới hạn 16 công/ngày!)
          </span>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="mode === 'check-in'">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Ghi chú
        </label>
        <textarea
          v-model="formData.notes"
          rows="3"
          placeholder="Ghi chú (tùy chọn)"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        ></textarea>
      </div>

      <!-- Quick time buttons -->
      <div class="flex gap-2">
        <button
          type="button"
          @click="setCurrentTime"
          class="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded"
        >
          <Clock :size="14" class="inline mr-1" />
          Giờ hiện tại
        </button>
        
        <button
          v-if="mode === 'check-in'"
          type="button"
          @click="setTime('08:00')"
          class="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded"
        >
          8:00
        </button>
        
        <button
          v-if="mode === 'check-out'"
          type="button"
          @click="setTime('17:00')"
          class="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded"
        >
          17:00
        </button>
      </div>

      <!-- Error message -->
      <div v-if="error" class="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded">
        {{ error }}
      </div>

      <!-- Action buttons -->
      <div class="flex gap-3 pt-2">
        <button
          type="submit"
          :disabled="submitting || (mode === 'check-out' && calculatedHours !== null && calculatedHours > 16)"
          class="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="submitting">Đang xử lý...</span>
          <span v-else>
            {{ mode === 'check-in' ? 'Chấm công vào' : 'Chấm công ra' }}
          </span>
        </button>
        
        <button
          type="button"
          @click="$emit('cancel')"
          class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Hủy
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Clock } from 'lucide-vue-next'
import attendanceService from '@/services/attendance'
import type { CheckInRequest, CheckOutRequest } from '@/services/attendance'
import { getCurrentDateInTimezone } from '@/utils/timezone'

interface Employee {
  id: number
  username: string
  first_name?: string
  last_name?: string
}

interface Props {
  mode: 'check-in' | 'check-out'
  employees?: Employee[]
  currentEmployeeId?: number
  showEmployeeSelect?: boolean
  existingRecord?: any
}

const props = withDefaults(defineProps<Props>(), {
  showEmployeeSelect: true,
})

const emit = defineEmits<{
  success: [data: any]
  cancel: []
}>()

const formData = ref({
  employee: props.currentEmployeeId || '',
  date: getCurrentDateInTimezone(),
  check_in_time: '',
  check_out_time: '',
  notes: '',
})

const submitting = ref(false)
const error = ref('')

const today = computed(() => getCurrentDateInTimezone())

// Calculate work hours for check-out
const calculatedHours = computed(() => {
  if (props.mode === 'check-out' && props.existingRecord?.check_in_time && formData.value.check_out_time) {
    const checkIn = parseTime(props.existingRecord.check_in_time)
    const checkOut = parseTime(formData.value.check_out_time)
    
    if (checkIn && checkOut) {
      let diff = checkOut - checkIn
      if (diff < 0) {
        diff += 24 * 60 * 60 * 1000 // Add 24 hours if check-out is next day
      }
      return diff / (1000 * 60 * 60) // Convert to hours
    }
  }
  return null
})

function parseTime(timeStr: string): number | null {
  const parts = timeStr.split(':')
  if (parts.length >= 2) {
    const hours = parseInt(parts[0] || '0')
    const minutes = parseInt(parts[1] || '0')
    const seconds = parts[2] ? parseInt(parts[2]) : 0
    return (hours * 60 * 60 + minutes * 60 + seconds) * 1000
  }
  return null
}

function setCurrentTime() {
  const now = new Date()
  const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
  
  if (props.mode === 'check-in') {
    formData.value.check_in_time = timeStr
  } else {
    formData.value.check_out_time = timeStr
  }
}

function setTime(time: string) {
  if (props.mode === 'check-in') {
    formData.value.check_in_time = time
  } else {
    formData.value.check_out_time = time
  }
}

async function handleSubmit() {
  error.value = ''
  submitting.value = true

  try {
    let response
    
    if (props.mode === 'check-in') {
      const data: CheckInRequest = {
        employee: Number(formData.value.employee),
        date: formData.value.date || '',
        check_in_time: formData.value.check_in_time + ':00',
        notes: formData.value.notes || undefined,
      }
      response = await attendanceService.checkIn(data)
    } else {
      const data: CheckOutRequest = {
        employee: Number(formData.value.employee),
        date: formData.value.date || '',
        check_out_time: formData.value.check_out_time + ':00',
      }
      response = await attendanceService.checkOut(data)
    }

    emit('success', response.data)
  } catch (err: any) {
    error.value = err.response?.data?.error || err.message || 'Có lỗi xảy ra'
  } finally {
    submitting.value = false
  }
}

// Set initial employee if provided
watch(() => props.currentEmployeeId, (newVal) => {
  if (newVal) {
    formData.value.employee = newVal
  }
}, { immediate: true })
</script>

<style scoped>
.attendance-form {
  max-width: 500px;
}
</style>
