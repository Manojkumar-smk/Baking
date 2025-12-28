"""
Image upload and management service using Cloudinary
"""
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO
from typing import Dict, List, Optional
from flask import current_app


class ImageService:
    """Service for handling image uploads to Cloudinary"""

    # Allowed image extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Cloudinary folder for product images
    PRODUCT_FOLDER = 'cookie-shop/products'

    # Image transformation presets
    THUMBNAIL_PRESET = {'width': 300, 'height': 300, 'crop': 'fill', 'quality': 'auto:good'}
    MEDIUM_PRESET = {'width': 800, 'height': 800, 'crop': 'limit', 'quality': 'auto:best'}
    LARGE_PRESET = {'width': 1200, 'height': 1200, 'crop': 'limit', 'quality': 'auto:best'}

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """
        Check if file extension is allowed

        Args:
            filename: Name of the file

        Returns:
            True if extension is allowed, False otherwise
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ImageService.ALLOWED_EXTENSIONS

    @staticmethod
    def validate_image(file) -> tuple[bool, Optional[str]]:
        """
        Validate uploaded image file

        Args:
            file: File object from request

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file:
            return False, "No file provided"

        if not file.filename:
            return False, "No filename provided"

        if not ImageService.allowed_file(file.filename):
            return False, f"File type not allowed. Allowed types: {', '.join(ImageService.ALLOWED_EXTENSIONS)}"

        # Check file size (max 10MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            return False, f"File too large. Maximum size: {max_size / (1024 * 1024)}MB"

        # Validate it's actually an image
        try:
            img = Image.open(file)
            img.verify()
            file.seek(0)  # Reset file pointer after verification
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"

        return True, None

    @staticmethod
    def upload_product_image(file, product_id: str, transformation: Optional[Dict] = None) -> Dict:
        """
        Upload product image to Cloudinary

        Args:
            file: File object from request
            product_id: ID of the product
            transformation: Optional transformation parameters

        Returns:
            Dictionary with upload result containing URLs
        """
        try:
            # Validate image
            is_valid, error = ImageService.validate_image(file)
            if not is_valid:
                raise ValueError(error)

            # Generate unique public_id using product_id
            public_id = f"{ImageService.PRODUCT_FOLDER}/{product_id}"

            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                file,
                public_id=public_id,
                folder=ImageService.PRODUCT_FOLDER,
                overwrite=True,
                resource_type='image',
                transformation=transformation or ImageService.MEDIUM_PRESET,
                tags=['product', 'cookie-shop']
            )

            # Generate optimized URLs
            result = {
                'url': upload_result['secure_url'],
                'public_id': upload_result['public_id'],
                'thumbnail_url': cloudinary.CloudinaryImage(upload_result['public_id']).build_url(
                    **ImageService.THUMBNAIL_PRESET
                ),
                'medium_url': cloudinary.CloudinaryImage(upload_result['public_id']).build_url(
                    **ImageService.MEDIUM_PRESET
                ),
                'large_url': cloudinary.CloudinaryImage(upload_result['public_id']).build_url(
                    **ImageService.LARGE_PRESET
                ),
                'format': upload_result['format'],
                'width': upload_result['width'],
                'height': upload_result['height'],
                'bytes': upload_result['bytes']
            }

            current_app.logger.info(f"Image uploaded to Cloudinary: {public_id}")
            return result

        except Exception as e:
            current_app.logger.error(f"Error uploading image to Cloudinary: {str(e)}")
            raise

    @staticmethod
    def upload_multiple_product_images(files: List, product_id: str) -> List[Dict]:
        """
        Upload multiple product images to Cloudinary

        Args:
            files: List of file objects
            product_id: ID of the product

        Returns:
            List of dictionaries with upload results
        """
        results = []
        for idx, file in enumerate(files):
            try:
                public_id = f"{ImageService.PRODUCT_FOLDER}/{product_id}_{idx}"
                result = ImageService.upload_product_image(file, public_id)
                results.append(result)
            except Exception as e:
                current_app.logger.error(f"Error uploading image {idx}: {str(e)}")
                # Continue with other images
                continue

        return results

    @staticmethod
    def delete_product_image(public_id: str) -> bool:
        """
        Delete product image from Cloudinary

        Args:
            public_id: Cloudinary public_id of the image

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            success = result.get('result') == 'ok'

            if success:
                current_app.logger.info(f"Image deleted from Cloudinary: {public_id}")
            else:
                current_app.logger.warning(f"Failed to delete image: {public_id}")

            return success

        except Exception as e:
            current_app.logger.error(f"Error deleting image from Cloudinary: {str(e)}")
            return False

    @staticmethod
    def get_image_url(public_id: str, transformation: Optional[Dict] = None) -> str:
        """
        Get optimized image URL from Cloudinary

        Args:
            public_id: Cloudinary public_id of the image
            transformation: Optional transformation parameters

        Returns:
            Optimized image URL
        """
        try:
            return cloudinary.CloudinaryImage(public_id).build_url(
                **(transformation or ImageService.MEDIUM_PRESET)
            )
        except Exception as e:
            current_app.logger.error(f"Error generating image URL: {str(e)}")
            return None

    @staticmethod
    def extract_public_id_from_url(url: str) -> Optional[str]:
        """
        Extract public_id from Cloudinary URL

        Args:
            url: Cloudinary image URL

        Returns:
            Public ID or None if not a Cloudinary URL
        """
        try:
            if 'cloudinary.com' not in url:
                return None

            # Extract public_id from URL
            # Format: https://res.cloudinary.com/cloud_name/image/upload/v123456/folder/image.jpg
            parts = url.split('/')

            # Find 'upload' index
            upload_idx = parts.index('upload')

            # Skip version if present (starts with 'v')
            start_idx = upload_idx + 1
            if parts[start_idx].startswith('v'):
                start_idx += 1

            # Get everything after version until extension
            public_id_parts = parts[start_idx:]
            public_id = '/'.join(public_id_parts)

            # Remove extension
            public_id = public_id.rsplit('.', 1)[0]

            return public_id

        except Exception as e:
            current_app.logger.error(f"Error extracting public_id from URL: {str(e)}")
            return None
