"""
Payment service for Stripe integration
"""
from typing import Dict, Optional
import stripe
from flask import current_app
from datetime import datetime
from app.database.db import db
from app.models.payment import Payment
from app.models.order import Order


class PaymentService:
    """Service for handling payment operations with Stripe"""

    @staticmethod
    def initialize_stripe():
        """Initialize Stripe with API key"""
        stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')

    @staticmethod
    def create_payment_intent(order_id: str, amount: float, currency: str = 'usd',
                             metadata: Optional[Dict] = None) -> Dict:
        """
        Create a Stripe PaymentIntent

        Args:
            order_id: Order ID
            amount: Amount in dollars (will be converted to cents)
            currency: Currency code (default: usd)
            metadata: Additional metadata

        Returns:
            Dict with client_secret and payment_intent_id
        """
        PaymentService.initialize_stripe()

        # Get order to validate
        order = Order.query.get(order_id)
        if not order:
            raise ValueError(f'Order {order_id} not found')

        # Convert amount to cents (Stripe uses smallest currency unit)
        amount_cents = int(amount * 100)

        # Prepare metadata
        payment_metadata = {
            'order_id': order_id,
            'order_number': order.order_number,
            'customer_email': order.customer_email
        }
        if metadata:
            payment_metadata.update(metadata)

        try:
            # Create PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=payment_metadata,
                description=f'Order {order.order_number}',
                receipt_email=order.customer_email,
                automatic_payment_methods={'enabled': True}
            )

            # Create payment record in database
            payment = Payment(
                order_id=order_id,
                stripe_payment_intent_id=intent.id,
                amount=amount,
                currency=currency.upper(),
                status='pending'
            )
            db.session.add(payment)
            db.session.commit()

            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'payment_id': payment.id
            }

        except stripe.error.StripeError as e:
            raise ValueError(f'Stripe error: {str(e)}')

    @staticmethod
    def confirm_payment(payment_intent_id: str) -> Dict:
        """
        Confirm a payment and update order status

        Args:
            payment_intent_id: Stripe PaymentIntent ID

        Returns:
            Dict with payment status
        """
        PaymentService.initialize_stripe()

        try:
            # Retrieve PaymentIntent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            # Find payment record
            payment = Payment.query.filter_by(
                stripe_payment_intent_id=payment_intent_id
            ).first()

            if not payment:
                raise ValueError(f'Payment record not found for intent {payment_intent_id}')

            # Update payment status based on intent status
            if intent.status == 'succeeded':
                payment.status = 'succeeded'
                payment.succeeded_at = datetime.utcnow()

                # Extract payment method details if available
                if intent.payment_method:
                    pm = stripe.PaymentMethod.retrieve(intent.payment_method)
                    if pm.card:
                        payment.payment_method = 'card'
                        payment.card_brand = pm.card.brand
                        payment.card_last4 = pm.card.last4

                # Update order payment status
                order = payment.order
                order.payment_status = 'paid'
                order.paid_at = datetime.utcnow()
                order.status = 'processing'  # Move to processing after payment

            elif intent.status == 'processing':
                payment.status = 'processing'
            elif intent.status == 'requires_payment_method':
                payment.status = 'requires_payment_method'
            elif intent.status == 'requires_confirmation':
                payment.status = 'requires_confirmation'
            elif intent.status == 'canceled':
                payment.status = 'canceled'
                order = payment.order
                order.payment_status = 'failed'

            db.session.commit()

            return {
                'payment_id': payment.id,
                'status': payment.status,
                'order_id': payment.order_id,
                'order_number': payment.order.order_number
            }

        except stripe.error.StripeError as e:
            raise ValueError(f'Stripe error: {str(e)}')

    @staticmethod
    def handle_webhook(payload: bytes, signature: str) -> Dict:
        """
        Handle Stripe webhook events

        Args:
            payload: Request body
            signature: Stripe signature header

        Returns:
            Dict with event handling result
        """
        PaymentService.initialize_stripe()

        webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')

        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
        except ValueError:
            raise ValueError('Invalid payload')
        except stripe.error.SignatureVerificationError:
            raise ValueError('Invalid signature')

        # Handle different event types
        if event.type == 'payment_intent.succeeded':
            intent = event.data.object
            PaymentService._handle_payment_succeeded(intent)

        elif event.type == 'payment_intent.payment_failed':
            intent = event.data.object
            PaymentService._handle_payment_failed(intent)

        elif event.type == 'charge.refunded':
            charge = event.data.object
            PaymentService._handle_refund(charge)

        return {'status': 'success', 'event_type': event.type}

    @staticmethod
    def _handle_payment_succeeded(intent):
        """Handle successful payment webhook"""
        payment = Payment.query.filter_by(
            stripe_payment_intent_id=intent.id
        ).first()

        if payment and payment.status != 'succeeded':
            payment.status = 'succeeded'
            payment.succeeded_at = datetime.utcnow()

            # Update order
            order = payment.order
            order.payment_status = 'paid'
            order.paid_at = datetime.utcnow()
            if order.status == 'pending':
                order.status = 'processing'

            db.session.commit()

    @staticmethod
    def _handle_payment_failed(intent):
        """Handle failed payment webhook"""
        payment = Payment.query.filter_by(
            stripe_payment_intent_id=intent.id
        ).first()

        if payment:
            payment.status = 'failed'

            # Update order
            order = payment.order
            order.payment_status = 'failed'

            db.session.commit()

    @staticmethod
    def _handle_refund(charge):
        """Handle refund webhook"""
        # Find payment by charge ID
        payment = Payment.query.filter_by(
            stripe_charge_id=charge.id
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
                     reason: Optional[str] = None) -> Dict:
        """
        Create a refund for a payment

        Args:
            payment_id: Payment ID
            amount: Refund amount (None for full refund)
            reason: Refund reason

        Returns:
            Dict with refund details
        """
        PaymentService.initialize_stripe()

        payment = Payment.query.get(payment_id)
        if not payment:
            raise ValueError(f'Payment {payment_id} not found')

        if payment.status != 'succeeded':
            raise ValueError('Can only refund succeeded payments')

        try:
            # Create refund
            refund_params = {
                'payment_intent': payment.stripe_payment_intent_id
            }

            if amount:
                refund_params['amount'] = int(amount * 100)

            if reason:
                refund_params['reason'] = reason

            refund = stripe.Refund.create(**refund_params)

            # Update payment status
            if refund.status == 'succeeded':
                payment.status = 'refunded'

                # Update order
                order = payment.order
                order.payment_status = 'refunded'
                order.status = 'refunded'

                db.session.commit()

            return {
                'refund_id': refund.id,
                'status': refund.status,
                'amount': refund.amount / 100
            }

        except stripe.error.StripeError as e:
            raise ValueError(f'Stripe error: {str(e)}')

    @staticmethod
    def get_payment_by_intent(payment_intent_id: str) -> Optional[Payment]:
        """Get payment by Stripe PaymentIntent ID"""
        return Payment.query.filter_by(
            stripe_payment_intent_id=payment_intent_id
        ).first()

    @staticmethod
    def get_payment(payment_id: str) -> Optional[Payment]:
        """Get payment by ID"""
        return Payment.query.get(payment_id)
