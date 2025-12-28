from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Tuple, Dict, Any
from app.database.db import db
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.utils.validators import is_valid_quantity


class CartService:
    """Cart management service"""

    @staticmethod
    def get_or_create_cart(user_id: str = None, session_id: str = None) -> Cart:
        """
        Get existing cart or create a new one

        Args:
            user_id: User ID (for authenticated users)
            session_id: Session ID (for guest users)

        Returns:
            Cart object
        """
        # Try to find existing cart
        if user_id:
            cart = Cart.query.filter_by(user_id=user_id).first()
        elif session_id:
            cart = Cart.query.filter_by(session_id=session_id).first()
        else:
            raise ValueError('Either user_id or session_id is required')

        # Create new cart if not found
        if not cart:
            cart = Cart(user_id=user_id, session_id=session_id)
            db.session.add(cart)
            db.session.commit()

        return cart

    @staticmethod
    def get_cart(user_id: str = None, session_id: str = None) -> Optional[Cart]:
        """
        Get cart for user or session

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            Cart object or None
        """
        if user_id:
            return Cart.query.filter_by(user_id=user_id).first()
        elif session_id:
            return Cart.query.filter_by(session_id=session_id).first()
        return None

    @staticmethod
    def add_to_cart(
        product_id: str,
        quantity: int,
        user_id: str = None,
        session_id: str = None
    ) -> Tuple[Optional[Cart], Optional[Dict[str, Any]]]:
        """
        Add item to cart

        Args:
            product_id: Product ID
            quantity: Quantity to add
            user_id: User ID (optional)
            session_id: Session ID (optional)

        Returns:
            Tuple of (cart, error_dict)
        """
        # Validate quantity
        if not is_valid_quantity(quantity):
            return None, {'error': 'Invalid quantity'}

        # Get product
        product = Product.query.get(product_id)
        if not product:
            return None, {'error': 'Product not found'}

        # Check if product is active and in stock
        if not product.is_active:
            return None, {'error': 'Product is not available'}

        if not product.in_stock or product.stock_quantity < quantity:
            return None, {'error': 'Insufficient stock'}

        try:
            # Get or create cart
            cart = CartService.get_or_create_cart(user_id, session_id)

            # Check if item already exists in cart
            cart_item = CartItem.query.filter_by(
                cart_id=cart.id,
                product_id=product_id
            ).first()

            if cart_item:
                # Update quantity
                new_quantity = cart_item.quantity + quantity

                # Check stock availability for new quantity
                if product.stock_quantity < new_quantity:
                    return None, {'error': f'Only {product.stock_quantity} items available'}

                cart_item.quantity = new_quantity
            else:
                # Create new cart item
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=product.price
                )
                db.session.add(cart_item)

            cart.updated_at = datetime.utcnow()
            db.session.commit()

            return cart, None

        except Exception as e:
            db.session.rollback()
            return None, {'error': f'Failed to add to cart: {str(e)}'}

    @staticmethod
    def update_cart_item(
        cart_item_id: str,
        quantity: int
    ) -> Tuple[Optional[CartItem], Optional[Dict[str, Any]]]:
        """
        Update cart item quantity

        Args:
            cart_item_id: Cart item ID
            quantity: New quantity

        Returns:
            Tuple of (cart_item, error_dict)
        """
        cart_item = CartItem.query.get(cart_item_id)

        if not cart_item:
            return None, {'error': 'Cart item not found'}

        # Validate quantity
        if quantity <= 0:
            return None, {'error': 'Quantity must be greater than 0'}

        if not is_valid_quantity(quantity):
            return None, {'error': 'Invalid quantity'}

        # Check stock availability
        product = cart_item.product
        if product.stock_quantity < quantity:
            return None, {'error': f'Only {product.stock_quantity} items available'}

        try:
            cart_item.quantity = quantity
            cart_item.cart.updated_at = datetime.utcnow()
            db.session.commit()

            return cart_item, None

        except Exception as e:
            db.session.rollback()
            return None, {'error': f'Failed to update cart item: {str(e)}'}

    @staticmethod
    def remove_from_cart(cart_item_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Remove item from cart

        Args:
            cart_item_id: Cart item ID

        Returns:
            Tuple of (success, error_dict)
        """
        cart_item = CartItem.query.get(cart_item_id)

        if not cart_item:
            return False, {'error': 'Cart item not found'}

        try:
            cart = cart_item.cart
            db.session.delete(cart_item)
            cart.updated_at = datetime.utcnow()
            db.session.commit()

            return True, None

        except Exception as e:
            db.session.rollback()
            return False, {'error': f'Failed to remove from cart: {str(e)}'}

    @staticmethod
    def clear_cart(cart_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Clear all items from cart

        Args:
            cart_id: Cart ID

        Returns:
            Tuple of (success, error_dict)
        """
        cart = Cart.query.get(cart_id)

        if not cart:
            return False, {'error': 'Cart not found'}

        try:
            # Delete all cart items
            CartItem.query.filter_by(cart_id=cart_id).delete()
            cart.updated_at = datetime.utcnow()
            db.session.commit()

            return True, None

        except Exception as e:
            db.session.rollback()
            return False, {'error': f'Failed to clear cart: {str(e)}'}

    @staticmethod
    def get_cart_total(cart: Cart) -> Dict[str, float]:
        """
        Calculate cart totals

        Args:
            cart: Cart object

        Returns:
            Dictionary with subtotal, tax, shipping, total
        """
        subtotal = sum((item.total_price for item in cart.items), Decimal('0'))

        # Calculate tax (example: 10%)
        tax_rate = Decimal('0.10')
        tax = subtotal * tax_rate

        # Calculate shipping (example: free shipping over $50, else $5)
        shipping = Decimal('0') if subtotal >= Decimal('50') else Decimal('5')

        total = subtotal + tax + shipping

        return {
            'subtotal': float(round(subtotal, 2)),
            'tax': float(round(tax, 2)),
            'shipping': float(round(shipping, 2)),
            'total': float(round(total, 2))
        }

    @staticmethod
    def validate_cart_items(cart: Cart) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate all cart items (stock availability, active products)

        Args:
            cart: Cart object

        Returns:
            Tuple of (is_valid, error_dict)
        """
        errors = []

        for item in cart.items:
            product = item.product

            # Check if product is active
            if not product.is_active:
                errors.append(f'{product.name} is no longer available')

            # Check stock availability
            if not product.in_stock:
                errors.append(f'{product.name} is out of stock')
            elif product.stock_quantity < item.quantity:
                errors.append(
                    f'Only {product.stock_quantity} of {product.name} available '
                    f'(you have {item.quantity} in cart)'
                )

        if errors:
            return False, {'errors': errors}

        return True, None

    @staticmethod
    def merge_carts(user_id: str, session_id: str) -> Tuple[Optional[Cart], Optional[Dict[str, Any]]]:
        """
        Merge guest cart with user cart (called when user logs in)

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            Tuple of (merged_cart, error_dict)
        """
        try:
            # Get both carts
            user_cart = Cart.query.filter_by(user_id=user_id).first()
            session_cart = Cart.query.filter_by(session_id=session_id).first()

            # If no session cart, return user cart or create new one
            if not session_cart:
                return CartService.get_or_create_cart(user_id=user_id), None

            # If no user cart, convert session cart to user cart
            if not user_cart:
                session_cart.user_id = user_id
                session_cart.session_id = None
                db.session.commit()
                return session_cart, None

            # Merge session cart items into user cart
            for session_item in session_cart.items:
                # Check if item already exists in user cart
                user_item = CartItem.query.filter_by(
                    cart_id=user_cart.id,
                    product_id=session_item.product_id
                ).first()

                if user_item:
                    # Increase quantity
                    user_item.quantity += session_item.quantity
                else:
                    # Move item to user cart
                    session_item.cart_id = user_cart.id

            # Delete session cart
            db.session.delete(session_cart)
            user_cart.updated_at = datetime.utcnow()
            db.session.commit()

            return user_cart, None

        except Exception as e:
            db.session.rollback()
            return None, {'error': f'Failed to merge carts: {str(e)}'}

    @staticmethod
    def cleanup_expired_carts():
        """
        Delete carts that haven't been updated in 30 days
        This should be run as a scheduled task
        """
        try:
            expiry_date = datetime.utcnow() - timedelta(days=30)
            expired_carts = Cart.query.filter(Cart.updated_at < expiry_date).all()

            for cart in expired_carts:
                db.session.delete(cart)

            db.session.commit()

            return len(expired_carts)

        except Exception as e:
            db.session.rollback()
            raise e
