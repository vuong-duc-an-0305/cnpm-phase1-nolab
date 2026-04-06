<template>
  <div class="schedule-calendar">
    <!-- Header với điều khiển -->
    <div class="bg-white rounded-lg shadow p-4 mb-4">
      <div class="flex items-center justify-between">
        <!-- Navigation -->
        <div class="flex items-center gap-2">
          <button
            @click="previousPeriod"
            class="p-2 hover:bg-gray-100 rounded-lg transition"
            title="Trước"
          >
            <ChevronLeft :size="20" />
          </button>
          <button
            @click="goToToday"
            class="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition"
          >
            Hôm nay
          </button>
          <button
            @click="nextPeriod"
            class="p-2 hover:bg-gray-100 rounded-lg transition"
            title="Sau"
          >
            <ChevronRight :size="20" />
          </button>
        </div>

        <!-- Tiêu đề hiển thị -->
        <h2 class="text-lg font-semibold text-gray-800">
          {{ displayTitle }}
        </h2>

        <!-- Toggle view tuần/tháng -->
        <div class="flex items-center gap-2">
          <button
            @click="viewMode = 'week'"
            :class="[
              'px-4 py-2 text-sm font-medium rounded-lg transition',
              viewMode === 'week'
                ? 'bg-blue-600 text-white'
                : 'text-gray-700 hover:bg-gray-100'
            ]"
          >
            <Calendar :size="16" class="inline mr-1" />
            Tuần
          </button>
          <button
            @click="viewMode = 'month'"
            :class="[
              'px-4 py-2 text-sm font-medium rounded-lg transition',
              viewMode === 'month'
                ? 'bg-blue-600 text-white'
                : 'text-gray-700 hover:bg-gray-100'
            ]"
          >
            <CalendarDays :size="16" class="inline mr-1" />
            Tháng
          </button>
        </div>
      </div>
    </div>

    <!-- Calendar Grid -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <!-- Tuần view -->
      <div v-if="viewMode === 'week'" class="grid grid-cols-7 border-b">
        <div
          v-for="day in weekDays"
          :key="day.date"
          class="border-r last:border-r-0"
        >
          <div class="p-3 bg-gray-50 text-center">
            <div class="text-xs font-medium text-gray-600">{{ day.dayName }}</div>
            <div
              :class="[
                'text-lg font-semibold mt-1',
                day.isToday ? 'text-blue-600' : 'text-gray-800'
              ]"
            >
              {{ day.dayNumber }}
            </div>
          </div>
          
          <!-- Lịch làm việc của ngày -->
          <div class="p-2 min-h-[200px] bg-gray-50/50">
            <div
              v-for="schedule in getSchedulesForDate(day.date)"
              :key="schedule.id"
              @click="handleScheduleClick(schedule, day.date)"
              :class="[
                'mb-2 p-2 bg-blue-50 border border-blue-200 rounded text-xs transition',
                canEditSchedule(schedule, day.date) ? 'cursor-pointer hover:bg-blue-100 hover:border-blue-300' : 'opacity-60 cursor-not-allowed'
              ]"
            >
              <div class="font-medium text-blue-900">{{ schedule.employee_username }}</div>
              <div class="text-blue-700">
                {{ schedule.shift_start_time }} - {{ schedule.shift_end_time }}
              </div>
            </div>
            
            <!-- Nút thêm lịch -->
            <button
              @click="$emit('add-schedule', day.date)"
              class="w-full py-2 mt-2 text-xs text-green-600 hover:bg-green-50 border border-green-200 border-dashed rounded transition"
            >
              <Plus :size="14" class="inline mr-1" />
              Thêm lịch
            </button>
          </div>
        </div>
      </div>

      <!-- Tháng view -->
      <div v-else class="p-4">
        <!-- Headers -->
        <div class="grid grid-cols-7 gap-2 mb-2">
          <div
            v-for="dayName in ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']"
            :key="dayName"
            class="text-center text-sm font-medium text-gray-600 py-2"
          >
            {{ dayName }}
          </div>
        </div>

        <!-- Days grid -->
        <div class="grid grid-cols-7 gap-2">
          <div
            v-for="day in monthDays"
            :key="day.date"
            :class="[
              'min-h-[120px] border rounded-lg p-2',
              day.isCurrentMonth ? 'bg-white' : 'bg-gray-50',
              day.isToday ? 'border-blue-500 border-2' : 'border-gray-200'
            ]"
          >
            <div
              :class="[
                'text-sm font-semibold mb-2',
                day.isToday ? 'text-blue-600' : day.isCurrentMonth ? 'text-gray-800' : 'text-gray-400'
              ]"
            >
              {{ day.dayNumber }}
            </div>

            <!-- Lịch làm việc của ngày -->
            <div class="space-y-1">
              <div
                v-for="schedule in getSchedulesForDate(day.date).slice(0, 2)"
                :key="schedule.id"
                @click="handleScheduleClick(schedule, day.date)"
                :class="[
                  'p-1 bg-blue-50 border border-blue-200 rounded text-xs truncate transition',
                  canEditSchedule(schedule, day.date) ? 'cursor-pointer hover:bg-blue-100 hover:border-blue-300' : 'opacity-60 cursor-not-allowed'
                ]"
              >
                <div class="font-medium text-blue-900">{{ schedule.employee_username }}</div>
              </div>
              <div
                v-if="getSchedulesForDate(day.date).length > 2"
                class="text-xs text-gray-500 text-center"
              >
                +{{ getSchedulesForDate(day.date).length - 2 }} khác
              </div>
            </div>

            <!-- Nút thêm lịch -->
            <button
              v-if="day.isCurrentMonth"
              @click="$emit('add-schedule', day.date)"
              class="w-full py-1 mt-2 text-xs text-green-600 hover:bg-green-50 border border-green-200 border-dashed rounded transition"
            >
              <Plus :size="12" class="inline" />
              Thêm
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ChevronLeft, ChevronRight, Calendar, CalendarDays, Plus } from 'lucide-vue-next'
import { getCurrentDateInTimezone, getWeekStart, getWeekEnd, getMonthStart, getMonthEnd, addDays, addMonths, parseDateInTimezone, formatDateToYMD, isToday } from '@/utils/timezone'
import type { WorkSchedule } from '@/services/attendance'

interface Props {
  schedules: WorkSchedule[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'add-schedule': [date: string]
  'edit-schedule': [schedule: WorkSchedule]
}>()

const viewMode = ref<'week' | 'month'>('week')
const currentDate = ref(getCurrentDateInTimezone())

// Tiêu đề hiển thị
const displayTitle = computed(() => {
  const date = parseDateInTimezone(currentDate.value)
  const month = date.getMonth() + 1
  const year = date.getFullYear()
  
  if (viewMode.value === 'week') {
    const weekStart = getWeekStart(currentDate.value)
    const weekEnd = getWeekEnd(currentDate.value)
    const startDate = parseDateInTimezone(weekStart)
    const endDate = parseDateInTimezone(weekEnd)
    
    if (startDate.getMonth() === endDate.getMonth()) {
      return `Tuần ${startDate.getDate()} - ${endDate.getDate()} Tháng ${month}/${year}`
    } else {
      return `Tuần ${startDate.getDate()}/${startDate.getMonth() + 1} - ${endDate.getDate()}/${endDate.getMonth() + 1}, ${year}`
    }
  } else {
    return `Tháng ${month}/${year}`
  }
})

// Dữ liệu cho tuần view
const weekDays = computed(() => {
  const weekStart = getWeekStart(currentDate.value)
  const days = []
  
  for (let i = 0; i < 7; i++) {
    const date = addDays(weekStart, i)
    const dateObj = parseDateInTimezone(date)
    days.push({
      date,
      dayName: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'][i],
      dayNumber: dateObj.getDate(),
      isToday: isToday(date)
    })
  }
  
  return days
})

// Dữ liệu cho tháng view
const monthDays = computed(() => {
  const date = parseDateInTimezone(currentDate.value)
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  
  const monthStart = getMonthStart(year, month)
  const monthEnd = getMonthEnd(year, month)
  
  const startDate = parseDateInTimezone(monthStart)
  const endDate = parseDateInTimezone(monthEnd)
  
  // Tìm ngày đầu tiên của tuần chứa ngày 1
  const firstDayOfWeek = startDate.getDay()
  const daysFromPreviousMonth = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1
  
  // Tìm ngày cuối cùng của tuần chứa ngày cuối tháng
  const lastDayOfWeek = endDate.getDay()
  const daysFromNextMonth = lastDayOfWeek === 0 ? 0 : 7 - lastDayOfWeek
  
  const days = []
  
  // Thêm ngày từ tháng trước
  for (let i = daysFromPreviousMonth; i > 0; i--) {
    const date = addDays(monthStart, -i)
    const dateObj = parseDateInTimezone(date)
    days.push({
      date,
      dayNumber: dateObj.getDate(),
      isCurrentMonth: false,
      isToday: isToday(date)
    })
  }
  
  // Thêm ngày trong tháng
  const daysInMonth = endDate.getDate()
  for (let i = 0; i < daysInMonth; i++) {
    const date = addDays(monthStart, i)
    const dateObj = parseDateInTimezone(date)
    days.push({
      date,
      dayNumber: dateObj.getDate(),
      isCurrentMonth: true,
      isToday: isToday(date)
    })
  }
  
  // Thêm ngày từ tháng sau
  for (let i = 1; i <= daysFromNextMonth; i++) {
    const date = addDays(monthEnd, i)
    const dateObj = parseDateInTimezone(date)
    days.push({
      date,
      dayNumber: dateObj.getDate(),
      isCurrentMonth: false,
      isToday: isToday(date)
    })
  }
  
  return days
})

// Lấy lịch làm việc cho một ngày cụ thể
function getSchedulesForDate(date: string): WorkSchedule[] {
  return props.schedules.filter(schedule => {
    const scheduleDate = schedule.schedule_date.split('T')[0]
    return scheduleDate === date
  })
}

// Kiểm tra xem có thể sửa lịch không (chưa đến giờ bắt đầu ca)
function canEditSchedule(schedule: WorkSchedule, date: string): boolean {
  const now = new Date()
  const scheduleDateTime = new Date(`${date}T${schedule.shift_start_time}`)
  return now < scheduleDateTime
}

// Xử lý click vào lịch
function handleScheduleClick(schedule: WorkSchedule, date: string) {
  if (canEditSchedule(schedule, date)) {
    emit('edit-schedule', schedule)
  }
}

// Navigation functions
function previousPeriod() {
  if (viewMode.value === 'week') {
    currentDate.value = addDays(currentDate.value, -7)
  } else {
    currentDate.value = addMonths(currentDate.value, -1)
  }
}

function nextPeriod() {
  if (viewMode.value === 'week') {
    currentDate.value = addDays(currentDate.value, 7)
  } else {
    currentDate.value = addMonths(currentDate.value, 1)
  }
}

function goToToday() {
  currentDate.value = getCurrentDateInTimezone()
}

// Watch để emit event khi thay đổi khoảng thời gian
watch([currentDate, viewMode], () => {
  // Parent component có thể listen để load schedules
}, { immediate: true })
</script>

<style scoped>
.schedule-calendar {
  width: 100%;
}
</style>
