from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import all models here to ensure they're registered with SQLAlchemy
        from app.models import (
            user,
            product,
            category,
            cart,
            cart_item,
            order,
            order_item,
            payment,
            address
        )

    return db
