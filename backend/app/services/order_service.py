"""
Order service for order management
"""
from typing import Dict, List, Optional
from datetime import datetime
from flask import current_app
from app.database.db import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.cart import Cart
from app.models.user import User
from app.services.cart_service import CartService


class OrderService:
    """Service for handling order operations"""

    @staticmethod
    def create_order_from_cart(user_id: Optional[str], session_id: Optional[str],
                               shipping_address: Dict, billing_address: Optional[Dict] = None,
                               customer_info: Optional[Dict] = None,
                               customer_notes: Optional[str] = None) -> Order:
        """
        Create order from cart

        Args:
            user_id: User ID (None for guest checkout)
            session_id: Session ID for guest cart
            shipping_address: Shipping address dict
            billing_address: Billing address dict (optional)
            customer_info: Customer info dict with email, first_name, last_name, phone
            customer_notes: Customer notes

        Returns:
            Created order
        """
        # Get cart
        if user_id:
            cart = Cart.query.filter_by(user_id=user_id).first()
        elif session_id:
            cart = Cart.query.filter_by(session_id=session_id).first()
        else:
            raise ValueError('Either user_id or session_id is required')

        if not cart or not cart.items:
            raise ValueError('Cart is empty')

        # Validate stock availability
        for cart_item in cart.items:
            product = cart_item.product
            if not product.is_active:
                raise ValueError(f'Product {product.name} is no longer available')
            if cart_item.quantity > product.stock_quantity:
                raise ValueError(
                    f'Insufficient stock for {product.name}. '
                    f'Available: {product.stock_quantity}, Requested: {cart_item.quantity}'
                )

        # Calculate totals
        totals = CartService.get_cart_total(cart)

        # Get customer information
        if user_id:
            user = User.query.get(user_id)
            customer_email = user.email
            customer_first_name = user.first_name
            customer_last_name = user.last_name
            customer_phone = None
        else:
            # Guest checkout - require customer info
            if not customer_info or 'email' not in customer_info:
                raise ValueError('Customer email is required for guest checkout')
            customer_email = customer_info.get('email')
            customer_first_name = customer_info.get('first_name')
            customer_last_name = customer_info.get('last_name')
            customer_phone = customer_info.get('phone')

        # Create order
        order = Order(
            user_id=user_id,
            customer_email=customer_email,
            customer_first_name=customer_first_name,
            customer_last_name=customer_last_name,
            customer_phone=customer_phone,
            subtotal=totals['subtotal'],
            tax_amount=totals['tax'],
            shipping_amount=totals['shipping'],
            discount_amount=0,
            total_amount=totals['total'],
            shipping_address=shipping_address,
            billing_address=billing_address or shipping_address,
            customer_notes=customer_notes,
            status='pending',
            payment_status='pending',
            fulfillment_status='unfulfilled'
        )

        db.session.add(order)
        db.session.flush()  # Get order ID

        # Create order items and reduce stock
        for cart_item in cart.items:
            product = cart_item.product

            # Create order item (denormalize product data)
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                product_sku=product.sku,
                product_image=product.image_url,
                quantity=cart_item.quantity,
                unit_price=float(product.price),
                total_price=float(product.price) * cart_item.quantity
            )
            db.session.add(order_item)

            # Reduce stock quantity
            product.stock_quantity -= cart_item.quantity
            if product.stock_quantity < 0:
                raise ValueError(f'Insufficient stock for {product.name}')

        # Clear cart
        CartService.clear_cart(cart.id)

        db.session.commit()

        return order

    @staticmethod
    def get_order(order_id: str, user_id: Optional[str] = None) -> Optional[Order]:
        """
        Get order by ID

        Args:
            order_id: Order ID
            user_id: User ID (for authorization check)

        Returns:
            Order or None
        """
        order = Order.query.get(order_id)

        # If user_id provided, verify ownership
        if order and user_id and order.user_id != user_id:
            return None

        return order

    @staticmethod
    def get_order_by_number(order_number: str, user_id: Optional[str] = None) -> Optional[Order]:
        """
        Get order by order number

        Args:
            order_number: Order number
            user_id: User ID (for authorization check)

        Returns:
            Order or None
        """
        order = Order.query.filter_by(order_number=order_number).first()

        # If user_id provided, verify ownership
        if order and user_id and order.user_id != user_id:
            return None

        return order

    @staticmethod
    def get_user_orders(user_id: str, page: int = 1, per_page: int = 10,
                       status: Optional[str] = None) -> Dict:
        """
        Get user's orders with pagination

        Args:
            user_id: User ID
            page: Page number
            per_page: Items per page
            status: Filter by status (optional)

        Returns:
            Dict with orders and pagination info
        """
        query = Order.query.filter_by(user_id=user_id)

        if status:
            query = query.filter_by(status=status)

        query = query.order_by(Order.created_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'orders': [order.to_dict(include_items=True) for order in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }

    @staticmethod
    def get_all_orders(page: int = 1, per_page: int = 20,
                      status: Optional[str] = None,
                      payment_status: Optional[str] = None,
                      search: Optional[str] = None) -> Dict:
        """
        Get all orders (admin) with pagination and filters

        Args:
            page: Page number
            per_page: Items per page
            status: Filter by order status
            payment_status: Filter by payment status
            search: Search by order number or customer email

        Returns:
            Dict with orders and pagination info
        """
        query = Order.query

        if status:
            query = query.filter_by(status=status)

        if payment_status:
            query = query.filter_by(payment_status=payment_status)

        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    Order.order_number.ilike(search_term),
                    Order.customer_email.ilike(search_term)
                )
            )

        query = query.order_by(Order.created_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'orders': [order.to_dict(include_items=True) for order in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }

    @staticmethod
    def update_order_status(order_id: str, status: str, internal_notes: Optional[str] = None) -> Order:
        """
        Update order status

        Args:
            order_id: Order ID
            status: New status
            internal_notes: Internal notes to append

        Returns:
            Updated order
        """
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded']
        if status not in valid_statuses:
            raise ValueError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')

        order = Order.query.get(order_id)
        if not order:
            raise ValueError(f'Order {order_id} not found')

        old_status = order.status
        order.status = status

        # Update timestamps based on status
        if status == 'shipped' and not order.shipped_at:
            order.shipped_at = datetime.utcnow()
        elif status == 'delivered' and not order.delivered_at:
            order.delivered_at = datetime.utcnow()
        elif status == 'cancelled' and not order.cancelled_at:
            order.cancelled_at = datetime.utcnow()

        # Add internal notes
        if internal_notes:
            existing_notes = order.internal_notes or ''
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            new_note = f'[{timestamp}] Status changed from {old_status} to {status}: {internal_notes}'
            order.internal_notes = f'{existing_notes}\n{new_note}'.strip()

        db.session.commit()

        return order

    @staticmethod
    def update_tracking_info(order_id: str, tracking_number: str,
                            tracking_url: Optional[str] = None,
                            shipping_method: Optional[str] = None) -> Order:
        """
        Update order tracking information

        Args:
            order_id: Order ID
            tracking_number: Tracking number
            tracking_url: Tracking URL (optional)
            shipping_method: Shipping method (optional)

        Returns:
            Updated order
        """
        order = Order.query.get(order_id)
        if not order:
            raise ValueError(f'Order {order_id} not found')

        order.tracking_number = tracking_number

        if tracking_url:
            order.tracking_url = tracking_url

        if shipping_method:
            order.shipping_method = shipping_method

        # Auto-update to shipped if not already
        if order.status == 'processing':
            order.status = 'shipped'
            order.shipped_at = datetime.utcnow()

        db.session.commit()

        return order

    @staticmethod
    def cancel_order(order_id: str, reason: Optional[str] = None) -> Order:
        """
        Cancel an order

        Args:
            order_id: Order ID
            reason: Cancellation reason

        Returns:
            Cancelled order
        """
        order = Order.query.get(order_id)
        if not order:
            raise ValueError(f'Order {order_id} not found')

        if order.status in ['delivered', 'cancelled', 'refunded']:
            raise ValueError(f'Cannot cancel order with status: {order.status}')

        # Restore stock for cancelled orders
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock_quantity += item.quantity

        order.status = 'cancelled'
        order.cancelled_at = datetime.utcnow()

        if reason:
            existing_notes = order.internal_notes or ''
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            new_note = f'[{timestamp}] Order cancelled: {reason}'
            order.internal_notes = f'{existing_notes}\n{new_note}'.strip()

        db.session.commit()

        return order

    @staticmethod
    def get_order_statistics() -> Dict:
        """
        Get order statistics for admin dashboard

        Returns:
            Dict with statistics
        """
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        processing_orders = Order.query.filter_by(status='processing').count()
        shipped_orders = Order.query.filter_by(status='shipped').count()

        total_revenue = db.session.query(
            db.func.sum(Order.total_amount)
        ).filter_by(payment_status='paid').scalar() or 0

        # Orders today
        today = datetime.utcnow().date()
        orders_today = Order.query.filter(
            db.func.date(Order.created_at) == today
        ).count()

        return {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'processing_orders': processing_orders,
            'shipped_orders': shipped_orders,
            'total_revenue': float(total_revenue),
            'orders_today': orders_today
        }
