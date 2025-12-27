/**
 * Payment service for Stripe payment operations
 */
import api from './api'

export interface CreatePaymentIntentRequest {
  order_id: string
  amount: number
  metadata?: Record<string, string>
}

export interface CreatePaymentIntentResponse {
  client_secret: string
  payment_intent_id: string
  payment_id: string
}

export interface ConfirmPaymentRequest {
  payment_intent_id: string
}

export interface ConfirmPaymentResponse {
  payment_id: string
  status: string
  order_id: string
  order_number: string
}

export const paymentService = {
  /**
   * Create a payment intent for an order
   */
  createPaymentIntent: async (data: CreatePaymentIntentRequest): Promise<CreatePaymentIntentResponse> => {
    const response = await api.post<CreatePaymentIntentResponse>('/payments/create-intent', data)
    return response.data
  },

  /**
   * Confirm a payment
   */
  confirmPayment: async (data: ConfirmPaymentRequest): Promise<ConfirmPaymentResponse> => {
    const response = await api.post<ConfirmPaymentResponse>('/payments/confirm', data)
    return response.data
  },

  /**
   * Get payment details
   */
  getPayment: async (paymentId: string): Promise<any> => {
    const response = await api.get(`/payments/${paymentId}`)
    return response.data
  }
}

export default paymentService
