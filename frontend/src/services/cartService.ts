import api from './api'
import { CartResponse, AddToCartRequest, UpdateCartItemRequest } from '@/types/cart.types'

// Get or create session ID for guest users
const getSessionId = (): string => {
  let sessionId = localStorage.getItem('cart_session_id')
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`
    localStorage.setItem('cart_session_id', sessionId)
  }
  return sessionId
}

// Add session ID header to requests
const withSessionHeader = () => {
  const sessionId = getSessionId()
  return {
    headers: {
      'X-Session-ID': sessionId,
    },
  }
}

export const cartService = {
  async getCart(): Promise<CartResponse> {
    const response = await api.get('/cart', withSessionHeader())
    return response.data
  },

  async addToCart(data: AddToCartRequest): Promise<CartResponse> {
    const response = await api.post('/cart/items', data, withSessionHeader())
    return response.data
  },

  async updateCartItem(itemId: string, data: UpdateCartItemRequest): Promise<CartResponse> {
    const response = await api.put(`/cart/items/${itemId}`, data, withSessionHeader())
    return response.data
  },

  async removeFromCart(itemId: string): Promise<void> {
    await api.delete(`/cart/items/${itemId}`, withSessionHeader())
  },

  async clearCart(): Promise<void> {
    await api.delete('/cart', withSessionHeader())
  },

  async validateCart(): Promise<{ valid: boolean; errors?: string[] }> {
    const response = await api.post('/cart/validate', {}, withSessionHeader())
    return response.data
  },

  async mergeCarts(sessionId: string): Promise<CartResponse> {
    const response = await api.post('/cart/merge', { session_id: sessionId })
    return response.data
  },

  getSessionId,
}

export default cartService
