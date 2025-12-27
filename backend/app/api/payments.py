"""
Payment API endpoints
"""
from flask import Blueprint, request, jsonify, current_app
from app.services.payment_service import PaymentService
from app.utils.decorators import token_required

payments_bp = Blueprint('payments', __name__, url_prefix='/api/v1/payments')


@payments_bp.route('/create-intent', methods=['POST'])
def create_payment_intent():
    """
    Create a Stripe PaymentIntent for an order

    Request body:
        {
            "order_id": "order-uuid",
            "amount": 29.99
        }

    Returns:
        {
            "client_secret": "pi_xxx_secret_xxx",
            "payment_intent_id": "pi_xxx",
            "payment_id": "payment-uuid"
        }
    """
    try:
        data = request.get_json()

        order_id = data.get('order_id')
        amount = data.get('amount')

        if not order_id or not amount:
            return jsonify({'error': 'order_id and amount are required'}), 400

        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid amount'}), 400

        result = PaymentService.create_payment_intent(
            order_id=order_id,
            amount=amount,
            metadata=data.get('metadata')
        )

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Error creating payment intent: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@payments_bp.route('/confirm', methods=['POST'])
def confirm_payment():
    """
    Confirm a payment and update order status

    Request body:
        {
            "payment_intent_id": "pi_xxx"
        }

    Returns:
        {
            "payment_id": "payment-uuid",
            "status": "succeeded",
            "order_id": "order-uuid",
            "order_number": "ORD-20240101-ABC123"
        }
    """
    try:
        data = request.get_json()

        payment_intent_id = data.get('payment_intent_id')

        if not payment_intent_id:
            return jsonify({'error': 'payment_intent_id is required'}), 400

        result = PaymentService.confirm_payment(payment_intent_id)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Error confirming payment: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@payments_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhook events

    Stripe sends events like:
    - payment_intent.succeeded
    - payment_intent.payment_failed
    - charge.refunded
    """
    try:
        payload = request.data
        signature = request.headers.get('Stripe-Signature')

        if not signature:
            return jsonify({'error': 'Missing signature'}), 400

        result = PaymentService.handle_webhook(payload, signature)

        return jsonify(result), 200

    except ValueError as e:
        current_app.logger.error(f'Webhook error: {str(e)}')
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Webhook processing error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@payments_bp.route('/<payment_id>', methods=['GET'])
@token_required
def get_payment(payment_id):
    """
    Get payment details

    Returns:
        {
            "id": "payment-uuid",
            "order_id": "order-uuid",
            "amount": 29.99,
            "status": "succeeded",
            ...
        }
    """
    try:
        payment = PaymentService.get_payment(payment_id)

        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        return jsonify(payment.to_dict()), 200

    except Exception as e:
        current_app.logger.error(f'Error fetching payment: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@payments_bp.route('/<payment_id>/refund', methods=['POST'])
@token_required
def create_refund(payment_id):
    """
    Create a refund for a payment (admin only)

    Request body:
        {
            "amount": 10.00,  // Optional, full refund if not provided
            "reason": "customer request"  // Optional
        }

    Returns:
        {
            "refund_id": "re_xxx",
            "status": "succeeded",
            "amount": 10.00
        }
    """
    try:
        from flask import g

        # Check admin permission
        if g.current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        data = request.get_json() or {}

        amount = data.get('amount')
        reason = data.get('reason')

        # Validate amount if provided
        if amount is not None:
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid amount'}), 400

        result = PaymentService.create_refund(
            payment_id=payment_id,
            amount=amount,
            reason=reason
        )

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Error creating refund: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500
