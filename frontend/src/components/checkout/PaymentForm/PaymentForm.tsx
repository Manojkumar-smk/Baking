import { useState, FormEvent } from 'react'
import {
  PaymentElement,
  useStripe,
  useElements,
} from '@stripe/react-stripe-js'
import styles from './PaymentForm.module.css'

interface PaymentFormProps {
  onSuccess: (paymentIntentId: string) => void
  onError: (error: string) => void
  onBack?: () => void
  amount: number
}

const PaymentForm = ({ onSuccess, onError, onBack, amount }: PaymentFormProps) => {
  const stripe = useStripe()
  const elements = useElements()
  const [isProcessing, setIsProcessing] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!stripe || !elements) {
      return
    }

    setIsProcessing(true)
    setErrorMessage(null)

    try {
      const { error, paymentIntent } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/checkout/success`,
        },
        redirect: 'if_required',
      })

      if (error) {
        setErrorMessage(error.message || 'An error occurred during payment')
        onError(error.message || 'An error occurred during payment')
      } else if (paymentIntent && paymentIntent.status === 'succeeded') {
        onSuccess(paymentIntent.id)
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Payment processing failed'
      setErrorMessage(message)
      onError(message)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <div className={styles.header}>
        <h2 className={styles.title}>Payment Information</h2>
        <div className={styles.amount}>
          Total: <span className={styles.amountValue}>${(amount / 100).toFixed(2)}</span>
        </div>
      </div>

      <div className={styles.paymentElement}>
        <PaymentElement />
      </div>

      {errorMessage && (
        <div className={styles.errorMessage}>
          {errorMessage}
        </div>
      )}

      <div className={styles.actions}>
        {onBack && (
          <button
            type="button"
            onClick={onBack}
            disabled={isProcessing}
            className={styles.backBtn}
          >
            Back
          </button>
        )}
        <button
          type="submit"
          disabled={!stripe || isProcessing}
          className={styles.submitBtn}
        >
          {isProcessing ? 'Processing...' : 'Pay Now'}
        </button>
      </div>

      <div className={styles.securityNote}>
        <svg
          className={styles.lockIcon}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
          />
        </svg>
        Secure payment powered by Stripe
      </div>
    </form>
  )
}

export default PaymentForm
