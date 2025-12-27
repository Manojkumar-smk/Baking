from flask import Blueprint, request, jsonify, g
from app.services.auth_service import AuthService
from app.utils.decorators import token_required

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()

    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    # Register user
    user, access_token, refresh_token_or_error = AuthService.register_user(
        email=data['email'],
        password=data['password'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone')
    )

    if not user:
        # Registration failed
        error = refresh_token_or_error
        return jsonify(error), 400

    # Return user data and tokens
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token_or_error
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()

    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    # Authenticate user
    user, access_token, refresh_token_or_error = AuthService.login_user(
        email=data['email'],
        password=data['password']
    )

    if not user:
        # Login failed
        error = refresh_token_or_error
        return jsonify(error), 401

    # Return user data and tokens
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token_or_error
    }), 200


@bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token"""
    data = request.get_json()

    if not data.get('refresh_token'):
        return jsonify({'error': 'Refresh token is required'}), 400

    # Generate new tokens
    access_token, refresh_token_or_error, *error = AuthService.refresh_access_token(
        data['refresh_token']
    )

    if not access_token:
        # Token refresh failed
        error_dict = error[0] if error else refresh_token_or_error
        return jsonify(error_dict), 401

    return jsonify({
        'message': 'Token refreshed successfully',
        'access_token': access_token,
        'refresh_token': refresh_token_or_error
    }), 200


@bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current authenticated user"""
    user = g.current_user

    return jsonify({
        'user': user.to_dict()
    }), 200


@bp.route('/me', methods=['PUT'])
@token_required
def update_profile():
    """Update current user profile"""
    data = request.get_json()
    user = g.current_user

    # Update profile
    updated_user, error = AuthService.update_user_profile(
        user.id,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone=data.get('phone')
    )

    if error:
        return jsonify(error), 400

    return jsonify({
        'message': 'Profile updated successfully',
        'user': updated_user.to_dict()
    }), 200


@bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password"""
    data = request.get_json()
    user = g.current_user

    # Validate required fields
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current and new passwords are required'}), 400

    # Change password
    success, error = AuthService.change_password(
        user.id,
        data['current_password'],
        data['new_password']
    )

    if not success:
        return jsonify(error), 400

    return jsonify({
        'message': 'Password changed successfully'
    }), 200


@bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """Logout user (client-side token removal)"""
    # In a JWT stateless system, logout is handled client-side
    # Optionally, implement token blacklist here

    return jsonify({
        'message': 'Logged out successfully'
    }), 200
