from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from sqlalchemy import func, and_, or_
from app.database.db import db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment


class AdminService:
    """Admin service for dashboard statistics and management"""

    @staticmethod
    def get_dashboard_stats() -> Dict[str, Any]:
        """
        Get dashboard statistics

        Returns:
            Dictionary with various statistics
        """
        # Get date ranges
        today = datetime.utcnow().date()
        thirty_days_ago = today - timedelta(days=30)
        seven_days_ago = today - timedelta(days=7)

        # Total revenue
        total_revenue = db.session.query(func.sum(Order.total)).filter(
            Order.payment_status == 'paid'
        ).scalar() or 0

        # Revenue this month
        month_revenue = db.session.query(func.sum(Order.total)).filter(
            and_(
                Order.payment_status == 'paid',
                Order.created_at >= thirty_days_ago
            )
        ).scalar() or 0

        # Total orders
        total_orders = Order.query.count()

        # Orders today
        orders_today = Order.query.filter(
            func.date(Order.created_at) == today
        ).count()

        # Pending orders
        pending_orders = Order.query.filter(
            Order.status.in_(['pending', 'processing'])
        ).count()

        # Total products
        total_products = Product.query.filter(Product.is_active == True).count()

        # Low stock products
        low_stock_count = Product.query.filter(
            and_(
                Product.stock_quantity > 0,
                Product.is_active == True
            )
        ).all()
        low_stock_count = len([p for p in low_stock_count if p.is_low_stock])

        # Out of stock products
        out_of_stock = Product.query.filter(
            and_(
                Product.stock_quantity == 0,
                Product.is_active == True
            )
        ).count()

        # Total customers
        total_customers = User.query.filter(User.role == 'customer').count()

        # New customers this week
        new_customers = User.query.filter(
            and_(
                User.role == 'customer',
                User.created_at >= seven_days_ago
            )
        ).count()

        # Recent orders (last 10)
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()

        # Top selling products (last 30 days)
        top_products = db.session.query(
            OrderItem.product_id,
            Product.name,
            func.sum(OrderItem.quantity).label('total_sold')
        ).join(
            Order, OrderItem.order_id == Order.id
        ).join(
            Product, OrderItem.product_id == Product.id
        ).filter(
            and_(
                Order.created_at >= thirty_days_ago,
                Order.payment_status == 'paid'
            )
        ).group_by(
            OrderItem.product_id, Product.name
        ).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(5).all()

        # Sales chart data (last 7 days)
        sales_chart = []
        for i in range(7):
            date = today - timedelta(days=i)
            daily_sales = db.session.query(func.sum(Order.total)).filter(
                and_(
                    func.date(Order.created_at) == date,
                    Order.payment_status == 'paid'
                )
            ).scalar() or 0

            sales_chart.append({
                'date': date.isoformat(),
                'sales': float(daily_sales)
            })

        sales_chart.reverse()  # Show oldest to newest

        return {
            'revenue': {
                'total': float(total_revenue),
                'this_month': float(month_revenue)
            },
            'orders': {
                'total': total_orders,
                'today': orders_today,
                'pending': pending_orders
            },
            'products': {
                'total': total_products,
                'low_stock': low_stock_count,
                'out_of_stock': out_of_stock
            },
            'customers': {
                'total': total_customers,
                'new_this_week': new_customers
            },
            'recent_orders': [order.to_dict() for order in recent_orders],
            'top_products': [
                {
                    'product_id': p.product_id,
                    'name': p.name,
                    'total_sold': int(p.total_sold)
                }
                for p in top_products
            ],
            'sales_chart': sales_chart
        }

    @staticmethod
    def get_all_orders(
        page: int = 1,
        per_page: int = 20,
        status: str = None,
        payment_status: str = None,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        Get all orders with filters and pagination

        Args:
            page: Page number
            per_page: Items per page
            status: Filter by order status
            payment_status: Filter by payment status
            start_date: Filter by start date (YYYY-MM-DD)
            end_date: Filter by end date (YYYY-MM-DD)

        Returns:
            Dictionary with orders and pagination info
        """
        query = Order.query

        # Apply filters
        if status:
            query = query.filter(Order.status == status)

        if payment_status:
            query = query.filter(Order.payment_status == payment_status)

        if start_date:
            try:
                start = datetime.fromisoformat(start_date)
                query = query.filter(Order.created_at >= start)
            except ValueError:
                pass

        if end_date:
            try:
                end = datetime.fromisoformat(end_date)
                # Add one day to include the end date
                end = end + timedelta(days=1)
                query = query.filter(Order.created_at < end)
            except ValueError:
                pass

        # Order by created_at descending
        query = query.order_by(Order.created_at.desc())

        # Paginate
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return {
            'orders': [order.to_dict() for order in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }

    @staticmethod
    def update_order_status(
        order_id: str,
        status: str
    ) -> Tuple[Optional[Order], Optional[Dict[str, Any]]]:
        """
        Update order status

        Args:
            order_id: Order ID
            status: New status

        Returns:
            Tuple of (order, error_dict)
        """
        order = Order.query.get(order_id)

        if not order:
            return None, {'error': 'Order not found'}

        # Validate status
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        if status not in valid_statuses:
            return None, {'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}

        try:
            order.status = status

            # Update timestamps based on status
            if status == 'shipped':
                order.shipped_at = datetime.utcnow()
                order.fulfillment_status = 'fulfilled'
            elif status == 'delivered':
                order.delivered_at = datetime.utcnow()
                order.fulfillment_status = 'fulfilled'
            elif status == 'cancelled':
                order.fulfillment_status = 'cancelled'

            order.updated_at = datetime.utcnow()
            db.session.commit()

            return order, None

        except Exception as e:
            db.session.rollback()
            return None, {'error': f'Failed to update order status: {str(e)}'}

    @staticmethod
    def update_tracking_info(
        order_id: str,
        tracking_number: str = None,
        tracking_url: str = None
    ) -> Tuple[Optional[Order], Optional[Dict[str, Any]]]:
        """
        Update order tracking information

        Args:
            order_id: Order ID
            tracking_number: Tracking number
            tracking_url: Tracking URL

        Returns:
            Tuple of (order, error_dict)
        """
        order = Order.query.get(order_id)

        if not order:
            return None, {'error': 'Order not found'}

        try:
            if tracking_number:
                order.tracking_number = tracking_number
            if tracking_url:
                order.tracking_url = tracking_url

            order.updated_at = datetime.utcnow()
            db.session.commit()

            return order, None

        except Exception as e:
            db.session.rollback()
            return None, {'error': f'Failed to update tracking info: {str(e)}'}

    @staticmethod
    def get_all_users(
        page: int = 1,
        per_page: int = 20,
        role: str = None,
        is_active: bool = None
    ) -> Dict[str, Any]:
        """
        Get all users with filters and pagination

        Args:
            page: Page number
            per_page: Items per page
            role: Filter by role
            is_active: Filter by active status

        Returns:
            Dictionary with users and pagination info
        """
        query = User.query

        # Apply filters
        if role:
            query = query.filter(User.role == role)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        # Order by created_at descending
        query = query.order_by(User.created_at.desc())

        # Paginate
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return {
            'users': [user.to_dict() for user in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }

    @staticmethod
    def update_user(
        user_id: str,
        **kwargs
    ) -> Tuple[Optional[User], Optional[Dict[str, Any]]]:
        """
        Update user details

        Args:
            user_id: User ID
            **kwargs: Fields to update (is_active, role)

        Returns:
            Tuple of (user, error_dict)
        """
        user = User.query.get(user_id)

        if not user:
            return None, {'error': 'User not found'}

        try:
            # Update allowed fields
            allowed_fields = ['is_active', 'role']

            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    # Validate role
                    if field == 'role' and value not in ['customer', 'admin']:
                        return None, {'error': 'Invalid role. Must be customer or admin'}

                    setattr(user, field, value)

            user.updated_at = datetime.utcnow()
            db.session.commit()

            return user, None

        except Exception as e:
            db.session.rollback()
            return None, {'error': f'Failed to update user: {str(e)}'}
