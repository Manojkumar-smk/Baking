import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import orderService from '@/services/orderService'
import type { Order } from '@/types/order.types'
import { useToast } from '@/contexts/ToastContext'
import styles from './OrderHistoryPage.module.css'

const OrderHistoryPage = () => {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const { showToast } = useToast()

  useEffect(() => {
    fetchOrders()
  }, [page, statusFilter])

  const fetchOrders = async () => {
    setLoading(true)
    try {
      const response = await orderService.getUserOrders(page, 10, statusFilter || undefined)
      setOrders(response.orders)
      setTotalPages(response.pages)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load orders'
      showToast(message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'delivered':
        return styles.statusDelivered
      case 'shipped':
        return styles.statusShipped
      case 'processing':
        return styles.statusProcessing
      case 'cancelled':
        return styles.statusCancelled
      default:
        return styles.statusPending
    }
  }

  if (loading && orders.length === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading orders...</p>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Order History</h1>
        <div className={styles.filters}>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value)
              setPage(1)
            }}
            className={styles.select}
          >
            <option value="">All Orders</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="shipped">Shipped</option>
            <option value="delivered">Delivered</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {orders.length === 0 ? (
        <div className={styles.empty}>
          <h2>No Orders Found</h2>
          <p>You haven't placed any orders yet.</p>
          <Link to="/products" className={styles.shopBtn}>
            Start Shopping
          </Link>
        </div>
      ) : (
        <>
          <div className={styles.orders}>
            {orders.map((order) => (
              <div key={order.id} className={styles.orderCard}>
                <div className={styles.orderHeader}>
                  <div className={styles.orderInfo}>
                    <div className={styles.orderNumber}>
                      Order #{order.order_number}
                    </div>
                    <div className={styles.orderDate}>
                      {new Date(order.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })}
                    </div>
                  </div>
                  <div className={styles.orderStatus}>
                    <span className={`${styles.statusBadge} ${getStatusBadgeClass(order.status)}`}>
                      {order.status.toUpperCase()}
                    </span>
                  </div>
                </div>

                <div className={styles.orderBody}>
                  <div className={styles.orderDetails}>
                    <div className={styles.detailRow}>
                      <span className={styles.detailLabel}>Total:</span>
                      <span className={styles.detailValue}>
                        ${order.total_amount.toFixed(2)}
                      </span>
                    </div>
                    <div className={styles.detailRow}>
                      <span className={styles.detailLabel}>Payment:</span>
                      <span className={`${styles.paymentBadge} ${styles[order.payment_status]}`}>
                        {order.payment_status.toUpperCase()}
                      </span>
                    </div>
                    {order.items && order.items.length > 0 && (
                      <div className={styles.detailRow}>
                        <span className={styles.detailLabel}>Items:</span>
                        <span className={styles.detailValue}>
                          {order.items.length} {order.items.length === 1 ? 'item' : 'items'}
                        </span>
                      </div>
                    )}
                  </div>

                  {order.items && order.items.length > 0 && (
                    <div className={styles.orderItems}>
                      {order.items.slice(0, 3).map((item) => (
                        <div key={item.id} className={styles.itemPreview}>
                          <div className={styles.itemImage}>
                            {item.product_image_url ? (
                              <img src={item.product_image_url} alt={item.product_name} />
                            ) : (
                              <div className={styles.noImage}>No Image</div>
                            )}
                          </div>
                          <div className={styles.itemInfo}>
                            <div className={styles.itemName}>{item.product_name}</div>
                            <div className={styles.itemQty}>Qty: {item.quantity}</div>
                          </div>
                        </div>
                      ))}
                      {order.items.length > 3 && (
                        <div className={styles.moreItems}>
                          +{order.items.length - 3} more items
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className={styles.orderFooter}>
                  <Link to={`/orders/${order.id}`} className={styles.viewBtn}>
                    View Details
                  </Link>
                  {order.status !== 'cancelled' && order.status !== 'delivered' && (
                    <button className={styles.trackBtn}>Track Order</button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className={styles.pagination}>
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1 || loading}
                className={styles.pageBtn}
              >
                Previous
              </button>
              <span className={styles.pageInfo}>
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages || loading}
                className={styles.pageBtn}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default OrderHistoryPage
