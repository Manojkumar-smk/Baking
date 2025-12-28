import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '@contexts/AuthContext'
import { CartProvider } from '@contexts/CartContext'
import { ToastProvider } from '@contexts/ToastContext'
import Routes from '@/routes'
import Chatbot from '@/components/Chatbot/Chatbot'

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <CartProvider>
            <Routes />
            <Chatbot />
          </CartProvider>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  )
}

export default App
