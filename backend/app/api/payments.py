"""
Payment API endpoints for Razorpay integration
"""
from flask import Blueprint, request, jsonify, current_app
from app.services.payment_service import PaymentService
from app.utils.decorators import token_required

payments_bp = Blueprint('payments', __name__, url_prefix='/api/v1/payments')


@payments_bp.route('/create-order', methods=['POST'])
def create_payment_order():
    """
    Create a Razorpay Order

    Request body:
        {
            "order_id": "order-uuid",
            "amount": 299.99,
            "currency": "INR"  // optional, defaults to INR
        }

    Returns:
        {
            "razorpay_order_id": "order_xxx",
            "amount": 29999,
            "currency": "INR",
            "payment_id": "payment-uuid",
            "key_id": "rzp_test_xxx"
        }
    """
    try:
        data = request.get_json()

        order_id = data.get('order_id')
        amount = data.get('amount')
        currency = data.get('currency', 'INR')

        if not order_id or not amount:
            return jsonify({'error': 'order_id and amount are required'}), 400

        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid amount'}), 400

        result = PaymentService.create_order(
            order_id=order_id,
            amount=amount,
            currency=currency,
            notes=data.get('notes')
        )

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Error creating Razorpay order: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@payments_bp.route('/verify', methods=['POST'])
def verify_payment():
    """
    Verify and confirm a Razorpay payment

    Request body:
        {
            "razorpay_order_id": "order_xxx",
            "razorpay_payment_id": "pay_xxx",
            "razorpay_signature": "signature_xxx"
        }

    Returns:
        {
            "payment_id": "payment-uuid",
            "status": "captured",
            "order_id": "order-uuid",
            "order_number": "ORD-20240101-ABC123"
        }
    """
    try:
        data = request.get_json()

        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return jsonify({
                'error': 'razorpay_order_id, razorpay_payment_id, and razorpay_signature are required'
            }), 400

        result = PaymentService.confirm_payment(
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature
        )

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Error verifying payment: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@payments_bp.route('/webhook', methods=['POST'])
def razorpay_webhook():
    """
    Handle Razorpay webhook events

    Razorpay sends events like:
    - payment.captured
    - payment.failed
    - payment.authorized
    - refund.created
    """
    try:
        payload = request.data
        signature = request.headers.get('X-Razorpay-Signature')

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
            "razorpay_order_id": "order_xxx",
            "amount": 299.99,
            "status": "captured",
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
            "amount": 100.00,  // Optional, full refund if not provided
            "notes": {         // Optional
                "reason": "customer request"
            }
        }

    Returns:
        {
            "refund_id": "rfnd_xxx",
            "status": "processed",
            "amount": 100.00
        }
    """
    try:
        from flask import g

        # Check admin permission
        if g.current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        data = request.get_json() or {}

        amount = data.get('amount')
        notes = data.get('notes')

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
            notes=notes
        )

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Error creating refund: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500
