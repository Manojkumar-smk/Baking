from flask import Blueprint

bp = Blueprint('admin', __name__)

@bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    return {'message': 'Admin dashboard endpoint - to be implemented'}, 501

@bp.route('/products', methods=['GET'])
def get_admin_products():
    return {'message': 'Admin get products endpoint - to be implemented'}, 501

@bp.route('/products', methods=['POST'])
def create_product():
    return {'message': 'Admin create product endpoint - to be implemented'}, 501
