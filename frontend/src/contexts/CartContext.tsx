import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { CartItem, Cart, CartTotals } from '@/types/cart.types'
import { Product } from '@/types/product.types'
import cartService from '@/services/cartService'
import { useToast } from './ToastContext'

interface CartContextType {
  cart: Cart | null
  items: CartItem[]
  totals: CartTotals
  itemCount: number
  loading: boolean
  addToCart: (product: Product, quantity?: number) => Promise<void>
  updateQuantity: (itemId: string, quantity: number) => Promise<void>
  removeItem: (itemId: string) => Promise<void>
  clearCart: () => Promise<void>
  refreshCart: () => Promise<void>
}

const CartContext = createContext<CartContextType | undefined>(undefined)

export function CartProvider({ children }: { children: ReactNode }) {
  const [cart, setCart] = useState<Cart | null>(null)
  const [items, setItems] = useState<CartItem[]>([])
  const [totals, setTotals] = useState<CartTotals>({
    subtotal: 0,
    tax: 0,
    shipping: 0,
    total: 0,
  })
  const [loading, setLoading] = useState(false)
  const { showToast } = useToast()

  // Load cart on mount
  useEffect(() => {
    loadCart()
  }, [])

  const loadCart = async () => {
    try {
      setLoading(true)
      const response = await cartService.getCart()
      setCart(response.cart)
      setItems(response.items)
      setTotals(response.totals)
    } catch (error: any) {
      console.error('Failed to load cart:', error)
    } finally {
      setLoading(false)
    }
  }

  const addToCart = async (product: Product, quantity = 1) => {
    try {
      setLoading(true)

      const response = await cartService.addToCart({
        product_id: product.id,
        quantity,
      })

      setCart(response.cart)
      setItems(response.items)
      setTotals(response.totals)

      showToast(`Added ${product.name} to cart`, 'success')
    } catch (error: any) {
      const message = error.response?.data?.error || 'Failed to add to cart'
      showToast(message, 'error')
      throw error
    } finally {
      setLoading(false)
    }
  }

  const updateQuantity = async (itemId: string, quantity: number) => {
    try {
      setLoading(true)

      const response = await cartService.updateCartItem(itemId, { quantity })

      setCart(response.cart)
      setItems(response.items)
      setTotals(response.totals)

      showToast('Cart updated', 'success')
    } catch (error: any) {
      const message = error.response?.data?.error || 'Failed to update cart'
      showToast(message, 'error')
      throw error
    } finally {
      setLoading(false)
    }
  }

  const removeItem = async (itemId: string) => {
    try {
      setLoading(true)

      await cartService.removeFromCart(itemId)

      // Refresh cart after removal
      await loadCart()

      showToast('Item removed from cart', 'success')
    } catch (error: any) {
      const message = error.response?.data?.error || 'Failed to remove item'
      showToast(message, 'error')
      throw error
    } finally {
      setLoading(false)
    }
  }

  const clearCart = async () => {
    try {
      setLoading(true)

      await cartService.clearCart()

      setCart(null)
      setItems([])
      setTotals({
        subtotal: 0,
        tax: 0,
        shipping: 0,
        total: 0,
      })

      showToast('Cart cleared', 'success')
    } catch (error: any) {
      const message = error.response?.data?.error || 'Failed to clear cart'
      showToast(message, 'error')
      throw error
    } finally {
      setLoading(false)
    }
  }

  const refreshCart = async () => {
    await loadCart()
  }

  const itemCount = items.reduce((total, item) => total + item.quantity, 0)

  const value = {
    cart,
    items,
    totals,
    itemCount,
    loading,
    addToCart,
    updateQuantity,
    removeItem,
    clearCart,
    refreshCart,
  }

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}

export function useCart() {
  const context = useContext(CartContext)
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider')
  }
  return context
}
