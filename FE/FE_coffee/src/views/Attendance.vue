<template>
  <div class="attendance-page p-6 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-800">Quản lý chấm công</h1>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow">
      <div class="border-b border-gray-200">
        <nav class="flex space-x-4 px-6" aria-label="Tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'py-4 px-4 border-b-2 font-medium text-sm transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            <component :is="tab.icon" :size="18" class="inline mr-2" />
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- Tab 1: Chấm công -->
        <div v-show="activeTab === 'attendance'" class="space-y-6">
          <!-- Filters -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Từ ngày</label>
              <input
                v-model="filters.start_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Đến ngày</label>
              <input
                v-model="filters.end_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Trạng thái</label>
              <select
                v-model="filters.status"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="">Tất cả</option>
                <option value="PRESENT">Có mặt</option>
                <option value="ABSENT">Vắng mặt</option>
                <option value="LATE">Đi muộn</option>
                <option value="OVERTIME">Tăng ca</option>
              </select>
            </div>
            <div class="flex items-end">
              <button
                @click="loadAttendanceRecords"
                class="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Tìm kiếm
              </button>
            </div>
          </div>

          <!-- Attendance table -->
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nhân viên</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ngày</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Giờ vào</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Giờ ra</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Số công</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trạng thái</th>
                  <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Thao tác</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-if="loading">
                  <td colspan="7" class="px-4 py-8 text-center text-gray-500">Đang tải...</td>
                </tr>
                <tr v-else-if="attendanceRecords.length === 0">
                  <td colspan="7" class="px-4 py-8 text-center text-gray-500">Không có dữ liệu</td>
                </tr>
                <tr v-else v-for="record in attendanceRecords" :key="record.id" class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-sm">{{ record.employee_username }}</td>
                  <td class="px-4 py-3 text-sm">{{ formatDate(record.date) }}</td>
                  <td class="px-4 py-3 text-sm">{{ formatTime(record.check_in_time) }}</td>
                  <td class="px-4 py-3 text-sm">{{ formatTime(record.check_out_time) }}</td>
                  <td class="px-4 py-3 text-sm font-semibold">{{ record.work_hours }}</td>
                  <td class="px-4 py-3 text-sm">
                    <span :class="getStatusClass(record.status)" class="px-2 py-1 rounded-full text-xs">
                      {{ record.status_display }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-center">
                    <div class="flex justify-center gap-2">
                      <button
                        v-if="!record.check_in_time"
                        @click="quickCheckIn(record)"
                        class="text-green-600 hover:text-green-800 px-2 py-1 rounded hover:bg-green-50"
                        title="Chấm công vào"
                      >
                        <Clock :size="16" class="inline" />
                        Vào ca
                      </button>
                      <button
                        v-else-if="record.check_in_time && !record.check_out_time"
                        @click="quickCheckOut(record)"
                        class="text-blue-600 hover:text-blue-800 px-2 py-1 rounded hover:bg-blue-50"
                        title="Kết ca"
                      >
                        <LogOut :size="16" class="inline" />
                        Kết ca
                      </button>
                      <span v-else class="text-gray-400 text-xs">Đã hoàn thành</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Tab 2: Lịch làm việc -->
        <div v-show="activeTab === 'schedule'" class="space-y-6">
          <ScheduleCalendar
            :schedules="workSchedules"
            @add-schedule="handleAddSchedule"
            @edit-schedule="handleEditSchedule"
          />
        </div>

        <!-- Tab 3: Báo cáo -->
        <div v-show="activeTab === 'report'" class="space-y-6">
          <SalaryCalculator :employees="employees" />
        </div>
      </div>
    </div>

    <!-- Schedule Form Modal -->
    <Teleport to="body">
      <div v-if="showScheduleModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
          <ScheduleForm
            :selected-date="selectedScheduleDate"
            :employees="employees"
            :schedule="selectedSchedule"
            @success="handleScheduleSuccess"
            @cancel="showScheduleModal = false"
          />
        </div>
      </div>
    </Teleport>

    <!-- Check-out Modal -->
    <Teleport to="body">
      <div v-if="showCheckOutModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <AttendanceForm
            mode="check-out"
            :employees="employees"
            :show-employee-select="false"
            :current-employee-id="selectedRecord?.employee"
            :existing-record="selectedRecord"
            @success="handleCheckOutSuccess"
            @cancel="showCheckOutModal = false"
          />
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Clock, Calendar, FileText, LogOut } from 'lucide-vue-next'
import AttendanceForm from '@/components/attendance/AttendanceForm.vue'
import ScheduleCalendar from '@/components/attendance/ScheduleCalendar.vue'
import ScheduleForm from '@/components/attendance/ScheduleForm.vue'
import SalaryCalculator from '@/components/attendance/SalaryCalculator.vue'
import attendanceService from '@/services/attendance'
import { userService } from '@/services/users'
import { useToast } from 'vue-toastification'
import { getCurrentDateInTimezone, addDays } from '@/utils/timezone'

const toast = useToast()

const tabs = [
  { id: 'attendance', name: 'Chấm công', icon: Clock },
  { id: 'schedule', name: 'Lịch làm việc', icon: Calendar },
  { id: 'report', name: 'Báo cáo & Tính lương', icon: FileText },
]

const activeTab = ref('attendance')
const loading = ref(false)
const showCheckOutModal = ref(false)
const showScheduleModal = ref(false)

const attendanceRecords = ref<any[]>([])
const workSchedules = ref<any[]>([])
const employees = ref<any[]>([])
const selectedRecord = ref<any>(null)
const selectedScheduleDate = ref('')
const selectedSchedule = ref<any>(null)

const filters = ref({
  start_date: addDays(getCurrentDateInTimezone(), -7),
  end_date: getCurrentDateInTimezone(),
  status: '',
})

async function loadAttendanceRecords() {
  try {
    loading.value = true
    const response = await attendanceService.getAttendanceRecords(filters.value)
    attendanceRecords.value = response.data.results || response.data || []
  } catch (error: any) {
    toast.error('Không thể tải dữ liệu chấm công')
  } finally {
    loading.value = false
  }
}

async function loadWorkSchedules() {
  try {
    loading.value = true
    const response = await attendanceService.getWorkSchedules({
      start_date: filters.value.start_date,
      end_date: filters.value.end_date,
    })
    workSchedules.value = response.data.results || response.data || []
  } catch (error: any) {
    toast.error('Không thể tải lịch làm việc')
  } finally {
    loading.value = false
  }
}

async function loadEmployees() {
  try {
    const response = await userService.getAll({ page_size: 100 })
    employees.value = response || []
  } catch (error: any) {
    toast.error('Không thể tải danh sách nhân viên')
  }
}

function openCheckOut(record: any) {
  selectedRecord.value = record
  showCheckOutModal.value = true
}

function handleCheckOutSuccess() {
  showCheckOutModal.value = false
  selectedRecord.value = null
  toast.success('Chấm công ra thành công!')
  loadAttendanceRecords()
}

async function quickCheckIn(record: any) {
  if (!record.id) return
  
  try {
    await attendanceService.quickCheckIn(record.id)
    toast.success('Chấm công vào thành công!')
    loadAttendanceRecords()
  } catch (error: any) {
    toast.error(error.response?.data?.error || 'Không thể chấm công vào')
  }
}

async function quickCheckOut(record: any) {
  if (!record.id) return
  
  try {
    await attendanceService.quickCheckOut(record.id)
    toast.success('Kết ca thành công! Công đã được tính.')
    loadAttendanceRecords()
  } catch (error: any) {
    toast.error(error.response?.data?.error || 'Không thể kết ca')
  }
}

function handleAddSchedule(date: string) {
  selectedScheduleDate.value = date
  selectedSchedule.value = null
  showScheduleModal.value = true
}

function handleEditSchedule(schedule: any) {
  const scheduleDate = schedule.schedule_date.split('T')[0]
  selectedScheduleDate.value = scheduleDate
  selectedSchedule.value = schedule
  showScheduleModal.value = true
}

function handleScheduleSuccess() {
  showScheduleModal.value = false
  selectedScheduleDate.value = ''
  selectedSchedule.value = null
  loadWorkSchedules()
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('vi-VN')
}

function formatTime(timeStr: string | null): string {
  if (!timeStr) return '-'
  // Cắt bỏ phần microseconds, chỉ giữ HH:MM:SS
  const parts = timeStr.split('.')
  return parts[0] || '-'
}

function getStatusClass(status: string): string {
  const classes: any = {
    PRESENT: 'bg-green-100 text-green-800',
    ABSENT: 'bg-red-100 text-red-800',
    LATE: 'bg-yellow-100 text-yellow-800',
    EARLY_LEAVE: 'bg-orange-100 text-orange-800',
    OVERTIME: 'bg-blue-100 text-blue-800',
    LEAVE: 'bg-gray-100 text-gray-800',
    SICK_LEAVE: 'bg-purple-100 text-purple-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

onMounted(() => {
  loadEmployees()
  loadAttendanceRecords()
  loadWorkSchedules()
})
</script>

<style scoped>
.attendance-page {
  min-height: calc(100vh - 4rem);
}
</style>
