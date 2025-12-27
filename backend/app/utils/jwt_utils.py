from datetime import datetime, timedelta
from jose import JWTError, jwt
from flask import current_app


def create_access_token(user_id: str, role: str) -> str:
    """
    Create JWT access token

    Args:
        user_id: User ID
        role: User role (customer/admin)

    Returns:
        JWT token string
    """
    expires = datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']

    payload = {
        'user_id': user_id,
        'role': role,
        'type': 'access',
        'exp': expires,
        'iat': datetime.utcnow()
    }

    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

    return token


def create_refresh_token(user_id: str) -> str:
    """
    Create JWT refresh token

    Args:
        user_id: User ID

    Returns:
        JWT refresh token string
    """
    expires = datetime.utcnow() + current_app.config['JWT_REFRESH_TOKEN_EXPIRES']

    payload = {
        'user_id': user_id,
        'type': 'refresh',
        'exp': expires,
        'iat': datetime.utcnow()
    }

    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

    return token


def verify_token(token: str, token_type: str = 'access') -> dict:
    """
    Verify and decode JWT token

    Args:
        token: JWT token string
        token_type: 'access' or 'refresh'

    Returns:
        Decoded token payload

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )

        # Verify token type
        if payload.get('type') != token_type:
            raise JWTError('Invalid token type')

        return payload

    except JWTError as e:
        raise JWTError(f'Token verification failed: {str(e)}')


def decode_token(token: str) -> dict:
    """
    Decode JWT token without verification (for debugging)

    Args:
        token: JWT token string

    Returns:
        Decoded token payload
    """
    try:
        return jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256'],
            options={'verify_exp': False}
        )
    except JWTError:
        return {}


def get_token_expiry(token: str) -> datetime:
    """
    Get token expiration datetime

    Args:
        token: JWT token string

    Returns:
        Expiration datetime
    """
    try:
        payload = decode_token(token)
        exp_timestamp = payload.get('exp')
        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp)
        return None
    except:
        return None
