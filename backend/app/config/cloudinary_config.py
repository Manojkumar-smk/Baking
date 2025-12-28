"""
Cloudinary configuration for image upload and management
"""
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv

load_dotenv()


def configure_cloudinary():
    """
    Configure Cloudinary with credentials from environment variables
    """
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET'),
        secure=True
    )


def get_cloudinary_config():
    """
    Get current Cloudinary configuration status
    """
    config = cloudinary.config()
    return {
        'cloud_name': config.cloud_name,
        'api_key': config.api_key[:4] + '****' if config.api_key else None,
        'configured': bool(config.cloud_name and config.api_key and config.api_secret)
    }


# Configure Cloudinary when module is imported
configure_cloudinary()
