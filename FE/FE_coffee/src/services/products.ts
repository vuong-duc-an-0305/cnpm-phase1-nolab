import { apiService } from './api'
import type { Product, ProductForm, PaginatedResponse, FilterOptions } from '@/types'

export const productService = {
  // Get all products with filters
  getAll: (filters?: FilterOptions): Promise<Product[]> => {
    return apiService.get('/products/', filters)
  },

  // Get product by ID
  getById: (id: number): Promise<Product> => {
    return apiService.get(`/products/${id}/`)
  },

  // Create new product
  create: (data: ProductForm): Promise<Product> => {
    return apiService.post('/products/', data)
  },

  // Update product
  update: (id: number, data: Partial<ProductForm>): Promise<Product> => {
    return apiService.put(`/products/${id}/`, data)
  },

  // Delete product
  delete: (id: number): Promise<void> => {
    return apiService.delete(`/products/${id}/`)
  },

  // Get available products only
  getAvailable: (): Promise<Product[]> => {
    return apiService.get('/products/available/')
  },

  // Check ingredients availability
  checkIngredients: (id: number, quantity: number): Promise<{
    product_id: number;
    product_name: string;
    quantity: number;
    is_available: boolean;
    missing_ingredients: any[];
  }> => {
    return apiService.post(`/products/${id}/check_ingredients/`, { quantity })
  },

  // Update product status
  updateStatus: (id: number, status: number): Promise<Product> => {
    return apiService.patch(`/products/${id}/update-status/`, { status })
  },

  // Get products by category
  getByCategory: (categoryId: number): Promise<Product[]> => {
    return apiService.get('/products/', { category_id: categoryId })
  },

  // Search products
  search: (query: string): Promise<Product[]> => {
    return apiService.get('/products/', { search: query })
  },
}
