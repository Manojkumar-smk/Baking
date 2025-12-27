from flask import Blueprint

bp = Blueprint('products', __name__)

@bp.route('', methods=['GET'])
def get_products():
    return {'message': 'Get products endpoint - to be implemented'}, 501

@bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    return {'message': f'Get product {product_id} - to be implemented'}, 501
