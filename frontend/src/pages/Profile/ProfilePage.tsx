import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import styles from './ProfilePage.module.css'

const ProfilePage = () => {
  const { user, logout } = useAuth()
  const [activeTab, setActiveTab] = useState<'account' | 'orders'>('account')

  if (!user) {
    return null
  }

  const handleLogout = () => {
    logout()
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>My Account</h1>
        <button onClick={handleLogout} className={styles.logoutBtn}>
          Logout
        </button>
      </div>

      <div className={styles.tabs}>
        <button
          className={activeTab === 'account' ? styles.tabActive : styles.tab}
          onClick={() => setActiveTab('account')}
        >
          Account Details
        </button>
        <button
          className={activeTab === 'orders' ? styles.tabActive : styles.tab}
          onClick={() => setActiveTab('orders')}
        >
          Order History
        </button>
      </div>

      {activeTab === 'account' && (
        <div className={styles.content}>
          <div className={styles.section}>
            <h2>Personal Information</h2>
            <div className={styles.infoGrid}>
              <div className={styles.infoItem}>
                <span className={styles.label}>First Name</span>
                <span className={styles.value}>{user.firstName}</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.label}>Last Name</span>
                <span className={styles.value}>{user.lastName}</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.label}>Email</span>
                <span className={styles.value}>{user.email}</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.label}>Account Type</span>
                <span className={styles.badge}>
                  {user.role === 'admin' ? 'Administrator' : 'Customer'}
                </span>
              </div>
            </div>
          </div>

          {user.role === 'admin' && (
            <div className={styles.section}>
              <h2>Admin Access</h2>
              <div className={styles.adminLinks}>
                <Link to="/admin/dashboard" className={styles.adminLink}>
                  <svg
                    className={styles.linkIcon}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                  Admin Dashboard
                </Link>
                <Link to="/admin/products" className={styles.adminLink}>
                  <svg
                    className={styles.linkIcon}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                    />
                  </svg>
                  Manage Products
                </Link>
                <Link to="/admin/orders" className={styles.adminLink}>
                  <svg
                    className={styles.linkIcon}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                    />
                  </svg>
                  Manage Orders
                </Link>
              </div>
            </div>
          )}

          <div className={styles.section}>
            <h2>Quick Actions</h2>
            <div className={styles.actions}>
              <Link to="/orders" className={styles.actionBtn}>
                View All Orders
              </Link>
              <Link to="/products" className={styles.actionBtn}>
                Continue Shopping
              </Link>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'orders' && (
        <div className={styles.content}>
          <div className={styles.section}>
            <h2>Recent Orders</h2>
            <div className={styles.ordersRedirect}>
              <p>View and manage all your orders</p>
              <Link to="/orders" className={styles.viewOrdersBtn}>
                Go to Order History
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProfilePage
