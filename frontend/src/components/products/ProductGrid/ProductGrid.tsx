import { Product } from '@/types/product.types'
import ProductCard from '../ProductCard/ProductCard'
import styles from './ProductGrid.module.css'

interface ProductGridProps {
  products: Product[]
  onAddToCart?: (product: Product) => void
  emptyMessage?: string
}

const ProductGrid = ({ products, onAddToCart, emptyMessage = 'No products found' }: ProductGridProps) => {
  if (products.length === 0) {
    return (
      <div className={styles.empty}>
        <p>{emptyMessage}</p>
      </div>
    )
  }

  return (
    <div className={styles.grid}>
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          onAddToCart={onAddToCart}
        />
      ))}
    </div>
  )
}

export default ProductGrid
