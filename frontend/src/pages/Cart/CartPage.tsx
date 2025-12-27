import { Link } from 'react-router-dom'
import { useCart } from '@/contexts/CartContext'
import styles from './CartPage.module.css'

const CartPage = () => {
  const { items, totals, itemCount, loading, updateQuantity, removeItem, clearCart } = useCart()

  const handleQuantityChange = async (itemId: string, newQuantity: number) => {
    if (newQuantity < 1) return
    try {
      await updateQuantity(itemId, newQuantity)
    } catch (error) {
      // Error is handled by CartContext
    }
  }

  const handleRemove = async (itemId: string) => {
    try {
      await removeItem(itemId)
    } catch (error) {
      // Error is handled by CartContext
    }
  }

  const handleClearCart = async () => {
    if (confirm('Are you sure you want to clear your cart?')) {
      try {
        await clearCart()
      } catch (error) {
        // Error is handled by CartContext
      }
    }
  }

  if (loading && items.length === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading cart...</div>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.empty}>
          <h2>Your Cart is Empty</h2>
          <p>Add some delicious cookies to your cart!</p>
          <Link to="/products" className={styles.shopButton}>
            Shop Cookies
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Shopping Cart</h1>
        <div className={styles.headerActions}>
          <span className={styles.itemCount}>
            {itemCount} {itemCount === 1 ? 'item' : 'items'}
          </span>
          <button onClick={handleClearCart} className={styles.clearBtn}>
            Clear Cart
          </button>
        </div>
      </div>

      <div className={styles.content}>
        {/* Cart Items */}
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
                <Link to={`/products/${item.product_id}`} className={styles.itemName}>
                  {item.product.name}
                </Link>
                <div className={styles.itemPrice}>
                  ${item.unit_price.toFixed(2)} each
                </div>
                {item.product.allergens && item.product.allergens.length > 0 && (
                  <div className={styles.allergens}>
                    <span className={styles.allergensLabel}>Allergens:</span>{' '}
                    {item.product.allergens.join(', ')}
                  </div>
                )}
              </div>

              <div className={styles.itemQuantity}>
                <label>Quantity:</label>
                <div className={styles.quantityControl}>
                  <button
                    onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                    disabled={loading}
                    className={styles.quantityBtn}
                  >
                    −
                  </button>
                  <input
                    type="number"
                    value={item.quantity}
                    onChange={(e) => {
                      const val = parseInt(e.target.value) || 1
                      handleQuantityChange(item.id, val)
                    }}
                    disabled={loading}
                    className={styles.quantityInput}
                    min="1"
                    max={item.product.stock_quantity}
                  />
                  <button
                    onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                    disabled={loading}
                    className={styles.quantityBtn}
                  >
                    +
                  </button>
                </div>
              </div>

              <div className={styles.itemTotal}>
                ${item.total_price.toFixed(2)}
              </div>

              <div className={styles.itemActions}>
                <button
                  onClick={() => handleRemove(item.id)}
                  disabled={loading}
                  className={styles.removeBtn}
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Cart Summary */}
        <div className={styles.summary}>
          <h2>Order Summary</h2>

          <div className={styles.summaryRow}>
            <span>Subtotal:</span>
            <span>${totals.subtotal.toFixed(2)}</span>
          </div>

          <div className={styles.summaryRow}>
            <span>Tax (10%):</span>
            <span>${totals.tax.toFixed(2)}</span>
          </div>

          <div className={styles.summaryRow}>
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

          <div className={styles.summaryDivider}></div>

          <div className={styles.summaryTotal}>
            <span>Total:</span>
            <span>${totals.total.toFixed(2)}</span>
          </div>

          <Link to="/checkout" className={styles.checkoutBtn}>
            Proceed to Checkout
          </Link>

          <Link to="/products" className={styles.continueShoppingLink}>
            ← Continue Shopping
          </Link>
        </div>
      </div>
    </div>
  )
}

export default CartPage
