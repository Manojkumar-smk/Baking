from flask import Blueprint, request, jsonify, g
from app.services.product_service import ProductService
from app.services.admin_service import AdminService
from app.utils.decorators import token_required, admin_required

bp = Blueprint('admin', __name__)


# ==================== Dashboard ====================

@bp.route('/dashboard', methods=['GET'])
@token_required
@admin_required
def get_dashboard():
    """Get admin dashboard statistics"""
    stats = AdminService.get_dashboard_stats()
    return jsonify(stats), 200


# ==================== Product Management ====================

@bp.route('/products', methods=['GET'])
@token_required
@admin_required
def get_admin_products():
    """
    Get all products (admin view with filters and pagination)

    Query params:
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
        category_id: Filter by category
        search: Search term
        in_stock_only: true/false
        is_active: true/false
        is_featured: true/false
        sort_by: Field to sort by (default: created_at)
        sort_order: asc/desc (default: desc)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id')
    search = request.args.get('search')
    in_stock_only = request.args.get('in_stock_only', 'false').lower() == 'true'
    is_active = request.args.get('is_active')
    is_featured = request.args.get('is_featured')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    # Convert string booleans to actual booleans
    if is_active is not None:
        is_active = is_active.lower() == 'true'
    if is_featured is not None:
        is_featured = is_featured.lower() == 'true'

    result = ProductService.get_all_products(
        page=page,
        per_page=per_page,
        category_id=category_id,
        search=search,
        in_stock_only=in_stock_only,
        is_active=is_active,
        is_featured=is_featured,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return jsonify(result), 200


@bp.route('/products', methods=['POST'])
@token_required
@admin_required
def create_product():
    """
    Create a new product with image upload

    Content-Type: multipart/form-data

    Form fields:
        name: Product name (required)
        price: Product price (required)
        description: Product description
        category_id: Category ID
        stock_quantity: Initial stock (default: 0)
        low_stock_threshold: Low stock alert threshold (default: 10)
        sku: Stock Keeping Unit
        image: Main product image file
        additional_images[]: Additional image files (multiple)
        ingredients: JSON array of ingredients
        allergens: JSON array of allergens
        is_featured: true/false (default: false)
        is_active: true/false (default: true)
    """
    # Get form data
    name = request.form.get('name')
    price = request.form.get('price', type=float)
    description = request.form.get('description')
    category_id = request.form.get('category_id')
    stock_quantity = request.form.get('stock_quantity', 0, type=int)
    low_stock_threshold = request.form.get('low_stock_threshold', 10, type=int)
    sku = request.form.get('sku')
    is_featured = request.form.get('is_featured', 'false').lower() == 'true'
    is_active = request.form.get('is_active', 'true').lower() == 'true'

    # Validate required fields
    if not name or price is None:
        return jsonify({'error': 'Name and price are required'}), 400

    # Get image files
    image_file = request.files.get('image')
    additional_images = request.files.getlist('additional_images[]')

    # Parse JSON arrays
    import json
    ingredients = None
    allergens = None

    try:
        if request.form.get('ingredients'):
            ingredients = json.loads(request.form.get('ingredients'))
        if request.form.get('allergens'):
            allergens = json.loads(request.form.get('allergens'))
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON format for ingredients or allergens'}), 400

    # Create product
    product, error = ProductService.create_product(
        name=name,
        price=price,
        description=description,
        category_id=category_id,
        stock_quantity=stock_quantity,
        low_stock_threshold=low_stock_threshold,
        sku=sku,
        image_file=image_file,
        additional_images=additional_images if additional_images else None,
        ingredients=ingredients,
        allergens=allergens,
        is_featured=is_featured,
        is_active=is_active
    )

    if error:
        return jsonify(error), 400

    return jsonify({
        'message': 'Product created successfully',
        'product': product.to_dict()
    }), 201


@bp.route('/products/<product_id>', methods=['GET'])
@token_required
@admin_required
def get_product(product_id):
    """Get single product details"""
    product = ProductService.get_product(product_id)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    return jsonify({'product': product.to_dict()}), 200


@bp.route('/products/<product_id>', methods=['PUT'])
@token_required
@admin_required
def update_product(product_id):
    """
    Update product details

    Content-Type: multipart/form-data
    Same fields as create_product
    """
    # Get form data
    data = {}

    if request.form.get('name'):
        data['name'] = request.form.get('name')
    if request.form.get('price'):
        data['price'] = float(request.form.get('price'))
    if request.form.get('description'):
        data['description'] = request.form.get('description')
    if request.form.get('category_id'):
        data['category_id'] = request.form.get('category_id')
    if request.form.get('stock_quantity'):
        data['stock_quantity'] = int(request.form.get('stock_quantity'))
    if request.form.get('low_stock_threshold'):
        data['low_stock_threshold'] = int(request.form.get('low_stock_threshold'))
    if request.form.get('sku'):
        data['sku'] = request.form.get('sku')
    if request.form.get('is_featured'):
        data['is_featured'] = request.form.get('is_featured').lower() == 'true'
    if request.form.get('is_active'):
        data['is_active'] = request.form.get('is_active').lower() == 'true'

    # Get image files
    if 'image' in request.files:
        data['image_file'] = request.files.get('image')

    additional_images = request.files.getlist('additional_images[]')
    if additional_images:
        data['additional_images'] = additional_images

    # Parse JSON arrays
    import json
    try:
        if request.form.get('ingredients'):
            data['ingredients'] = json.loads(request.form.get('ingredients'))
        if request.form.get('allergens'):
            data['allergens'] = json.loads(request.form.get('allergens'))
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON format for ingredients or allergens'}), 400

    # Update product
    product, error = ProductService.update_product(product_id, **data)

    if error:
        return jsonify(error), 400

    return jsonify({
        'message': 'Product updated successfully',
        'product': product.to_dict()
    }), 200


@bp.route('/products/<product_id>/stock', methods=['PUT'])
@token_required
@admin_required
def update_product_stock(product_id):
    """
    Update product stock quantity

    Body: { "stock_quantity": 100 }
    """
    data = request.get_json()

    if 'stock_quantity' not in data:
        return jsonify({'error': 'stock_quantity is required'}), 400

    stock_quantity = data['stock_quantity']

    # Update stock
    product, error = ProductService.update_stock(product_id, stock_quantity)

    if error:
        return jsonify(error), 400

    return jsonify({
        'message': 'Stock updated successfully',
        'product': product.to_dict()
    }), 200


@bp.route('/products/<product_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_product(product_id):
    """
    Delete product (soft delete)

    Query param:
        hard: true/false - If true, permanently delete the product
    """
    hard_delete = request.args.get('hard', 'false').lower() == 'true'

    if hard_delete:
        success, error = ProductService.hard_delete_product(product_id)
    else:
        success, error = ProductService.delete_product(product_id)

    if not success:
        return jsonify(error), 400

    return jsonify({
        'message': 'Product deleted successfully'
    }), 200


@bp.route('/products/<product_id>/images', methods=['POST'])
@token_required
@admin_required
def upload_product_images(product_id):
    """
    Upload additional product images

    Content-Type: multipart/form-data
    Form field: images[] (multiple files)
    """
    product = ProductService.get_product(product_id)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Get image files
    images = request.files.getlist('images[]')

    if not images:
        return jsonify({'error': 'No images provided'}), 400

    # Update product with additional images
    product, error = ProductService.update_product(
        product_id,
        additional_images=images
    )

    if error:
        return jsonify(error), 400

    return jsonify({
        'message': 'Images uploaded successfully',
        'product': product.to_dict()
    }), 200


@bp.route('/products/low-stock', methods=['GET'])
@token_required
@admin_required
def get_low_stock_products():
    """
    Get products with low stock

    Query param:
        threshold: Stock threshold (optional, uses product's own threshold if not provided)
    """
    threshold = request.args.get('threshold', type=int)

    products = ProductService.get_low_stock_products(threshold)

    return jsonify({
        'products': [p.to_dict() for p in products],
        'count': len(products)
    }), 200


# ==================== Order Management ====================

@bp.route('/orders', methods=['GET'])
@token_required
@admin_required
def get_admin_orders():
    """
    Get all orders with filters

    Query params:
        page, per_page, status, payment_status, start_date, end_date
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    payment_status = request.args.get('payment_status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    result = AdminService.get_all_orders(
        page=page,
        per_page=per_page,
        status=status,
        payment_status=payment_status,
        start_date=start_date,
        end_date=end_date
    )

    return jsonify(result), 200


@bp.route('/orders/<order_id>/status', methods=['PUT'])
@token_required
@admin_required
def update_order_status(order_id):
    """
    Update order status

    Body: { "status": "processing" | "shipped" | "delivered" | "cancelled" }
    """
    data = request.get_json()

    if 'status' not in data:
        return jsonify({'error': 'status is required'}), 400

    order, error = AdminService.update_order_status(order_id, data['status'])

    if error:
        return jsonify(error), 400

    return jsonify({
        'message': 'Order status updated successfully',
        'order': order.to_dict()
    }), 200


@bp.route('/orders/<order_id>/tracking', methods=['PUT'])
@token_required
@admin_required
def update_order_tracking(order_id):
    """
    Update order tracking information

    Body: {
        "tracking_number": "...",
        "tracking_url": "..."
    }
    """
    data = request.get_json()

    tracking_number = data.get('tracking_number')
    tracking_url = data.get('tracking_url')

    order, error = AdminService.update_tracking_info(
        order_id,
        tracking_number,
        tracking_url
    )

    if error:
        return jsonify(error), 400

    return jsonify({
        'message': 'Tracking information updated successfully',
        'order': order.to_dict()
    }), 200


# ==================== User Management ====================

@bp.route('/users', methods=['GET'])
@token_required
@admin_required
def get_all_users():
    """
    Get all users with pagination

    Query params: page, per_page, role, is_active
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role')
    is_active = request.args.get('is_active')

    if is_active is not None:
        is_active = is_active.lower() == 'true'

    result = AdminService.get_all_users(
        page=page,
        per_page=per_page,
        role=role,
        is_active=is_active
    )

    return jsonify(result), 200


@bp.route('/users/<user_id>', methods=['PUT'])
@token_required
@admin_required
def update_user(user_id):
    """
    Update user details

    Body: { "is_active": true/false, "role": "customer" | "admin" }
    """
    data = request.get_json()

    user, error = AdminService.update_user(user_id, **data)

    if error:
        return jsonify(error), 400

    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    }), 200
