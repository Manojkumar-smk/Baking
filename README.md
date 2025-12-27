# Online Cookie Sales Website

A full-stack e-commerce platform for selling cookies online, built with modern web technologies.

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: Python + Flask + SQLAlchemy
- **Database**: PostgreSQL
- **Payment**: Stripe
- **Authentication**: JWT (JSON Web Tokens)
- **State Management**: React Context API
- **Styling**: CSS Modules

## Features

### Customer Features
- Browse products with images, prices, and stock status
- Search and filter products by category
- Add products to shopping cart (in-stock items only)
- Secure checkout with Stripe payment integration
- User authentication and profile management
- Order history and tracking

### Admin Features
- Product management with image upload
- Stock quantity control and inventory management
- In stock/Out of stock status management
- Order processing and fulfillment
- Dashboard with sales analytics
- User management

## Project Structure

This project follows the **AI_FullStack_Development_Kit** pattern:

```
Baking/
├── .claude/          # Claude Code configuration
├── PRPs/             # Prompts, Requests, and Patterns
├── agents/           # AI agent configurations
├── skills/           # Reusable development skills
├── examples/         # Sample data and configurations
├── frontend/         # React TypeScript application
├── backend/          # Flask Python API
├── database/         # Database schemas and seeds
├── docs/             # Documentation
├── docker/           # Docker configurations
└── scripts/          # Automation scripts
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Git

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
python scripts/seed_database.py
flask run
```

Backend runs on: http://localhost:5000

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:5173

### Database Setup

```bash
# Using Docker
docker-compose up -d postgres

# Or create manually
createdb cookie_shop
```

## Environment Variables

Copy `.env.example` files to `.env.development` in both frontend and backend directories and configure:

**Backend (.env.development)**:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/cookie_shop
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
STRIPE_SECRET_KEY=sk_test_...
FRONTEND_URL=http://localhost:5173
```

**Frontend (.env.development)**:
```
VITE_API_URL=http://localhost:5000/api/v1
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## Development Workflow

1. Create admin user via seed script
2. Login as admin
3. Add product categories and products with images
4. Test customer flow: browse → cart → checkout
5. Test admin features: manage products, process orders

## Documentation

- [API Documentation](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Architecture Overview](docs/ARCHITECTURE.md)

## Security

- JWT authentication with short-lived tokens
- Password hashing with bcrypt
- CORS configuration
- Input validation
- SQL injection prevention (SQLAlchemy ORM)
- Secure file uploads
- Admin-only routes protection
- Stripe webhook signature verification

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment instructions using Docker and Docker Compose.

## License

[MIT License](LICENSE)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Claude Code Integration

This project is optimized for development with Claude Code CLI. See [CLAUDE.md](CLAUDE.md) for details on using AI-assisted development features.

---

Generated with Claude Code - AI-powered full-stack development
