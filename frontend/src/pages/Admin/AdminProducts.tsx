import { useState, useEffect } from 'react'
import { Product, ProductFilters } from '@/types/product.types'
import adminService from '@/services/adminService'
import ProductForm from '@/components/admin/ProductManager/ProductForm'
import styles from './AdminProducts.module.css'

const AdminProducts = () => {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)

  // Pagination and filters
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterInStock, setFilterInStock] = useState(false)
  const [filterActive, setFilterActive] = useState<boolean | undefined>(true)

  useEffect(() => {
    loadProducts()
  }, [currentPage, searchTerm, filterInStock, filterActive])

  const loadProducts = async () => {
    try {
      setLoading(true)
      setError(null)

      const filters: ProductFilters = {
        page: currentPage,
        per_page: 20,
        search: searchTerm || undefined,
        in_stock_only: filterInStock || undefined,
        is_active: filterActive,
        sort_by: 'created_at',
        sort_order: 'desc',
      }

      const response = await adminService.getProducts(filters)
      setProducts(response.products)
      setTotalPages(response.pages)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load products')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateProduct = () => {
    setEditingProduct(null)
    setShowForm(true)
  }

  const handleEditProduct = (product: Product) => {
    setEditingProduct(product)
    setShowForm(true)
  }

  const handleFormClose = () => {
    setShowForm(false)
    setEditingProduct(null)
  }

  const handleFormSuccess = () => {
    setShowForm(false)
    setEditingProduct(null)
    loadProducts()
  }

  const handleDeleteProduct = async (productId: string) => {
    if (!confirm('Are you sure you want to delete this product?')) {
      return
    }

    try {
      await adminService.deleteProduct(productId, false) // Soft delete
      loadProducts()
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to delete product')
    }
  }

  const handleUpdateStock = async (productId: string, newStock: number) => {
    try {
      await adminService.updateStock(productId, newStock)
      loadProducts()
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to update stock')
    }
  }

  const getStockStatusBadge = (product: Product) => {
    if (!product.in_stock) {
      return <span className={styles.badgeOutOfStock}>Out of Stock</span>
    } else if (product.is_low_stock) {
      return <span className={styles.badgeLowStock}>Low Stock</span>
    } else {
      return <span className={styles.badgeInStock}>In Stock</span>
    }
  }

  if (loading && products.length === 0) {
    return <div className={styles.loading}>Loading products...</div>
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Product Management</h1>
        <button onClick={handleCreateProduct} className={styles.btnPrimary}>
          + Add New Product
        </button>
      </div>

      {/* Filters */}
      <div className={styles.filters}>
        <input
          type="text"
          placeholder="Search products..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value)
            setCurrentPage(1)
          }}
          className={styles.searchInput}
        />

        <label className={styles.checkboxLabel}>
          <input
            type="checkbox"
            checked={filterInStock}
            onChange={(e) => {
              setFilterInStock(e.target.checked)
              setCurrentPage(1)
            }}
          />
          Show only in stock
        </label>

        <select
          value={filterActive === undefined ? 'all' : filterActive ? 'active' : 'inactive'}
          onChange={(e) => {
            const value = e.target.value
            setFilterActive(value === 'all' ? undefined : value === 'active')
            setCurrentPage(1)
          }}
          className={styles.select}
        >
          <option value="all">All Products</option>
          <option value="active">Active Only</option>
          <option value="inactive">Inactive Only</option>
        </select>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {/* Products Table */}
      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Image</th>
              <th>Name</th>
              <th>SKU</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Status</th>
              <th>Featured</th>
              <th>Active</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.id}>
                <td>
                  {product.image_url ? (
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className={styles.productImage}
                    />
                  ) : (
                    <div className={styles.noImage}>No Image</div>
                  )}
                </td>
                <td>
                  <div className={styles.productName}>{product.name}</div>
                  {product.description && (
                    <div className={styles.productDesc}>
                      {product.description.substring(0, 60)}...
                    </div>
                  )}
                </td>
                <td>{product.sku || '-'}</td>
                <td className={styles.price}>${product.price.toFixed(2)}</td>
                <td>
                  <div className={styles.stockControl}>
                    <input
                      type="number"
                      value={product.stock_quantity}
                      onChange={(e) => {
                        const newStock = parseInt(e.target.value) || 0
                        if (newStock !== product.stock_quantity) {
                          handleUpdateStock(product.id, newStock)
                        }
                      }}
                      className={styles.stockInput}
                      min="0"
                    />
                  </div>
                </td>
                <td>{getStockStatusBadge(product)}</td>
                <td>
                  <span className={product.is_featured ? styles.badgeYes : styles.badgeNo}>
                    {product.is_featured ? 'Yes' : 'No'}
                  </span>
                </td>
                <td>
                  <span className={product.is_active ? styles.badgeActive : styles.badgeInactive}>
                    {product.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>
                  <div className={styles.actions}>
                    <button
                      onClick={() => handleEditProduct(product)}
                      className={styles.btnEdit}
                      title="Edit"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteProduct(product.id)}
                      className={styles.btnDelete}
                      title="Delete"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}

            {products.length === 0 && (
              <tr>
                <td colSpan={9} className={styles.emptyState}>
                  No products found. Create your first product to get started!
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className={styles.pagination}>
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className={styles.btnPage}
          >
            Previous
          </button>

          <span className={styles.pageInfo}>
            Page {currentPage} of {totalPages}
          </span>

          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className={styles.btnPage}
          >
            Next
          </button>
        </div>
      )}

      {/* Product Form Modal */}
      {showForm && (
        <ProductForm
          product={editingProduct}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
        />
      )}
    </div>
  )
}

export default AdminProducts
