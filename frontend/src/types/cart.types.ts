import { Product } from './product.types'

export interface CartItem {
  id: string
  cart_id: string
  product_id: string
  product: Product
  quantity: number
  unit_price: number
  total_price: number
  created_at: string
}

export interface Cart {
  id: string
  user_id: string | null
  session_id: string | null
  items: CartItem[]
  created_at: string
  updated_at: string
  expires_at: string
}

export interface CartTotals {
  subtotal: number
  tax: number
  shipping: number
  total: number
}

export interface CartResponse {
  cart: Cart | null
  items: CartItem[]
  totals: CartTotals
  session_id?: string
}

export interface AddToCartRequest {
  product_id: string
  quantity: number
}

export interface UpdateCartItemRequest {
  quantity: number
}
