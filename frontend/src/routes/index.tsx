import { Routes as RouterRoutes, Route } from 'react-router-dom'
import Layout from '@components/common/Layout/Layout'

// Placeholder component - will be replaced with actual pages
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
        <Route index element={<PlaceholderPage title="Home" />} />
        <Route path="products" element={<PlaceholderPage title="Products" />} />
        <Route path="cart" element={<PlaceholderPage title="Cart" />} />
        <Route path="checkout" element={<PlaceholderPage title="Checkout" />} />
        <Route path="login" element={<PlaceholderPage title="Login" />} />
        <Route path="register" element={<PlaceholderPage title="Register" />} />
        <Route path="*" element={<PlaceholderPage title="404 - Page Not Found" />} />
      </Route>
    </RouterRoutes>
  )
}

export default Routes
