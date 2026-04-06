<template>
  <div class="salary-calculator bg-white rounded-lg shadow p-6">
    <h3 class="text-lg font-semibold mb-4">Tính lương nhân viên</h3>

    <form @submit.prevent="calculate" class="space-y-4">
      <!-- Month and Year -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Tháng <span class="text-red-500">*</span>
          </label>
          <select v-model="formData.month" required class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option v-for="m in 12" :key="m" :value="m">Tháng {{ m }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Năm <span class="text-red-500">*</span>
          </label>
          <select v-model="formData.year" required class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
      </div>

      <!-- Employee selection with checkboxes -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-gray-700">
            Chọn nhân viên <span class="text-red-500">*</span>
          </label>
          <button
            type="button"
            @click="toggleSelectAll"
            class="text-xs text-blue-600 hover:text-blue-800"
          >
            {{ isAllSelected ? 'Bỏ chọn tất cả' : 'Chọn tất cả' }}
          </button>
        </div>
        <div class="border border-gray-300 rounded-md p-3 max-h-48 overflow-y-auto space-y-2">
          <label
            v-for="emp in employees"
            :key="emp.id"
            class="flex items-center hover:bg-gray-50 p-2 rounded cursor-pointer"
          >
            <input
              type="checkbox"
              :value="emp.id"
              v-model="selectedEmployees"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            />
            <span class="ml-2 text-sm">{{ emp.username }} - {{ emp.first_name }} {{ emp.last_name }}</span>
          </label>
          <div v-if="employees.length === 0" class="text-sm text-gray-500 text-center py-2">
            Không có nhân viên
          </div>
        </div>
        <div v-if="selectedEmployees.length > 0" class="text-xs text-gray-600 mt-1">
          Đã chọn {{ selectedEmployees.length }} nhân viên
        </div>
      </div>

      <!-- Bonus for each employee -->
      <div v-if="selectedEmployees.length > 0">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Thưởng (tùy chọn)
        </label>
        <div class="border border-gray-300 rounded-md p-3 max-h-64 overflow-y-auto space-y-3">
          <div
            v-for="empId in selectedEmployees"
            :key="empId"
            class="flex items-center justify-between gap-2 p-2 bg-gray-50 rounded"
          >
            <label class="text-sm font-medium text-gray-700 flex-1">
              {{ getEmployeeName(empId) }}
            </label>
            <input
              v-model.number="employeeBonuses[empId]"
              type="number"
              min="0"
              step="1000"
              placeholder="0"
              class="w-32 px-2 py-1 text-sm border border-gray-300 rounded-md"
            />
          </div>
        </div>
      </div>

      <div class="flex gap-2">
        <button
          type="submit"
          :disabled="calculating || selectedEmployees.length === 0"
          class="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {{ calculating ? 'Đang tính...' : 'Tính lương' }}
        </button>
        <button
          v-if="results.length > 0"
          type="button"
          @click="exportToExcel"
          :disabled="exporting"
          class="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50"
        >
          <Download :size="16" class="inline mr-1" />
          {{ exporting ? 'Đang xuất...' : 'Xuất Excel' }}
        </button>
      </div>
    </form>

    <!-- Results Table -->
    <div v-if="results.length > 0" class="mt-6">
      <div class="border-t pt-4">
        <h4 class="font-semibold mb-3">Kết quả tính lương ({{ results.length }} nhân viên)</h4>
        
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Nhân viên</th>
                <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Lương CB</th>
                <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Số công</th>
                <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Tỷ lệ</th>
                <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Thưởng</th>
                <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Tổng lương</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Ghi chú</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(res, idx) in results" :key="idx" class="hover:bg-gray-50">
                <td class="px-4 py-2 text-sm">{{ res.employee_name }}</td>
                <td class="px-4 py-2 text-sm text-right">{{ formatCurrency(res.base_salary) }}</td>
                <td class="px-4 py-2 text-sm text-right">{{ res.actual_work_hours }} / {{ res.max_work_hours_in_month }}</td>
                <td class="px-4 py-2 text-sm text-right">{{ res.work_hours_percentage }}%</td>
                <td class="px-4 py-2 text-sm text-right text-green-600">{{ formatCurrency(res.bonus) }}</td>
                <td class="px-4 py-2 text-sm text-right font-semibold text-blue-600">{{ formatCurrency(res.final_salary) }}</td>
                <td class="px-4 py-2 text-xs text-gray-600">
                  <div v-if="res.details">
                    <div v-if="res.details.total_days_late > 0" class="text-yellow-600">Muộn: {{ res.details.total_days_late }} lần</div>
                    <div v-if="res.details.early_leave_count > 0" class="text-orange-600">Về sớm: {{ res.details.early_leave_count }} lần</div>
                    <div v-if="res.details.total_days_absent > 0" class="text-red-600">Nghỉ: {{ res.details.total_days_absent }} lần</div>
                  </div>
                  <span v-else class="text-gray-400">-</span>
                </td>
              </tr>
            </tbody>
            <tfoot class="bg-gray-50">
              <tr>
                <td colspan="5" class="px-4 py-2 text-sm font-semibold text-right">Tổng cộng:</td>
                <td class="px-4 py-2 text-sm font-bold text-right text-blue-600">{{ formatCurrency(totalSalary) }}</td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- Details -->
        <div class="mt-4 p-3 bg-gray-50 rounded text-xs">
          <div><strong>Ghi chú:</strong></div>
          <div>• Bảng lương được tính cho tháng {{ formData.month }}/{{ formData.year }}</div>
          <div>• Nhấn "Xuất Excel" để tải file bảng lương chi tiết</div>
        </div>
      </div>
    </div>

    <!-- Old single result (keep for backward compatibility) -->
    <div v-else-if="result" class="mt-6 space-y-4">
      <div class="border-t pt-4">
        <h4 class="font-semibold mb-3">Kết quả tính lương</h4>
        
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600">Lương cơ bản:</span>
            <span class="font-medium">{{ formatCurrency(result.base_salary) }}</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-600">Số công thực tế:</span>
            <span class="font-medium">{{ result.actual_work_hours }} công</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-600">Số công tối đa trong tháng:</span>
            <span class="font-medium">{{ result.max_work_hours_in_month }} công</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-600">Tỷ lệ công:</span>
            <span class="font-medium">{{ result.work_hours_percentage }}%</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-600">Lương tính theo công:</span>
            <span class="font-medium">{{ formatCurrency(result.calculated_salary) }}</span>
          </div>
          
          <div v-if="result.bonus > 0" class="flex justify-between">
            <span class="text-gray-600">Thưởng:</span>
            <span class="font-medium text-green-600">+ {{ formatCurrency(result.bonus) }}</span>
          </div>
          
          <div class="flex justify-between pt-3 border-t-2 border-gray-300">
            <span class="font-semibold text-lg">Lương cuối cùng:</span>
            <span class="font-bold text-xl text-blue-600">{{ formatCurrency(result.final_salary) }}</span>
          </div>
        </div>

        <!-- Details -->
        <div class="mt-4 p-3 bg-gray-50 rounded text-xs space-y-1">
          <div><strong>Chi tiết chấm công:</strong></div>
          <div>• Ngày có mặt: {{ result.details?.total_days_present }} ngày</div>
          <div>• Ngày vắng mặt: {{ result.details?.total_days_absent }} ngày</div>
          <div>• Ngày đi muộn: {{ result.details?.total_days_late }} ngày</div>
          <div>• Trung bình giờ/ngày: {{ result.details?.average_work_hours_per_day }} giờ</div>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="mt-4 bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded text-sm">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Download } from 'lucide-vue-next'
import attendanceService from '@/services/attendance'
import type { SalaryCalculation } from '@/services/attendance'
import { useToast } from 'vue-toastification'
import * as XLSX from 'xlsx'
import { formatDateDisplay } from '@/utils/timezone'

const toast = useToast()

interface Employee {
  id: number
  username: string
  first_name?: string
  last_name?: string
}

interface Props {
  employees: Employee[]
}

const props = defineProps<Props>()

const formData = ref({
  month: new Date().getMonth() + 1,
  year: new Date().getFullYear(),
})

const selectedEmployees = ref<number[]>([])
const employeeBonuses = ref<Record<number, number>>({})
const calculating = ref(false)
const exporting = ref(false)
const result = ref<SalaryCalculation | null>(null)
const results = ref<(SalaryCalculation & { employee_name: string })[]>([])
const error = ref('')

const years = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => currentYear - i)
})

const isAllSelected = computed(() => {
  return selectedEmployees.value.length === props.employees.length && props.employees.length > 0
})

const totalSalary = computed(() => {
  if (!results.value || results.value.length === 0) {
    return 0
  }
  const total = results.value.reduce((sum, r) => {
    const salary = Number(r?.final_salary) || 0
    return sum + salary
  }, 0)
  console.log('Total Salary Calculation:', { results: results.value, total })
  return total
})

function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedEmployees.value = []
  } else {
    selectedEmployees.value = props.employees.map(e => e.id)
  }
}

function getEmployeeName(empId: number): string {
  const employee = props.employees.find(e => e.id === empId)
  return employee ? `${employee.username} - ${employee.first_name || ''} ${employee.last_name || ''}` : ''
}

async function calculate() {
  if (selectedEmployees.value.length === 0) {
    toast.warning('Vui lòng chọn ít nhất một nhân viên')
    return
  }

  error.value = ''
  result.value = null
  results.value = []
  calculating.value = true

  try {
    const promises = selectedEmployees.value.map(async (empId) => {
      const bonus = employeeBonuses.value[empId] || 0
      const response = await attendanceService.calculateSalary(
        empId,
        formData.value.month,
        formData.value.year,
        bonus || undefined
      )
      const employee = props.employees.find(e => e.id === empId)
      return {
        ...response.data,
        employee_name: `${employee?.username || ''} - ${employee?.first_name || ''} ${employee?.last_name || ''}`
      }
    })

    results.value = await Promise.all(promises)
    toast.success(`Tính lương thành công cho ${results.value.length} nhân viên`)
  } catch (err: any) {
    error.value = err.response?.data?.error || err.message || 'Có lỗi xảy ra'
    toast.error(error.value)
  } finally {
    calculating.value = false
  }
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND'
  }).format(value)
}

function exportToExcel() {
  try {
    exporting.value = true

    const today = new Date().toISOString().split('T')[0] || ''
    
    // Tạo worksheet data
    const worksheetData: any[][] = [
      ['BẢNG LƯƠNG NHÂN VIÊN'],
      [`Tháng ${formData.value.month}/${formData.value.year}`],
      [`Ngày xuất: ${formatDateDisplay(today)}`],
      [], // Empty row
      ['STT', 'Nhân viên', 'Lương cơ bản', 'Số công thực tế', 'Số công tối đa', 'Tỷ lệ công (%)', 'Lương theo công', 'Thưởng', 'Tổng lương', 'Ghi chú'],
    ]

    // Add data rows
    results.value.forEach((res, idx) => {
      let note = ''
      if (res.details) {
        const notes: string[] = []
        if (res.details.total_days_late > 0) notes.push(`Muộn: ${res.details.total_days_late} lần`)
        if (res.details.early_leave_count && res.details.early_leave_count > 0) notes.push(`Về sớm: ${res.details.early_leave_count} lần`)
        if (res.details.total_days_absent > 0) notes.push(`Nghỉ: ${res.details.total_days_absent} lần`)
        note = notes.join(', ')
      }
      
      worksheetData.push([
        idx + 1,
        res.employee_name,
        res.base_salary,
        res.actual_work_hours,
        res.max_work_hours_in_month,
        res.work_hours_percentage,
        res.calculated_salary,
        res.bonus,
        res.final_salary,
        note
      ])
    })

    // Add total row
    worksheetData.push([
      '',
      'TỔNG CỘNG',
      '',
      '',
      '',
      '',
      '',
      '',
      totalSalary.value,
      ''
    ])

    // Chi tiết chấm công
    worksheetData.push([])
    worksheetData.push(['CHI TIẾT CHẤM CÔNG'])
    worksheetData.push(['STT', 'Nhân viên', 'Ngày có mặt', 'Ngày vắng mặt', 'Ngày đi muộn', 'TB giờ/ngày'])
    
    results.value.forEach((res, idx) => {
      worksheetData.push([
        idx + 1,
        res.employee_name,
        res.details?.total_days_present || 0,
        res.details?.total_days_absent || 0,
        res.details?.total_days_late || 0,
        res.details?.average_work_hours_per_day || 0
      ])
    })

    // Create workbook and worksheet
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.aoa_to_sheet(worksheetData)

    // Set column widths
    ws['!cols'] = [
      { wch: 5 },  // STT
      { wch: 30 }, // Nhân viên
      { wch: 15 }, // Lương CB
      { wch: 12 }, // Số công thực tế
      { wch: 12 }, // Số công tối đa
      { wch: 12 }, // Tỷ lệ
      { wch: 15 }, // Lương theo công
      { wch: 12 }, // Thưởng
      { wch: 15 }, // Tổng lương
      { wch: 30 }, // Ghi chú
    ]

    // Merge cells for header
    ws['!merges'] = [
      { s: { r: 0, c: 0 }, e: { r: 0, c: 9 } }, // Title
      { s: { r: 1, c: 0 }, e: { r: 1, c: 9 } }, // Month/Year
      { s: { r: 2, c: 0 }, e: { r: 2, c: 9 } }, // Date
    ]

    // Add worksheet to workbook
    XLSX.utils.book_append_sheet(wb, ws, `Lương T${formData.value.month}`)

    // Generate filename
    const filename = `BangLuong_T${formData.value.month}_${formData.value.year}.xlsx`

    // Write file
    XLSX.writeFile(wb, filename)

    toast.success('Xuất file Excel thành công!')
  } catch (err: any) {
    toast.error('Không thể xuất file Excel: ' + err.message)
  } finally {
    exporting.value = false
  }
}
</script>
