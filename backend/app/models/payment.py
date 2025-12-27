from datetime import datetime
from app.database.db import db
from sqlalchemy.dialects.postgresql import JSONB
import uuid


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)

    # Stripe information
    stripe_payment_intent_id = db.Column(db.String(255), unique=True, index=True)
    stripe_charge_id = db.Column(db.String(255))
    stripe_customer_id = db.Column(db.String(255))

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD', nullable=False)
    status = db.Column(db.String(50), default='pending', nullable=False, index=True)
    # Status values: pending, succeeded, failed, refunded, cancelled
    payment_method = db.Column(db.String(50))  # card, wallet, etc.

    # Card details (last 4 digits only)
    card_brand = db.Column(db.String(50))
    card_last4 = db.Column(db.String(4))

    # Metadata
    metadata = db.Column(JSONB)
    error_message = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    succeeded_at = db.Column(db.DateTime)
    failed_at = db.Column(db.DateTime)

    # Relationships
    order = db.relationship('Order', back_populates='payments')

    # Constraints
    __table_args__ = (
        db.CheckConstraint('amount > 0', name='check_positive_amount'),
    )

    def to_dict(self):
        """Convert payment to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'stripe_payment_intent_id': self.stripe_payment_intent_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'status': self.status,
            'payment_method': self.payment_method,
            'card_brand': self.card_brand,
            'card_last4': self.card_last4,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'succeeded_at': self.succeeded_at.isoformat() if self.succeeded_at else None
        }

    def __repr__(self):
        return f'<Payment {self.id}>'
