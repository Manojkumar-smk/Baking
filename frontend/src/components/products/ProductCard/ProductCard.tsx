import { Link } from 'react-router-dom'
import { Product } from '@/types/product.types'
import styles from './ProductCard.module.css'

interface ProductCardProps {
  product: Product
  onAddToCart?: (product: Product) => void
}

const ProductCard = ({ product, onAddToCart }: ProductCardProps) => {
  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault()
    if (onAddToCart && product.in_stock) {
      onAddToCart(product)
    }
  }

  const getImageUrl = (imageUrl: string | null): string | undefined => {
    if (!imageUrl) return undefined
    if (imageUrl.startsWith('http')) return imageUrl
    const apiUrl = import.meta.env.VITE_API_URL
    const backendUrl = apiUrl.replace('/api/v1', '')
    return `${backendUrl}${imageUrl}`
  }

  return (
    <Link to={`/products/${product.id}`} className={styles.card}>
      <div className={styles.imageContainer}>
        {product.image_url ? (
          <img
            src={getImageUrl(product.image_url)}
            alt={product.name}
            className={styles.image}
          />
        ) : (
          <div className={styles.noImage}>No Image</div>
        )}

        {product.is_featured && (
          <div className={styles.featuredBadge}>Featured</div>
        )}

        {!product.in_stock && (
          <div className={styles.outOfStockOverlay}>
            <span>Out of Stock</span>
          </div>
        )}

        {product.in_stock && product.is_low_stock && (
          <div className={styles.lowStockBadge}>Low Stock</div>
        )}
      </div>

      <div className={styles.content}>
        <h3 className={styles.name}>{product.name}</h3>

        {product.description && (
          <p className={styles.description}>
            {product.description.substring(0, 80)}
            {product.description.length > 80 && '...'}
          </p>
        )}

        <div className={styles.footer}>
          <div className={styles.price}>${product.price.toFixed(2)}</div>

          <button
            onClick={handleAddToCart}
            disabled={!product.in_stock}
            className={styles.addToCartBtn}
          >
            {product.in_stock ? 'Add to Cart' : 'Out of Stock'}
          </button>
        </div>

        {product.allergens && product.allergens.length > 0 && (
          <div className={styles.allergens}>
            <span className={styles.allergensLabel}>Allergens:</span>{' '}
            {product.allergens.join(', ')}
          </div>
        )}
      </div>
    </Link>
  )
}

export default ProductCard
