import { Link } from 'react-router-dom'
import { useAuth } from '@contexts/AuthContext'
import { useCart } from '@contexts/CartContext'

function Header() {
  const { isAuthenticated, user, logout } = useAuth()
  const { itemCount } = useCart()

  return (
    <header style={{
      backgroundColor: '#8b4513',
      color: 'white',
      padding: '1rem',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <div className="container" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Link to="/" style={{ color: 'white', fontSize: '1.5rem', fontWeight: 'bold', textDecoration: 'none' }}>
          🍪 Cookie Shop
        </Link>

        <nav style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
          <Link to="/" style={{ color: 'white' }}>Home</Link>
          <Link to="/products" style={{ color: 'white' }}>Products</Link>
          <Link to="/cart" style={{ color: 'white', position: 'relative' }}>
            Cart
            {itemCount > 0 && (
              <span style={{
                position: 'absolute',
                top: '-8px',
                right: '-8px',
                backgroundColor: '#ff6b6b',
                borderRadius: '50%',
                padding: '2px 6px',
                fontSize: '0.75rem'
              }}>
                {itemCount}
              </span>
            )}
          </Link>

          {isAuthenticated ? (
            <>
              <span style={{ color: 'white' }}>Hello, {user?.firstName}</span>
              {user?.role === 'admin' && (
                <Link to="/admin" style={{ color: 'white' }}>Admin</Link>
              )}
              <button onClick={logout} style={{ color: 'white', cursor: 'pointer' }}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" style={{ color: 'white' }}>Login</Link>
              <Link to="/register" style={{ color: 'white' }}>Register</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}

export default Header
