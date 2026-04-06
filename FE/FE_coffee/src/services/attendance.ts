/**
 * Attendance Service - API calls for attendance and work schedule management
 */
import apiClient from './api'

export interface AttendanceRecord {
  id?: number
  employee: number
  employee_name?: string
  employee_username?: string
  date: string
  check_in_time?: string | null
  check_out_time?: string | null
  work_hours: number
  status: 'PRESENT' | 'ABSENT' | 'LATE' | 'EARLY_LEAVE' | 'OVERTIME' | 'LEAVE' | 'SICK_LEAVE'
  status_display?: string
  notes?: string
  approved_by?: number | null
  approved_by_username?: string | null
  approved_at?: string | null
  created_at?: string
  updated_at?: string
}

export interface WorkSchedule {
  id?: number
  employee: number
  employee_name?: string
  employee_username?: string
  schedule_date: string
  shift_start_time: string
  shift_end_time: string
  scheduled_hours?: number
  is_active: boolean
  notes?: string
  created_at?: string
  updated_at?: string
}

export interface AttendanceSummary {
  employee_id: number
  employee_name: string
  employee_username: string
  month: number
  year: number
  total_work_hours: number
  total_days_present: number
  total_days_absent: number
  total_days_late: number
  total_days_early_leave?: number
  total_overtime_hours: number
  total_days_leave?: number
  total_days_sick_leave?: number
  average_work_hours_per_day: number
}

export interface SalaryCalculation {
  employee_id: number
  employee_name: string
  employee_username: string
  month: number
  year: number
  base_salary: number
  actual_work_hours: number
  max_work_hours_in_month: number
  work_hours_percentage: number
  calculated_salary: number
  bonus: number
  final_salary: number
  details: {
    total_days_present: number
    total_days_absent: number
    total_days_late: number
    early_leave_count: number
    average_work_hours_per_day: number
  }
}

export interface CheckInRequest {
  employee: number
  date: string
  check_in_time: string
  notes?: string
}

export interface CheckOutRequest {
  employee: number
  date: string
  check_out_time: string
}

const attendanceService = {
  // ===== ATTENDANCE RECORDS =====
  
  /**
   * Lấy danh sách bản ghi chấm công
   */
  getAttendanceRecords(params?: {
    employee?: number
    date?: string
    status?: string
    start_date?: string
    end_date?: string
    page?: number
    page_size?: number
  }) {
    return apiClient.get('/attendance/records/', { params })
  },

  /**
   * Tạo bản ghi chấm công mới
   */
  createAttendanceRecord(data: AttendanceRecord) {
    return apiClient.post('/attendance/records/', data)
  },

  /**
   * Lấy chi tiết bản ghi chấm công
   */
  getAttendanceRecordById(id: number) {
    return apiClient.get(`/attendance/records/${id}/`)
  },

  /**
   * Cập nhật bản ghi chấm công
   */
  updateAttendanceRecord(id: number, data: Partial<AttendanceRecord>) {
    return apiClient.patch(`/attendance/records/${id}/`, data)
  },

  /**
   * Xóa bản ghi chấm công
   */
  deleteAttendanceRecord(id: number) {
    return apiClient.delete(`/attendance/records/${id}/`)
  },

  /**
   * Chấm công vào ca
   */
  checkIn(data: CheckInRequest) {
    return apiClient.post('/attendance/records/check_in/', data)
  },

  /**
   * Chấm công ra ca
   */
  checkOut(data: CheckOutRequest) {
    return apiClient.post('/attendance/records/check_out/', data)
  },

  /**
   * Tổng hợp chấm công theo tháng
   */
  getAttendanceSummary(employee: number, month: number, year: number) {
    return apiClient.get('/attendance/records/summary/', {
      params: { employee, month, year }
    })
  },

  /**
   * Phê duyệt bản ghi chấm công
   */
  approveAttendanceRecord(id: number) {
    return apiClient.post(`/attendance/records/${id}/approve/`)
  },

  /**
   * Chấm công vào ca nhanh (từ attendance record)
   */
  quickCheckIn(id: number, checkInTime?: string) {
    return apiClient.post(`/attendance/records/${id}/quick_check_in/`, {
      check_in_time: checkInTime
    })
  },

  /**
   * Kết ca nhanh (từ attendance record)
   */
  quickCheckOut(id: number, checkOutTime?: string) {
    return apiClient.post(`/attendance/records/${id}/quick_check_out/`, {
      check_out_time: checkOutTime
    })
  },

  // ===== WORK SCHEDULES =====

  /**
   * Lấy danh sách lịch làm việc
   */
  getWorkSchedules(params?: {
    employee?: number
    schedule_date?: string
    is_active?: boolean
    start_date?: string
    end_date?: string
    page?: number
    page_size?: number
  }) {
    return apiClient.get('/attendance/schedules/', { params })
  },

  /**
   * Tạo lịch làm việc mới
   */
  createWorkSchedule(data: WorkSchedule) {
    return apiClient.post('/attendance/schedules/', data)
  },

  /**
   * Lấy chi tiết lịch làm việc
   */
  getWorkScheduleById(id: number) {
    return apiClient.get(`/attendance/schedules/${id}/`)
  },

  /**
   * Cập nhật lịch làm việc
   */
  updateWorkSchedule(id: number, data: Partial<WorkSchedule>) {
    return apiClient.patch(`/attendance/schedules/${id}/`, data)
  },

  /**
   * Xóa lịch làm việc
   */
  deleteWorkSchedule(id: number) {
    return apiClient.delete(`/attendance/schedules/${id}/`)
  },

  /**
   * Lấy lịch làm việc theo tuần hoặc khoảng thời gian tùy chỉnh
   */
  getWeeklySchedule(startDate?: string, endDate?: string) {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    return apiClient.get('/attendance/schedules/weekly/', { params })
  },

  /**
   * Lấy lịch làm việc theo tháng
   */
  getMonthlySchedule(month?: number, year?: number) {
    const params: any = {}
    if (month) params.month = month
    if (year) params.year = year
    return apiClient.get('/attendance/schedules/monthly/', { params })
  },

  // ===== SALARY CALCULATION =====

  /**
   * Tính lương cho nhân viên
   */
  calculateSalary(employee: number, month: number, year: number, bonus?: number) {
    const params: any = { employee, month, year }
    if (bonus !== undefined) params.bonus = bonus
    return apiClient.get('/attendance/salary/calculate/', { params })
  },

  /**
   * Tạo phiếu lương
   */
  generateSalarySlip(employee: number, month: number, year: number, bonus?: number) {
    const params: any = { employee, month, year }
    if (bonus !== undefined) params.bonus = bonus
    return apiClient.get('/attendance/salary/slip/', { params })
  },
}

export default attendanceService
