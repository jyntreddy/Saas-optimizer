# Makefile for SaaS Optimizer

.PHONY: help setup start stop restart logs clean test backend-shell frontend-shell db-migrate

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - copy env files
	@echo "Setting up environment files..."
	@test -f .env || cp .env.example .env
	@test -f backend/.env || cp backend/.env.example backend/.env
	@test -f frontend/.env.local || cp frontend/.env.local.example frontend/.env.local
	@echo "Setup complete! Please update environment files with your configuration."

start: ## Start all services
	@echo "Starting services..."
	cd infra && docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

stop: ## Stop all services
	@echo "Stopping services..."
	cd infra && docker-compose down

restart: ## Restart all services
	@echo "Restarting services..."
	cd infra && docker-compose restart

logs: ## View logs from all services
	cd infra && docker-compose logs -f

logs-backend: ## View backend logs
	cd infra && docker-compose logs -f backend

logs-frontend: ## View frontend logs
	cd infra && docker-compose logs -f frontend

clean: ## Stop and remove all containers, volumes, and images
	@echo "Cleaning up..."
	cd infra && docker-compose down -v --rmi all
	@echo "Cleanup complete!"

test: ## Run all tests
	@echo "Running backend tests..."
	cd backend && pytest
	@echo "Running frontend tests..."
	cd frontend && npm test

test-backend: ## Run backend tests with coverage
	cd backend && pytest --cov=app tests/

backend-shell: ## Open shell in backend container
	cd infra && docker-compose exec backend bash

frontend-shell: ## Open shell in frontend container
	cd infra && docker-compose exec frontend sh

db-migrate: ## Run database migrations
	cd infra && docker-compose exec backend alembic upgrade head

db-downgrade: ## Rollback last database migration
	cd infra && docker-compose exec backend alembic downgrade -1

db-shell: ## Open PostgreSQL shell
	cd infra && docker-compose exec postgres psql -U postgres -d saas_optimizer

build: ## Build all Docker images
	cd infra && docker-compose build

rebuild: ## Rebuild all Docker images from scratch
	cd infra && docker-compose build --no-cache

dev-backend: ## Run backend in development mode (local)
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run frontend in development mode (local)
	cd frontend && npm run dev

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

format: ## Format code
	cd backend && black app/ tests/
	cd frontend && npm run format

lint: ## Lint code
	cd backend && flake8 app/ tests/
	cd frontend && npm run lint
