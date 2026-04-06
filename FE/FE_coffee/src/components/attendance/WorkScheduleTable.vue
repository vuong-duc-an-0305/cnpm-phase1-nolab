<template>
  <div class="work-schedule-table">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nhân viên</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ngày</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Giờ bắt đầu</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Giờ kết thúc</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Số giờ</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trạng thái</th>
            <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Thao tác</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-if="loading">
            <td colspan="7" class="px-4 py-8 text-center text-gray-500">
              <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <p class="mt-2">Đang tải...</p>
            </td>
          </tr>
          
          <tr v-else-if="schedules.length === 0">
            <td colspan="7" class="px-4 py-8 text-center text-gray-500">
              Không có lịch làm việc
            </td>
          </tr>
          
          <tr v-else v-for="schedule in schedules" :key="schedule.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 text-sm">
              <div class="font-medium">{{ schedule.employee_username }}</div>
              <div class="text-gray-500 text-xs">{{ schedule.employee_name }}</div>
            </td>
            <td class="px-4 py-3 text-sm">{{ formatDate(schedule.schedule_date) }}</td>
            <td class="px-4 py-3 text-sm">{{ schedule.shift_start_time }}</td>
            <td class="px-4 py-3 text-sm">{{ schedule.shift_end_time }}</td>
            <td class="px-4 py-3 text-sm">
              <span class="font-semibold">{{ formatHours(schedule.scheduled_hours) }}</span> giờ
            </td>
            <td class="px-4 py-3 text-sm">
              <span
                :class="[
                  'px-2 py-1 rounded-full text-xs',
                  schedule.is_active
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                ]"
              >
                {{ schedule.is_active ? 'Hoạt động' : 'Không hoạt động' }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm text-center">
              <div class="flex justify-center gap-2">
                <button
                  @click="$emit('edit', schedule)"
                  class="text-blue-600 hover:text-blue-800"
                  title="Sửa"
                >
                  <Edit2 :size="16" />
                </button>
                <button
                  v-if="!readonly"
                  @click="$emit('delete', schedule)"
                  class="text-red-600 hover:text-red-800"
                  title="Xóa"
                >
                  <Trash2 :size="16" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Edit2, Trash2 } from 'lucide-vue-next'
import type { WorkSchedule } from '@/services/attendance'

interface Props {
  schedules: WorkSchedule[]
  loading?: boolean
  readonly?: boolean
}

defineProps<Props>()

defineEmits<{
  edit: [schedule: WorkSchedule]
  delete: [schedule: WorkSchedule]
}>()

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('vi-VN')
}

function formatHours(hours: any): string {
  if (hours === null || hours === undefined) return 'N/A'
  const num = typeof hours === 'number' ? hours : parseFloat(hours)
  return isNaN(num) ? 'N/A' : num.toFixed(1)
}
</script>
