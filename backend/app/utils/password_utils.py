import re
from passlib.hash import bcrypt


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return bcrypt.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify password against hash

    Args:
        password: Plain text password
        hashed_password: Hashed password to verify against

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.verify(password, hashed_password)
    except:
        return False


def validate_password_strength(password: str) -> tuple[bool, list]:
    """
    Validate password meets security requirements

    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    if len(password) < 8:
        errors.append('Password must be at least 8 characters long')

    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')

    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')

    if not re.search(r'\d', password):
        errors.append('Password must contain at least one digit')

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character')

    return (len(errors) == 0, errors)


def generate_password_reset_token() -> str:
    """
    Generate a random password reset token

    Returns:
        Random token string
    """
    import secrets
    return secrets.token_urlsafe(32)
