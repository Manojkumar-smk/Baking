import { Link } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { useCart } from '@/contexts/CartContext'
import styles from './Header.module.css'

function Header() {
  const { isAuthenticated, user, logout } = useAuth()
  const { itemCount } = useCart()

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link to="/" className={styles.logo}>
          🍪 Cookie Shop
        </Link>

        <nav className={styles.nav}>
          <Link to="/" className={styles.navLink}>Home</Link>
          <Link to="/products" className={styles.navLink}>Products</Link>
          <Link to="/cart" className={styles.cartLink}>
            <span>Cart</span>
            {itemCount > 0 && (
              <span className={styles.cartBadge}>{itemCount}</span>
            )}
          </Link>

          {isAuthenticated ? (
            <>
              <span className={styles.greeting}>Hello, {user?.first_name}</span>
              {user?.role === 'admin' && (
                <Link to="/admin/products" className={styles.navLink}>Admin</Link>
              )}
              <Link to="/profile" className={styles.navLink}>Profile</Link>
              <button onClick={logout} className={styles.logoutBtn}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className={styles.navLink}>Login</Link>
              <Link to="/register" className={styles.navLink}>Register</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}

export default Header
