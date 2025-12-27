from functools import wraps
from flask import request, jsonify, g
from app.utils.jwt_utils import verify_token
from jose import JWTError
from app.models.user import User


def token_required(f):
    """
    Decorator to require valid JWT token
    Extracts user from token and adds to Flask g object
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401

        try:
            # Verify token
            payload = verify_token(token, 'access')
            user_id = payload.get('user_id')

            # Get user from database
            user = User.query.get(user_id)

            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401

            # Add user to Flask g object
            g.current_user = user
            g.user_id = user_id
            g.user_role = user.role

        except JWTError as e:
            return jsonify({'error': f'Token is invalid: {str(e)}'}), 401
        except Exception as e:
            return jsonify({'error': 'Authentication failed'}), 401

        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """
    Decorator to require admin role
    Must be used after @token_required
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if user is authenticated (should be set by @token_required)
        if not hasattr(g, 'current_user'):
            return jsonify({'error': 'Authentication required'}), 401

        # Check if user is admin
        if g.current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        return f(*args, **kwargs)

    return decorated


def optional_token(f):
    """
    Decorator to optionally extract user from token
    If token is present and valid, adds user to g object
    If no token or invalid token, continues without user
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                pass

        if token:
            try:
                payload = verify_token(token, 'access')
                user_id = payload.get('user_id')
                user = User.query.get(user_id)

                if user and user.is_active:
                    g.current_user = user
                    g.user_id = user_id
                    g.user_role = user.role
            except:
                pass  # Continue without user if token is invalid

        return f(*args, **kwargs)

    return decorated
