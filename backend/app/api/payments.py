from flask import Blueprint

bp = Blueprint('payments', __name__)

@bp.route('/create-intent', methods=['POST'])
def create_payment_intent():
    return {'message': 'Create payment intent endpoint - to be implemented'}, 501

@bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    return {'message': 'Stripe webhook endpoint - to be implemented'}, 501
