from flask import Blueprint

bp = Blueprint('categories', __name__)

@bp.route('', methods=['GET'])
def get_categories():
    return {'message': 'Get categories endpoint - to be implemented'}, 501
