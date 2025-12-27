from flask import Blueprint, request, jsonify
from app.models.category import Category
from app.services.product_service import ProductService

bp = Blueprint('categories', __name__)


@bp.route('', methods=['GET'])
def get_categories():
    """
    Get all categories (public endpoint)

    Returns all categories ordered by display_order
    """
    categories = Category.query.order_by(Category.display_order.asc()).all()

    return jsonify({
        'categories': [category.to_dict() for category in categories],
        'count': len(categories)
    }), 200


@bp.route('/<category_id>', methods=['GET'])
def get_category(category_id):
    """
    Get single category details (public endpoint)
    """
    category = Category.query.get(category_id)

    if not category:
        return jsonify({'error': 'Category not found'}), 404

    return jsonify({'category': category.to_dict()}), 200


@bp.route('/<category_id>/products', methods=['GET'])
def get_category_products(category_id):
    """
    Get products in a specific category (public endpoint)

    Query params:
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
        sort_by: Field to sort by (default: created_at)
        sort_order: asc/desc (default: desc)
    """
    # Verify category exists
    category = Category.query.get(category_id)

    if not category:
        return jsonify({'error': 'Category not found'}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    # Get products in this category
    result = ProductService.get_all_products(
        page=page,
        per_page=per_page,
        category_id=category_id,
        in_stock_only=True,
        is_active=True,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return jsonify(result), 200


@bp.route('/slug/<slug>', methods=['GET'])
def get_category_by_slug(slug):
    """
    Get category by slug (public endpoint)
    """
    category = Category.query.filter_by(slug=slug).first()

    if not category:
        return jsonify({'error': 'Category not found'}), 404

    return jsonify({'category': category.to_dict()}), 200
