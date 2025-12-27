/**
 * Order type definitions
 */

export interface ShippingAddress {
  full_name: string
  street_address: string
  city: string
  state: string
  postal_code: string
  country: string
  phone?: string
}

export interface OrderItem {
  id: string
  product_id: string
  product_name: string
  product_sku: string
  product_image_url: string
  quantity: number
  unit_price: number
  total_price: number
}

export interface Order {
  id: string
  order_number: string
  user_id?: string
  customer_email: string
  customer_first_name: string
  customer_last_name: string
  customer_phone?: string
  subtotal: number
  tax_amount: number
  shipping_amount: number
  discount_amount: number
  total_amount: number
  shipping_address: ShippingAddress
  billing_address?: ShippingAddress
  status: OrderStatus
  payment_status: PaymentStatus
  fulfillment_status: FulfillmentStatus
  shipping_method?: string
  tracking_number?: string
  tracking_url?: string
  customer_notes?: string
  items?: OrderItem[]
  created_at: string
  paid_at?: string
  shipped_at?: string
  delivered_at?: string
}

export type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'refunded'
export type PaymentStatus = 'pending' | 'paid' | 'failed' | 'refunded'
export type FulfillmentStatus = 'unfulfilled' | 'partial' | 'fulfilled'

export interface OrderListResponse {
  orders: Order[]
  total: number
  page: number
  per_page: number
  pages: number
  has_next: boolean
  has_prev: boolean
}

export interface CreateOrderRequest {
  shipping_address: ShippingAddress
  billing_address?: ShippingAddress
  customer_info?: {
    email: string
    first_name: string
    last_name: string
    phone?: string
  }
  customer_notes?: string
}

export interface CreateOrderResponse {
  order: Order
  order_id: string
  order_number: string
}
