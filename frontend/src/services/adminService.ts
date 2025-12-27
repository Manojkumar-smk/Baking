import api from './api'
import { Product, ProductFormData, ProductFilters, ProductListResponse } from '@/types/product.types'

export const adminService = {
  // ==================== Dashboard ====================

  async getDashboardStats() {
    const response = await api.get('/admin/dashboard')
    return response.data
  },

  // ==================== Product Management ====================

  async getProducts(filters: ProductFilters = {}): Promise<ProductListResponse> {
    const params = new URLSearchParams()

    if (filters.page) params.append('page', filters.page.toString())
    if (filters.per_page) params.append('per_page', filters.per_page.toString())
    if (filters.category_id) params.append('category_id', filters.category_id)
    if (filters.search) params.append('search', filters.search)
    if (filters.in_stock_only !== undefined) params.append('in_stock_only', filters.in_stock_only.toString())
    if (filters.is_active !== undefined) params.append('is_active', filters.is_active.toString())
    if (filters.is_featured !== undefined) params.append('is_featured', filters.is_featured.toString())
    if (filters.sort_by) params.append('sort_by', filters.sort_by)
    if (filters.sort_order) params.append('sort_order', filters.sort_order)

    const response = await api.get(`/admin/products?${params.toString()}`)
    return response.data
  },

  async getProduct(productId: string): Promise<Product> {
    const response = await api.get(`/admin/products/${productId}`)
    return response.data.product
  },

  async createProduct(data: ProductFormData): Promise<Product> {
    const formData = new FormData()

    formData.append('name', data.name)
    formData.append('price', data.price.toString())

    if (data.description) formData.append('description', data.description)
    if (data.category_id) formData.append('category_id', data.category_id)
    formData.append('stock_quantity', data.stock_quantity.toString())
    formData.append('low_stock_threshold', data.low_stock_threshold.toString())
    if (data.sku) formData.append('sku', data.sku)
    formData.append('is_featured', data.is_featured.toString())
    formData.append('is_active', data.is_active.toString())

    // Add main image
    if (data.image) {
      formData.append('image', data.image)
    }

    // Add additional images
    if (data.additional_images && data.additional_images.length > 0) {
      data.additional_images.forEach((file) => {
        formData.append('additional_images[]', file)
      })
    }

    // Add ingredients and allergens as JSON
    if (data.ingredients && data.ingredients.length > 0) {
      formData.append('ingredients', JSON.stringify(data.ingredients))
    }
    if (data.allergens && data.allergens.length > 0) {
      formData.append('allergens', JSON.stringify(data.allergens))
    }

    const response = await api.post('/admin/products', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data.product
  },

  async updateProduct(productId: string, data: Partial<ProductFormData>): Promise<Product> {
    const formData = new FormData()

    if (data.name) formData.append('name', data.name)
    if (data.price !== undefined) formData.append('price', data.price.toString())
    if (data.description) formData.append('description', data.description)
    if (data.category_id) formData.append('category_id', data.category_id)
    if (data.stock_quantity !== undefined) formData.append('stock_quantity', data.stock_quantity.toString())
    if (data.low_stock_threshold !== undefined) formData.append('low_stock_threshold', data.low_stock_threshold.toString())
    if (data.sku) formData.append('sku', data.sku)
    if (data.is_featured !== undefined) formData.append('is_featured', data.is_featured.toString())
    if (data.is_active !== undefined) formData.append('is_active', data.is_active.toString())

    // Add main image
    if (data.image) {
      formData.append('image', data.image)
    }

    // Add additional images
    if (data.additional_images && data.additional_images.length > 0) {
      data.additional_images.forEach((file) => {
        formData.append('additional_images[]', file)
      })
    }

    // Add ingredients and allergens as JSON
    if (data.ingredients) {
      formData.append('ingredients', JSON.stringify(data.ingredients))
    }
    if (data.allergens) {
      formData.append('allergens', JSON.stringify(data.allergens))
    }

    const response = await api.put(`/admin/products/${productId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data.product
  },

  async updateStock(productId: string, stockQuantity: number): Promise<Product> {
    const response = await api.put(`/admin/products/${productId}/stock`, {
      stock_quantity: stockQuantity,
    })
    return response.data.product
  },

  async deleteProduct(productId: string, hardDelete = false): Promise<void> {
    const params = hardDelete ? '?hard=true' : ''
    await api.delete(`/admin/products/${productId}${params}`)
  },

  async uploadProductImages(productId: string, images: File[]): Promise<Product> {
    const formData = new FormData()

    images.forEach((file) => {
      formData.append('images[]', file)
    })

    const response = await api.post(`/admin/products/${productId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data.product
  },

  async getLowStockProducts(threshold?: number): Promise<Product[]> {
    const params = threshold ? `?threshold=${threshold}` : ''
    const response = await api.get(`/admin/products/low-stock${params}`)
    return response.data.products
  },

  // ==================== Order Management ====================

  async getOrders(filters: any = {}) {
    const params = new URLSearchParams()

    if (filters.page) params.append('page', filters.page.toString())
    if (filters.per_page) params.append('per_page', filters.per_page.toString())
    if (filters.status) params.append('status', filters.status)
    if (filters.payment_status) params.append('payment_status', filters.payment_status)
    if (filters.start_date) params.append('start_date', filters.start_date)
    if (filters.end_date) params.append('end_date', filters.end_date)

    const response = await api.get(`/admin/orders?${params.toString()}`)
    return response.data
  },

  async updateOrderStatus(orderId: string, status: string) {
    const response = await api.put(`/admin/orders/${orderId}/status`, { status })
    return response.data.order
  },

  async updateOrderTracking(orderId: string, trackingNumber: string, trackingUrl?: string) {
    const response = await api.put(`/admin/orders/${orderId}/tracking`, {
      tracking_number: trackingNumber,
      tracking_url: trackingUrl,
    })
    return response.data.order
  },

  // ==================== User Management ====================

  async getUsers(filters: any = {}) {
    const params = new URLSearchParams()

    if (filters.page) params.append('page', filters.page.toString())
    if (filters.per_page) params.append('per_page', filters.per_page.toString())
    if (filters.role) params.append('role', filters.role)
    if (filters.is_active !== undefined) params.append('is_active', filters.is_active.toString())

    const response = await api.get(`/admin/users?${params.toString()}`)
    return response.data
  },

  async updateUser(userId: string, data: { is_active?: boolean; role?: string }) {
    const response = await api.put(`/admin/users/${userId}`, data)
    return response.data.user
  },
}

export default adminService
