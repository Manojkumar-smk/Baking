from flask import Blueprint

bp = Blueprint('cart', __name__)

@bp.route('', methods=['GET'])
def get_cart():
    return {'message': 'Get cart endpoint - to be implemented'}, 501

@bp.route('/items', methods=['POST'])
def add_to_cart():
    return {'message': 'Add to cart endpoint - to be implemented'}, 501
