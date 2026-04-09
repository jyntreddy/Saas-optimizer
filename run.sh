#!/bin/bash

echo "🔍 Checking if Docker is running..."

if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo ""
    echo "Please start Docker Desktop and try again:"
    echo "  1. Open Docker Desktop from Applications"
    echo "  2. Wait for it to start completely"
    echo "  3. Run this script again"
    echo ""
    exit 1
fi

echo "✅ Docker is running!"
echo ""
echo "🚀 Starting SaaS Optimizer Platform..."
echo ""
echo "📦 Services being started:"
echo "   - PostgreSQL database (port 5432)"
echo "   - Redis cache (port 6379)"
echo "   - FastAPI backend (port 8000)"
echo "   - Streamlit frontend (port 8501)"
echo ""
echo "⏳ Building images (this may take a few minutes on first run)..."
echo ""

docker-compose up --build

echo ""
echo "✅ All services started!"
echo ""
echo "🌐 Access the application:"
echo "  Frontend: http://localhost:8501"
echo "  Backend API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 To stop: Press Ctrl+C, then run: docker-compose down"
echo ""
