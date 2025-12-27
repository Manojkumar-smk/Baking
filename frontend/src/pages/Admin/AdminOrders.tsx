import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import adminService from '@/services/adminService'
import { useToast } from '@/contexts/ToastContext'
import type { Order } from '@/types/order.types'
import styles from './AdminOrders.module.css'

interface OrdersResponse {
  orders: Order[]
  total: number
  pages: number
  current_page: number
  per_page: number
  has_next: boolean
  has_prev: boolean
}

const AdminOrders = () => {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [statusFilter, setStatusFilter] = useState('')
  const [paymentFilter, setPaymentFilter] = useState('')
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [showStatusModal, setShowStatusModal] = useState(false)
  const [showTrackingModal, setShowTrackingModal] = useState(false)
  const [newStatus, setNewStatus] = useState('')
  const [trackingNumber, setTrackingNumber] = useState('')
  const [trackingUrl, setTrackingUrl] = useState('')
  const [updating, setUpdating] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    fetchOrders()
  }, [page, statusFilter, paymentFilter])

  const fetchOrders = async () => {
    setLoading(true)
    try {
      const response: OrdersResponse = await adminService.getOrders({
        page,
        per_page: 20,
        status: statusFilter || undefined,
        payment_status: paymentFilter || undefined,
      })
      setOrders(response.orders)
      setTotalPages(response.pages)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load orders'
      showToast(message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateStatus = async () => {
    if (!selectedOrder || !newStatus) return
    setUpdating(true)
    try {
      await adminService.updateOrderStatus(selectedOrder.id, newStatus)
      showToast('Order status updated', 'success')
      setShowStatusModal(false)
      setSelectedOrder(null)
      setNewStatus('')
      await fetchOrders()
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update status'
      showToast(message, 'error')
    } finally {
      setUpdating(false)
    }
  }

  const handleUpdateTracking = async () => {
    if (!selectedOrder || !trackingNumber) return
    setUpdating(true)
    try {
      await adminService.updateOrderTracking(
        selectedOrder.id,
        trackingNumber,
        trackingUrl || undefined
      )
      showToast('Tracking information updated', 'success')
      setShowTrackingModal(false)
      setSelectedOrder(null)
      setTrackingNumber('')
      setTrackingUrl('')
      await fetchOrders()
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update tracking'
      showToast(message, 'error')
    } finally {
      setUpdating(false)
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
        <h1>Order Management</h1>
        <button onClick={fetchOrders} className={styles.refreshBtn}>
          Refresh
        </button>
      </div>

      <div className={styles.filters}>
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value)
            setPage(1)
          }}
          className={styles.select}
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="shipped">Shipped</option>
          <option value="delivered">Delivered</option>
          <option value="cancelled">Cancelled</option>
        </select>

        <select
          value={paymentFilter}
          onChange={(e) => {
            setPaymentFilter(e.target.value)
            setPage(1)
          }}
          className={styles.select}
        >
          <option value="">All Payments</option>
          <option value="pending">Pending</option>
          <option value="paid">Paid</option>
          <option value="failed">Failed</option>
          <option value="refunded">Refunded</option>
        </select>
      </div>

      {orders.length === 0 ? (
        <div className={styles.empty}>
          <h2>No Orders Found</h2>
          <p>No orders match the selected filters.</p>
        </div>
      ) : (
        <>
          <div className={styles.tableContainer}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Order #</th>
                  <th>Customer</th>
                  <th>Date</th>
                  <th>Total</th>
                  <th>Status</th>
                  <th>Payment</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id}>
                    <td>
                      <Link to={`/orders/${order.id}`} className={styles.orderLink}>
                        {order.order_number}
                      </Link>
                    </td>
                    <td>
                      <div className={styles.customerInfo}>
                        <div className={styles.customerName}>
                          {order.customer_first_name} {order.customer_last_name}
                        </div>
                        <div className={styles.customerEmail}>{order.customer_email}</div>
                      </div>
                    </td>
                    <td>
                      {new Date(order.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      })}
                    </td>
                    <td className={styles.total}>${order.total_amount.toFixed(2)}</td>
                    <td>
                      <span className={`${styles.badge} ${getStatusBadgeClass(order.status)}`}>
                        {order.status.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <span className={`${styles.badge} ${styles[order.payment_status]}`}>
                        {order.payment_status.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <div className={styles.actions}>
                        <button
                          onClick={() => {
                            setSelectedOrder(order)
                            setNewStatus(order.status)
                            setShowStatusModal(true)
                          }}
                          className={styles.actionBtn}
                        >
                          Status
                        </button>
                        <button
                          onClick={() => {
                            setSelectedOrder(order)
                            setTrackingNumber(order.tracking_number || '')
                            setTrackingUrl(order.tracking_url || '')
                            setShowTrackingModal(true)
                          }}
                          className={styles.actionBtn}
                        >
                          Tracking
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
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

      {/* Status Update Modal */}
      {showStatusModal && selectedOrder && (
        <div className={styles.modal} onClick={() => setShowStatusModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h3>Update Order Status</h3>
            <p className={styles.orderNumber}>Order #{selectedOrder.order_number}</p>
            <select
              value={newStatus}
              onChange={(e) => setNewStatus(e.target.value)}
              className={styles.modalSelect}
            >
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
              <option value="shipped">Shipped</option>
              <option value="delivered">Delivered</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <div className={styles.modalActions}>
              <button
                onClick={() => setShowStatusModal(false)}
                className={styles.cancelBtn}
                disabled={updating}
              >
                Cancel
              </button>
              <button
                onClick={handleUpdateStatus}
                className={styles.saveBtn}
                disabled={updating || newStatus === selectedOrder.status}
              >
                {updating ? 'Updating...' : 'Update'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tracking Update Modal */}
      {showTrackingModal && selectedOrder && (
        <div className={styles.modal} onClick={() => setShowTrackingModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h3>Update Tracking Information</h3>
            <p className={styles.orderNumber}>Order #{selectedOrder.order_number}</p>
            <div className={styles.formGroup}>
              <label>Tracking Number *</label>
              <input
                type="text"
                value={trackingNumber}
                onChange={(e) => setTrackingNumber(e.target.value)}
                className={styles.input}
                placeholder="Enter tracking number"
              />
            </div>
            <div className={styles.formGroup}>
              <label>Tracking URL (Optional)</label>
              <input
                type="url"
                value={trackingUrl}
                onChange={(e) => setTrackingUrl(e.target.value)}
                className={styles.input}
                placeholder="https://..."
              />
            </div>
            <div className={styles.modalActions}>
              <button
                onClick={() => setShowTrackingModal(false)}
                className={styles.cancelBtn}
                disabled={updating}
              >
                Cancel
              </button>
              <button
                onClick={handleUpdateTracking}
                className={styles.saveBtn}
                disabled={updating || !trackingNumber.trim()}
              >
                {updating ? 'Updating...' : 'Update'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminOrders
