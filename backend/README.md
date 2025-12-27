# Cookie Shop Backend

Flask Python backend for the Cookie Shop e-commerce platform.

## Tech Stack

- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **Flask-Migrate** - Database migrations
- **JWT** - Authentication
- **Stripe** - Payment processing
- **Bcrypt** - Password hashing

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env.development
```

Edit `.env.development` with your configuration:
- Database URL
- Secret keys
- Stripe keys

4. Initialize database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Seed database (optional):
```bash
python scripts/seed_database.py
```

### Running the Application

Development server:
```bash
python app.py
```

Or using Flask CLI:
```bash
flask run
```

API will be available at: http://localhost:5000

### API Documentation

Base URL: `http://localhost:5000/api/v1`

#### Endpoints:

**Authentication:**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user

**Products:**
- `GET /products` - List products
- `GET /products/:id` - Get product details
- `GET /products/featured` - Get featured products

**Cart:**
- `GET /cart` - Get user's cart
- `POST /cart/items` - Add item to cart
- `PUT /cart/items/:id` - Update cart item
- `DELETE /cart/items/:id` - Remove cart item

**Orders:**
- `GET /orders` - List user's orders
- `POST /orders` - Create order
- `GET /orders/:id` - Get order details

**Payments:**
- `POST /payments/create-intent` - Create Stripe payment intent
- `POST /payments/confirm` - Confirm payment
- `POST /payments/webhook` - Stripe webhook

**Admin:**
- `GET /admin/dashboard` - Dashboard stats
- `POST /admin/products` - Create product
- `PUT /admin/products/:id` - Update product
- `GET /admin/orders` - List all orders

See `docs/API.md` for full documentation.

### Database Migrations

Create new migration:
```bash
flask db migrate -m "Description"
```

Apply migrations:
```bash
flask db upgrade
```

Rollback migration:
```bash
flask db downgrade
```

### Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=app tests/
```

### Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # Database models
│   ├── api/                 # API endpoints
│   ├── services/            # Business logic
│   ├── middleware/          # Custom middleware
│   ├── utils/               # Utilities
│   ├── config/              # Configuration
│   └── database/            # Database setup
├── migrations/              # Database migrations
├── tests/                   # Tests
├── scripts/                 # Utility scripts
├── static/                  # Static files
├── requirements.txt         # Dependencies
└── app.py                   # Entry point
```

### Environment Variables

Required variables in `.env`:

```
# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# CORS
CORS_ORIGINS=http://localhost:5173
```

### Common Commands

```bash
# Create admin user
python scripts/create_admin.py

# Seed database
python scripts/seed_database.py

# Backup database
python scripts/backup_db.py

# Run development server
python app.py

# Run production server
gunicorn wsgi:app
```
