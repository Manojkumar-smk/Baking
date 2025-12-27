from flask import Blueprint

bp = Blueprint('orders', __name__)

@bp.route('', methods=['GET'])
def get_orders():
    return {'message': 'Get orders endpoint - to be implemented'}, 501

@bp.route('', methods=['POST'])
def create_order():
    return {'message': 'Create order endpoint - to be implemented'}, 501
