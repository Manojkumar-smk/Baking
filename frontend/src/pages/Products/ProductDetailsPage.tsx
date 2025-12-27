import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useProduct } from '@/hooks/useProducts'
import { useCart } from '@/contexts/CartContext'
import styles from './ProductDetailsPage.module.css'

const ProductDetailsPage = () => {
  const { productId } = useParams<{ productId: string }>()
  const { product, loading, error } = useProduct(productId)
  const { addToCart } = useCart()
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [quantity, setQuantity] = useState(1)

  const handleAddToCart = async () => {
    if (product && product.in_stock) {
      try {
        await addToCart(product, quantity)
        setQuantity(1) // Reset quantity after adding
      } catch (error) {
        // Error is handled by CartContext
      }
    }
  }

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading product...</div>
      </div>
    )
  }

  if (error || !product) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          {error || 'Product not found'}
        </div>
        <Link to="/products" className={styles.backLink}>
          ← Back to Products
        </Link>
      </div>
    )
  }

  const displayImage = selectedImage || product.image_url
  const additionalImages = product.images || []

  return (
    <div className={styles.container}>
      <Link to="/products" className={styles.backLink}>
        ← Back to Products
      </Link>

      <div className={styles.content}>
        {/* Image Gallery */}
        <div className={styles.gallery}>
          <div className={styles.mainImageContainer}>
            {displayImage ? (
              <img
                src={displayImage}
                alt={product.name}
                className={styles.mainImage}
              />
            ) : (
              <div className={styles.noImage}>No Image Available</div>
            )}

            {!product.in_stock && (
              <div className={styles.outOfStockOverlay}>
                <span>Out of Stock</span>
              </div>
            )}
          </div>

          {(product.image_url || additionalImages.length > 0) && (
            <div className={styles.thumbnails}>
              {product.image_url && (
                <button
                  onClick={() => setSelectedImage(product.image_url)}
                  className={`${styles.thumbnail} ${selectedImage === product.image_url || !selectedImage ? styles.active : ''}`}
                >
                  <img src={product.image_url} alt={product.name} />
                </button>
              )}

              {additionalImages.map((image, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedImage(image)}
                  className={`${styles.thumbnail} ${selectedImage === image ? styles.active : ''}`}
                >
                  <img src={image} alt={`${product.name} ${index + 1}`} />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className={styles.info}>
          {product.is_featured && (
            <div className={styles.featuredBadge}>Featured Product</div>
          )}

          <h1 className={styles.name}>{product.name}</h1>

          <div className={styles.price}>${product.price.toFixed(2)}</div>

          {product.description && (
            <p className={styles.description}>{product.description}</p>
          )}

          {/* Stock Status */}
          <div className={styles.stockStatus}>
            {product.in_stock ? (
              product.is_low_stock ? (
                <span className={styles.lowStock}>
                  Low Stock - Only {product.stock_quantity} left!
                </span>
              ) : (
                <span className={styles.inStock}>In Stock</span>
              )
            ) : (
              <span className={styles.outOfStock}>Out of Stock</span>
            )}
          </div>

          {/* Add to Cart */}
          {product.in_stock && (
            <div className={styles.addToCart}>
              <div className={styles.quantityControl}>
                <label>Quantity:</label>
                <div className={styles.quantityButtons}>
                  <button
                    onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                    className={styles.quantityBtn}
                  >
                    −
                  </button>
                  <input
                    type="number"
                    value={quantity}
                    onChange={(e) => {
                      const val = parseInt(e.target.value) || 1
                      setQuantity(Math.max(1, Math.min(product.stock_quantity, val)))
                    }}
                    className={styles.quantityInput}
                    min="1"
                    max={product.stock_quantity}
                  />
                  <button
                    onClick={() => setQuantity((q) => Math.min(product.stock_quantity, q + 1))}
                    className={styles.quantityBtn}
                  >
                    +
                  </button>
                </div>
              </div>

              <button
                onClick={handleAddToCart}
                className={styles.addToCartBtn}
              >
                Add to Cart
              </button>
            </div>
          )}

          {/* Product Details */}
          <div className={styles.details}>
            {product.sku && (
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>SKU:</span>
                <span className={styles.detailValue}>{product.sku}</span>
              </div>
            )}

            {product.ingredients && product.ingredients.length > 0 && (
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Ingredients:</span>
                <span className={styles.detailValue}>
                  {product.ingredients.join(', ')}
                </span>
              </div>
            )}

            {product.allergens && product.allergens.length > 0 && (
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Allergens:</span>
                <span className={`${styles.detailValue} ${styles.allergens}`}>
                  {product.allergens.join(', ')}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProductDetailsPage
