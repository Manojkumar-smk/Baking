from datetime import datetime
from app.database.db import db
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
import uuid


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id', ondelete='SET NULL'))
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    compare_at_price = db.Column(db.Numeric(10, 2))  # Original price for sales
    cost = db.Column(db.Numeric(10, 2))  # Cost for profit calculation
    sku = db.Column(db.String(100), unique=True, index=True)
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    low_stock_threshold = db.Column(db.Integer, default=10)
    weight_grams = db.Column(db.Integer)  # For shipping calculation
    image_url = db.Column(db.String(500))  # Main product image
    images = db.Column(JSONB)  # Additional images array
    ingredients = db.Column(ARRAY(db.Text))
    allergens = db.Column(ARRAY(db.Text))
    nutritional_info = db.Column(JSONB)
    is_featured = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    tags = db.Column(ARRAY(db.Text))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    category = db.relationship('Category', back_populates='products')
    cart_items = db.relationship('CartItem', back_populates='product', lazy='dynamic')
    order_items = db.relationship('OrderItem', back_populates='product', lazy='dynamic')

    # Constraints
    __table_args__ = (
        db.CheckConstraint('price > 0', name='check_positive_price'),
        db.CheckConstraint('stock_quantity >= 0', name='check_positive_stock'),
    )

    @property
    def in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        """Check if product is low in stock"""
        return 0 < self.stock_quantity <= self.low_stock_threshold

    def to_dict(self, include_stock=True):
        """Convert product to dictionary"""
        data = {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'price': float(self.price) if self.price else 0,
            'compare_at_price': float(self.compare_at_price) if self.compare_at_price else None,
            'sku': self.sku,
            'image_url': self.image_url,
            'images': self.images,
            'ingredients': self.ingredients,
            'allergens': self.allergens,
            'nutritional_info': self.nutritional_info,
            'is_featured': self.is_featured,
            'is_active': self.is_active,
            'tags': self.tags,
            'in_stock': self.in_stock,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_stock:
            data['stock_quantity'] = self.stock_quantity
            data['is_low_stock'] = self.is_low_stock

        return data

    def __repr__(self):
        return f'<Product {self.name}>'
