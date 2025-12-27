import { Routes as RouterRoutes, Route } from 'react-router-dom'
import Layout from '@/components/common/Layout/Layout'
import ProtectedRoute from '@/components/common/ProtectedRoute/ProtectedRoute'

// Pages
import HomePage from '@/pages/Home/HomePage'
import ProductsPage from '@/pages/Products/ProductsPage'
import ProductDetailsPage from '@/pages/Products/ProductDetailsPage'
import CartPage from '@/pages/Cart/CartPage'
import CheckoutPage from '@/pages/Checkout/CheckoutPage'
import OrderSuccessPage from '@/pages/Checkout/OrderSuccessPage'
import LoginPage from '@/pages/Auth/LoginPage'
import RegisterPage from '@/pages/Auth/RegisterPage'
import ProfilePage from '@/pages/Profile/ProfilePage'
import OrderHistoryPage from '@/pages/Orders/OrderHistoryPage'
import OrderDetailsPage from '@/pages/Orders/OrderDetailsPage'
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
        <Route path="checkout" element={<CheckoutPage />} />
        <Route path="checkout/success" element={<OrderSuccessPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />

        {/* Protected User Routes */}
        <Route
          path="profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="orders"
          element={
            <ProtectedRoute>
              <OrderHistoryPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="orders/:orderId"
          element={
            <ProtectedRoute>
              <OrderDetailsPage />
            </ProtectedRoute>
          }
        />

        {/* Admin Routes */}
        <Route
          path="admin/products"
          element={
            <ProtectedRoute requireAdmin>
              <AdminProducts />
            </ProtectedRoute>
          }
        />
        <Route
          path="admin/dashboard"
          element={
            <ProtectedRoute requireAdmin>
              <PlaceholderPage title="Admin Dashboard" />
            </ProtectedRoute>
          }
        />
        <Route
          path="admin/orders"
          element={
            <ProtectedRoute requireAdmin>
              <PlaceholderPage title="Admin Orders" />
            </ProtectedRoute>
          }
        />

        {/* 404 */}
        <Route path="*" element={<PlaceholderPage title="404 - Page Not Found" />} />
      </Route>
    </RouterRoutes>
  )
}

export default Routes
