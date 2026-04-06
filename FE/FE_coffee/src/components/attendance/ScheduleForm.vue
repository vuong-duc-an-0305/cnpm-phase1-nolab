<template>
  <div class="schedule-form">
    <h3 class="text-lg font-semibold text-gray-800 mb-4">
      {{ editMode ? 'Sửa lịch làm việc' : 'Thêm lịch làm việc' }} - {{ formatDateDisplay(selectedDate) }}
    </h3>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- Chọn nhân viên -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Nhân viên <span class="text-red-500">*</span>
        </label>
        <select
          v-model="formData.employee"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">-- Chọn nhân viên --</option>
          <option
            v-for="emp in employees"
            :key="emp.id"
            :value="emp.id"
          >
            {{ emp.username }} - {{ emp.employee_detail?.full_name || 'N/A' }}
          </option>
        </select>
      </div>

      <!-- Giờ bắt đầu -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Giờ bắt đầu <span class="text-red-500">*</span>
          </label>
          <input
            v-model="formData.shift_start_time"
            type="time"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <!-- Giờ kết thúc -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Giờ kết thúc <span class="text-red-500">*</span>
          </label>
          <input
            v-model="formData.shift_end_time"
            type="time"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <!-- Số giờ dự kiến (tự động tính) -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Số giờ dự kiến
        </label>
        <div class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md text-gray-700">
          {{ calculatedHours }} giờ
        </div>
      </div>

      <!-- Ghi chú -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Ghi chú
        </label>
        <textarea
          v-model="formData.notes"
          rows="3"
          placeholder="Nhập ghi chú nếu có..."
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        ></textarea>
      </div>

      <!-- Buttons -->
      <div class="flex justify-end gap-3 pt-2">
        <button
          type="button"
          @click="$emit('cancel')"
          class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
        >
          Hủy
        </button>
        <button
          type="submit"
          :disabled="submitting"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="submitting">Đang lưu...</span>
          <span v-else>
            <Plus :size="16" class="inline mr-1" />
            Thêm lịch
          </span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { Plus } from 'lucide-vue-next'
import { formatDateDisplay } from '@/utils/timezone'
import attendanceService from '@/services/attendance'
import type { WorkSchedule } from '@/services/attendance'
import { useToast } from 'vue-toastification'

interface Props {
  selectedDate: string
  employees: any[]
  schedule?: WorkSchedule | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  success: []
  cancel: []
}>()

const toast = useToast()
const submitting = ref(false)
const editMode = computed(() => !!props.schedule)

const formData = ref({
  employee: '',
  shift_start_time: '08:00',
  shift_end_time: '17:00',
  is_active: true,
  notes: ''
})

// Tính số giờ làm việc tự động
const calculatedHours = computed(() => {
  const start = formData.value.shift_start_time
  const end = formData.value.shift_end_time
  
  if (!start || !end) return 0
  
  const [startHour, startMin] = start.split(':').map(Number)
  const [endHour, endMin] = end.split(':').map(Number)
  
  const startMinutes = (startHour ?? 0) * 60 + (startMin ?? 0)
  const endMinutes = (endHour ?? 0) * 60 + (endMin ?? 0)
  
  let diffMinutes = endMinutes - startMinutes
  if (diffMinutes < 0) {
    diffMinutes += 24 * 60 // Xử lý ca đêm
  }
  
  return (diffMinutes / 60).toFixed(1)
})

async function handleSubmit() {
  try {
    submitting.value = true
    
    const payload = {
      employee: Number(formData.value.employee),
      schedule_date: props.selectedDate,
      shift_start_time: formData.value.shift_start_time,
      shift_end_time: formData.value.shift_end_time,
      scheduled_hours: typeof calculatedHours.value === 'string' ? parseFloat(calculatedHours.value) : calculatedHours.value,
      is_active: formData.value.is_active,
      notes: formData.value.notes
    }
    
    if (editMode.value && props.schedule?.id) {
      await attendanceService.updateWorkSchedule(props.schedule.id, payload as any)
      toast.success('Cập nhật lịch làm việc thành công!')
    } else {
      await attendanceService.createWorkSchedule(payload as any)
      toast.success('Thêm lịch làm việc thành công!')
    }
    
    emit('success')
    
    // Reset form nếu không phải edit mode
    if (!editMode.value) {
      formData.value = {
        employee: '',
        shift_start_time: '08:00',
        shift_end_time: '17:00',
        is_active: true,
        notes: ''
      }
    }
  } catch (error: any) {
    const action = editMode.value ? 'cập nhật' : 'thêm'
    toast.error(error.response?.data?.error || `Không thể ${action} lịch làm việc`)
  } finally {
    submitting.value = false
  }
}

// Load dữ liệu schedule khi edit
onMounted(() => {
  if (props.schedule) {
    formData.value = {
      employee: String(props.schedule.employee),
      shift_start_time: props.schedule.shift_start_time,
      shift_end_time: props.schedule.shift_end_time,
      is_active: props.schedule.is_active,
      notes: props.schedule.notes || ''
    }
  }
})

// Reset form khi thay đổi ngày hoặc schedule
watch([() => props.selectedDate, () => props.schedule], () => {
  if (props.schedule) {
    formData.value = {
      employee: String(props.schedule.employee),
      shift_start_time: props.schedule.shift_start_time,
      shift_end_time: props.schedule.shift_end_time,
      is_active: props.schedule.is_active,
      notes: props.schedule.notes || ''
    }
  } else {
    formData.value = {
      employee: '',
      shift_start_time: '08:00',
      shift_end_time: '17:00',
      is_active: true,
      notes: ''
    }
  }
})
</script>

<style scoped>
.schedule-form {
  width: 100%;
}
</style>
