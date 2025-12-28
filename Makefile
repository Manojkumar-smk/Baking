.PHONY: help build up down restart logs clean seed-data db-migrate db-shell test

# Default target
help:
	@echo "Cookie Shop Docker Commands"
	@echo "============================"
	@echo "make build        - Build all Docker images"
	@echo "make up           - Start all services"
	@echo "make down         - Stop all services"
	@echo "make restart      - Restart all services"
	@echo "make logs         - View all logs"
	@echo "make logs-backend - View backend logs"
	@echo "make logs-frontend- View frontend logs"
	@echo "make logs-db      - View database logs"
	@echo "make clean        - Stop and remove all containers, networks, and volumes"
	@echo "make seed-data    - Seed database with demo data"
	@echo "make db-migrate   - Run database migrations"
	@echo "make db-shell     - Access PostgreSQL shell"
	@echo "make backend-shell- Access backend container shell"
	@echo "make test         - Run tests in backend container"
	@echo "make status       - Show status of all containers"

# Build all images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:5000/api/v1"
	@echo ""
	@echo "Run 'make logs' to view logs"
	@echo "Run 'make seed-data' to populate demo data"

# Start all services with logs
up-logs:
	docker-compose up

# Stop all services
down:
	docker-compose down

# Restart all services
restart:
	docker-compose restart

# View all logs
logs:
	docker-compose logs -f

# View backend logs
logs-backend:
	docker-compose logs -f backend

# View frontend logs
logs-frontend:
	docker-compose logs -f frontend

# View database logs
logs-db:
	docker-compose logs -f postgres

# Clean everything (including volumes)
clean:
	docker-compose down -v
	@echo "All containers, networks, and volumes removed!"

# Seed database with demo data
seed-data:
	@echo "Seeding database with demo data..."
	docker-compose exec backend python scripts/seed_demo_data.py
	@echo "Demo data seeded successfully!"

# Run database migrations
db-migrate:
	docker-compose exec backend flask db upgrade

# Access PostgreSQL shell
db-shell:
	docker-compose exec postgres psql -U postgres -d cookie_shop_dev

# Access backend container shell
backend-shell:
	docker-compose exec backend bash

# Run tests in backend container
test:
	docker-compose exec backend pytest

# Show status of all containers
status:
	docker-compose ps

# Rebuild and restart specific service
rebuild-backend:
	docker-compose up --build -d backend

rebuild-frontend:
	docker-compose up --build -d frontend

# Initialize project (first time setup)
init: build up db-migrate seed-data
	@echo ""
	@echo "========================================"
	@echo "Cookie Shop is ready!"
	@echo "========================================"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:5000/api/v1"
	@echo ""
	@echo "Run 'make logs' to view application logs"
