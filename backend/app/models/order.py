from datetime import datetime
from app.database.db import db
from sqlalchemy.dialects.postgresql import JSONB
import uuid
import random
import string


def generate_order_number():
    """Generate unique order number"""
    timestamp = datetime.utcnow().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f'ORD-{timestamp}-{random_str}'


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_number = db.Column(db.String(50), unique=True, nullable=False, default=generate_order_number, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'))

    # Customer Information (denormalized for record keeping)
    customer_email = db.Column(db.String(255), nullable=False)
    customer_first_name = db.Column(db.String(100))
    customer_last_name = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))

    # Pricing
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    shipping_amount = db.Column(db.Numeric(10, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)

    # Addresses (denormalized as JSONB)
    shipping_address = db.Column(JSONB, nullable=False)
    billing_address = db.Column(JSONB)

    # Status tracking
    status = db.Column(db.String(50), default='pending', nullable=False, index=True)
    # Status values: pending, processing, shipped, delivered, cancelled, refunded
    payment_status = db.Column(db.String(50), default='pending', nullable=False, index=True)
    # Payment status: pending, paid, failed, refunded
    fulfillment_status = db.Column(db.String(50), default='unfulfilled', nullable=False)
    # Fulfillment: unfulfilled, partial, fulfilled

    # Shipping
    shipping_method = db.Column(db.String(100))
    tracking_number = db.Column(db.String(200))
    tracking_url = db.Column(db.String(500))

    # Notes
    customer_notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    paid_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan', lazy='dynamic')
    payments = db.relationship('Payment', back_populates='order', lazy='dynamic')

    # Constraints
    __table_args__ = (
        db.CheckConstraint('total_amount >= 0', name='check_positive_total'),
    )

    def to_dict(self, include_items=True):
        """Convert order to dictionary"""
        data = {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'customer_email': self.customer_email,
            'customer_first_name': self.customer_first_name,
            'customer_last_name': self.customer_last_name,
            'customer_phone': self.customer_phone,
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'shipping_amount': float(self.shipping_amount),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'shipping_address': self.shipping_address,
            'billing_address': self.billing_address,
            'status': self.status,
            'payment_status': self.payment_status,
            'fulfillment_status': self.fulfillment_status,
            'shipping_method': self.shipping_method,
            'tracking_number': self.tracking_number,
            'tracking_url': self.tracking_url,
            'customer_notes': self.customer_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None
        }

        if include_items:
            data['items'] = [item.to_dict() for item in self.items]

        return data

    def __repr__(self):
        return f'<Order {self.order_number}>'
