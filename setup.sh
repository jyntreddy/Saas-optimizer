#!/bin/bash
set -e

echo "Starting SaaS Optimizer setup..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Copy environment files if they don't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please update .env with your configuration"
fi

if [ ! -f backend/.env ]; then
    echo "Creating backend/.env file..."
    cp backend/.env.example backend/.env
    echo "Please update backend/.env with your configuration"
fi

if [ ! -f frontend/.env.local ]; then
    echo "Creating frontend/.env.local file..."
    cp frontend/.env.local.example frontend/.env.local
    echo "Please update frontend/.env.local with your configuration"
fi

# Build and start containers
echo "Building Docker containers..."
cd infra
docker-compose up -d --build

echo ""
echo "SaaS Optimizer is starting up!"
echo ""
echo "Services:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - nginx: http://localhost"
echo ""
echo "Run 'docker-compose logs -f' to view logs"
echo "Run 'docker-compose down' to stop all services"
