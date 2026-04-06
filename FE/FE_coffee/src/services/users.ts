import { apiService } from './api'

export interface EmployeeDetail {
  full_name?: string
  avatar?: string
  phone_number?: string
  citizen_id?: string
  gender?: 'MALE' | 'FEMALE' | 'OTHER'
  date_of_birth?: string
  address?: string
  emergency_contact_name?: string
  emergency_contact_phone?: string
  emergency_contact_relationship?: string
  hire_date?: string
  salary?: number
  notes?: string
  created_at?: string
  updated_at?: string
}

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  full_name: string
  role: string
  groups: string[]
  is_active: boolean
  is_staff: boolean
  date_joined: string
  employee_detail?: EmployeeDetail | null
}

export interface UserForm {
  username: string
  password?: string
  email: string
  first_name: string
  last_name: string
  role: 'admin' | 'manager' | 'cashier' | 'waiter'
  employee_detail?: Partial<EmployeeDetail>
}

export const userService = {
  // Lấy danh sách users (thay thế getEmployees)
  getAll: async (params?: { search?: string; page?: number; page_size?: number }): Promise<User[]> => {
    return apiService.get('/auth/users/', params)
  },

  // Lấy chi tiết user
  getById: async (id: number): Promise<User> => {
    return apiService.get(`/auth/users/${id}/`)
  },

  // Tạo user mới
  create: async (data: UserForm): Promise<User> => {
    return apiService.post('/auth/users/', data)
  },

  // Cập nhật user (dùng PATCH cho partial update)
  update: async (id: number, data: Partial<UserForm>): Promise<User> => {
    return apiService.patch(`/auth/users/${id}/`, data)
  },

  // Xóa user
  delete: async (id: number): Promise<void> => {
    return apiService.delete(`/auth/users/${id}/`)
  },

  // Lấy employee detail
  getEmployeeDetail: async (userId: number): Promise<EmployeeDetail> => {
    return apiService.get(`/auth/users/${userId}/detail/`)
  },

  // Cập nhật employee detail
  updateEmployeeDetail: async (userId: number, data: Partial<EmployeeDetail>): Promise<EmployeeDetail> => {
    return apiService.patch(`/auth/users/${userId}/detail/`, data)
  }
}
