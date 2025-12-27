from flask import Blueprint, request, jsonify, g
from app.services.cart_service import CartService
from app.utils.decorators import optional_token
import uuid

bp = Blueprint('cart', __name__)


def get_session_id():
    """
    Get or create session ID for guest users
    In production, this would come from the client
    """
    session_id = request.headers.get('X-Session-ID')
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


@bp.route('', methods=['GET'])
@optional_token
def get_cart():
    """
    Get cart contents

    For authenticated users: uses user_id
    For guests: uses session_id from X-Session-ID header
    """
    user_id = g.user_id if hasattr(g, 'user_id') else None
    session_id = None if user_id else get_session_id()

    cart = CartService.get_cart(user_id=user_id, session_id=session_id)

    if not cart:
        # Return empty cart
        return jsonify({
            'cart': None,
            'items': [],
            'totals': {
                'subtotal': 0,
                'tax': 0,
                'shipping': 0,
                'total': 0
            },
            'session_id': session_id
        }), 200

    # Calculate totals
    totals = CartService.get_cart_total(cart)

    return jsonify({
        'cart': cart.to_dict(),
        'items': [item.to_dict() for item in cart.items],
        'totals': totals,
        'session_id': session_id
    }), 200


@bp.route('/items', methods=['POST'])
@optional_token
def add_to_cart():
    """
    Add item to cart

    Body: {
        "product_id": "...",
        "quantity": 1
    }
    """
    data = request.get_json()

    if not data.get('product_id'):
        return jsonify({'error': 'product_id is required'}), 400

    quantity = data.get('quantity', 1)
    user_id = g.user_id if hasattr(g, 'user_id') else None
    session_id = None if user_id else get_session_id()

    # Add to cart
    cart, error = CartService.add_to_cart(
        product_id=data['product_id'],
        quantity=quantity,
        user_id=user_id,
        session_id=session_id
    )

    if error:
        return jsonify(error), 400

    # Calculate totals
    totals = CartService.get_cart_total(cart)

    return jsonify({
        'message': 'Item added to cart',
        'cart': cart.to_dict(),
        'items': [item.to_dict() for item in cart.items],
        'totals': totals,
        'session_id': session_id
    }), 200


@bp.route('/items/<cart_item_id>', methods=['PUT'])
@optional_token
def update_cart_item(cart_item_id):
    """
    Update cart item quantity

    Body: { "quantity": 2 }
    """
    data = request.get_json()

    if 'quantity' not in data:
        return jsonify({'error': 'quantity is required'}), 400

    cart_item, error = CartService.update_cart_item(
        cart_item_id,
        data['quantity']
    )

    if error:
        return jsonify(error), 400

    # Get cart and calculate totals
    cart = cart_item.cart
    totals = CartService.get_cart_total(cart)

    return jsonify({
        'message': 'Cart item updated',
        'cart': cart.to_dict(),
        'items': [item.to_dict() for item in cart.items],
        'totals': totals
    }), 200


@bp.route('/items/<cart_item_id>', methods=['DELETE'])
@optional_token
def remove_from_cart(cart_item_id):
    """
    Remove item from cart
    """
    success, error = CartService.remove_from_cart(cart_item_id)

    if not success:
        return jsonify(error), 400

    return jsonify({
        'message': 'Item removed from cart'
    }), 200


@bp.route('', methods=['DELETE'])
@optional_token
def clear_cart():
    """
    Clear all items from cart
    """
    user_id = g.user_id if hasattr(g, 'user_id') else None
    session_id = None if user_id else get_session_id()

    cart = CartService.get_cart(user_id=user_id, session_id=session_id)

    if not cart:
        return jsonify({'error': 'Cart not found'}), 404

    success, error = CartService.clear_cart(cart.id)

    if not success:
        return jsonify(error), 400

    return jsonify({
        'message': 'Cart cleared'
    }), 200


@bp.route('/validate', methods=['POST'])
@optional_token
def validate_cart():
    """
    Validate cart items (stock availability, active products)
    """
    user_id = g.user_id if hasattr(g, 'user_id') else None
    session_id = None if user_id else get_session_id()

    cart = CartService.get_cart(user_id=user_id, session_id=session_id)

    if not cart:
        return jsonify({'error': 'Cart not found'}), 404

    is_valid, error = CartService.validate_cart_items(cart)

    if not is_valid:
        return jsonify(error), 400

    return jsonify({
        'message': 'Cart is valid',
        'valid': True
    }), 200


@bp.route('/merge', methods=['POST'])
@optional_token
def merge_carts():
    """
    Merge guest cart with user cart (called after login)

    Requires authentication
    Body: { "session_id": "..." }
    """
    if not hasattr(g, 'user_id'):
        return jsonify({'error': 'Authentication required'}), 401

    data = request.get_json()
    session_id = data.get('session_id')

    if not session_id:
        return jsonify({'error': 'session_id is required'}), 400

    cart, error = CartService.merge_carts(g.user_id, session_id)

    if error:
        return jsonify(error), 400

    # Calculate totals
    totals = CartService.get_cart_total(cart)

    return jsonify({
        'message': 'Carts merged successfully',
        'cart': cart.to_dict(),
        'items': [item.to_dict() for item in cart.items],
        'totals': totals
    }), 200
