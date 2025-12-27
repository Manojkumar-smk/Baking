export interface Product {
  id: string
  name: string
  slug: string
  description: string | null
  price: number
  sku: string | null
  stock_quantity: number
  low_stock_threshold: number
  in_stock: boolean
  is_low_stock: boolean
  image_url: string | null
  images: string[] | null
  category_id: string | null
  category?: Category
  ingredients: string[] | null
  allergens: string[] | null
  is_featured: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Category {
  id: string
  name: string
  slug: string
  description: string | null
  image_url: string | null
  display_order: number
  created_at: string
  updated_at: string
}

export interface ProductFormData {
  name: string
  price: number
  description?: string
  category_id?: string
  stock_quantity: number
  low_stock_threshold: number
  sku?: string
  image?: File
  additional_images?: File[]
  ingredients?: string[]
  allergens?: string[]
  is_featured: boolean
  is_active: boolean
}

export interface ProductFilters {
  page?: number
  per_page?: number
  category_id?: string
  search?: string
  in_stock_only?: boolean
  is_active?: boolean
  is_featured?: boolean
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface ProductListResponse {
  products: Product[]
  total: number
  pages: number
  current_page: number
  per_page: number
  has_next: boolean
  has_prev: boolean
}
