import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { loadStripe } from '@stripe/stripe-js'
import { Elements } from '@stripe/react-stripe-js'
import { useCart } from '@/contexts/CartContext'
import { useToast } from '@/contexts/ToastContext'
import orderService from '@/services/orderService'
import paymentService from '@/services/paymentService'
import ShippingForm from '@/components/checkout/ShippingForm/ShippingForm'
import PaymentForm from '@/components/checkout/PaymentForm/PaymentForm'
import OrderSummary from '@/components/checkout/OrderSummary/OrderSummary'
import type { ShippingAddress } from '@/types/order.types'
import styles from './CheckoutPage.module.css'

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '')

type CheckoutStep = 'shipping' | 'payment' | 'processing'

const CheckoutPage = () => {
  const navigate = useNavigate()
  const { items, totals, clearCart } = useCart()
  const { showToast } = useToast()

  const [step, setStep] = useState<CheckoutStep>('shipping')
  const [shippingAddress, setShippingAddress] = useState<ShippingAddress | null>(null)
  const [clientSecret, setClientSecret] = useState<string>('')
  const [orderId, setOrderId] = useState<string>('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Redirect to cart if empty
    if (items.length === 0) {
      navigate('/cart')
      showToast('Your cart is empty', 'error')
    }
  }, [items, navigate, showToast])

  const handleShippingSubmit = async (address: ShippingAddress) => {
    setLoading(true)
    try {
      // Create order
      const { order, order_id } = await orderService.createOrder({
        shipping_address: address,
        billing_address: address,
        customer_info: {
          email: 'guest@example.com', // TODO: Use actual user email when auth is implemented
          first_name: address.full_name.split(' ')[0] || address.full_name,
          last_name: address.full_name.split(' ').slice(1).join(' ') || '',
          phone: address.phone,
        },
      })

      setOrderId(order_id)
      setShippingAddress(address)

      // Create payment intent
      const amountInCents = Math.round(totals.total * 100)
      const { client_secret } = await paymentService.createPaymentIntent({
        order_id: order_id,
        amount: amountInCents,
        metadata: {
          order_number: order.order_number,
        },
      })

      setClientSecret(client_secret)
      setStep('payment')
      showToast('Shipping information saved', 'success')
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to process shipping information'
      showToast(message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handlePaymentSuccess = async (paymentIntentId: string) => {
    setStep('processing')
    try {
      // Confirm payment with backend
      await paymentService.confirmPayment({
        payment_intent_id: paymentIntentId,
      })

      // Clear cart
      await clearCart()

      showToast('Payment successful!', 'success')

      // Navigate to success page
      navigate(`/checkout/success?order=${orderId}`)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to confirm payment'
      showToast(message, 'error')
      setStep('payment')
    }
  }

  const handlePaymentError = (error: string) => {
    showToast(error, 'error')
  }

  const handleBackToShipping = () => {
    setStep('shipping')
  }

  if (items.length === 0) {
    return null
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Checkout</h1>
        <div className={styles.steps}>
          <div className={step === 'shipping' ? styles.stepActive : styles.step}>
            <span className={styles.stepNumber}>1</span>
            <span className={styles.stepLabel}>Shipping</span>
          </div>
          <div className={styles.stepDivider}></div>
          <div className={step === 'payment' || step === 'processing' ? styles.stepActive : styles.step}>
            <span className={styles.stepNumber}>2</span>
            <span className={styles.stepLabel}>Payment</span>
          </div>
        </div>
      </div>

      <div className={styles.content}>
        <div className={styles.main}>
          {step === 'shipping' && (
            <ShippingForm
              initialData={shippingAddress || undefined}
              onSubmit={handleShippingSubmit}
              onBack={() => navigate('/cart')}
            />
          )}

          {step === 'payment' && clientSecret && (
            <Elements
              stripe={stripePromise}
              options={{
                clientSecret,
                appearance: {
                  theme: 'stripe',
                  variables: {
                    colorPrimary: '#8b4513',
                  },
                },
              }}
            >
              <PaymentForm
                amount={Math.round(totals.total * 100)}
                onSuccess={handlePaymentSuccess}
                onError={handlePaymentError}
                onBack={handleBackToShipping}
              />
            </Elements>
          )}

          {step === 'processing' && (
            <div className={styles.processing}>
              <div className={styles.spinner}></div>
              <h2>Processing your order...</h2>
              <p>Please wait while we confirm your payment.</p>
            </div>
          )}

          {loading && (
            <div className={styles.overlay}>
              <div className={styles.spinner}></div>
            </div>
          )}
        </div>

        <aside className={styles.sidebar}>
          <OrderSummary items={items} totals={totals} />
        </aside>
      </div>
    </div>
  )
}

export default CheckoutPage
