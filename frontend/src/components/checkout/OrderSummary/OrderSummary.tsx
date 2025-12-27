import { CartItem, CartTotals } from '@/types/cart.types'
import styles from './OrderSummary.module.css'

interface OrderSummaryProps {
  items: CartItem[]
  totals: CartTotals
}

const OrderSummary = ({ items, totals }: OrderSummaryProps) => {
  return (
    <div className={styles.summary}>
      <h2 className={styles.title}>Order Summary</h2>

      <div className={styles.items}>
        {items.map((item) => (
          <div key={item.id} className={styles.item}>
            <div className={styles.itemImage}>
              {item.product.image_url ? (
                <img src={item.product.image_url} alt={item.product.name} />
              ) : (
                <div className={styles.noImage}>No Image</div>
              )}
            </div>
            <div className={styles.itemDetails}>
              <div className={styles.itemName}>{item.product.name}</div>
              <div className={styles.itemQuantity}>Qty: {item.quantity}</div>
              <div className={styles.itemPrice}>
                ${item.unit_price.toFixed(2)} each
              </div>
            </div>
            <div className={styles.itemTotal}>
              ${item.total_price.toFixed(2)}
            </div>
          </div>
        ))}
      </div>

      <div className={styles.divider}></div>

      <div className={styles.totals}>
        <div className={styles.totalRow}>
          <span>Subtotal:</span>
          <span>${totals.subtotal.toFixed(2)}</span>
        </div>
        <div className={styles.totalRow}>
          <span>Tax (10%):</span>
          <span>${totals.tax.toFixed(2)}</span>
        </div>
        <div className={styles.totalRow}>
          <span>Shipping:</span>
          <span>
            {totals.shipping === 0 ? (
              <span className={styles.freeShipping}>FREE</span>
            ) : (
              `$${totals.shipping.toFixed(2)}`
            )}
          </span>
        </div>

        {totals.subtotal < 50 && totals.subtotal > 0 && (
          <div className={styles.shippingNote}>
            Add ${(50 - totals.subtotal).toFixed(2)} more for free shipping!
          </div>
        )}

        <div className={styles.divider}></div>

        <div className={styles.totalRow + ' ' + styles.grandTotal}>
          <span>Total:</span>
          <span>${totals.total.toFixed(2)}</span>
        </div>
      </div>

      <div className={styles.secureCheckout}>
        <svg
          className={styles.shieldIcon}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
          />
        </svg>
        Secure Checkout
      </div>
    </div>
  )
}

export default OrderSummary
