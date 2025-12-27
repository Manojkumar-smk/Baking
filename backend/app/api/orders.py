"""
Order API endpoints
"""
from flask import Blueprint, request, jsonify, current_app, g
from app.services.order_service import OrderService
from app.utils.decorators import token_required, optional_token

orders_bp = Blueprint('orders', __name__, url_prefix='/api/v1/orders')


def get_session_id():
    """Get session ID from headers"""
    return request.headers.get('X-Session-ID')


@orders_bp.route('', methods=['POST'])
@optional_token
def create_order():
    """
    Create order from cart

    Request body:
        {
            "shipping_address": {
                "full_name": "John Doe",
                "street_address": "123 Main St",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "US",
                "phone": "555-1234"
            },
            "billing_address": {...},  // Optional, uses shipping if not provided
            "customer_info": {  // Required for guest checkout
                "email": "customer@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "555-1234"
            },
            "customer_notes": "Please ring doorbell"  // Optional
        }

    Returns:
        {
            "order": {...},
            "order_id": "order-uuid",
            "order_number": "ORD-20240101-ABC123"
        }
    """
    try:
        data = request.get_json()

        # Get user_id if authenticated, otherwise session_id
        user_id = g.get('current_user', {}).get('id') if hasattr(g, 'current_user') else None
        session_id = get_session_id()

        shipping_address = data.get('shipping_address')
        if not shipping_address:
            return jsonify({'error': 'shipping_address is required'}), 400

        # Validate required shipping address fields
        required_fields = ['full_name', 'street_address', 'city', 'state', 'postal_code', 'country']
        missing_fields = [f for f in required_fields if f not in shipping_address]
        if missing_fields:
            return jsonify({'error': f'Missing shipping address fields: {", ".join(missing_fields)}'}), 400

        billing_address = data.get('billing_address')
        customer_info = data.get('customer_info')
        customer_notes = data.get('customer_notes')

        order = OrderService.create_order_from_cart(
            user_id=user_id,
            session_id=session_id,
            shipping_address=shipping_address,
            billing_address=billing_address,
            customer_info=customer_info,
            customer_notes=customer_notes
        )

        return jsonify({
            'order': order.to_dict(include_items=True),
            'order_id': order.id,
            'order_number': order.order_number
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Error creating order: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@orders_bp.route('', methods=['GET'])
@token_required
def get_user_orders():
    """
    Get authenticated user's orders

    Query params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10)
        - status: Filter by status (optional)

    Returns:
        {
            "orders": [...],
            "total": 50,
            "page": 1,
            "per_page": 10,
            "pages": 5,
            "has_next": true,
            "has_prev": false
        }
    """
    try:
        user_id = g.current_user.id

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')

        result = OrderService.get_user_orders(
            user_id=user_id,
            page=page,
            per_page=per_page,
            status=status
        )

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f'Error fetching user orders: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@orders_bp.route('/<order_id>', methods=['GET'])
@token_required
def get_order(order_id):
    """
    Get single order details

    Returns:
        {
            "id": "order-uuid",
            "order_number": "ORD-20240101-ABC123",
            ...
        }
    """
    try:
        user_id = g.current_user.id

        order = OrderService.get_order(order_id, user_id)

        if not order:
            return jsonify({'error': 'Order not found'}), 404

        return jsonify(order.to_dict(include_items=True)), 200

    except Exception as e:
        current_app.logger.error(f'Error fetching order: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@orders_bp.route('/number/<order_number>', methods=['GET'])
@optional_token
def get_order_by_number(order_number):
    """
    Get order by order number

    Allows both authenticated and guest users to view their order
    """
    try:
        user_id = g.get('current_user', {}).get('id') if hasattr(g, 'current_user') else None

        order = OrderService.get_order_by_number(order_number, user_id)

        if not order:
            return jsonify({'error': 'Order not found'}), 404

        return jsonify(order.to_dict(include_items=True)), 200

    except Exception as e:
        current_app.logger.error(f'Error fetching order: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@orders_bp.route('/<order_id>/cancel', methods=['PUT'])
@token_required
def cancel_order(order_id):
    """
    Cancel an order

    Request body:
        {
            "reason": "Changed my mind"  // Optional
        }

    Returns:
        {
            "order": {...}
        }
    """
    try:
        user_id = g.current_user.id

        # Verify order ownership
        order = OrderService.get_order(order_id, user_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        data = request.get_json() or {}
        reason = data.get('reason')

        order = OrderService.cancel_order(order_id, reason)

        return jsonify({'order': order.to_dict(include_items=True)}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Error cancelling order: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500
