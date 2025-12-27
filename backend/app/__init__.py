import os
from flask import Flask
from flask_cors import CORS
from app.config.base import config
from app.database.db import init_db


def create_app(config_name=None):
    """Application factory pattern"""

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    # Initialize database
    init_db(app)

    # Register blueprints (API routes)
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Cookie Shop API is running'}, 200

    return app


def register_blueprints(app):
    """Register Flask blueprints (API routes)"""
    from app.api import auth, products, categories, cart, users, admin
    from app.api.orders import orders_bp
    from app.api.payments import payments_bp

    # API v1 - Note: Some blueprints already have url_prefix set
    api_prefix = '/api/v1'

    app.register_blueprint(auth.bp, url_prefix=f'{api_prefix}/auth')
    app.register_blueprint(products.bp, url_prefix=f'{api_prefix}/products')
    app.register_blueprint(categories.bp, url_prefix=f'{api_prefix}/categories')
    app.register_blueprint(cart.bp, url_prefix=f'{api_prefix}/cart')
    app.register_blueprint(orders_bp)  # Has url_prefix='/api/v1/orders' in blueprint
    app.register_blueprint(payments_bp)  # Has url_prefix='/api/v1/payments' in blueprint
    app.register_blueprint(users.bp, url_prefix=f'{api_prefix}/users')
    app.register_blueprint(admin.bp, url_prefix=f'{api_prefix}/admin')


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500

    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request'}, 400

    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized'}, 401

    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden'}, 403
