import { useState, useEffect } from 'react'
import { Product, ProductFilters, ProductListResponse } from '@/types/product.types'
import productService from '@/services/productService'

export const useProducts = (filters: ProductFilters = {}) => {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pagination, setPagination] = useState({
    total: 0,
    pages: 0,
    currentPage: 1,
    hasNext: false,
    hasPrev: false,
  })

  useEffect(() => {
    loadProducts()
  }, [
    filters.page,
    filters.per_page,
    filters.category_id,
    filters.search,
    filters.is_featured,
    filters.sort_by,
    filters.sort_order,
  ])

  const loadProducts = async () => {
    try {
      setLoading(true)
      setError(null)

      const response: ProductListResponse = await productService.getProducts(filters)

      setProducts(response.products)
      setPagination({
        total: response.total,
        pages: response.pages,
        currentPage: response.current_page,
        hasNext: response.has_next,
        hasPrev: response.has_prev,
      })
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load products')
      setProducts([])
    } finally {
      setLoading(false)
    }
  }

  const refetch = () => {
    loadProducts()
  }

  return {
    products,
    loading,
    error,
    pagination,
    refetch,
  }
}

export const useFeaturedProducts = (limit = 8) => {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadFeaturedProducts()
  }, [limit])

  const loadFeaturedProducts = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await productService.getFeaturedProducts(limit)
      setProducts(response)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load featured products')
      setProducts([])
    } finally {
      setLoading(false)
    }
  }

  return {
    products,
    loading,
    error,
  }
}

export const useProduct = (productId: string | undefined) => {
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (productId) {
      loadProduct()
    }
  }, [productId])

  const loadProduct = async () => {
    if (!productId) return

    try {
      setLoading(true)
      setError(null)

      const response = await productService.getProduct(productId)
      setProduct(response)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load product')
      setProduct(null)
    } finally {
      setLoading(false)
    }
  }

  return {
    product,
    loading,
    error,
    refetch: loadProduct,
  }
}
