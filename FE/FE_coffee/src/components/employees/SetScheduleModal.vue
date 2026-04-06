<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="closeModal"></div>

      <!-- Modal panel -->
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start">
            <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
              <h3 class="text-lg font-medium leading-6 text-gray-900 mb-4">
                Đặt lịch làm việc cho {{ employeeName }}
              </h3>

              <form @submit.prevent="handleSubmit" class="space-y-4">
                <!-- Date -->
                <div>
                  <label for="schedule-date" class="block text-sm font-medium text-gray-700">
                    Ngày làm việc <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="schedule-date"
                    v-model="formData.schedule_date"
                    type="date"
                    required
                    class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <!-- Shift Start Time -->
                <div>
                  <label for="shift-start" class="block text-sm font-medium text-gray-700">
                    Giờ bắt đầu <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="shift-start"
                    v-model="formData.shift_start_time"
                    type="time"
                    required
                    class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <!-- Shift End Time -->
                <div>
                  <label for="shift-end" class="block text-sm font-medium text-gray-700">
                    Giờ kết thúc <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="shift-end"
                    v-model="formData.shift_end_time"
                    type="time"
                    required
                    class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <!-- Scheduled Hours (auto-calculated) -->
                <div v-if="scheduledHours" class="bg-blue-50 p-3 rounded-md">
                  <p class="text-sm text-blue-800">
                    <span class="font-medium">Số giờ dự kiến:</span> {{ scheduledHours }} giờ ({{ scheduledHours }} công)
                  </p>
                </div>

                <!-- Notes -->
                <div>
                  <label for="notes" class="block text-sm font-medium text-gray-700">
                    Ghi chú
                  </label>
                  <textarea
                    id="notes"
                    v-model="formData.notes"
                    rows="3"
                    class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Ghi chú về ca làm việc..."
                  ></textarea>
                </div>

                <!-- Error message -->
                <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
                  {{ error }}
                </div>
              </form>
            </div>
          </div>
        </div>

        <!-- Footer buttons -->
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button
            type="button"
            @click="handleSubmit"
            :disabled="submitting"
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="submitting">Đang lưu...</span>
            <span v-else>Lưu lịch</span>
          </button>
          <button
            type="button"
            @click="closeModal"
            :disabled="submitting"
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Hủy
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import attendanceService from '@/services/attendance'
import { useToast } from 'vue-toastification'
import { getCurrentDateInTimezone } from '@/utils/timezone'

const toast = useToast()

interface Props {
  show: boolean
  employeeId: number
  employeeName: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'success'): void
}>()

const formData = ref({
  schedule_date: '',
  shift_start_time: '',
  shift_end_time: '',
  notes: ''
})

const submitting = ref(false)
const error = ref('')

// Auto-calculate scheduled hours
const scheduledHours = computed(() => {
  if (!formData.value.shift_start_time || !formData.value.shift_end_time) {
    return null
  }

  const start = parseTime(formData.value.shift_start_time)
  const end = parseTime(formData.value.shift_end_time)

  if (start === null || end === null) {
    return null
  }

  let diff = end - start
  if (diff < 0) {
    // Cross midnight (e.g., 22:00 to 06:00)
    diff = (24 * 60 * 60 * 1000) + diff
  }

  const hours = diff / (60 * 60 * 1000)
  return Math.round(hours * 100) / 100 // Round to 2 decimal places
})

function parseTime(timeStr: string): number | null {
  if (!timeStr) return null
  const parts = timeStr.split(':')
  if (parts.length !== 2) return null
  const hours = parseInt(parts[0] || '0')
  const minutes = parseInt(parts[1] || '0')
  return (hours * 60 * 60 + minutes * 60) * 1000
}

async function handleSubmit() {
  error.value = ''
  
  if (!formData.value.schedule_date || !formData.value.shift_start_time || !formData.value.shift_end_time) {
    error.value = 'Vui lòng điền đầy đủ thông tin bắt buộc'
    return
  }

  // Validate scheduled hours
  if (scheduledHours.value && scheduledHours.value > 16) {
    error.value = 'Số giờ làm việc không được vượt quá 16 giờ/ngày'
    return
  }

  try {
    submitting.value = true
    
    await attendanceService.createWorkSchedule({
      employee: props.employeeId,
      schedule_date: formData.value.schedule_date,
      shift_start_time: formData.value.shift_start_time + ':00',
      shift_end_time: formData.value.shift_end_time + ':00',
      notes: formData.value.notes || undefined,
      is_active: true
    })

    toast.success('Đã đặt lịch làm việc thành công!')
    emit('success')
    closeModal()
  } catch (err: any) {
    console.error('Error creating work schedule:', err)
    error.value = err.response?.data?.detail || err.response?.data?.error || 'Có lỗi xảy ra khi đặt lịch'
  } finally {
    submitting.value = false
  }
}

function closeModal() {
  if (!submitting.value) {
    resetForm()
    emit('close')
  }
}

function resetForm() {
  formData.value = {
    schedule_date: '',
    shift_start_time: '',
    shift_end_time: '',
    notes: ''
  }
  error.value = ''
}

// Set default date to today when modal opens
watch(() => props.show, (newVal) => {
  if (newVal) {
    const today = getCurrentDateInTimezone()
    if (today) {
      formData.value.schedule_date = today
    }
  }
})
</script>

<style scoped>
/* Modal animation */
.fixed {
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
