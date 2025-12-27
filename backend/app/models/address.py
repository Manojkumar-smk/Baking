from datetime import datetime
from app.database.db import db
import uuid


class Address(db.Model):
    __tablename__ = 'addresses'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    address_type = db.Column(db.String(20), default='shipping', nullable=False)  # shipping or billing
    is_default = db.Column(db.Boolean, default=False, nullable=False)

    full_name = db.Column(db.String(200), nullable=False)
    street_address = db.Column(db.String(255), nullable=False)
    apartment = db.Column(db.String(100))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), default='USA', nullable=False)
    phone = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='addresses')

    def to_dict(self):
        """Convert address to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'address_type': self.address_type,
            'is_default': self.is_default,
            'full_name': self.full_name,
            'street_address': self.street_address,
            'apartment': self.apartment,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Address {self.id}>'
