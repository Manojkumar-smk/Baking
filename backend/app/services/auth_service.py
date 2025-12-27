from datetime import datetime
from app.database.db import db
from app.models.user import User
from app.utils.jwt_utils import create_access_token, create_refresh_token, verify_token
from app.utils.password_utils import hash_password, validate_password_strength
from app.utils.validators import is_valid_email
from jose import JWTError


class AuthService:
    """Authentication service for user registration and login"""

    @staticmethod
    def register_user(email: str, password: str, first_name: str, last_name: str, phone: str = None) -> tuple:
        """
        Register a new user

        Args:
            email: User email
            password: User password
            first_name: User first name
            last_name: User last name
            phone: User phone (optional)

        Returns:
            Tuple of (user, access_token, refresh_token) or (None, None, None) with error
        """
        # Validate email
        if not is_valid_email(email):
            return None, None, {'error': 'Invalid email address'}

        # Check if user already exists
        existing_user = User.query.filter_by(email=email.lower()).first()
        if existing_user:
            return None, None, {'error': 'Email already registered'}

        # Validate password strength
        is_strong, errors = validate_password_strength(password)
        if not is_strong:
            return None, None, {'error': 'Weak password', 'details': errors}

        try:
            # Create new user
            user = User(
                email=email.lower(),
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            user.set_password(password)

            # Save to database
            db.session.add(user)
            db.session.commit()

            # Generate tokens
            access_token = create_access_token(user.id, user.role)
            refresh_token = create_refresh_token(user.id)

            return user, access_token, refresh_token

        except Exception as e:
            db.session.rollback()
            return None, None, {'error': f'Registration failed: {str(e)}'}

    @staticmethod
    def login_user(email: str, password: str) -> tuple:
        """
        Authenticate user and generate tokens

        Args:
            email: User email
            password: User password

        Returns:
            Tuple of (user, access_token, refresh_token) or (None, None, None) with error
        """
        # Find user
        user = User.query.filter_by(email=email.lower()).first()

        if not user:
            return None, None, {'error': 'Invalid email or password'}

        # Check if user is active
        if not user.is_active:
            return None, None, {'error': 'Account is deactivated'}

        # Verify password
        if not user.check_password(password):
            return None, None, {'error': 'Invalid email or password'}

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Generate tokens
        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token(user.id)

        return user, access_token, refresh_token

    @staticmethod
    def refresh_access_token(refresh_token: str) -> tuple:
        """
        Generate new access token from refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            Tuple of (access_token, new_refresh_token) or (None, None) with error
        """
        try:
            # Verify refresh token
            payload = verify_token(refresh_token, 'refresh')
            user_id = payload.get('user_id')

            # Get user
            user = User.query.get(user_id)

            if not user or not user.is_active:
                return None, None, {'error': 'User not found or inactive'}

            # Generate new tokens
            new_access_token = create_access_token(user.id, user.role)
            new_refresh_token = create_refresh_token(user.id)

            return new_access_token, new_refresh_token

        except JWTError as e:
            return None, None, {'error': f'Invalid refresh token: {str(e)}'}
        except Exception as e:
            return None, None, {'error': f'Token refresh failed: {str(e)}'}

    @staticmethod
    def get_user_by_id(user_id: str):
        """Get user by ID"""
        return User.query.get(user_id)

    @staticmethod
    def update_user_profile(user_id: str, **kwargs):
        """
        Update user profile

        Args:
            user_id: User ID
            **kwargs: Fields to update

        Returns:
            Updated user or None with error
        """
        user = User.query.get(user_id)

        if not user:
            return None, {'error': 'User not found'}

        try:
            # Update allowed fields
            allowed_fields = ['first_name', 'last_name', 'phone']

            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    setattr(user, field, value)

            user.updated_at = datetime.utcnow()
            db.session.commit()

            return user, None

        except Exception as e:
            db.session.rollback()
            return None, {'error': f'Profile update failed: {str(e)}'}

    @staticmethod
    def change_password(user_id: str, current_password: str, new_password: str):
        """
        Change user password

        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password

        Returns:
            Success boolean and error dict if any
        """
        user = User.query.get(user_id)

        if not user:
            return False, {'error': 'User not found'}

        # Verify current password
        if not user.check_password(current_password):
            return False, {'error': 'Current password is incorrect'}

        # Validate new password
        is_strong, errors = validate_password_strength(new_password)
        if not is_strong:
            return False, {'error': 'Weak password', 'details': errors}

        try:
            user.set_password(new_password)
            user.updated_at = datetime.utcnow()
            db.session.commit()

            return True, None

        except Exception as e:
            db.session.rollback()
            return False, {'error': f'Password change failed: {str(e)}'}
