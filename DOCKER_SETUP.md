# Docker Setup Guide

This guide explains how to run the Cookie Shop application using Docker and Docker Compose.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0 or higher
- At least 4GB of available RAM
- At least 10GB of available disk space

## Quick Start

1. **Configure Environment Variables**

   Copy the Docker environment files and update them with your settings:

   ```bash
   # Backend environment is already created at backend/.env.docker
   # Frontend environment is already created at frontend/.env.docker

   # Update Stripe keys in both files if you want to test payments
   ```

2. **Build and Start All Services**

   ```bash
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL database on port 5432
   - Backend API on port 5000
   - Frontend app on port 3000
   - Redis cache on port 6379

3. **Access the Application**

   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000/api/v1
   - API Docs: http://localhost:5000/api/v1/docs

## Detailed Commands

### Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# Start with build (after code changes)
docker-compose up --build -d

# Start specific service
docker-compose up backend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (database data will be lost!)
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

### View Logs

```bash
# View all logs
docker-compose logs

# Follow logs (real-time)
docker-compose logs -f

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Follow specific service logs
docker-compose logs -f backend
```

### Database Operations

#### Run Migrations

```bash
# Migrations run automatically when backend starts
# To run manually:
docker-compose exec backend flask db upgrade
```

#### Seed Demo Data

```bash
# Access backend container
docker-compose exec backend bash

# Inside the container, run:
python scripts/seed_demo_data.py

# Or in one command:
docker-compose exec backend python scripts/seed_demo_data.py
```

#### Access PostgreSQL

```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d cookie_shop_dev

# Dump database
docker-compose exec postgres pg_dump -U postgres cookie_shop_dev > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres -d cookie_shop_dev < backup.sql
```

### Container Management

#### Execute Commands in Containers

```bash
# Access backend container shell
docker-compose exec backend bash

# Access frontend container shell
docker-compose exec frontend sh

# Run Python commands
docker-compose exec backend python -c "from app import create_app; print('OK')"

# Install new Python package
docker-compose exec backend pip install package-name
docker-compose exec backend pip freeze > requirements.txt
```

#### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

#### View Service Status

```bash
# List running containers
docker-compose ps

# View resource usage
docker stats
```

### Development Workflow

#### Making Code Changes

**Backend Changes:**
```bash
# The backend uses gunicorn with --reload flag in docker-compose.yml
# Code changes will auto-reload

# If you need to rebuild:
docker-compose up --build backend
```

**Frontend Changes:**
```bash
# Frontend is built into static files
# You need to rebuild after changes:
docker-compose up --build frontend
```

#### Installing New Dependencies

**Backend:**
```bash
# Add package to requirements.txt
echo "new-package==1.0.0" >> backend/requirements.txt

# Rebuild backend
docker-compose up --build backend
```

**Frontend:**
```bash
# Access frontend builder or rebuild
docker-compose build frontend
```

### Troubleshooting

#### Port Already in Use

```bash
# Check what's using the port
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000

# Kill the process or change ports in docker-compose.yml
```

#### Database Connection Issues

```bash
# Check if database is ready
docker-compose exec postgres pg_isready -U postgres

# View database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

#### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database not ready - wait a few seconds
# 2. Migration failed - check migration files
# 3. Missing environment variables - check .env.docker
```

#### Clear Everything and Start Fresh

```bash
# Stop all containers
docker-compose down

# Remove all volumes (WARNING: deletes database!)
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Rebuild everything
docker-compose up --build
```

#### Frontend Not Loading

```bash
# Check if nginx is running
docker-compose ps frontend

# Check nginx logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up --build frontend
```

### Performance Tips

1. **Use Docker Desktop Settings**
   - Allocate at least 4GB RAM to Docker
   - Enable file sharing for the project directory

2. **Reduce Build Time**
   - Use `.dockerignore` files (already included)
   - Build without cache only when necessary: `docker-compose build --no-cache`

3. **Monitor Resources**
   ```bash
   docker stats
   ```

## Environment Variables

### Backend (.env.docker)

```
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/cookie_shop_dev
JWT_SECRET_KEY=your-jwt-secret
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
REDIS_URL=redis://redis:6379/0
```

### Frontend (.env.docker)

```
VITE_API_URL=http://localhost:5000/api/v1
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
VITE_APP_NAME=Cookie Shop
VITE_APP_URL=http://localhost:3000
```

## Production Deployment

For production deployment, create a separate `docker-compose.prod.yml` with:

1. Remove debug flags
2. Use production-grade secrets
3. Add proper SSL/TLS certificates
4. Use environment-specific configuration
5. Set up proper backup strategies
6. Configure health checks and monitoring

Example production command:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Nginx Docker Hub](https://hub.docker.com/_/nginx)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review container logs: `docker-compose logs`
3. Verify environment variables are set correctly
4. Ensure all required ports are available
