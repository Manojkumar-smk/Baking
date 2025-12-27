import os
import uuid
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import current_app
from typing import Tuple, Optional


ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_MIME_TYPES = {
    'image/png',
    'image/jpeg',
    'image/gif',
    'image/webp'
}


def allowed_file(filename: str, allowed_extensions: set = ALLOWED_IMAGE_EXTENSIONS) -> bool:
    """
    Check if file has an allowed extension

    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions

    Returns:
        True if file extension is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_image_file(file: FileStorage) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded image file

    Args:
        file: Uploaded file from request

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file:
        return False, 'No file provided'

    if file.filename == '':
        return False, 'No file selected'

    # Check file extension
    if not allowed_file(file.filename):
        return False, f'File type not allowed. Allowed types: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'

    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False, f'Invalid file type. Must be an image.'

    # Check file size (max 5MB by default, can be configured)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer

    max_size = current_app.config.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024)  # 5MB
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        return False, f'File too large. Maximum size: {max_size_mb}MB'

    return True, None


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename using UUID

    Args:
        original_filename: Original filename from upload

    Returns:
        Unique filename with original extension
    """
    # Get file extension
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''

    # Generate unique filename
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    return unique_name


def save_product_image(file: FileStorage, product_id: str = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Save uploaded product image to disk

    Args:
        file: Uploaded file from request
        product_id: Optional product ID for organizing files

    Returns:
        Tuple of (file_path, error_message)
        file_path is the relative path to the saved file
    """
    # Validate file
    is_valid, error = validate_image_file(file)
    if not is_valid:
        return None, error

    # Secure the filename
    original_filename = secure_filename(file.filename)

    # Generate unique filename
    unique_filename = generate_unique_filename(original_filename)

    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(
        current_app.config.get('UPLOAD_FOLDER', 'static/uploads'),
        'products'
    )

    # Create full path
    full_upload_dir = os.path.join(current_app.root_path, upload_dir)
    os.makedirs(full_upload_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(full_upload_dir, unique_filename)
    try:
        file.save(file_path)
    except Exception as e:
        return None, f'Failed to save file: {str(e)}'

    # Return relative path for database storage
    relative_path = f'/static/uploads/products/{unique_filename}'

    return relative_path, None


def delete_product_image(image_path: str) -> bool:
    """
    Delete product image from disk

    Args:
        image_path: Relative path to the image (e.g., /static/uploads/products/image.jpg)

    Returns:
        True if deleted successfully, False otherwise
    """
    if not image_path:
        return False

    try:
        # Convert relative path to absolute path
        # Remove leading slash if present
        clean_path = image_path.lstrip('/')

        full_path = os.path.join(current_app.root_path, clean_path)

        if os.path.exists(full_path):
            os.remove(full_path)
            return True

        return False

    except Exception as e:
        current_app.logger.error(f'Failed to delete image {image_path}: {str(e)}')
        return False


def save_multiple_images(files: list, product_id: str = None) -> Tuple[list, list]:
    """
    Save multiple product images

    Args:
        files: List of FileStorage objects
        product_id: Optional product ID

    Returns:
        Tuple of (saved_paths, errors)
        saved_paths is a list of relative paths to saved files
        errors is a list of error messages
    """
    saved_paths = []
    errors = []

    for file in files:
        file_path, error = save_product_image(file, product_id)

        if file_path:
            saved_paths.append(file_path)
        else:
            errors.append(error)

    return saved_paths, errors


def delete_multiple_images(image_paths: list) -> int:
    """
    Delete multiple product images

    Args:
        image_paths: List of relative image paths

    Returns:
        Number of images successfully deleted
    """
    deleted_count = 0

    for image_path in image_paths:
        if delete_product_image(image_path):
            deleted_count += 1

    return deleted_count
