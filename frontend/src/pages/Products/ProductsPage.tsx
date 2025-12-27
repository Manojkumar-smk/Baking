import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Product, Category } from '@/types/product.types'
import { useProducts } from '@/hooks/useProducts'
import productService from '@/services/productService'
import ProductGrid from '@/components/products/ProductGrid/ProductGrid'
import { useCart } from '@/contexts/CartContext'
import styles from './ProductsPage.module.css'

const ProductsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(
    searchParams.get('category') || undefined
  )
  const [searchTerm, setSearchTerm] = useState(searchParams.get('search') || '')
  const [currentPage, setCurrentPage] = useState(1)

  const { products, loading, error, pagination } = useProducts({
    page: currentPage,
    per_page: 20,
    category_id: selectedCategory,
    search: searchTerm || undefined,
    sort_by: 'created_at',
    sort_order: 'desc',
  })

  useEffect(() => {
    loadCategories()
  }, [])

  useEffect(() => {
    // Update URL params when filters change
    const params: Record<string, string> = {}
    if (selectedCategory) params.category = selectedCategory
    if (searchTerm) params.search = searchTerm
    setSearchParams(params)
  }, [selectedCategory, searchTerm])

  const loadCategories = async () => {
    try {
      const data = await productService.getCategories()
      setCategories(data)
    } catch (err) {
      console.error('Failed to load categories:', err)
    }
  }

  const handleCategoryChange = (categoryId: string | undefined) => {
    setSelectedCategory(categoryId)
    setCurrentPage(1)
  }

  const handleSearchChange = (value: string) => {
    setSearchTerm(value)
    setCurrentPage(1)
  }

  const { addToCart } = useCart()

  const handleAddToCart = async (product: Product) => {
    try {
      await addToCart(product, 1)
    } catch (error) {
      // Error is handled by CartContext
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Our Cookies</h1>
        <p>Freshly baked and ready to delight!</p>
      </div>

      <div className={styles.content}>
        {/* Sidebar Filters */}
        <aside className={styles.sidebar}>
          <div className={styles.filterSection}>
            <h3>Search</h3>
            <input
              type="text"
              placeholder="Search cookies..."
              value={searchTerm}
              onChange={(e) => handleSearchChange(e.target.value)}
              className={styles.searchInput}
            />
          </div>

          <div className={styles.filterSection}>
            <h3>Categories</h3>
            <div className={styles.categoryList}>
              <button
                onClick={() => handleCategoryChange(undefined)}
                className={`${styles.categoryBtn} ${!selectedCategory ? styles.active : ''}`}
              >
                All Categories
              </button>

              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => handleCategoryChange(category.id)}
                  className={`${styles.categoryBtn} ${selectedCategory === category.id ? styles.active : ''}`}
                >
                  {category.name}
                </button>
              ))}
            </div>
          </div>

          {selectedCategory && (
            <button
              onClick={() => {
                setSelectedCategory(undefined)
                setSearchTerm('')
              }}
              className={styles.clearFilters}
            >
              Clear Filters
            </button>
          )}
        </aside>

        {/* Products Grid */}
        <main className={styles.main}>
          {loading && products.length === 0 ? (
            <div className={styles.loading}>Loading products...</div>
          ) : error ? (
            <div className={styles.error}>{error}</div>
          ) : (
            <>
              <div className={styles.resultInfo}>
                <p>
                  Showing {products.length} of {pagination.total} products
                  {searchTerm && ` for "${searchTerm}"`}
                  {selectedCategory && categories.find(c => c.id === selectedCategory) &&
                    ` in ${categories.find(c => c.id === selectedCategory)?.name}`
                  }
                </p>
              </div>

              <ProductGrid
                products={products}
                onAddToCart={handleAddToCart}
                emptyMessage={
                  searchTerm || selectedCategory
                    ? 'No products match your filters. Try adjusting your search.'
                    : 'No products available at this time.'
                }
              />

              {/* Pagination */}
              {pagination.pages > 1 && (
                <div className={styles.pagination}>
                  <button
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    disabled={!pagination.hasPrev || loading}
                    className={styles.pageBtn}
                  >
                    Previous
                  </button>

                  <span className={styles.pageInfo}>
                    Page {currentPage} of {pagination.pages}
                  </span>

                  <button
                    onClick={() => setCurrentPage((p) => Math.min(pagination.pages, p + 1))}
                    disabled={!pagination.hasNext || loading}
                    className={styles.pageBtn}
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  )
}

export default ProductsPage
