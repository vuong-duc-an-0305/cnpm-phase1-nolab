import { apiService } from './api'
import { cacheService } from './cache'
import type { DashboardStats, Order, Product, Customer, Ingredient } from '../types'
import { getCurrentDateInTimezone, formatDateToYMD, addDays } from '../utils/timezone'

export interface DashboardData {
  stats: DashboardStats
  recentOrders: Order[]
  lowStockItems: Ingredient[]
  totalProducts: number
  totalCustomers: number
}

export const dashboardService = {
  // Lấy dữ liệu tổng quan cho dashboard
  getDashboardData: async (): Promise<DashboardData> => {
    // Cache key based on current date
    const today = getCurrentDateInTimezone()
    const cacheKey = `dashboard_data_${today}`
    
    return cacheService.cached(cacheKey, async () => {
      try {
        // Lấy thống kê doanh thu hôm nay (ngày thực tế) - bao gồm tất cả trạng thái đơn hàng
        const todayStr = today
        const revenueStats = await apiService.get('/orders/revenue_stats/', {
          from_date: todayStr,
          to_date: todayStr,
          include_all_status: true
        })

      // Lấy đơn hàng gần đây (5 đơn mới nhất)
      const ordersResponse = await apiService.get('/orders/', {
        ordering: '-OrderDate',
        limit: 5
      })
      const recentOrders = ordersResponse.results || []

      // Lấy sản phẩm sắp hết hàng (quantity = 0 hoặc < MinQuantity)
      const ingredientsResponse = await apiService.get('/ingredients/')
      const lowStockItems = ingredientsResponse.results?.filter((item: any) => {
        const quantity = Number(item.QuantityInStock) || 0
        const minQuantity = Number(item.MinQuantity) || 0
        return quantity === 0 || quantity < minQuantity
      }) || []

      // Lấy tổng số sản phẩm
      const productsResponse = await apiService.get('/products/')
      const totalProducts = productsResponse.results?.length || productsResponse.length || 0

      // Lấy tổng số khách hàng
      const customersResponse = await apiService.get('/customers/')
      const totalCustomers = customersResponse.results?.length || customersResponse.length || 0

      // Tính toán thống kê
      const summary = revenueStats.summary || {}
      const stats: DashboardStats = {
        total_orders: summary.total_orders || 0,
        total_revenue: summary.total_revenue || '0',
        total_customers: totalCustomers,
        total_products: totalProducts,
        revenue_growth: 0, // Có thể tính toán so với ngày trước
        orders_growth: 0,
        customers_growth: 0,
        products_growth: 0
      }

      return {
        stats,
        recentOrders: recentOrders.slice(0, 5),
        lowStockItems: lowStockItems.slice(0, 3),
        totalProducts,
        totalCustomers
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      throw error
    }
    }, 5) // Cache for 5 minutes
  },

  // Lấy thống kê theo khoảng thời gian
  getStatsByPeriod: async (fromDate: string, toDate: string, includeAllStatus: boolean = false): Promise<DashboardStats> => {
    try {
      const revenueStats = await apiService.get('/orders/revenue_stats/', {
        from_date: fromDate,
        to_date: toDate,
        include_all_status: includeAllStatus
      })

      const summary = revenueStats.summary || {}
      return {
        total_orders: summary.total_orders || 0,
        total_revenue: summary.total_revenue || '0',
        total_customers: 0, // Cần API riêng để lấy số khách hàng mới
        total_products: 0, // Cần API riêng để lấy số sản phẩm mới
        revenue_growth: 0,
        orders_growth: 0,
        customers_growth: 0,
        products_growth: 0
      }
    } catch (error) {
      console.error('Error fetching stats by period:', error)
      throw error
    }
  },

  // Lấy sản phẩm bán chạy
  getBestSellingProducts: async (limit: number = 5) => {
    try {
      const todayStr = getCurrentDateInTimezone()
      const result = await apiService.get('/orders/best_selling/', {
        from_date: todayStr,
        to_date: todayStr,
        limit
      })
      return result.best_selling_products || []
    } catch (error) {
      console.error('Error fetching best selling products:', error)
      return []
    }
  },

  // Lấy sản phẩm bán chạy theo period
  getBestSellingProductsByPeriod: async (fromDate: string, toDate: string, period: string, limit: number = 5) => {
    try {
      let interval = 'day'
      
      switch (period) {
        case 'day':
          interval = 'day'
          break
        case 'week':
          interval = 'week'
          break
        case 'month':
          interval = 'month'
          break
        case 'year':
          interval = 'year'
          break
        default:
          interval = 'day'
      }

      const result = await apiService.get('/orders/best_selling/', {
        from_date: fromDate,
        to_date: toDate,
        interval: interval,
        limit
      })
      return result.best_selling_products || []
    } catch (error) {
      console.error('Error fetching best selling products by period:', error)
      return []
    }
  },

  // Lấy xu hướng doanh thu
  getRevenueTrend: async (days: number = 7) => {
    try {
      const toDate = getCurrentDateInTimezone()
      const fromDate = addDays(toDate, -days)

      const result = await apiService.get('/orders/revenue_trend/', {
        from_date: fromDate,
        to_date: toDate,
        interval: 'day'
      })

      return result
    } catch (error) {
      console.error('Error fetching revenue trend:', error)
      return {
        labels: [],
        datasets: [{ label: 'Doanh thu', data: [] }],
        interval: 'day'
      }
    }
  },

  // Lấy xu hướng doanh thu theo period
  getRevenueTrendByPeriod: async (fromDate: string, toDate: string, period: string) => {
    const cacheKey = `revenue_trend_${fromDate}_${toDate}_${period}`
    
    return cacheService.cached(cacheKey, async () => {
      try {
        let interval = 'day'
        
        switch (period) {
          case 'day':
            interval = 'day'
            break
          case 'week':
            interval = 'week'
            break
          case 'month':
            interval = 'month'
            break
          case 'year':
            interval = 'year'
            break
          default:
            interval = 'day'
        }

        const result = await apiService.get('/orders/revenue_trend/', {
          from_date: fromDate,
          to_date: toDate,
          interval: interval
        })

        return result
      } catch (error) {
        console.error('Error fetching revenue trend by period:', error)
        return {
          labels: [],
          datasets: [{ label: 'Doanh thu', data: [] }],
          interval: period
        }
      }
    }, 10) // Cache for 10 minutes
  }
}
