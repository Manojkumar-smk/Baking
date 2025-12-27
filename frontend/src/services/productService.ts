import api from './api'
import { Product, ProductFilters, ProductListResponse, Category } from '@/types/product.types'

export const productService = {
  // ==================== Products ====================

  async getProducts(filters: ProductFilters = {}): Promise<ProductListResponse> {
    const params = new URLSearchParams()

    if (filters.page) params.append('page', filters.page.toString())
    if (filters.per_page) params.append('per_page', filters.per_page.toString())
    if (filters.category_id) params.append('category_id', filters.category_id)
    if (filters.search) params.append('search', filters.search)
    if (filters.is_featured !== undefined) params.append('is_featured', filters.is_featured.toString())
    if (filters.sort_by) params.append('sort_by', filters.sort_by)
    if (filters.sort_order) params.append('sort_order', filters.sort_order)

    const response = await api.get(`/products?${params.toString()}`)
    return response.data
  },

  async getProduct(productId: string): Promise<Product> {
    const response = await api.get(`/products/${productId}`)
    return response.data.product
  },

  async getProductBySlug(slug: string): Promise<Product> {
    const response = await api.get(`/products/slug/${slug}`)
    return response.data.product
  },

  async getFeaturedProducts(limit = 8): Promise<Product[]> {
    const response = await api.get(`/products/featured?limit=${limit}`)
    return response.data.products
  },

  async searchProducts(query: string, page = 1, perPage = 20): Promise<ProductListResponse> {
    const params = new URLSearchParams()
    params.append('q', query)
    params.append('page', page.toString())
    params.append('per_page', perPage.toString())

    const response = await api.get(`/products/search?${params.toString()}`)
    return response.data
  },

  // ==================== Categories ====================

  async getCategories(): Promise<Category[]> {
    const response = await api.get('/categories')
    return response.data.categories
  },

  async getCategory(categoryId: string): Promise<Category> {
    const response = await api.get(`/categories/${categoryId}`)
    return response.data.category
  },

  async getCategoryBySlug(slug: string): Promise<Category> {
    const response = await api.get(`/categories/slug/${slug}`)
    return response.data.category
  },

  async getCategoryProducts(categoryId: string, page = 1, perPage = 20): Promise<ProductListResponse> {
    const params = new URLSearchParams()
    params.append('page', page.toString())
    params.append('per_page', perPage.toString())

    const response = await api.get(`/categories/${categoryId}/products?${params.toString()}`)
    return response.data
  },
}

export default productService
