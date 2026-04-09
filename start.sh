#!/bin/bash

echo "🚀 Starting SaaS Optimizer Platform..."
echo ""
echo "📦 Building and starting all services with Docker Compose..."
echo "   - PostgreSQL database (port 5432)"
echo "   - Redis cache (port 6379)"
echo "   - FastAPI backend (port 8000)"
echo "   - Streamlit frontend (port 8501)"
echo ""

# Build and start all services
docker-compose up --build

echo ""
echo "✅ All services started!"
echo ""
echo "Access the application:"
echo "  Frontend: http://localhost:8501"
echo "  Backend API Docs: http://localhost:8000/docs"
echo ""
