import { Routes as RouterRoutes, Route } from 'react-router-dom'
import Layout from '@/components/common/Layout/Layout'

// Pages
import HomePage from '@/pages/Home/HomePage'
import ProductsPage from '@/pages/Products/ProductsPage'
import ProductDetailsPage from '@/pages/Products/ProductDetailsPage'
import CartPage from '@/pages/Cart/CartPage'
import AdminProducts from '@/pages/Admin/AdminProducts'

// Placeholder component for pages not yet implemented
const PlaceholderPage = ({ title }: { title: string }) => (
  <div style={{ padding: '2rem', textAlign: 'center' }}>
    <h1>{title}</h1>
    <p>This page is under construction.</p>
  </div>
)

function Routes() {
  return (
    <RouterRoutes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="products" element={<ProductsPage />} />
        <Route path="products/:productId" element={<ProductDetailsPage />} />
        <Route path="cart" element={<CartPage />} />
        <Route path="checkout" element={<PlaceholderPage title="Checkout" />} />
        <Route path="login" element={<PlaceholderPage title="Login" />} />
        <Route path="register" element={<PlaceholderPage title="Register" />} />
        <Route path="profile" element={<PlaceholderPage title="Profile" />} />

        {/* Admin Routes */}
        <Route path="admin/products" element={<AdminProducts />} />
        <Route path="admin/dashboard" element={<PlaceholderPage title="Admin Dashboard" />} />
        <Route path="admin/orders" element={<PlaceholderPage title="Admin Orders" />} />

        {/* 404 */}
        <Route path="*" element={<PlaceholderPage title="404 - Page Not Found" />} />
      </Route>
    </RouterRoutes>
  )
}

export default Routes
