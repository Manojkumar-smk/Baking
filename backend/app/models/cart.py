from datetime import datetime, timedelta
from app.database.db import db
import uuid


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'))
    session_id = db.Column(db.String(255), index=True)  # For guest users
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))

    # Relationships
    user = db.relationship('User', back_populates='carts')
    items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan', lazy='dynamic')

    # Constraints
    __table_args__ = (
        db.CheckConstraint('user_id IS NOT NULL OR session_id IS NOT NULL', name='check_user_or_session'),
    )

    @property
    def total_items(self):
        """Calculate total number of items in cart"""
        return sum(item.quantity for item in self.items)

    @property
    def subtotal(self):
        """Calculate cart subtotal"""
        return sum(item.quantity * item.unit_price for item in self.items)

    def to_dict(self):
        """Convert cart to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'items': [item.to_dict() for item in self.items],
            'total_items': self.total_items,
            'subtotal': float(self.subtotal),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Cart {self.id}>'
