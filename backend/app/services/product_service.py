from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from sqlalchemy import or_, and_
from werkzeug.datastructures import FileStorage
from app.database.db import db
from app.models.product import Product
from app.models.category import Category
from app.utils.file_upload import save_product_image, delete_product_image, save_multiple_images
from app.utils.validators import is_valid_price, sanitize_input


class ProductService:
    """Product management service for admin operations"""

    @staticmethod
    def create_product(
        name: str,
        price: float,
        description: str = None,
        category_id: str = None,
        stock_quantity: int = 0,
        low_stock_threshold: int = 10,
        sku: str = None,
        image_file: FileStorage = None,
        additional_images: list = None,
        ingredients: list = None,
        allergens: list = None,
        is_featured: bool = False,
        is_active: bool = True
    ) -> Tuple[Optional[Product], Optional[Dict[str, Any]]]:
        """
        Create a new product

        Args:
            name: Product name
            price: Product price
            description: Product description
            category_id: Category ID
            stock_quantity: Initial stock quantity
            low_stock_threshold: Low stock alert threshold
            sku: Stock Keeping Unit
            image_file: Main product image file
            additional_images: List of additional image files
            ingredients: List of ingredients
            allergens: List of allergens
            is_featured: Whether product is featured
            is_active: Whether product is active

        Returns:
            Tuple of (product, error_dict)
        """
        # Validate required fields
        if not name or not price:
            return None, {'error': 'Name and price are required'}

        # Validate price
        if not is_valid_price(price):
            return None, {'error': 'Invalid price. Must be between 0 and 999,999'}

        # Sanitize inputs
        name = sanitize_input(name, max_length=255)
        description = sanitize_input(description, max_length=2000) if description else None
        sku = sanitize_input(sku, max_length=100) if sku else None

        # Generate slug from name
        slug = name.lower().replace(' ', '-').replace('/', '-')

        # Check if slug already exists
        existing_product = Product.query.filter_by(slug=slug).first()
        if existing_product:
            # Append random string to make it unique
            import random
            import string
            slug = f"{slug}-{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"

        # Check if SKU already exists
        if sku:
            existing_sku = Product.query.filter_by(sku=sku).first()
            if existing_sku:
                return None, {'error': f'SKU {sku} already exists'}

        # Validate category if provided
        if category_id:
            category = Category.query.get(category_id)
            if not category:
                return None, {'error': 'Invalid category'}

        try:
            # Create product
            product = Product(
                name=name,
                slug=slug,
                price=price,
                description=description,
                category_id=category_id,
                stock_quantity=stock_quantity,
                low_stock_threshold=low_stock_threshold,
                sku=sku,
                is_featured=is_featured,
                is_active=is_active
            )

            # Handle main image upload
            if image_file:
                image_path, error = save_product_image(image_file)
                if error:
                    return None, {'error': f'Image upload failed: {error}'}
                product.image_url = image_path

            # Handle additional images
            if additional_images and len(additional_images) > 0:
                saved_paths, errors = save_multiple_images(additional_images)
                if saved_paths:
                    product.images = saved_paths

            # Set ingredients and allergens
            if ingredients:
                product.ingredients = ingredients
            if allergens:
                product.allergens = allergens

            # Save to database
            db.session.add(product)
            db.session.commit()

            return product, None

        except Exception as e:
            db.session.rollback()
            return None, {'error': f'Failed to create product: {str(e)}'}

    @staticmethod
    def update_product(
        product_id: str,
        name: str = None,
        price: float = None,
        description: str = None,
        category_id: str = None,
        stock_quantity: int = None,
        low_stock_threshold: int = None,
        sku: str = None,
        image_file: FileStorage = None,
        additional_images: list = None,
        ingredients: list = None,
        allergens: list = None,
        is_featured: bool = None,
        is_active: bool = None
    ) -> Tuple[Optional[Product], Optional[Dict[str, Any]]]:
        """
        Update an existing product

        Args:
            product_id: Product ID
            (other args same as create_product)

        Returns:
            Tuple of (product, error_dict)
        """
        product = Product.query.get(product_id)

        if not product:
            return None, {'error': 'Product not found'}

        try:
            # Update fields if provided
            if name is not None:
                product.name = sanitize_input(name, max_length=255)
                # Update slug
                product.slug = name.lower().replace(' ', '-').replace('/', '-')

            if price is not None:
                if not is_valid_price(price):
                    return None, {'error': 'Invalid price'}
                product.price = price

            if description is not None:
                product.description = sanitize_input(description, max_length=2000)

            if category_id is not None:
                category = Category.query.get(category_id)
                if not category:
                    return None, {'error': 'Invalid category'}
                product.category_id = category_id

            if stock_quantity is not None:
                product.stock_quantity = stock_quantity

            if low_stock_threshold is not None:
                product.low_stock_threshold = low_stock_threshold

            if sku is not None:
                # Check if SKU already exists for another product
                existing_sku = Product.query.filter(
                    and_(Product.sku == sku, Product.id != product_id)
                ).first()
                if existing_sku:
                    return None, {'error': f'SKU {sku} already exists'}
                product.sku = sanitize_input(sku, max_length=100)

            if is_featured is not None:
                product.is_featured = is_featured

            if is_active is not None:
                product.is_active = is_active

            # Handle main image update
            if image_file:
                # Delete old image if exists
                if product.image_url:
                    delete_product_image(product.image_url)

                # Upload new image
                image_path, error = save_product_image(image_file, product_id)
                if error:
                    return None, {'error': f'Image upload failed: {error}'}
                product.image_url = image_path

            # Handle additional images
            if additional_images and len(additional_images) > 0:
                saved_paths, errors = save_multiple_images(additional_images, product_id)
                if saved_paths:
                    # Append to existing images or create new list
                    current_images = product.images or []
                    product.images = current_images + saved_paths

            # Update ingredients and allergens
            if ingredients is not None:
                product.ingredients = ingredients

            if allergens is not None:
                product.allergens = allergens

            product.updated_at = datetime.utcnow()
            db.session.commit()

            return product, None

        except Exception as e:
            db.session.rollback()
            return None, {'error': f'Failed to update product: {str(e)}'}

    @staticmethod
    def update_stock(product_id: str, quantity: int) -> Tuple[Optional[Product], Optional[Dict[str, Any]]]:
        """
        Update product stock quantity

        Args:
            product_id: Product ID
            quantity: New stock quantity

        Returns:
            Tuple of (product, error_dict)
        """
        product = Product.query.get(product_id)

        if not product:
            return None, {'error': 'Product not found'}

        if quantity < 0:
            return None, {'error': 'Stock quantity cannot be negative'}

        try:
            product.stock_quantity = quantity
            product.updated_at = datetime.utcnow()
            db.session.commit()

            return product, None

        except Exception as e:
            db.session.rollback()
            return None, {'error': f'Failed to update stock: {str(e)}'}

    @staticmethod
    def delete_product(product_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Delete a product (soft delete by setting is_active to False)

        Args:
            product_id: Product ID

        Returns:
            Tuple of (success, error_dict)
        """
        product = Product.query.get(product_id)

        if not product:
            return False, {'error': 'Product not found'}

        try:
            # Soft delete - just set is_active to False
            product.is_active = False
            product.updated_at = datetime.utcnow()
            db.session.commit()

            return True, None

        except Exception as e:
            db.session.rollback()
            return False, {'error': f'Failed to delete product: {str(e)}'}

    @staticmethod
    def hard_delete_product(product_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Permanently delete a product and its images

        Args:
            product_id: Product ID

        Returns:
            Tuple of (success, error_dict)
        """
        product = Product.query.get(product_id)

        if not product:
            return False, {'error': 'Product not found'}

        try:
            # Delete images
            if product.image_url:
                delete_product_image(product.image_url)

            if product.images:
                for image_path in product.images:
                    delete_product_image(image_path)

            # Delete from database
            db.session.delete(product)
            db.session.commit()

            return True, None

        except Exception as e:
            db.session.rollback()
            return False, {'error': f'Failed to delete product: {str(e)}'}

    @staticmethod
    def get_product(product_id: str) -> Optional[Product]:
        """Get product by ID"""
        return Product.query.get(product_id)

    @staticmethod
    def get_product_by_slug(slug: str) -> Optional[Product]:
        """Get product by slug"""
        return Product.query.filter_by(slug=slug).first()

    @staticmethod
    def get_all_products(
        page: int = 1,
        per_page: int = 20,
        category_id: str = None,
        search: str = None,
        in_stock_only: bool = False,
        is_active: bool = True,
        is_featured: bool = None,
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ) -> Dict[str, Any]:
        """
        Get paginated list of products with filters

        Args:
            page: Page number
            per_page: Items per page
            category_id: Filter by category
            search: Search term for name/description
            in_stock_only: Only show products in stock
            is_active: Filter by active status
            is_featured: Filter by featured status
            sort_by: Field to sort by
            sort_order: 'asc' or 'desc'

        Returns:
            Dict with products, pagination info
        """
        query = Product.query

        # Apply filters
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)

        if category_id:
            query = query.filter(Product.category_id == category_id)

        if in_stock_only:
            query = query.filter(Product.stock_quantity > 0)

        if is_featured is not None:
            query = query.filter(Product.is_featured == is_featured)

        if search:
            search_term = f'%{search}%'
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.sku.ilike(search_term)
                )
            )

        # Apply sorting
        if sort_by and hasattr(Product, sort_by):
            order_column = getattr(Product, sort_by)
            if sort_order == 'desc':
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())

        # Paginate
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return {
            'products': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }

    @staticmethod
    def get_low_stock_products(threshold: int = None) -> list:
        """
        Get products with low stock

        Args:
            threshold: Stock threshold (uses product's low_stock_threshold if not provided)

        Returns:
            List of products with low stock
        """
        if threshold:
            products = Product.query.filter(
                and_(
                    Product.stock_quantity > 0,
                    Product.stock_quantity <= threshold,
                    Product.is_active == True
                )
            ).all()
        else:
            # Use each product's own threshold
            products = Product.query.filter(
                and_(
                    Product.stock_quantity > 0,
                    Product.is_active == True
                )
            ).all()

            products = [p for p in products if p.is_low_stock]

        return products

    @staticmethod
    def reduce_stock(product_id: str, quantity: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Reduce product stock (used during order creation)

        Args:
            product_id: Product ID
            quantity: Quantity to reduce

        Returns:
            Tuple of (success, error_dict)
        """
        product = Product.query.get(product_id)

        if not product:
            return False, {'error': 'Product not found'}

        if product.stock_quantity < quantity:
            return False, {'error': f'Insufficient stock. Available: {product.stock_quantity}'}

        try:
            product.stock_quantity -= quantity
            product.updated_at = datetime.utcnow()
            db.session.commit()

            return True, None

        except Exception as e:
            db.session.rollback()
            return False, {'error': f'Failed to reduce stock: {str(e)}'}
