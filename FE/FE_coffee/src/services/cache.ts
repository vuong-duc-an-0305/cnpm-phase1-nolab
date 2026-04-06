/**
 * Cache utility using sessionStorage
 * Giúp cache API responses để tăng performance
 */

interface CacheItem<T> {
  data: T
  timestamp: number
  ttl: number // Time to live in milliseconds
}

class CacheService {
  private prefix = 'app_cache_'

  /**
   * Lưu data vào cache
   */
  set<T>(key: string, data: T, ttlMinutes: number = 5): void {
    try {
      const cacheItem: CacheItem<T> = {
        data,
        timestamp: Date.now(),
        ttl: ttlMinutes * 60 * 1000, // Convert to milliseconds
      }
      sessionStorage.setItem(this.prefix + key, JSON.stringify(cacheItem))
    } catch (error) {
      console.warn('Failed to cache data:', error)
    }
  }

  /**
   * Lấy data từ cache
   * Trả về null nếu không tồn tại hoặc đã hết hạn
   */
  get<T>(key: string): T | null {
    try {
      const cached = sessionStorage.getItem(this.prefix + key)
      if (!cached) return null

      const cacheItem: CacheItem<T> = JSON.parse(cached)
      const now = Date.now()

      // Check if cache has expired
      if (now - cacheItem.timestamp > cacheItem.ttl) {
        this.remove(key)
        return null
      }

      return cacheItem.data
    } catch (error) {
      console.warn('Failed to get cached data:', error)
      return null
    }
  }

  /**
   * Kiểm tra xem key có tồn tại và còn hạn không
   */
  has(key: string): boolean {
    return this.get(key) !== null
  }

  /**
   * Xóa một key khỏi cache
   */
  remove(key: string): void {
    try {
      sessionStorage.removeItem(this.prefix + key)
    } catch (error) {
      console.warn('Failed to remove cached data:', error)
    }
  }

  /**
   * Xóa tất cả cache
   */
  clear(): void {
    try {
      const keys = Object.keys(sessionStorage)
      keys.forEach(key => {
        if (key.startsWith(this.prefix)) {
          sessionStorage.removeItem(key)
        }
      })
    } catch (error) {
      console.warn('Failed to clear cache:', error)
    }
  }

  /**
   * Xóa cache đã hết hạn
   */
  cleanup(): void {
    try {
      const keys = Object.keys(sessionStorage)
      keys.forEach(key => {
        if (key.startsWith(this.prefix)) {
          const cacheKey = key.replace(this.prefix, '')
          this.get(cacheKey) // This will auto-remove expired items
        }
      })
    } catch (error) {
      console.warn('Failed to cleanup cache:', error)
    }
  }

  /**
   * Wrapper function để cache API calls
   * Tự động cache response và trả về cached data nếu còn hạn
   */
  async cached<T>(
    key: string,
    fetchFn: () => Promise<T>,
    ttlMinutes: number = 5
  ): Promise<T> {
    // Check cache first
    const cached = this.get<T>(key)
    if (cached !== null) {
      return cached
    }

    // Fetch fresh data
    const data = await fetchFn()
    
    // Cache the result
    this.set(key, data, ttlMinutes)
    
    return data
  }
}

export const cacheService = new CacheService()

// Auto cleanup on app load
cacheService.cleanup()
