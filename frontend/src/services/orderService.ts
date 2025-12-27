/**
 * Order service for order-related API calls
 */
import api from './api'
import type { Order, OrderListResponse, CreateOrderRequest, CreateOrderResponse } from '@/types/order.types'

// Get session ID for guest checkout
const getSessionId = (): string => {
  let sessionId = localStorage.getItem('cart_session_id')
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`
    localStorage.setItem('cart_session_id', sessionId)
  }
  return sessionId
}

// Add session ID header to requests
const addSessionHeader = () => {
  const sessionId = getSessionId()
  return {
    headers: {
      'X-Session-ID': sessionId
    }
  }
}

export const orderService = {
  /**
   * Create order from cart
   */
  createOrder: async (data: CreateOrderRequest): Promise<CreateOrderResponse> => {
    const response = await api.post<CreateOrderResponse>('/orders', data, addSessionHeader())
    return response.data
  },

  /**
   * Get user's orders
   */
  getUserOrders: async (page = 1, perPage = 10, status?: string): Promise<OrderListResponse> => {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString()
    })

    if (status) {
      params.append('status', status)
    }

    const response = await api.get<OrderListResponse>(`/orders?${params}`)
    return response.data
  },

  /**
   * Get single order by ID
   */
  getOrder: async (orderId: string): Promise<Order> => {
    const response = await api.get<Order>(`/orders/${orderId}`)
    return response.data
  },

  /**
   * Get order by order number
   */
  getOrderByNumber: async (orderNumber: string): Promise<Order> => {
    const response = await api.get<Order>(`/orders/number/${orderNumber}`)
    return response.data
  },

  /**
   * Cancel an order
   */
  cancelOrder: async (orderId: string, reason?: string): Promise<{ order: Order }> => {
    const response = await api.put<{ order: Order }>(`/orders/${orderId}/cancel`, { reason })
    return response.data
  }
}

export default orderService
