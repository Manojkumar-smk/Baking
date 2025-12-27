import { useState, useEffect } from 'react'
import { Product, ProductFormData } from '@/types/product.types'
import adminService from '@/services/adminService'
import styles from './ProductForm.module.css'

interface ProductFormProps {
  product: Product | null
  onClose: () => void
  onSuccess: () => void
}

const ProductForm = ({ product, onClose, onSuccess }: ProductFormProps) => {
  const [formData, setFormData] = useState<ProductFormData>({
    name: '',
    price: 0,
    description: '',
    stock_quantity: 0,
    low_stock_threshold: 10,
    sku: '',
    is_featured: false,
    is_active: true,
  })

  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [additionalPreviews, setAdditionalPreviews] = useState<string[]>([])
  const [ingredientsInput, setIngredientsInput] = useState('')
  const [allergensInput, setAllergensInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name,
        price: product.price,
        description: product.description || '',
        stock_quantity: product.stock_quantity,
        low_stock_threshold: product.low_stock_threshold,
        sku: product.sku || '',
        is_featured: product.is_featured,
        is_active: product.is_active,
        ingredients: product.ingredients || [],
        allergens: product.allergens || [],
      })

      setImagePreview(product.image_url || null)
      setIngredientsInput(product.ingredients?.join(', ') || '')
      setAllergensInput(product.allergens?.join(', ') || '')
    }
  }, [product])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked
      setFormData((prev) => ({ ...prev, [name]: checked }))
    } else if (type === 'number') {
      setFormData((prev) => ({ ...prev, [name]: parseFloat(value) || 0 }))
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }))
    }
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setFormData((prev) => ({ ...prev, image: file }))

      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleAdditionalImagesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files) {
      const filesArray = Array.from(files)
      setFormData((prev) => ({ ...prev, additional_images: filesArray }))

      // Create previews
      const previews: string[] = []
      filesArray.forEach((file) => {
        const reader = new FileReader()
        reader.onloadend = () => {
          previews.push(reader.result as string)
          if (previews.length === filesArray.length) {
            setAdditionalPreviews(previews)
          }
        }
        reader.readAsDataURL(file)
      })
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      // Parse ingredients and allergens
      const ingredients = ingredientsInput
        .split(',')
        .map((item) => item.trim())
        .filter((item) => item.length > 0)

      const allergens = allergensInput
        .split(',')
        .map((item) => item.trim())
        .filter((item) => item.length > 0)

      const submitData: ProductFormData = {
        ...formData,
        ingredients: ingredients.length > 0 ? ingredients : undefined,
        allergens: allergens.length > 0 ? allergens : undefined,
      }

      if (product) {
        // Update existing product
        await adminService.updateProduct(product.id, submitData)
      } else {
        // Create new product
        await adminService.createProduct(submitData)
      }

      onSuccess()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to save product')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.modal}>
      <div className={styles.modalContent}>
        <div className={styles.modalHeader}>
          <h2>{product ? 'Edit Product' : 'Create New Product'}</h2>
          <button onClick={onClose} className={styles.closeBtn}>
            ×
          </button>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="name">Product Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                placeholder="e.g., Chocolate Chip Cookie"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="price">Price *</label>
              <input
                type="number"
                id="price"
                name="price"
                value={formData.price}
                onChange={handleInputChange}
                required
                step="0.01"
                min="0"
                placeholder="0.00"
              />
            </div>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows={4}
              placeholder="Describe your product..."
            />
          </div>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="sku">SKU</label>
              <input
                type="text"
                id="sku"
                name="sku"
                value={formData.sku}
                onChange={handleInputChange}
                placeholder="e.g., CHOC-001"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="stock_quantity">Stock Quantity *</label>
              <input
                type="number"
                id="stock_quantity"
                name="stock_quantity"
                value={formData.stock_quantity}
                onChange={handleInputChange}
                required
                min="0"
                placeholder="0"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="low_stock_threshold">Low Stock Threshold</label>
              <input
                type="number"
                id="low_stock_threshold"
                name="low_stock_threshold"
                value={formData.low_stock_threshold}
                onChange={handleInputChange}
                min="0"
                placeholder="10"
              />
            </div>
          </div>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="ingredients">Ingredients (comma-separated)</label>
              <input
                type="text"
                id="ingredients"
                value={ingredientsInput}
                onChange={(e) => setIngredientsInput(e.target.value)}
                placeholder="flour, butter, sugar, chocolate chips"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="allergens">Allergens (comma-separated)</label>
              <input
                type="text"
                id="allergens"
                value={allergensInput}
                onChange={(e) => setAllergensInput(e.target.value)}
                placeholder="wheat, dairy, eggs"
              />
            </div>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="image">Main Product Image</label>
            <input
              type="file"
              id="image"
              accept="image/*"
              onChange={handleImageChange}
            />
            {imagePreview && (
              <div className={styles.imagePreview}>
                <img src={imagePreview} alt="Preview" />
              </div>
            )}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="additional_images">Additional Images</label>
            <input
              type="file"
              id="additional_images"
              accept="image/*"
              multiple
              onChange={handleAdditionalImagesChange}
            />
            {additionalPreviews.length > 0 && (
              <div className={styles.additionalPreviews}>
                {additionalPreviews.map((preview, index) => (
                  <div key={index} className={styles.imagePreviewSmall}>
                    <img src={preview} alt={`Preview ${index + 1}`} />
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  name="is_featured"
                  checked={formData.is_featured}
                  onChange={handleInputChange}
                />
                <span>Featured Product</span>
              </label>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleInputChange}
                />
                <span>Active (visible to customers)</span>
              </label>
            </div>
          </div>

          <div className={styles.formActions}>
            <button type="button" onClick={onClose} className={styles.btnCancel}>
              Cancel
            </button>
            <button type="submit" disabled={loading} className={styles.btnSubmit}>
              {loading ? 'Saving...' : product ? 'Update Product' : 'Create Product'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ProductForm
