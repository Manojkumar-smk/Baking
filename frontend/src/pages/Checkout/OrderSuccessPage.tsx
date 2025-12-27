import { useEffect, useState } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import orderService from '@/services/orderService'
import type { Order } from '@/types/order.types'
import styles from './OrderSuccessPage.module.css'

const OrderSuccessPage = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const orderId = searchParams.get('order')

  useEffect(() => {
    if (!orderId) {
      navigate('/products')
      return
    }

    const fetchOrder = async () => {
      try {
        const orderData = await orderService.getOrder(orderId)
        setOrder(orderData)
      } catch (err) {
        setError('Failed to load order details')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchOrder()
  }, [orderId, navigate])

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading order details...</p>
        </div>
      </div>
    )
  }

  if (error || !order) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>Order Not Found</h2>
          <p>{error || 'Unable to retrieve order information'}</p>
          <Link to="/products" className={styles.button}>
            Continue Shopping
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.success}>
        <div className={styles.iconWrapper}>
          <svg
            className={styles.checkIcon}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>

        <h1>Order Confirmed!</h1>
        <p className={styles.subtitle}>
          Thank you for your order. We've sent a confirmation email to{' '}
          <strong>{order.customer_email}</strong>
        </p>

        <div className={styles.orderInfo}>
          <div className={styles.infoRow}>
            <span className={styles.label}>Order Number:</span>
            <span className={styles.value}>{order.order_number}</span>
          </div>
          <div className={styles.infoRow}>
            <span className={styles.label}>Order Date:</span>
            <span className={styles.value}>
              {new Date(order.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </span>
          </div>
          <div className={styles.infoRow}>
            <span className={styles.label}>Total Amount:</span>
            <span className={styles.valueHighlight}>${order.total_amount.toFixed(2)}</span>
          </div>
          <div className={styles.infoRow}>
            <span className={styles.label}>Payment Status:</span>
            <span className={`${styles.badge} ${styles[order.payment_status]}`}>
              {order.payment_status.toUpperCase()}
            </span>
          </div>
        </div>

        <div className={styles.divider}></div>

        <div className={styles.shippingInfo}>
          <h3>Shipping Address</h3>
          <div className={styles.address}>
            <p>{order.shipping_address.full_name}</p>
            <p>{order.shipping_address.street_address}</p>
            <p>
              {order.shipping_address.city}, {order.shipping_address.state}{' '}
              {order.shipping_address.postal_code}
            </p>
            <p>{order.shipping_address.country}</p>
            {order.shipping_address.phone && <p>Phone: {order.shipping_address.phone}</p>}
          </div>
        </div>

        {order.items && order.items.length > 0 && (
          <>
            <div className={styles.divider}></div>
            <div className={styles.items}>
              <h3>Order Items</h3>
              {order.items.map((item) => (
                <div key={item.id} className={styles.item}>
                  <div className={styles.itemImage}>
                    {item.product_image_url ? (
                      <img src={item.product_image_url} alt={item.product_name} />
                    ) : (
                      <div className={styles.noImage}>No Image</div>
                    )}
                  </div>
                  <div className={styles.itemDetails}>
                    <div className={styles.itemName}>{item.product_name}</div>
                    <div className={styles.itemMeta}>
                      Qty: {item.quantity} × ${item.unit_price.toFixed(2)}
                    </div>
                  </div>
                  <div className={styles.itemTotal}>${item.total_price.toFixed(2)}</div>
                </div>
              ))}
            </div>
          </>
        )}

        <div className={styles.actions}>
          <Link to="/products" className={styles.primaryButton}>
            Continue Shopping
          </Link>
          <Link to={`/orders/${order.id}`} className={styles.secondaryButton}>
            View Order Details
          </Link>
        </div>

        <div className={styles.helpText}>
          <p>
            Need help? Contact us at{' '}
            <a href="mailto:support@cookieshop.com">support@cookieshop.com</a>
          </p>
        </div>
      </div>
    </div>
  )
}

export default OrderSuccessPage
