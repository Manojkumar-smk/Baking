#!/usr/bin/env python3
"""
Seed script to populate database with demo data for local testing
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database.db import db
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from passlib.hash import bcrypt


def clear_data():
    """Clear existing data"""
    print("Clearing existing data...")

    # Order matters due to foreign keys
    OrderItem.query.delete()
    Payment.query.delete()
    Order.query.delete()
    CartItem.query.delete()
    Cart.query.delete()
    Product.query.delete()
    Category.query.delete()
    User.query.delete()

    db.session.commit()
    print("✓ Data cleared")


def seed_users():
    """Create demo users"""
    print("\nCreating demo users...")

    users = [
        {
            'email': 'admin@cookieshop.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_active': True
        },
        {
            'email': 'customer@example.com',
            'password': 'customer123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'customer',
            'is_active': True
        },
        {
            'email': 'jane@example.com',
            'password': 'jane123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'customer',
            'is_active': True
        }
    ]

    created_users = {}
    for user_data in users:
        user = User(
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'],
            is_active=user_data['is_active']
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        created_users[user_data['email']] = user
        print(f"  ✓ Created {user_data['role']}: {user_data['email']} (password: {user_data['password']})")

    db.session.commit()
    print(f"✓ Created {len(users)} users")
    return created_users


def seed_categories():
    """Create product categories"""
    print("\nCreating categories...")

    categories_data = [
        {'name': 'Chocolate Chip', 'description': 'Classic chocolate chip cookies'},
        {'name': 'Sugar Cookies', 'description': 'Sweet and simple sugar cookies'},
        {'name': 'Oatmeal', 'description': 'Hearty oatmeal cookies'},
        {'name': 'Special', 'description': 'Specialty and seasonal cookies'},
    ]

    categories = {}
    for cat_data in categories_data:
        category = Category(
            name=cat_data['name'],
            description=cat_data['description']
        )
        db.session.add(category)
        categories[cat_data['name']] = category
        print(f"  ✓ Created category: {cat_data['name']}")

    db.session.commit()
    print(f"✓ Created {len(categories_data)} categories")
    return categories


def seed_products(categories):
    """Create demo products"""
    print("\nCreating products...")

    products_data = [
        {
            'name': 'Classic Chocolate Chip',
            'description': 'Traditional chocolate chip cookies made with premium chocolate chips',
            'price': 12.99,
            'category': 'Chocolate Chip',
            'stock_quantity': 100,
            'sku': 'CCC-001',
            'is_featured': True,
            'is_active': True,
            'ingredients': ['Flour', 'Butter', 'Sugar', 'Chocolate Chips', 'Eggs', 'Vanilla'],
            'allergens': ['Wheat', 'Eggs', 'Dairy']
        },
        {
            'name': 'Double Chocolate Delight',
            'description': 'Rich chocolate cookies with extra chocolate chips',
            'price': 14.99,
            'category': 'Chocolate Chip',
            'stock_quantity': 75,
            'sku': 'DCD-001',
            'is_featured': True,
            'is_active': True,
            'ingredients': ['Flour', 'Cocoa', 'Butter', 'Sugar', 'Chocolate Chips', 'Eggs'],
            'allergens': ['Wheat', 'Eggs', 'Dairy']
        },
        {
            'name': 'Vanilla Sugar Cookies',
            'description': 'Sweet vanilla sugar cookies perfect for any occasion',
            'price': 10.99,
            'category': 'Sugar Cookies',
            'stock_quantity': 120,
            'sku': 'VSC-001',
            'is_featured': False,
            'is_active': True,
            'ingredients': ['Flour', 'Butter', 'Sugar', 'Eggs', 'Vanilla', 'Baking Powder'],
            'allergens': ['Wheat', 'Eggs', 'Dairy']
        },
        {
            'name': 'Lemon Sugar Cookies',
            'description': 'Refreshing lemon-flavored sugar cookies',
            'price': 11.99,
            'category': 'Sugar Cookies',
            'stock_quantity': 90,
            'sku': 'LSC-001',
            'is_featured': False,
            'is_active': True,
            'ingredients': ['Flour', 'Butter', 'Sugar', 'Eggs', 'Lemon Zest', 'Lemon Juice'],
            'allergens': ['Wheat', 'Eggs', 'Dairy']
        },
        {
            'name': 'Oatmeal Raisin',
            'description': 'Hearty oatmeal cookies with sweet raisins',
            'price': 11.99,
            'category': 'Oatmeal',
            'stock_quantity': 80,
            'sku': 'OAT-001',
            'is_featured': True,
            'is_active': True,
            'ingredients': ['Oats', 'Flour', 'Butter', 'Sugar', 'Raisins', 'Eggs', 'Cinnamon'],
            'allergens': ['Wheat', 'Eggs', 'Dairy']
        },
        {
            'name': 'Oatmeal Chocolate Chip',
            'description': 'Best of both worlds - oatmeal with chocolate chips',
            'price': 13.99,
            'category': 'Oatmeal',
            'stock_quantity': 60,
            'sku': 'OCC-001',
            'is_featured': False,
            'is_active': True,
            'ingredients': ['Oats', 'Flour', 'Butter', 'Sugar', 'Chocolate Chips', 'Eggs'],
            'allergens': ['Wheat', 'Eggs', 'Dairy']
        },
        {
            'name': 'Peanut Butter Cookies',
            'description': 'Creamy peanut butter cookies',
            'price': 12.99,
            'category': 'Special',
            'stock_quantity': 70,
            'sku': 'PBC-001',
            'is_featured': False,
            'is_active': True,
            'ingredients': ['Flour', 'Peanut Butter', 'Sugar', 'Eggs', 'Butter'],
            'allergens': ['Wheat', 'Eggs', 'Dairy', 'Peanuts']
        },
        {
            'name': 'Snickerdoodle',
            'description': 'Classic cinnamon sugar cookies',
            'price': 11.99,
            'category': 'Special',
            'stock_quantity': 85,
            'sku': 'SNI-001',
            'is_featured': True,
            'is_active': True,
            'ingredients': ['Flour', 'Butter', 'Sugar', 'Eggs', 'Cinnamon', 'Cream of Tartar'],
            'allergens': ['Wheat', 'Eggs', 'Dairy']
        },
        {
            'name': 'Low Stock Item',
            'description': 'This product has low stock for testing',
            'price': 9.99,
            'category': 'Special',
            'stock_quantity': 5,
            'sku': 'LOW-001',
            'low_stock_threshold': 10,
            'is_featured': False,
            'is_active': True,
            'ingredients': ['Flour', 'Sugar', 'Butter'],
            'allergens': ['Wheat', 'Dairy']
        },
        {
            'name': 'Out of Stock Item',
            'description': 'This product is out of stock for testing',
            'price': 9.99,
            'category': 'Special',
            'stock_quantity': 0,
            'sku': 'OUT-001',
            'is_featured': False,
            'is_active': True,
            'ingredients': ['Flour', 'Sugar', 'Butter'],
            'allergens': ['Wheat', 'Dairy']
        }
    ]

    products = []
    for prod_data in products_data:
        category = categories.get(prod_data['category'])
        product = Product(
            name=prod_data['name'],
            description=prod_data['description'],
            price=Decimal(str(prod_data['price'])),
            category_id=category.id if category else None,
            stock_quantity=prod_data['stock_quantity'],
            low_stock_threshold=prod_data.get('low_stock_threshold', 10),
            sku=prod_data['sku'],
            is_featured=prod_data['is_featured'],
            is_active=prod_data['is_active'],
            ingredients=prod_data.get('ingredients', []),
            allergens=prod_data.get('allergens', [])
        )
        db.session.add(product)
        products.append(product)
        print(f"  ✓ Created product: {prod_data['name']} (${prod_data['price']}, Stock: {prod_data['stock_quantity']})")

    db.session.commit()
    print(f"✓ Created {len(products_data)} products")
    return products


def seed_orders(users, products):
    """Create demo orders"""
    print("\nCreating demo orders...")

    customer = users.get('customer@example.com')
    jane = users.get('jane@example.com')

    if not customer or not products:
        print("  ⚠ Skipping orders - missing users or products")
        return []

    orders_data = [
        {
            'user': customer,
            'customer_email': customer.email,
            'customer_first_name': customer.first_name,
            'customer_last_name': customer.last_name,
            'status': 'delivered',
            'payment_status': 'paid',
            'shipping_address': {
                'full_name': f'{customer.first_name} {customer.last_name}',
                'street_address': '123 Main St',
                'city': 'San Francisco',
                'state': 'CA',
                'postal_code': '94102',
                'country': 'US',
                'phone': '555-0101'
            },
            'items': [
                {'product': products[0], 'quantity': 2},
                {'product': products[1], 'quantity': 1}
            ],
            'days_ago': 10,
            'tracking_number': 'TRACK123456789'
        },
        {
            'user': customer,
            'customer_email': customer.email,
            'customer_first_name': customer.first_name,
            'customer_last_name': customer.last_name,
            'status': 'shipped',
            'payment_status': 'paid',
            'shipping_address': {
                'full_name': f'{customer.first_name} {customer.last_name}',
                'street_address': '123 Main St',
                'city': 'San Francisco',
                'state': 'CA',
                'postal_code': '94102',
                'country': 'US',
                'phone': '555-0101'
            },
            'items': [
                {'product': products[2], 'quantity': 3}
            ],
            'days_ago': 3,
            'tracking_number': 'TRACK987654321'
        },
        {
            'user': jane,
            'customer_email': jane.email,
            'customer_first_name': jane.first_name,
            'customer_last_name': jane.last_name,
            'status': 'processing',
            'payment_status': 'paid',
            'shipping_address': {
                'full_name': f'{jane.first_name} {jane.last_name}',
                'street_address': '456 Oak Ave',
                'city': 'Los Angeles',
                'state': 'CA',
                'postal_code': '90001',
                'country': 'US',
                'phone': '555-0102'
            },
            'items': [
                {'product': products[4], 'quantity': 2},
                {'product': products[5], 'quantity': 2}
            ],
            'days_ago': 1
        },
        {
            'user': customer,
            'customer_email': customer.email,
            'customer_first_name': customer.first_name,
            'customer_last_name': customer.last_name,
            'status': 'pending',
            'payment_status': 'pending',
            'shipping_address': {
                'full_name': f'{customer.first_name} {customer.last_name}',
                'street_address': '123 Main St',
                'city': 'San Francisco',
                'state': 'CA',
                'postal_code': '94102',
                'country': 'US',
                'phone': '555-0101'
            },
            'items': [
                {'product': products[7], 'quantity': 1}
            ],
            'days_ago': 0
        }
    ]

    orders = []
    for order_data in orders_data:
        # Calculate order totals
        subtotal = sum(
            item['product'].price * item['quantity']
            for item in order_data['items']
        )
        tax_amount = subtotal * Decimal('0.10')
        shipping_amount = Decimal('0') if subtotal >= 50 else Decimal('5.99')
        total_amount = subtotal + tax_amount + shipping_amount

        # Create order
        order = Order(
            user_id=order_data['user'].id,
            customer_email=order_data['customer_email'],
            customer_first_name=order_data['customer_first_name'],
            customer_last_name=order_data['customer_last_name'],
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_amount=shipping_amount,
            discount_amount=Decimal('0'),
            total_amount=total_amount,
            status=order_data['status'],
            payment_status=order_data['payment_status'],
            fulfillment_status='fulfilled' if order_data['status'] in ['shipped', 'delivered'] else 'unfulfilled',
            shipping_address=order_data['shipping_address'],
            billing_address=order_data['shipping_address'],
            tracking_number=order_data.get('tracking_number'),
            created_at=datetime.utcnow() - timedelta(days=order_data['days_ago'])
        )

        # Set status-specific timestamps
        if order_data['status'] == 'delivered':
            order.paid_at = order.created_at + timedelta(hours=1)
            order.shipped_at = order.created_at + timedelta(days=2)
            order.delivered_at = order.created_at + timedelta(days=5)
        elif order_data['status'] == 'shipped':
            order.paid_at = order.created_at + timedelta(hours=1)
            order.shipped_at = order.created_at + timedelta(days=1)
        elif order_data['payment_status'] == 'paid':
            order.paid_at = order.created_at + timedelta(hours=1)

        db.session.add(order)
        db.session.flush()

        # Create order items
        for item_data in order_data['items']:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product'].id,
                product_name=item_data['product'].name,
                product_sku=item_data['product'].sku,
                product_image_url=item_data['product'].image_url,
                quantity=item_data['quantity'],
                unit_price=item_data['product'].price,
                total_price=item_data['product'].price * item_data['quantity']
            )
            db.session.add(order_item)

        # Create payment if paid
        if order_data['payment_status'] == 'paid':
            payment = Payment(
                order_id=order.id,
                amount=total_amount,
                currency='usd',
                status='succeeded',
                payment_method='card',
                stripe_payment_intent_id=f'pi_demo_{order.id}',
                created_at=order.paid_at or order.created_at
            )
            db.session.add(payment)

        orders.append(order)
        print(f"  ✓ Created order: {order.order_number} ({order_data['status']}, ${total_amount})")

    db.session.commit()
    print(f"✓ Created {len(orders)} orders")
    return orders


def main():
    """Main seeding function"""
    app = create_app()

    with app.app_context():
        print("=" * 60)
        print("SEEDING DEMO DATA FOR LOCAL TESTING")
        print("=" * 60)

        # Clear existing data
        response = input("\n⚠️  This will DELETE all existing data. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Seeding cancelled.")
            return

        clear_data()

        # Seed data
        users = seed_users()
        categories = seed_categories()
        products = seed_products(categories)
        orders = seed_orders(users, products)

        print("\n" + "=" * 60)
        print("✓ DEMO DATA SEEDED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📝 Demo Accounts:")
        print("-" * 60)
        print("Admin Account:")
        print("  Email: admin@cookieshop.com")
        print("  Password: admin123")
        print("\nCustomer Account:")
        print("  Email: customer@example.com")
        print("  Password: customer123")
        print("\nAnother Customer:")
        print("  Email: jane@example.com")
        print("  Password: jane123")
        print("-" * 60)
        print(f"\n📊 Summary:")
        print(f"  • {len(users)} users created")
        print(f"  • {len(categories)} categories created")
        print(f"  • {len(products)} products created")
        print(f"  • {len(orders)} orders created")
        print("\n💳 For Stripe testing, use test card:")
        print("  Card: 4242 4242 4242 4242")
        print("  Expiry: Any future date (e.g., 12/25)")
        print("  CVC: Any 3 digits (e.g., 123)")
        print("  ZIP: Any 5 digits (e.g., 12345)")
        print("\n🚀 You can now start testing!")
        print("=" * 60)


if __name__ == '__main__':
    main()
