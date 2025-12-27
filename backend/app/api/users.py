from flask import Blueprint

bp = Blueprint('users', __name__)

@bp.route('/profile', methods=['GET'])
def get_profile():
    return {'message': 'Get profile endpoint - to be implemented'}, 501

@bp.route('/addresses', methods=['GET'])
def get_addresses():
    return {'message': 'Get addresses endpoint - to be implemented'}, 501
