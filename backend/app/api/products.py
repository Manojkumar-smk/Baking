from flask import Blueprint, request, jsonify
from app.services.product_service import ProductService
from app.models.category import Category

bp = Blueprint('products', __name__)


@bp.route('', methods=['GET'])
def get_products():
    """
    Get products for customer view (public endpoint)

    Query params:
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
        category_id: Filter by category
        search: Search term
        is_featured: true/false - Filter featured products
        sort_by: Field to sort by (default: created_at)
        sort_order: asc/desc (default: desc)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id')
    search = request.args.get('search')
    is_featured = request.args.get('is_featured')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    # Convert string booleans
    if is_featured is not None:
        is_featured = is_featured.lower() == 'true'

    # Get products - only show active products with stock
    result = ProductService.get_all_products(
        page=page,
        per_page=per_page,
        category_id=category_id,
        search=search,
        in_stock_only=True,  # Only show in-stock products to customers
        is_active=True,      # Only show active products
        is_featured=is_featured,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return jsonify(result), 200


@bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    Get single product details (public endpoint)

    Returns product only if it's active
    """
    product = ProductService.get_product(product_id)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Only show active products to customers
    if not product.is_active:
        return jsonify({'error': 'Product not available'}), 404

    return jsonify({'product': product.to_dict()}), 200


@bp.route('/slug/<slug>', methods=['GET'])
def get_product_by_slug(slug):
    """
    Get product by slug (public endpoint)

    Returns product only if it's active
    """
    product = ProductService.get_product_by_slug(slug)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Only show active products to customers
    if not product.is_active:
        return jsonify({'error': 'Product not available'}), 404

    return jsonify({'product': product.to_dict()}), 200


@bp.route('/featured', methods=['GET'])
def get_featured_products():
    """
    Get featured products (public endpoint)

    Query params:
        limit: Number of products to return (default: 8)
    """
    limit = request.args.get('limit', 8, type=int)

    result = ProductService.get_all_products(
        page=1,
        per_page=limit,
        in_stock_only=True,
        is_active=True,
        is_featured=True,
        sort_by='created_at',
        sort_order='desc'
    )

    return jsonify({
        'products': result['products'],
        'count': len(result['products'])
    }), 200


@bp.route('/search', methods=['GET'])
def search_products():
    """
    Search products by name or description (public endpoint)

    Query params:
        q: Search query (required)
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
    """
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    result = ProductService.get_all_products(
        page=page,
        per_page=per_page,
        search=query,
        in_stock_only=True,
        is_active=True,
        sort_by='created_at',
        sort_order='desc'
    )

    return jsonify(result), 200
