import { Link } from 'react-router-dom'
import { useFeaturedProducts } from '@/hooks/useProducts'
import ProductGrid from '@/components/products/ProductGrid/ProductGrid'
import styles from './HomePage.module.css'

const HomePage = () => {
  const { products, loading } = useFeaturedProducts(8)

  const handleAddToCart = (product: any) => {
    // TODO: Implement add to cart functionality
    console.log('Add to cart:', product)
    alert(`Added ${product.name} to cart!`)
  }

  return (
    <div className={styles.container}>
      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles.heroContent}>
          <h1 className={styles.heroTitle}>Freshly Baked Cookies</h1>
          <p className={styles.heroSubtitle}>
            Handcrafted with love, delivered to your door
          </p>
          <Link to="/products" className={styles.heroButton}>
            Shop Now
          </Link>
        </div>
        <div className={styles.heroImage}>
          {/* Placeholder for hero image */}
          <div className={styles.heroImagePlaceholder}>🍪</div>
        </div>
      </section>

      {/* Featured Products */}
      <section className={styles.featuredSection}>
        <div className={styles.sectionHeader}>
          <h2>Featured Cookies</h2>
          <Link to="/products" className={styles.viewAllLink}>
            View All →
          </Link>
        </div>

        {loading ? (
          <div className={styles.loading}>Loading featured products...</div>
        ) : (
          <ProductGrid
            products={products}
            onAddToCart={handleAddToCart}
            emptyMessage="No featured products available at this time."
          />
        )}
      </section>

      {/* Features Section */}
      <section className={styles.features}>
        <div className={styles.feature}>
          <div className={styles.featureIcon}>🎂</div>
          <h3>Fresh Daily</h3>
          <p>Baked fresh every morning with premium ingredients</p>
        </div>

        <div className={styles.feature}>
          <div className={styles.featureIcon}>🚚</div>
          <h3>Fast Delivery</h3>
          <p>Quick and reliable delivery right to your doorstep</p>
        </div>

        <div className={styles.feature}>
          <div className={styles.featureIcon}>✨</div>
          <h3>Quality Guaranteed</h3>
          <p>100% satisfaction or your money back</p>
        </div>
      </section>
    </div>
  )
}

export default HomePage
