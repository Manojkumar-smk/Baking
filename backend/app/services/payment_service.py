"""
Payment service for Razorpay integration
"""
from typing import Dict, Optional
import razorpay
import hmac
import hashlib
from flask import current_app
from datetime import datetime
from app.database.db import db
from app.models.payment import Payment
from app.models.order import Order


class PaymentService:
    """Service for handling payment operations with Razorpay"""

    @staticmethod
    def get_razorpay_client():
        """Initialize and return Razorpay client"""
        key_id = current_app.config.get('RAZORPAY_KEY_ID')
        key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')

        if not key_id or not key_secret:
            raise ValueError('Razorpay credentials not configured')

        return razorpay.Client(auth=(key_id, key_secret))

    @staticmethod
    def create_order(order_id: str, amount: float, currency: str = 'INR',
                    receipt: Optional[str] = None, notes: Optional[Dict] = None) -> Dict:
        """
        Create a Razorpay Order

        Args:
            order_id: Order ID from our database
            amount: Amount in rupees (will be converted to paise)
            currency: Currency code (default: INR)
            receipt: Receipt number (optional)
            notes: Additional notes (optional)

        Returns:
            Dict with razorpay_order_id and payment details
        """
        client = PaymentService.get_razorpay_client()

        # Get order to validate
        order = Order.query.get(order_id)
        if not order:
            raise ValueError(f'Order {order_id} not found')

        # Convert amount to paise (Razorpay uses smallest currency unit)
        amount_paise = int(amount * 100)

        # Prepare notes
        payment_notes = {
            'order_id': order_id,
            'order_number': order.order_number,
            'customer_email': order.customer_email
        }
        if notes:
            payment_notes.update(notes)

        try:
            # Create Razorpay Order
            razorpay_order = client.order.create({
                'amount': amount_paise,
                'currency': currency,
                'receipt': receipt or order.order_number,
                'notes': payment_notes
            })

            # Create payment record in database
            payment = Payment(
                order_id=order_id,
                razorpay_order_id=razorpay_order['id'],
                amount=amount,
                currency=currency.upper(),
                status='created',
                payment_metadata=payment_notes
            )
            db.session.add(payment)
            db.session.commit()

            return {
                'razorpay_order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'payment_id': payment.id,
                'key_id': current_app.config.get('RAZORPAY_KEY_ID')
            }

        except razorpay.errors.BadRequestError as e:
            raise ValueError(f'Razorpay error: {str(e)}')

    @staticmethod
    def verify_payment_signature(razorpay_order_id: str, razorpay_payment_id: str,
                                 razorpay_signature: str) -> bool:
        """
        Verify Razorpay payment signature

        Args:
            razorpay_order_id: Razorpay order ID
            razorpay_payment_id: Razorpay payment ID
            razorpay_signature: Razorpay signature

        Returns:
            True if signature is valid, False otherwise
        """
        key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')

        # Generate expected signature
        message = f'{razorpay_order_id}|{razorpay_payment_id}'
        expected_signature = hmac.new(
            key_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, razorpay_signature)

    @staticmethod
    def confirm_payment(razorpay_order_id: str, razorpay_payment_id: str,
                       razorpay_signature: str) -> Dict:
        """
        Confirm a payment and update order status

        Args:
            razorpay_order_id: Razorpay order ID
            razorpay_payment_id: Razorpay payment ID
            razorpay_signature: Razorpay signature

        Returns:
            Dict with payment status
        """
        # Verify signature
        if not PaymentService.verify_payment_signature(
            razorpay_order_id, razorpay_payment_id, razorpay_signature
        ):
            raise ValueError('Invalid payment signature')

        # Find payment record
        payment = Payment.query.filter_by(
            razorpay_order_id=razorpay_order_id
        ).first()

        if not payment:
            raise ValueError(f'Payment record not found for order {razorpay_order_id}')

        try:
            client = PaymentService.get_razorpay_client()

            # Fetch payment details from Razorpay
            razorpay_payment = client.payment.fetch(razorpay_payment_id)

            # Update payment record
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = razorpay_payment['status']  # 'captured', 'authorized', etc.

            # Extract payment method details
            if razorpay_payment.get('method'):
                payment.payment_method = razorpay_payment['method']

            # Extract card details if payment method is card
            if razorpay_payment.get('card'):
                card = razorpay_payment['card']
                payment.card_brand = card.get('network')
                payment.card_last4 = card.get('last4')

            # If payment is captured, mark as succeeded
            if razorpay_payment['status'] == 'captured':
                payment.status = 'captured'
                payment.succeeded_at = datetime.utcnow()

                # Update order payment status
                order = payment.order
                order.payment_status = 'paid'
                order.paid_at = datetime.utcnow()
                order.status = 'processing'  # Move to processing after payment

            db.session.commit()

            return {
                'payment_id': payment.id,
                'status': payment.status,
                'order_id': payment.order_id,
                'order_number': payment.order.order_number
            }

        except razorpay.errors.BadRequestError as e:
            raise ValueError(f'Razorpay error: {str(e)}')

    @staticmethod
    def handle_webhook(payload: bytes, signature: str) -> Dict:
        """
        Handle Razorpay webhook events

        Args:
            payload: Request body
            signature: Razorpay signature header (X-Razorpay-Signature)

        Returns:
            Dict with event handling result
        """
        webhook_secret = current_app.config.get('RAZORPAY_WEBHOOK_SECRET')

        if not webhook_secret:
            raise ValueError('Razorpay webhook secret not configured')

        # Verify webhook signature
        expected_signature = hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, signature):
            raise ValueError('Invalid webhook signature')

        # Parse event
        import json
        event = json.loads(payload.decode('utf-8'))

        event_type = event.get('event')

        # Handle different event types
        if event_type == 'payment.captured':
            PaymentService._handle_payment_captured(event['payload']['payment']['entity'])

        elif event_type == 'payment.failed':
            PaymentService._handle_payment_failed(event['payload']['payment']['entity'])

        elif event_type == 'payment.authorized':
            PaymentService._handle_payment_authorized(event['payload']['payment']['entity'])

        elif event_type == 'refund.created':
            PaymentService._handle_refund(event['payload']['refund']['entity'])

        return {'status': 'success', 'event_type': event_type}

    @staticmethod
    def _handle_payment_captured(payment_data):
        """Handle payment captured webhook"""
        payment = Payment.query.filter_by(
            razorpay_order_id=payment_data['order_id']
        ).first()

        if payment and payment.status != 'captured':
            payment.razorpay_payment_id = payment_data['id']
            payment.status = 'captured'
            payment.succeeded_at = datetime.utcnow()

            # Update payment method details
            if payment_data.get('method'):
                payment.payment_method = payment_data['method']

            if payment_data.get('card'):
                card = payment_data['card']
                payment.card_brand = card.get('network')
                payment.card_last4 = card.get('last4')

            # Update order
            order = payment.order
            order.payment_status = 'paid'
            order.paid_at = datetime.utcnow()
            if order.status == 'pending':
                order.status = 'processing'

            db.session.commit()

    @staticmethod
    def _handle_payment_authorized(payment_data):
        """Handle payment authorized webhook"""
        payment = Payment.query.filter_by(
            razorpay_order_id=payment_data['order_id']
        ).first()

        if payment:
            payment.razorpay_payment_id = payment_data['id']
            payment.status = 'authorized'

            db.session.commit()

    @staticmethod
    def _handle_payment_failed(payment_data):
        """Handle failed payment webhook"""
        payment = Payment.query.filter_by(
            razorpay_order_id=payment_data.get('order_id')
        ).first()

        if payment:
            payment.status = 'failed'
            payment.failed_at = datetime.utcnow()
            payment.error_message = payment_data.get('error_description')

            # Update order
            order = payment.order
            order.payment_status = 'failed'

            db.session.commit()

    @staticmethod
    def _handle_refund(refund_data):
        """Handle refund webhook"""
        # Find payment by payment ID
        payment = Payment.query.filter_by(
            razorpay_payment_id=refund_data['payment_id']
        ).first()

        if payment:
            payment.status = 'refunded'

            # Update order
            order = payment.order
            order.payment_status = 'refunded'
            order.status = 'refunded'

            db.session.commit()

    @staticmethod
    def create_refund(payment_id: str, amount: Optional[float] = None,
                     notes: Optional[Dict] = None) -> Dict:
        """
        Create a refund for a payment

        Args:
            payment_id: Payment ID
            amount: Refund amount in rupees (None for full refund)
            notes: Additional notes

        Returns:
            Dict with refund details
        """
        client = PaymentService.get_razorpay_client()

        payment = Payment.query.get(payment_id)
        if not payment:
            raise ValueError(f'Payment {payment_id} not found')

        if payment.status not in ['captured', 'authorized']:
            raise ValueError('Can only refund captured or authorized payments')

        if not payment.razorpay_payment_id:
            raise ValueError('Razorpay payment ID not found')

        try:
            # Create refund
            refund_data = {}

            if amount:
                refund_data['amount'] = int(amount * 100)  # Convert to paise

            if notes:
                refund_data['notes'] = notes

            refund = client.payment.refund(payment.razorpay_payment_id, refund_data)

            # Update payment status
            payment.status = 'refunded'

            # Update order
            order = payment.order
            order.payment_status = 'refunded'
            order.status = 'refunded'

            db.session.commit()

            return {
                'refund_id': refund['id'],
                'status': refund['status'],
                'amount': refund.get('amount', 0) / 100  # Convert paise to rupees
            }

        except razorpay.errors.BadRequestError as e:
            raise ValueError(f'Razorpay error: {str(e)}')

    @staticmethod
    def get_payment_by_order_id(razorpay_order_id: str) -> Optional[Payment]:
        """Get payment by Razorpay Order ID"""
        return Payment.query.filter_by(
            razorpay_order_id=razorpay_order_id
        ).first()

    @staticmethod
    def get_payment(payment_id: str) -> Optional[Payment]:
        """Get payment by ID"""
        return Payment.query.get(payment_id)
