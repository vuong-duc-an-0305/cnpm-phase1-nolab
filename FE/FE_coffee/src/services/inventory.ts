import { apiService } from './api'
import type { Ingredient, IngredientForm, Import, ImportForm, ImportDetail, FilterOptions } from '@/types'

export const inventoryService = {
  // Get all ingredients
  getAll: (filters?: FilterOptions): Promise<Ingredient[]> => {
    return apiService.get('/ingredients/', filters)
  },

  // Get ingredient by ID
  getById: (id: number): Promise<Ingredient> => {
    return apiService.get(`/ingredients/${id}/`)
  },

  // Create new ingredient
  create: (data: IngredientForm): Promise<Ingredient> => {
    return apiService.post('/ingredients/', data)
  },

  // Update ingredient
  update: (id: number, data: Partial<IngredientForm>): Promise<Ingredient> => {
    return apiService.put(`/ingredients/${id}/`, data)
  },

  // Delete ingredient
  delete: (id: number): Promise<void> => {
    return apiService.delete(`/ingredients/${id}/`)
  },

  // Get low stock ingredients
  getLowStock: (): Promise<Ingredient[]> => {
    // BE chuẩn dùng low_stock; fallback low-stock nếu cấu hình khác
    return apiService.get('/ingredients/low_stock/').catch(async (err) => {
      if (err?.response?.status === 404) {
        return apiService.get('/ingredients/low-stock/')
      }
      throw err
    })
  },

  // Add stock to ingredient
  addStock: (id: number, quantity: number, note?: string): Promise<Ingredient> => {
    // BE chuẩn dùng add_stock; fallback add-stock nếu cấu hình khác
    return apiService
      .post(`/ingredients/${id}/add_stock/`, { quantity, note })
      .catch(async (err) => {
        if (err?.response?.status === 404) {
          return apiService.post(`/ingredients/${id}/add-stock/`, { quantity, note })
        }
        throw err
      })
  },

  // Reduce stock from ingredient
  reduceStock: (id: number, quantity: number, note?: string): Promise<Ingredient> => {
    // BE chuẩn dùng reduce_stock; fallback reduce-stock nếu cấu hình khác
    return apiService
      .post(`/ingredients/${id}/reduce_stock/`, { quantity, note })
      .catch(async (err) => {
        if (err?.response?.status === 404) {
          return apiService.post(`/ingredients/${id}/reduce-stock/`, { quantity, note })
        }
        throw err
      })
  },

  // Search ingredients
  search: (query: string): Promise<Ingredient[]> => {
    return apiService.get('/ingredients/', { search: query })
  },
}

export const importService = {
  // Get all imports
  getAll: (filters?: FilterOptions): Promise<Import[]> => {
    return apiService.get('/inventory/', filters)
  },

  // Get import by ID
  getById: (id: number): Promise<Import> => {
    return apiService.get(`/inventory/${id}/`)
  },

  // Create new import
  create: (data: ImportForm): Promise<Import> => {
    return apiService.post('/inventory/', data)
  },

  // Delete import
  delete: (id: number): Promise<void> => {
    return apiService.delete(`/inventory/${id}/`)
  },

  // Get import statistics
  getStatistics: (fromDate?: string, toDate?: string): Promise<{
    summary: {
      total_imports: number;
      total_cost: string;
      average_import_value: string;
    };
    top_ingredients: Array<{
      IngredientID: number;
      IngredientID__IngredientName: string;
      total_quantity: string;
      total_cost: string;
      import_count: number;
    }>;
  }> => {
    return apiService.get('/inventory/statistics/', { from_date: fromDate, to_date: toDate })
  },

  // Get ingredient import history
  getIngredientHistory: (ingredientId: number): Promise<ImportDetail[]> => {
    return apiService.get('/inventory/ingredient-history/', { ingredient_id: ingredientId })
  },

  // Get import details
  getImportDetails: (importId?: number, ingredientId?: number): Promise<ImportDetail[]> => {
    const params: any = {}
    if (importId) params.import_id = importId
    if (ingredientId) params.ingredient_id = ingredientId
    return apiService.get('/import-details/', params)
  },
}
