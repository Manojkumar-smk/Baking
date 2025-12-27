import re
from email_validator import validate_email, EmailNotValidError


def is_valid_email(email: str) -> bool:
    """
    Validate email address format

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def is_valid_phone(phone: str) -> bool:
    """
    Validate phone number format

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)

    # Check if it's 10 digits (US) or has country code
    if re.match(r'^\+?1?\d{10,}$', cleaned):
        return True

    return False


def is_valid_postal_code(postal_code: str, country: str = 'USA') -> bool:
    """
    Validate postal code format

    Args:
        postal_code: Postal code to validate
        country: Country code

    Returns:
        True if valid, False otherwise
    """
    if country == 'USA':
        # US ZIP code: 12345 or 12345-6789
        return bool(re.match(r'^\d{5}(-\d{4})?$', postal_code))

    # Add more country validations as needed
    return len(postal_code) > 0


def sanitize_input(text: str, max_length: int = None) -> str:
    """
    Sanitize user input

    Args:
        text: Text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ''

    # Remove leading/trailing whitespace
    text = text.strip()

    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text


def is_valid_price(price: float) -> bool:
    """
    Validate price value

    Args:
        price: Price to validate

    Returns:
        True if valid, False otherwise
    """
    return price > 0 and price < 1000000  # Maximum $999,999.99


def is_valid_quantity(quantity: int) -> bool:
    """
    Validate quantity value

    Args:
        quantity: Quantity to validate

    Returns:
        True if valid, False otherwise
    """
    return quantity > 0 and quantity <= 10000  # Maximum 10,000 units
