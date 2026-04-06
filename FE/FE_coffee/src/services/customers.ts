import { apiService } from './api'
import type { Customer, CustomerForm, PaginatedResponse, FilterOptions } from '@/types'

export const customerService = {
  // Get all customers with filters
  getAll: (filters?: FilterOptions): Promise<Customer[]> => {
    return apiService.get('/customers/', filters)
  },

  // Get customer by ID
  getById: (id: number): Promise<Customer> => {
    return apiService.get(`/customers/${id}/`)
  },

  // Create new customer
  create: (data: CustomerForm): Promise<Customer> => {
    return apiService.post('/customers/', data)
  },

  // Update customer
  update: (id: number, data: Partial<CustomerForm>): Promise<Customer> => {
    return apiService.put(`/customers/${id}/`, data)
  },

  // Delete customer
  delete: (id: number): Promise<void> => {
    return apiService.delete(`/customers/${id}/`)
  },

  // Get customer by phone
  getByPhone: (phone: string): Promise<Customer> => {
    return apiService.get('/customers/by_phone/', { phone })
  },

  // Get VIP customers
  getVIP: (minPoints?: number): Promise<Customer[]> => {
    return apiService.get('/customers/vip/', { min_points: minPoints })
  },

  // Add loyalty points
  addPoints: (id: number, points: number, note?: string): Promise<Customer> => {
    return apiService.post(`/customers/${id}/add_points/`, { points, note })
  },

  // Redeem loyalty points
  redeemPoints: (id: number, points: number, note?: string): Promise<Customer> => {
    return apiService.post(`/customers/${id}/redeem_points/`, { points, note })
  },

  // Get customer order history
  getOrderHistory: (id: number): Promise<any[]> => {
    return apiService.get(`/customers/${id}/order_history/`)
  },

  // Search customers
  search: (query: string): Promise<Customer[]> => {
    return apiService.get('/customers/', { search: query })
  },

  // Get customers by membership level
  getByMembershipLevel: (level: string): Promise<Customer[]> => {
    return apiService.get('/customers/', { membership_level: level })
  },
}
