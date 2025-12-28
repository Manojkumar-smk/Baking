import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import orderService from '@/services/orderService'
import type { Order } from '@/types/order.types'
import { useToast } from '@/contexts/ToastContext'
import styles from './OrderDetailsPage.module.css'

const OrderDetailsPage = () => {
  const { orderId } = useParams<{ orderId: string }>()
  const navigate = useNavigate()
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)
  const [cancelling, setCancelling] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    if (!orderId) {
      navigate('/orders')
      return
    }
    fetchOrder()
  }, [orderId])

  const fetchOrder = async () => {
    if (!orderId) return
    setLoading(true)
    try {
      const orderData = await orderService.getOrder(orderId)
      setOrder(orderData)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load order'
      showToast('error', message)
      navigate('/orders')
    } finally {
      setLoading(false)
    }
  }

  const handleCancelOrder = async () => {
    if (!order || !orderId) return
    if (!confirm('Are you sure you want to cancel this order?')) return

    setCancelling(true)
    try {
      await orderService.cancelOrder(orderId, 'Customer requested cancellation')
      showToast('success', 'Order cancelled successfully')
      await fetchOrder()
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to cancel order'
      showToast('error', message)
    } finally {
      setCancelling(false)
    }
  }

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

  if (!order) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>Order Not Found</h2>
          <Link to="/orders" className={styles.backBtn}>
            Back to Orders
          </Link>
        </div>
      </div>
    )
  }

  const canCancelOrder = order.status === 'pending' || order.status === 'processing'

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Link to="/orders" className={styles.backLink}>
          ← Back to Orders
        </Link>
        <h1>Order Details</h1>
      </div>

      <div className={styles.grid}>
        <div className={styles.mainContent}>
          <div className={styles.section}>
            <div className={styles.sectionHeader}>
              <div>
                <h2>Order #{order.order_number}</h2>
                <p className={styles.orderDate}>
                  Placed on {new Date(order.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>
              <div className={styles.statusBadges}>
                <span className={`${styles.badge} ${styles[order.status]}`}>
                  {order.status.toUpperCase()}
                </span>
                <span className={`${styles.badge} ${styles[order.payment_status]}`}>
                  Payment: {order.payment_status.toUpperCase()}
                </span>
              </div>
            </div>
          </div>

          <div className={styles.section}>
            <h3>Order Items</h3>
            <div className={styles.items}>
              {order.items?.map((item) => (
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
                    <div className={styles.itemSku}>SKU: {item.product_sku}</div>
                    <div className={styles.itemPrice}>
                      ${item.unit_price.toFixed(2)} × {item.quantity}
                    </div>
                  </div>
                  <div className={styles.itemTotal}>
                    ${item.total_price.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className={styles.section}>
            <h3>Shipping Address</h3>
            <div className={styles.address}>
              <p className={styles.addressName}>{order.shipping_address.full_name}</p>
              <p>{order.shipping_address.street_address}</p>
              <p>
                {order.shipping_address.city}, {order.shipping_address.state}{' '}
                {order.shipping_address.postal_code}
              </p>
              <p>{order.shipping_address.country}</p>
              {order.shipping_address.phone && (
                <p className={styles.phone}>Phone: {order.shipping_address.phone}</p>
              )}
            </div>
          </div>

          {order.tracking_number && (
            <div className={styles.section}>
              <h3>Tracking Information</h3>
              <div className={styles.tracking}>
                <div className={styles.trackingNumber}>
                  <span className={styles.label}>Tracking Number:</span>
                  <span className={styles.value}>{order.tracking_number}</span>
                </div>
                {order.tracking_url && (
                  <a
                    href={order.tracking_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={styles.trackBtn}
                  >
                    Track Package
                  </a>
                )}
              </div>
            </div>
          )}
        </div>

        <div className={styles.sidebar}>
          <div className={styles.summary}>
            <h3>Order Summary</h3>
            <div className={styles.summaryRow}>
              <span>Subtotal:</span>
              <span>${order.subtotal.toFixed(2)}</span>
            </div>
            <div className={styles.summaryRow}>
              <span>Tax:</span>
              <span>${order.tax_amount.toFixed(2)}</span>
            </div>
            <div className={styles.summaryRow}>
              <span>Shipping:</span>
              <span>
                {order.shipping_amount === 0 ? (
                  <span className={styles.free}>FREE</span>
                ) : (
                  `$${order.shipping_amount.toFixed(2)}`
                )}
              </span>
            </div>
            {order.discount_amount > 0 && (
              <div className={styles.summaryRow}>
                <span>Discount:</span>
                <span className={styles.discount}>
                  -${order.discount_amount.toFixed(2)}
                </span>
              </div>
            )}
            <div className={styles.divider}></div>
            <div className={styles.summaryTotal}>
              <span>Total:</span>
              <span>${order.total_amount.toFixed(2)}</span>
            </div>
          </div>

          {canCancelOrder && (
            <button
              onClick={handleCancelOrder}
              disabled={cancelling}
              className={styles.cancelBtn}
            >
              {cancelling ? 'Cancelling...' : 'Cancel Order'}
            </button>
          )}

          <div className={styles.help}>
            <h4>Need Help?</h4>
            <p>Contact us at</p>
            <a href="mailto:support@cookieshop.com">support@cookieshop.com</a>
          </div>
        </div>
      </div>
    </div>
  )
}

export default OrderDetailsPage
