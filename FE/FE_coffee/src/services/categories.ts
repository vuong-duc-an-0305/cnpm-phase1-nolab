import { apiService } from './api'
import type { Category, PaginatedResponse } from '@/types'

export const categoryService = {
  // Get all categories
  getAll: (): Promise<Category[]> => {
    return apiService.get('/categories/')
  },

  // Get category by ID
  getById: (id: number): Promise<Category> => {
    return apiService.get(`/categories/${id}/`)
  },

  // Create new category
  create: (data: { CategoryName: string }): Promise<Category> => {
    return apiService.post('/categories/', data)
  },

  // Update category
  update: (id: number, data: { CategoryName: string }): Promise<Category> => {
    return apiService.put(`/categories/${id}/`, data)
  },

  // Delete category
  delete: (id: number): Promise<void> => {
    return apiService.delete(`/categories/${id}/`)
  },

  // Get categories with product count
  getWithProductCount: (): Promise<Category[]> => {
    return apiService.get('/categories/')
  },
}
