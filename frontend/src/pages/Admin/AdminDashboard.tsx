import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import adminService from '@/services/adminService'
import { useToast } from '@/contexts/ToastContext'
import styles from './AdminDashboard.module.css'

interface DashboardStats {
  revenue: {
    total: number
    this_month: number
  }
  orders: {
    total: number
    today: number
    pending: number
  }
  products: {
    total: number
    low_stock: number
    out_of_stock: number
  }
  customers: {
    total: number
    new_this_week: number
  }
  recent_orders: any[]
  top_products: Array<{
    product_id: string
    name: string
    total_sold: number
  }>
  sales_chart: Array<{
    date: string
    sales: number
  }>
}

const AdminDashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const { showToast } = useToast()

  useEffect(() => {
    fetchDashboardStats()
  }, [])

  const fetchDashboardStats = async () => {
    setLoading(true)
    try {
      const data = await adminService.getDashboardStats()
      setStats(data)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load dashboard'
      showToast('error', message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>Failed to load dashboard</h2>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Admin Dashboard</h1>
        <button onClick={fetchDashboardStats} className={styles.refreshBtn}>
          Refresh
        </button>
      </div>

      {/* KPI Cards */}
      <div className={styles.kpiGrid}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiIcon} style={{ background: '#28a745' }}>
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className={styles.kpiContent}>
            <div className={styles.kpiLabel}>Total Revenue</div>
            <div className={styles.kpiValue}>${stats.revenue.total.toFixed(2)}</div>
            <div className={styles.kpiSubtext}>
              ${stats.revenue.this_month.toFixed(2)} this month
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiIcon} style={{ background: '#007bff' }}>
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
          </div>
          <div className={styles.kpiContent}>
            <div className={styles.kpiLabel}>Total Orders</div>
            <div className={styles.kpiValue}>{stats.orders.total}</div>
            <div className={styles.kpiSubtext}>
              {stats.orders.today} today • {stats.orders.pending} pending
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiIcon} style={{ background: '#8b4513' }}>
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <div className={styles.kpiContent}>
            <div className={styles.kpiLabel}>Products</div>
            <div className={styles.kpiValue}>{stats.products.total}</div>
            <div className={styles.kpiSubtext}>
              {stats.products.low_stock} low stock • {stats.products.out_of_stock} out
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiIcon} style={{ background: '#6f42c1' }}>
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <div className={styles.kpiContent}>
            <div className={styles.kpiLabel}>Customers</div>
            <div className={styles.kpiValue}>{stats.customers.total}</div>
            <div className={styles.kpiSubtext}>
              +{stats.customers.new_this_week} this week
            </div>
          </div>
        </div>
      </div>

      <div className={styles.grid}>
        {/* Sales Chart */}
        <div className={styles.section}>
          <h2>Sales (Last 7 Days)</h2>
          <div className={styles.chartContainer}>
            <div className={styles.chart}>
              {stats.sales_chart.map((item, index) => {
                const maxSales = Math.max(...stats.sales_chart.map(d => d.sales))
                const height = maxSales > 0 ? (item.sales / maxSales) * 100 : 0
                return (
                  <div key={index} className={styles.chartBar}>
                    <div
                      className={styles.bar}
                      style={{ height: `${height}%` }}
                      title={`$${item.sales.toFixed(2)}`}
                    ></div>
                    <div className={styles.chartLabel}>
                      {new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Top Products */}
        <div className={styles.section}>
          <h2>Top Products (Last 30 Days)</h2>
          {stats.top_products.length > 0 ? (
            <div className={styles.topProducts}>
              {stats.top_products.map((product, index) => (
                <div key={product.product_id} className={styles.topProduct}>
                  <div className={styles.rank}>#{index + 1}</div>
                  <div className={styles.productInfo}>
                    <div className={styles.productName}>{product.name}</div>
                    <div className={styles.productSales}>{product.total_sold} sold</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className={styles.emptyState}>No sales data available</div>
          )}
        </div>
      </div>

      {/* Recent Orders */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2>Recent Orders</h2>
          <Link to="/admin/orders" className={styles.viewAllLink}>
            View All →
          </Link>
        </div>
        {stats.recent_orders.length > 0 ? (
          <div className={styles.ordersTable}>
            <table>
              <thead>
                <tr>
                  <th>Order #</th>
                  <th>Customer</th>
                  <th>Date</th>
                  <th>Total</th>
                  <th>Status</th>
                  <th>Payment</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_orders.slice(0, 10).map((order) => (
                  <tr key={order.id}>
                    <td>
                      <Link to={`/orders/${order.id}`} className={styles.orderLink}>
                        {order.order_number}
                      </Link>
                    </td>
                    <td>{order.customer_email}</td>
                    <td>{new Date(order.created_at).toLocaleDateString()}</td>
                    <td>${order.total_amount.toFixed(2)}</td>
                    <td>
                      <span className={`${styles.badge} ${styles[order.status]}`}>
                        {order.status.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <span className={`${styles.badge} ${styles[order.payment_status]}`}>
                        {order.payment_status.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className={styles.emptyState}>No recent orders</div>
        )}
      </div>

      {/* Quick Actions */}
      <div className={styles.quickActions}>
        <h2>Quick Actions</h2>
        <div className={styles.actionButtons}>
          <Link to="/admin/orders" className={styles.actionBtn}>
            Manage Orders
          </Link>
          <Link to="/admin/products" className={styles.actionBtn}>
            Manage Products
          </Link>
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard
