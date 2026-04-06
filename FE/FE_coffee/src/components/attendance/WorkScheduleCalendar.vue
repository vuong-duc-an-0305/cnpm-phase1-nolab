<template>
  <div class="work-schedule-calendar">
    <!-- Header with view selector and navigation -->
    <div class="calendar-header">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-4">
          <h3 class="text-lg font-semibold">
            {{ viewMode === 'week' ? 'Lịch làm việc tuần' : 'Lịch làm việc tháng' }}
          </h3>
          <div class="flex gap-2">
            <button
              @click="viewMode = 'week'"
              :class="[
                'px-3 py-1 rounded text-sm',
                viewMode === 'week'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 hover:bg-gray-300'
              ]"
            >
              Tuần
            </button>
            <button
              @click="viewMode = 'month'"
              :class="[
                'px-3 py-1 rounded text-sm',
                viewMode === 'month'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 hover:bg-gray-300'
              ]"
            >
              Tháng
            </button>
          </div>
        </div>
        
        <div class="flex items-center gap-3">
          <button
            @click="previousPeriod"
            class="p-2 rounded hover:bg-gray-100"
            title="Kỳ trước"
          >
            <ChevronLeft :size="20" />
          </button>
          
          <div class="text-sm font-medium">
            {{ currentPeriodLabel }}
          </div>
          
          <button
            @click="nextPeriod"
            class="p-2 rounded hover:bg-gray-100"
            title="Kỳ sau"
          >
            <ChevronRight :size="20" />
          </button>
          
          <button
            @click="goToToday"
            class="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Hôm nay
          </button>
          
          <button
            v-if="!readonly"
            @click="$emit('add-schedule')"
            class="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600"
          >
            <Plus :size="16" class="inline mr-1" />
            Thêm ca
          </button>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="mt-2 text-gray-600">Đang tải...</p>
    </div>

    <!-- Calendar grid -->
    <div v-else class="calendar-grid">
      <!-- Week view -->
      <div v-if="viewMode === 'week'" class="week-view">
        <div class="grid grid-cols-8 gap-2">
          <!-- Header row -->
          <div class="font-semibold text-sm text-gray-600 p-2">Nhân viên</div>
          <div
            v-for="day in weekDays"
            :key="day.date"
            class="font-semibold text-sm text-center p-2"
            :class="{ 'text-blue-600': isToday(day.date) }"
          >
            <div>{{ day.dayName }}</div>
            <div class="text-xs text-gray-500">{{ formatDate(day.date) }}</div>
          </div>

          <!-- Employee rows -->
          <template v-for="employee in employees" :key="employee.id">
            <div class="p-2 border-r flex items-center">
              <span class="text-sm font-medium">{{ employee.username }}</span>
            </div>
            
            <div
              v-for="day in weekDays"
              :key="`${employee.id}-${day.date}`"
              class="border p-1 min-h-[60px]"
              :class="{ 'bg-blue-50': isToday(day.date) }"
            >
              <div
                v-for="schedule in getSchedulesForEmployeeAndDate(employee.id, day.date)"
                :key="schedule.id"
                @click="$emit('edit-schedule', schedule)"
                class="schedule-item mb-1 p-1 rounded text-xs cursor-pointer hover:opacity-80"
                :class="getScheduleClass(schedule)"
                :title="`${schedule.shift_start_time} - ${schedule.shift_end_time}`"
              >
                <div class="font-medium">
                  {{ schedule.shift_start_time?.substring(0, 5) }} - {{ schedule.shift_end_time?.substring(0, 5) }}
                </div>
                <div v-if="schedule.scheduled_hours" class="text-xs opacity-75">
                  {{ schedule.scheduled_hours }}h
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Month view -->
      <div v-else class="month-view">
        <div class="grid grid-cols-7 gap-1">
          <!-- Day names header -->
          <div
            v-for="dayName in ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']"
            :key="dayName"
            class="text-center font-semibold text-sm text-gray-600 p-2"
          >
            {{ dayName }}
          </div>

          <!-- Calendar days -->
          <div
            v-for="day in monthDays"
            :key="day.date"
            class="border min-h-[100px] p-2"
            :class="{
              'bg-gray-50': !day.isCurrentMonth,
              'bg-blue-50': isToday(day.date),
              'bg-white': day.isCurrentMonth && !isToday(day.date)
            }"
          >
            <div class="text-sm font-medium mb-1" :class="{ 'text-blue-600': isToday(day.date) }">
              {{ new Date(day.date).getDate() }}
            </div>
            
            <div class="space-y-1">
              <div
                v-for="schedule in getSchedulesForDate(day.date)"
                :key="schedule.id"
                @click="$emit('edit-schedule', schedule)"
                class="schedule-item p-1 rounded text-xs cursor-pointer hover:opacity-80"
                :class="getScheduleClass(schedule)"
                :title="`${schedule.employee_username}: ${schedule.shift_start_time} - ${schedule.shift_end_time}`"
              >
                <div class="font-medium truncate">{{ schedule.employee_username }}</div>
                <div class="text-xs opacity-75">
                  {{ schedule.shift_start_time?.substring(0, 5) }} - {{ schedule.shift_end_time?.substring(0, 5) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Legend -->
    <div class="mt-4 flex items-center gap-4 text-xs">
      <span class="font-medium">Chú thích:</span>
      <div class="flex items-center gap-1">
        <div class="w-4 h-4 rounded bg-green-100 border border-green-300"></div>
        <span>Ca sáng (6h-14h)</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="w-4 h-4 rounded bg-yellow-100 border border-yellow-300"></div>
        <span>Ca chiều (14h-22h)</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="w-4 h-4 rounded bg-purple-100 border border-purple-300"></div>
        <span>Ca tối (18h-02h)</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="w-4 h-4 rounded bg-blue-100 border border-blue-300"></div>
        <span>Ca khác</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ChevronLeft, ChevronRight, Plus } from 'lucide-vue-next'
import type { WorkSchedule } from '@/services/attendance'
import { 
  formatDateToYMD, 
  parseDateInTimezone, 
  getCurrentDateInTimezone,
  getNowInTimezone 
} from '@/utils/timezone'

interface Employee {
  id: number
  username: string
  first_name?: string
  last_name?: string
}

interface Props {
  schedules: WorkSchedule[]
  employees: Employee[]
  loading?: boolean
  readonly?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'add-schedule': []
  'edit-schedule': [schedule: WorkSchedule]
  'period-change': [startDate: string, endDate: string]
}>()

const viewMode = ref<'week' | 'month'>('week')
const currentDate = ref(getNowInTimezone())

// Week view computed properties
const weekDays = computed(() => {
  const days = []
  const start = getWeekStart(currentDate.value)
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(start)
    date.setDate(start.getDate() + i)
    days.push({
      date: formatDateToYMD(date),
      dayName: ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'][date.getDay()],
    })
  }
  
  return days
})

// Month view computed properties
const monthDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  
  // Start from Monday of the week containing the first day
  const startDate = getWeekStart(firstDay)
  
  // End on Sunday of the week containing the last day
  const endDate = new Date(lastDay)
  endDate.setDate(lastDay.getDate() + (7 - lastDay.getDay()))
  
  const days = []
  const current = new Date(startDate)
  
  while (current <= endDate) {
    days.push({
      date: formatDateToYMD(current),
      isCurrentMonth: current.getMonth() === month,
    })
    current.setDate(current.getDate() + 1)
  }
  
  return days
})

const currentPeriodLabel = computed(() => {
  if (viewMode.value === 'week') {
    const start = weekDays.value[0]
    const end = weekDays.value[6]
    if (start && end) {
      return `${formatDate(start.date)} - ${formatDate(end.date)}`
    }
    return ''
  } else {
    return `Tháng ${currentDate.value.getMonth() + 1}/${currentDate.value.getFullYear()}`
  }
})

// Helper functions
function getWeekStart(date: Date): Date {
  const d = new Date(date)
  const day = d.getDay()
  const diff = day === 0 ? -6 : 1 - day // Monday as start of week
  d.setDate(d.getDate() + diff)
  d.setHours(0, 0, 0, 0)
  return d
}

function formatDate(dateStr: string): string {
  const date = parseDateInTimezone(dateStr)
  return `${date.getDate()}/${date.getMonth() + 1}`
}

function isToday(dateStr: string): boolean {
  const today = getCurrentDateInTimezone()
  return dateStr === today
}

function getSchedulesForEmployeeAndDate(employeeId: number, date: string): WorkSchedule[] {
  return props.schedules.filter(
    s => s.employee === employeeId && s.schedule_date === date && s.is_active
  )
}

function getSchedulesForDate(date: string): WorkSchedule[] {
  return props.schedules.filter(s => s.schedule_date === date && s.is_active)
}

function getScheduleClass(schedule: WorkSchedule): string {
  // Determine shift type based on start time
  const startTime = schedule.shift_start_time || '0:0'
  const startHour = parseInt(startTime.split(':')[0] || '0')
  
  if (startHour >= 6 && startHour < 14) {
    return 'bg-green-100 border border-green-300 text-green-800'
  } else if (startHour >= 14 && startHour < 18) {
    return 'bg-yellow-100 border border-yellow-300 text-yellow-800'
  } else if (startHour >= 18 || startHour < 6) {
    return 'bg-purple-100 border border-purple-300 text-purple-800'
  } else {
    return 'bg-blue-100 border border-blue-300 text-blue-800'
  }
}

// Navigation functions
function previousPeriod() {
  if (viewMode.value === 'week') {
    currentDate.value.setDate(currentDate.value.getDate() - 7)
  } else {
    currentDate.value.setMonth(currentDate.value.getMonth() - 1)
  }
  currentDate.value = new Date(currentDate.value)
  emitPeriodChange()
}

function nextPeriod() {
  if (viewMode.value === 'week') {
    currentDate.value.setDate(currentDate.value.getDate() + 7)
  } else {
    currentDate.value.setMonth(currentDate.value.getMonth() + 1)
  }
  currentDate.value = new Date(currentDate.value)
  emitPeriodChange()
}

function goToToday() {
  currentDate.value = getNowInTimezone()
  emitPeriodChange()
}

function emitPeriodChange() {
  if (viewMode.value === 'week') {
    const startDay = weekDays.value[0]
    const endDay = weekDays.value[6]
    if (startDay && endDay) {
      emit('period-change', startDay.date, endDay.date)
    }
  } else {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth()
    const start = formatDateToYMD(new Date(year, month, 1))
    const end = formatDateToYMD(new Date(year, month + 1, 0))
    emit('period-change', start, end)
  }
}

// Watch for view mode changes
watch(viewMode, () => {
  emitPeriodChange()
})

// Initial period change
onMounted(() => {
  emitPeriodChange()
})
</script>

<style scoped>
.work-schedule-calendar {
  @apply bg-white rounded-lg shadow p-4;
}

.schedule-item {
  @apply transition-all duration-200;
}

.schedule-item:hover {
  @apply shadow-sm transform scale-105;
}

.week-view {
  @apply overflow-x-auto;
}

.month-view {
  @apply min-h-[600px];
}
</style>
