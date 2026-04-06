/**
 * WebSocket Service for Real-time Updates
 * Phase 2: Replace polling with push notifications
 */

type WebSocketMessageHandler = (data: any) => void

interface WebSocketConfig {
  url: string
  onMessage: WebSocketMessageHandler
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
  reconnectDelay?: number
  maxReconnectAttempts?: number
}

class WebSocketService {
  private ws: WebSocket | null = null
  private config: WebSocketConfig | null = null
  private reconnectAttempts = 0
  private reconnectTimer: number | null = null
  private heartbeatTimer: number | null = null
  private isConnecting = false
  private manualClose = false

  /**
   * Kết nối WebSocket
   */
  connect(config: WebSocketConfig) {
    // Ngăn multiple connections
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      console.log('WebSocket already connected or connecting')
      return
    }

    this.config = config
    this.manualClose = false
    this.isConnecting = true

    try {
      console.log(`[WebSocket] Connecting to ${config.url}...`)
      this.ws = new WebSocket(config.url)

      this.ws.onopen = () => {
        console.log('[WebSocket] ✅ Connected')
        this.isConnecting = false
        this.reconnectAttempts = 0
        
        // Start heartbeat
        this.startHeartbeat()
        
        if (config.onOpen) {
          config.onOpen()
        }
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // Ignore pong messages
          if (data.type === 'pong') {
            return
          }
          
          // Log received message
          console.log('[WebSocket] 📨 Received:', data.type, data)
          
          // Call message handler
          config.onMessage(data)
        } catch (error) {
          console.error('[WebSocket] Error parsing message:', error)
        }
      }

      this.ws.onclose = (event) => {
        console.log(`[WebSocket] ❌ Disconnected (code: ${event.code})`)
        this.isConnecting = false
        this.stopHeartbeat()
        
        if (config.onClose) {
          config.onClose()
        }

        // Auto reconnect if not manually closed
        if (!this.manualClose) {
          this.reconnect()
        }
      }

      this.ws.onerror = (error) => {
        console.error('[WebSocket] ⚠️ Error:', error)
        this.isConnecting = false
        
        if (config.onError) {
          config.onError(error)
        }
      }
    } catch (error) {
      console.error('[WebSocket] Failed to connect:', error)
      this.isConnecting = false
      this.reconnect()
    }
  }

  /**
   * Reconnect với exponential backoff
   */
  private reconnect() {
    if (!this.config || this.manualClose) {
      return
    }

    const maxAttempts = this.config.maxReconnectAttempts || 5
    const baseDelay = this.config.reconnectDelay || 3000

    if (this.reconnectAttempts >= maxAttempts) {
      console.error('[WebSocket] Max reconnect attempts reached')
      return
    }

    this.reconnectAttempts++
    
    // Exponential backoff: 3s, 6s, 12s, 24s, 48s
    const delay = Math.min(baseDelay * Math.pow(2, this.reconnectAttempts - 1), 60000)
    
    console.log(`[WebSocket] Reconnecting in ${delay / 1000}s... (Attempt ${this.reconnectAttempts}/${maxAttempts})`)

    this.reconnectTimer = window.setTimeout(() => {
      this.connect(this.config!)
    }, delay)
  }

  /**
   * Heartbeat để duy trì connection
   */
  private startHeartbeat() {
    this.stopHeartbeat()
    
    // Send ping every 30 seconds
    this.heartbeatTimer = window.setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({
          type: 'ping',
          timestamp: Date.now()
        })
      }
    }, 30000)
  }

  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * Gửi message qua WebSocket
   */
  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('[WebSocket] Cannot send - not connected')
    }
  }

  /**
   * Đóng connection
   */
  disconnect() {
    console.log('[WebSocket] Manually disconnecting...')
    this.manualClose = true
    this.stopHeartbeat()
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    this.reconnectAttempts = 0
    this.config = null
  }

  /**
   * Kiểm tra trạng thái kết nối
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

// Export singleton instance
export const websocketService = new WebSocketService()

// Export for composable
export function useWebSocket(url: string, onMessage: WebSocketMessageHandler) {
  const connect = () => {
    websocketService.connect({
      url,
      onMessage,
      onOpen: () => {
        console.log(`Connected to ${url}`)
      },
      onClose: () => {
        console.log(`Disconnected from ${url}`)
      },
      reconnectDelay: 3000,
      maxReconnectAttempts: 5
    })
  }

  const disconnect = () => {
    websocketService.disconnect()
  }

  const send = (data: any) => {
    websocketService.send(data)
  }

  return {
    connect,
    disconnect,
    send,
    isConnected: () => websocketService.isConnected()
  }
}
